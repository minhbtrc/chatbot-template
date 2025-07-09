from typing import Any, Generator, AsyncGenerator

from injector import inject

from src.common.config import Config
from src.experts.base import BaseExpert
from src.base.components import MemoryInterface
from src.base.brains import BrainInterface
from src.common.logging import logger
from src.common.schemas import ChatResponse
from src.experts.deepresearch_bot.graphs.simple_workflow import SimpleWorkflow


class DeepResearchExpert(BaseExpert):
    @inject
    def __init__(
        self,
        config: Config,
        memory: MemoryInterface,
        brain: BrainInterface,
    ):
        """
        Initialize the Deep Research Expert.
        
        Args:
            config: Application configuration
            memory: Memory implementation for storing conversation history
            brain: Brain implementation (not used in this expert as it uses LangGraph)
        """
        super().__init__(config, memory, brain)
        self.simple_workflow = SimpleWorkflow(config, memory, brain)

        logger.info("Deep Research Expert initialized")

    def _prepare_context(self, sentence: str, conversation_id: str, user_id: str, **kwargs: Any) -> str:
        """
        Prepare context for the deep research workflow.
        
        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            **kwargs: Additional arguments
            
        Returns:
            Empty string as context is handled by the LangGraph workflow
        """
        return ""
    
    async def _aprepare_context(self, sentence: str, user_id: str, **kwargs: Any) -> str:
        """
        Prepare context for the deep research workflow (async version).
        
        Args:
            sentence: User input
            user_id: ID of the user
            **kwargs: Additional arguments
            
        Returns:
            Empty string as context is handled by the LangGraph workflow
        """
        return ""
    
    def process(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a user query using the deep research workflow.
        
        Args:
            query: User input query
            conversation_id: ID for the conversation
            user_id: ID of the user
            
        Returns:
            ChatResponse with research results
        """
        history = self._prepare_history(query, conversation_id, user_id)
        initial_state = self.simple_workflow.get_initial_state(history=history)
        
        # Run the research workflow
        logger.debug("Starting deep research workflow")
        try:
            result = self.simple_workflow.graph.invoke(initial_state, {"recursion_limit": self.config.graph_recursion_limit})
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[graph workflow ERROR] {e}", exc_info=True)
        
        # Extract the final response
        if result.get("messages") and len(result["messages"]) > 0:
            final_message = result["messages"][-1]
            response_content = final_message.content
        else:
            response_content = "I apologize, but I couldn't generate a research response."
        
        logger.debug(f"Deep research workflow completed: {response_content[:100]}...")
        
        # Save the assistant response to memory
        self.memory.add_message(
            role="assistant", 
            content=response_content, 
            conversation_id=conversation_id
        )
        
        # Return structured response
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id or "default",
            additional_kwargs={
                "sources": result.get("sources_gathered", []),
                "research_loops": result.get("research_loop_count", 0)
            }
        )
    
    async def aprocess(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a user query using the deep research workflow (async version).
        
        Args:
            query: User input query
            conversation_id: ID for the conversation
            user_id: ID of the user
            
        Returns:
            ChatResponse with research results
        """
        history = self._prepare_history(query, conversation_id, user_id)
        initial_state = self.simple_workflow.get_initial_state(history=history)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        try:
            result = await self.simple_workflow.graph.ainvoke(initial_state, {"recursion_limit": self.config.graph_recursion_limit})
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[graph workflow ERROR] {e}", exc_info=True)
        
        # Extract the final response
        if result.get("messages") and len(result["messages"]) > 0:
            final_message = result["messages"][-1]
            response_content = final_message.content
        else:
            response_content = "I apologize, but I couldn't generate a research response."
        
        logger.debug(f"Async deep research workflow completed: {response_content[:100]}...")
        
        # Save the assistant response to memory
        self.memory.add_message(
            role="assistant", 
            content=response_content, 
            conversation_id=conversation_id
        )
        
        # Return structured response
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id or "default",
            additional_kwargs={
                "sources": result.get("sources_gathered", []),
                "research_loops": result.get("research_loop_count", 0)
            }
        )
    
    def stream_call(self, sentence: str, conversation_id: str, user_id: str) -> Generator[str, None, None]:
        """
        Stream a response using the deep research workflow.
        
        Note: LangGraph doesn't support streaming by default, so this falls back to
        processing the full request and yielding the complete response.
        
        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            
        Yields:
            Chunks of the response content
        """
        # For now, process the full request and yield the result
        history = self._prepare_history(sentence, conversation_id, user_id)
        initial_state = self.simple_workflow.get_initial_state(history=history)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        
        full_response: str = ""
        
        for chunk in self.simple_workflow.graph.stream(initial_state, {"recursion_limit": self.config.graph_recursion_limit}, stream_mode="messages"):
            full_response += chunk[0].content
            yield chunk[0].content
        
        logger.debug(f"Brain async streaming response completed: {full_response[:100]}...")
        
        # Save the assistant message to memory
        logger.debug("Saving assistant message to memory")
        self.memory.add_message(
            role="assistant", content=full_response, conversation_id=conversation_id
        )
        logger.debug("Assistant message saved to memory")
    
    async def astream_call(self, sentence: str, conversation_id: str, user_id: str) -> AsyncGenerator[str, None]:
        """
        Stream a response using the deep research workflow (async version).
        
        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            
        Yields:
            Chunks of the response content
        """
        # For now, process the full request and yield the result
        history = self._prepare_history(sentence, conversation_id, user_id)
        initial_state = self.simple_workflow.get_initial_state(history=history)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        
        full_response: str = ""
        
        async for chunk in self.simple_workflow.graph.astream(initial_state, {"recursion_limit": self.config.graph_recursion_limit}, stream_mode="messages"):
            full_response += chunk[0].content
            yield chunk[0].content
        
        logger.debug(f"Brain async streaming response completed: {full_response[:100]}...")
        
        # Save the assistant message to memory
        logger.debug("Saving assistant message to memory")
        self.memory.add_message(
            role="assistant", content=full_response, conversation_id=conversation_id
        )
        logger.debug("Assistant message saved to memory")
