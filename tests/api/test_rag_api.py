#!/usr/bin/env python3
"""
Test script for the RAG API document processing endpoint.
"""
import pytest
import requests
import tempfile
import os

def create_test_pdf() -> str:
    """Create a simple test PDF file for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
        
        # Create a simple PDF with some text
        c = canvas.Canvas(temp_path, pagesize=letter)
        c.drawString(100, 750, "Test Document for RAG API")
        c.drawString(100, 730, "This is a test document to verify the RAG API functionality.")
        c.drawString(100, 710, "It contains some sample text that can be indexed and searched.")
        c.drawString(100, 690, "The document processing should work correctly with this content.")
        c.save()
        
        return temp_path
    except ImportError:
        print("reportlab not installed. Creating a simple text file instead.")
        # Create a simple text file if reportlab is not available
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w') as temp_file:
            temp_file.write("Test Document for RAG API\n")
            temp_file.write("This is a test document to verify the RAG API functionality.\n")
            temp_file.write("It contains some sample text that can be indexed and searched.\n")
            temp_file.write("The document processing should work correctly with this content.\n")
            return temp_file.name

@pytest.mark.integration
def test_process_document():
    """Test the process-document endpoint."""
    api_url = "http://localhost:8080"
    print("Creating test document...")
    test_file_path = create_test_pdf()
    
    try:
        print(f"Test file created: {test_file_path}")
        print(f"File exists: {os.path.exists(test_file_path)}")
        print(f"File size: {os.path.getsize(test_file_path)} bytes")
        
        # Test the API endpoint
        url = f"{api_url}/api/v1/rag/process-document"
        
        with open(test_file_path, 'rb') as f:
            files = {'file': (os.path.basename(test_file_path), f, 'application/pdf')}
            
            print(f"Sending request to: {url}")
            response = requests.post(url, files=files)
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            # Use assertion instead of return
            assert response.status_code == 200, f"Document processing failed with status {response.status_code}: {response.text}"
            print("✅ Document processing successful!")
                
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running - skipping integration test")
    except Exception as e:
        pytest.fail(f"Error testing API: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
            print(f"Cleaned up test file: {test_file_path}")

@pytest.mark.integration
def test_query():
    """Test the query endpoint."""
    api_url = "http://localhost:8080"
    url = f"{api_url}/api/v1/rag/query"
    
    data = {
        "query": "What is this document about?",
        "conversation_id": "test_conversation",
        "max_chunks": 5
    }
    
    try:
        print(f"Sending query to: {url}")
        response = requests.post(url, json=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Use assertion instead of return
        assert response.status_code == 200, f"Query failed with status {response.status_code}: {response.text}"
        print("✅ Query successful!")
            
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running - skipping integration test")
    except Exception as e:
        pytest.fail(f"Error testing query: {e}")

# Keep the original script functionality for manual testing
if __name__ == "__main__":
    print("Testing RAG API...")
    print("=" * 50)
    
    # Test document processing
    print("\n1. Testing document processing...")
    try:
        test_process_document()
        doc_success = True
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        doc_success = False
    
    # Test querying (only if document processing succeeded)
    if doc_success:
        print("\n2. Testing query...")
        try:
            test_query()
            query_success = True
        except Exception as e:
            print(f"❌ Query failed: {e}")
            query_success = False
    else:
        print("\n2. Skipping query test due to document processing failure")
        query_success = False
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Document Processing: {'✅ PASS' if doc_success else '❌ FAIL'}")
    print(f"Query: {'✅ PASS' if query_success else '❌ FAIL'}") 