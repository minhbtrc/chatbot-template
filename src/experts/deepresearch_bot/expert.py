"""
Deep Research Bot Expert that uses LangGraph workflow for comprehensive research.
"""
from typing import Any, Dict, Generator, AsyncGenerator, Union, List
import ast
import json
import re

from injector import inject
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch

from src.common.config import Config
from src.experts.base import BaseExpert
from src.base.components import MemoryInterface
from src.base.brains import BrainInterface
from src.common.logging import logger
from src.common.schemas import ChatResponse
import src.experts.deepresearch_bot.prompts as deepresearch_prompts
from .utils import (
    get_current_date,
    get_research_topic,
)
from .state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)

load_dotenv()


class DeepResearchExpert(BaseExpert):
    """
    Deep Research Expert that uses LangGraph workflow for comprehensive web research.
    
    This expert performs multi-step research using web search, reflection, and synthesis
    to provide comprehensive answers to complex questions.
    """
    
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
        self.graph = self._build_graph()

        logger.info("Deep Research Expert initialized with LangGraph workflow")

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create our Agent Graph
        builder = StateGraph(OverallState)  # type: ignore

        # Define the nodes we will cycle between
        builder.add_node("generate_query", self._generate_query)  # type: ignore
        builder.add_node("web_research", self._web_research)  # type: ignore
        builder.add_node("reflection", self._reflection)  # type: ignore
        builder.add_node("finalize_answer", self._finalize_answer)  # type: ignore

        # Set the entrypoint as `generate_query`
        builder.add_edge(START, "generate_query")
        # Add conditional edge to continue with search queries in a parallel branch
        builder.add_conditional_edges(
            "generate_query", self._continue_to_web_research, ["web_research", "finalize_answer"]  # type: ignore
        )
        # Reflect on the web research
        builder.add_edge("web_research", "reflection")
        # Evaluate the research
        builder.add_conditional_edges(
            "reflection", self._evaluate_research, ["web_research", "finalize_answer"]  # type: ignore
        )
        # Finalize the answer
        builder.add_edge("finalize_answer", END)

        return builder.compile(name="deep-search-agent")  # type: ignore

    def _generate_query(self, state: OverallState, config: RunnableConfig = None) -> QueryGenerationState:  # type: ignore
        """LangGraph node that generates search queries based on the User's question."""

        try:
            # Format the prompt
            current_date = get_current_date()
            formatted_prompt = deepresearch_prompts.query_writer_instructions.format(
                current_date=current_date,
                number_queries=state["initial_search_query_count"],
            )
            
            # Use the LLM client to generate structured output
            # messages = [{"role": "user", "content": formatted_prompt}]
            response = self.brain.think(history=state["messages"], system_message=formatted_prompt)
            
            # Parse the response to extract queries (simplified for now)
            # In a real implementation, you'd want to use structured output
            content = response.get("content", "")
            match = re.search(r"```json\s*\n*(.*?)\n*```", content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                raise ValueError(f"No match found for content: {content}")
            try:
                output = ast.literal_eval(content)
            except Exception as e:
                output = json.loads(content)
            
            return {
                "query_list": output["query"][:state["initial_search_query_count"]],
                "do_research": output["do_research"]
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[generate_query node ERROR] {e}", exc_info=True)
            return {
                "query_list": [],
                "do_research": False
            }

    def _continue_to_web_research(self, state: QueryGenerationState):
        """LangGraph node that sends the search queries to the web research node."""
        if state["do_research"] is True:
            return [
                Send("web_research", {"search_query": search_query, "id": str(idx)})
                for idx, search_query in enumerate(state["query_list"])
            ]
        else:
            return "finalize_answer"

    def _web_research(self, state: WebSearchState, config: RunnableConfig = None) -> Dict[str, Any]:  # type: ignore
        """LangGraph node that performs web research using the native Google Search API tool."""
        try:
            # search_tool = CustomSearchTool()
            search_tool = TavilySearch()
            results = search_tool.run(state["search_query"])

            sources_gathered: List[Dict[str, Any]] = []
            snippet_blocks: List[str] = []

            # Tavily returns results in a different format - extract the content
            if isinstance(results, str):
                # If results is a string, it might be the formatted content
                web_research_result = [results] if results.strip() else ["No useful results found"]
                return {
                    "sources_gathered": [],
                    "search_query": [state["search_query"]],
                    "web_research_result": web_research_result,
                }
            
            # Handle Tavily's structured response format
            if isinstance(results, dict):
                organic_results = results.get("results", [])
            elif isinstance(results, list):
                organic_results = results
            else:
                organic_results = []

            for i, result in enumerate(organic_results):
                title = result.get("title", "").strip()
                url = result.get("url", "").strip()  # Tavily uses "url" instead of "link"
                snippet = result.get("content", "").strip()  # Tavily uses "content" instead of "snippet"

                if not title or not url:
                    continue  # skip bad results

                # Define short_url as a numbered citation marker
                short_url = f"[{i + 1}]"
                value = url  # or expand this to dict(url, title) if needed

                sources_gathered.append({
                    "title": title,
                    "short_url": short_url,
                    "value": value,
                    "snippet": snippet,
                })

                snippet_blocks.append(f"{short_url} {title}: {snippet}")

            web_research_result = ["\n".join(snippet_blocks)] if snippet_blocks else ["No useful results found"]

            return {
                "sources_gathered": sources_gathered,
                "search_query": [state["search_query"]],
                "web_research_result": web_research_result,
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[web_research node ERROR] {e}", exc_info=True)
            return {
                "sources_gathered": [],
                "search_query": [state.get("search_query", "unknown")],
                "web_research_result": ["Error: web search failed"]
            }

    def _reflection(self, state: OverallState, config: RunnableConfig = None) -> ReflectionState:  # type: ignore
        """LangGraph node that identifies knowledge gaps and generates potential follow-up queries."""
        try:
            # Increment the research loop count
            state["research_loop_count"] = state.get("research_loop_count", 0) + 1  # type: ignore

            # Format the prompt
            current_date = get_current_date()
            formatted_prompt = deepresearch_prompts.reflection_instructions.format(
                current_date=current_date,
                research_topic=get_research_topic(state["messages"]),  # type: ignore
                summaries="\n\n---\n\n".join(state["web_research_result"]),  # type: ignore
            )
            
            # Use LLM client for reflection
            response = self.brain.think([{"role": "user", "content": formatted_prompt}])
            
            # Parse response (simplified - in real implementation use structured output)
            # content = response.get("content", "")
            # lines = content.split('\n')
            content = response.get("content", "")
            match = re.search(r"```json\s*\n*(.*?)\n*```", content, re.DOTALL)
            if match:
                content = match.group(1)
            else:
                raise ValueError(f"No match found for content: {content}")
            
            try:
                output = ast.literal_eval(content)
            except Exception as e:
                output = json.loads(content)
            
            # Simple parsing logic (would be better with structured output)
            is_sufficient = output["is_sufficient"]
            knowledge_gap = output["knowledge_gap"]
            follow_up_queries = output["follow_up_queries"]#[line.strip() for line in lines if line.strip().startswith('-')][:2]

            return {
                "is_sufficient": is_sufficient,
                "knowledge_gap": knowledge_gap,
                "follow_up_queries": follow_up_queries,
                "research_loop_count": state["research_loop_count"],
                "number_of_ran_queries": len(state["search_query"]),  # type: ignore
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[reflection node ERROR] {e}", exc_info=True)
            return {
                "is_sufficient": False,
                "knowledge_gap": "Error in reflection node",
                "follow_up_queries": [],
                "research_loop_count": state["research_loop_count"],
                "number_of_ran_queries": len(state["search_query"]),  # type: ignore
            }

    def _evaluate_research(
        self,
        state: ReflectionState,
        config: RunnableConfig = None,  # type: ignore
    ) -> Union[str, List[Send]]:
        """LangGraph routing function that determines the next step in the research flow."""
        
        if state["is_sufficient"] or state["research_loop_count"] >= self.config.max_research_loops:
            return "finalize_answer"
        else:
            return [
                Send(
                    "web_research",
                    {
                        "search_query": follow_up_query,
                        "id": str(state["number_of_ran_queries"] + int(idx)),
                    },
                )
                for idx, follow_up_query in enumerate(state["follow_up_queries"])  # type: ignore
            ]

    def _finalize_answer(self, state: OverallState, config: RunnableConfig = None) -> Dict[str, Any]:  # type: ignore
        """LangGraph node that finalizes the research summary."""
        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = deepresearch_prompts.answer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),  # type: ignore
            summaries="\n---\n\n".join(state["web_research_result"]),  # type: ignore
        )

        # Use LLM client for final answer
        response = self.brain.think([{"role": "user", "content": formatted_prompt}])
        content = response.get("content", "")

        # Replace the short urls with the original urls and add all used urls to the sources_gathered
        unique_sources = []
        for source in state["sources_gathered"]:  # type: ignore
            if source.get("short_url", "") in content:  # type: ignore
                content = content.replace(
                    source["short_url"], source["value"]  # type: ignore
                )
                unique_sources.append(source)  # type: ignore

        return {
            "messages": [AIMessage(content=content)],
            "sources_gathered": unique_sources,
        }

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
    
    def _get_initial_state(self, query: str, conversation_id: str, user_id: str) -> OverallState:
        # Prepare history and add user message
        history = self._prepare_history(query, conversation_id, user_id)
        
        # Create initial state for the workflow
        initial_state: OverallState = {
            "messages": history,
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": self.config.number_of_initial_queries,
            "max_research_loops": self.config.max_research_loops,
            "research_loop_count": 0,
        }
        return initial_state
    
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
        initial_state = self._get_initial_state(query=query, conversation_id=conversation_id, user_id=user_id)
        
        # Run the research workflow
        logger.debug("Starting deep research workflow")
        try:
            result = self.graph.invoke(initial_state, {"recursion_limit": self.config.graph_recursion_limit})
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
        initial_state = self._get_initial_state(query=query, conversation_id=conversation_id, user_id=user_id)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        try:
            result = await self.graph.ainvoke(initial_state)
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
        initial_state = self._get_initial_state(query=sentence, conversation_id=conversation_id, user_id=user_id)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        
        full_response: str = ""
        
        for chunk in self.graph.stream(initial_state, stream_mode="messages"):
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
        initial_state = self._get_initial_state(query=sentence, conversation_id=conversation_id, user_id=user_id)
        
        # Run the research workflow asynchronously
        logger.debug("Starting async deep research workflow")
        
        full_response: str = ""
        
        async for chunk in self.graph.astream(initial_state, stream_mode="messages"):
            full_response += chunk[0].content
            yield chunk[0].content
        
        logger.debug(f"Brain async streaming response completed: {full_response[:100]}...")
        
        # Save the assistant message to memory
        logger.debug("Saving assistant message to memory")
        self.memory.add_message(
            role="assistant", content=full_response, conversation_id=conversation_id
        )
        logger.debug("Assistant message saved to memory")
