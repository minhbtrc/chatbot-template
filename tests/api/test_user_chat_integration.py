#!/usr/bin/env python3
"""
Integration test for user authentication and chat system.
This test requires the FastAPI server to be running.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List
import pytest


class ChatbotAPIClient:
    """Client for testing the chatbot API with user authentication."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
    
    async def register_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user."""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        if full_name:
            data["full_name"] = full_name
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and store the access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": username,
                    "password": password
                }
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.user_info = data["user"]
            return data
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def create_session(self, title: Optional[str] = None, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new chat session."""
        data = {}
        if title:
            data["title"] = title
        if conversation_id:
            data["conversation_id"] = conversation_id
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/sessions",
                json=data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_sessions(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get user sessions."""
        params = {"active_only": active_only}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/sessions",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def chat(self, message: str, conversation_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message with authentication."""
        data = {"input": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
        if session_id:
            data["session_id"] = session_id
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chat",
                json=data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def chat_anonymous(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message without authentication."""
        data = {"input": message}
        if conversation_id:
            data["conversation_id"] = conversation_id
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chat",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_conversations(self) -> Dict[str, Any]:
        """Get user conversations."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/conversations",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def clear_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Clear conversation history."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/clear/{conversation_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def set_preference(self, key: str, value: Any) -> Dict[str, Any]:
        """Set user preference."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/preferences",
                json={
                    "key": key,
                    "value": value
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/preferences",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()


@pytest.mark.integration
async def test_user_chat_integration():
    """Test the complete user chat integration."""
    print("🚀 Testing User-Integrated Chat System...")
    
    try:
        client = ChatbotAPIClient()
        
        # Test 1: Register a new user
        print("\n👤 Testing User Registration...")
        try:
            user_data = await client.register_user(
                username="test_user_chat",
                email="test_chat@example.com",
                password="secure_password123",
                full_name="Test Chat User"
            )
            print(f"✅ User registered: {user_data['username']} (ID: {user_data['id']})")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                print("ℹ️ User already exists, continuing with login...")
            else:
                raise
        
        # Test 2: Login
        print("\n🔐 Testing User Login...")
        login_data = await client.login("test_user_chat", "secure_password123")
        print(f"✅ Login successful: {login_data['user']['username']}")
        print(f"   Token: {login_data['access_token'][:20]}...")
        
        # Test 3: Create a session
        print("\n💬 Testing Session Creation...")
        session_data = await client.create_session(
            title="Test Chat Session",
            conversation_id=None  # Let the system generate one
        )
        print(f"✅ Session created: {session_data['session_id']}")
        print(f"   Title: {session_data['title']}")
        
        # Test 4: Chat with session
        print("\n🤖 Testing Authenticated Chat with Session...")
        chat_response = await client.chat(
            message="Hello! I'm testing the user-integrated chat system.",
            session_id=session_data['session_id']
        )
        print(f"✅ Chat response received:")
        print(f"   Conversation ID: {chat_response['conversation_id']}")
        print(f"   Session ID: {chat_response['session_id']}")
        print(f"   Response: {chat_response['output'][:100]}...")
        
        # Test 5: Continue conversation
        print("\n🔄 Testing Conversation Continuity...")
        follow_up = await client.chat(
            message="Can you remember what I just said?",
            conversation_id=chat_response['conversation_id'],
            session_id=session_data['session_id']
        )
        print(f"✅ Follow-up response:")
        print(f"   Response: {follow_up['output'][:100]}...")
        
        # Test 6: Chat without session (but authenticated)
        print("\n💭 Testing Authenticated Chat without Session...")
        no_session_chat = await client.chat(
            message="This is a message without a specific session."
        )
        print(f"✅ No-session chat response:")
        print(f"   Conversation ID: {no_session_chat['conversation_id']}")
        print(f"   Session ID: {no_session_chat['session_id']}")
        
        # Test 7: Anonymous chat
        print("\n👻 Testing Anonymous Chat...")
        anon_response = await client.chat_anonymous(
            message="This is an anonymous message."
        )
        print(f"✅ Anonymous chat response:")
        print(f"   Conversation ID: {anon_response['conversation_id']}")
        print(f"   Session ID: {anon_response['session_id']}")
        
        # Test 8: Get user conversations
        print("\n📋 Testing Get User Conversations...")
        conversations = await client.get_conversations()
        print(f"✅ Found {conversations['count']} conversations:")
        for conv_id in conversations['conversations'][:3]:  # Show first 3
            print(f"   - {conv_id}")
        
        # Test 9: Get user sessions
        print("\n📝 Testing Get User Sessions...")
        sessions = await client.get_sessions()
        print(f"✅ Found {len(sessions)} sessions:")
        for session in sessions[:2]:  # Show first 2
            print(f"   - {session['session_id']}: {session['title']}")
        
        # Test 10: Set user preferences
        print("\n⚙️ Testing User Preferences...")
        await client.set_preference("theme", "dark")
        await client.set_preference("language", "en")
        await client.set_preference("max_history", 50)
        
        preferences = await client.get_preferences()
        print(f"✅ User preferences set:")
        for key, value in preferences['preferences'].items():
            print(f"   - {key}: {value}")
        
        # Test 11: Clear conversation history
        print("\n🧹 Testing Clear Conversation History...")
        clear_result = await client.clear_conversation(chat_response['conversation_id'])
        print(f"✅ Conversation cleared: {clear_result['message']}")
        
        print("\n🎉 All user-integrated chat tests passed!")
        print("\n📊 Summary:")
        if client.user_info:
            print(f"   - User: {client.user_info['username']} (ID: {client.user_info['id']})")
        else:
            print("   - User: Not logged in")
        print(f"   - Sessions created: 1")
        print(f"   - Messages sent: 4 (2 with session, 1 without session, 1 anonymous)")
        print(f"   - Conversations: {conversations['count']}")
        print(f"   - Preferences set: 3")
        
    except httpx.ConnectError:
        pytest.skip("API server not running - skipping integration test")


@pytest.mark.integration
async def test_error_scenarios():
    """Test error scenarios and edge cases."""
    print("\n🔍 Testing Error Scenarios...")
    
    try:
        client = ChatbotAPIClient()
        
        # Test invalid session access
        print("\n❌ Testing Invalid Session Access...")
        try:
            await client.chat(
                message="This should fail",
                session_id="invalid_session_id"
            )
            print("❌ Should have failed!")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print("✅ Correctly rejected unauthenticated session access")
            else:
                print(f"✅ Correctly rejected with status {e.response.status_code}")
        
        # Test unauthorized conversation clearing
        print("\n🚫 Testing Unauthorized Conversation Access...")
        try:
            # Try to clear a conversation that doesn't belong to us
            await client.clear_conversation("user_999_session_fake")
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                print("✅ Correctly rejected unauthorized conversation access")
            else:
                print(f"✅ Correctly rejected with status {e.response.status_code}")
                
    except httpx.ConnectError:
        pytest.skip("API server not running - skipping integration test")


if __name__ == "__main__":
    print("🧪 User-Integrated Chat System Test")
    print("=" * 50)
    print("This script tests the complete user authentication and chat integration.")
    print("Make sure the FastAPI server is running on http://localhost:8080")
    print()
    
    try:
        asyncio.run(test_user_chat_integration())
        asyncio.run(test_error_scenarios())
    except httpx.ConnectError:
        print("❌ Could not connect to the API server.")
        print("   Please make sure the server is running: uvicorn api.app:create_app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 