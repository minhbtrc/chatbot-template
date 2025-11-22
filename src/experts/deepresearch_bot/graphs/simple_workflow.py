"""
Deep Research Bot Expert that uses LangGraph workflow for comprehensive research.
"""
from typing import Any, Dict, Union, List
import ast
import json
import re

from injector import inject
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch

from src.common.config import Config
from src.base.components import MemoryInterface
from src.base.brains import BrainInterface
from src.common.logging import logger
import src.experts.deepresearch_bot.prompts as deepresearch_prompts
from src.experts.deepresearch_bot.utils import (
    get_current_date,
    get_research_topic,
)
from src.experts.deepresearch_bot.state import (
    OverallState,
    ƒ,
    ReflectionState,
    WebSearchState,
)
from src.experts.deepresearch_bot.models import WebSearchResult


class SimpleWorkflow:
    """
    Deep Research Expert that uses LangGraph workflow for comprehensive web research.
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
        self.config = config
        self.memory = memory
        self.brain = brain
        self.graph = self._build_graph()

    def get_initial_state(self, history: List[Dict[str, Any]]) -> OverallState:
        # Create initial state for the workflow
        initial_state: OverallState = {
            "messages": history,
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": self.config.number_of_initial_queries,
            "max_research_loops": self.config.max_research_loops,
            "research_loop_count": 0,
            "current_queries": [],
        }
        return initial_state

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
                "current_queries": [
                    q["query"] if isinstance(q, dict) else q
                    for q in output["query"][:state["initial_search_query_count"]]
                ],
                "do_research": output["do_research"]
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[generate_query node ERROR] {e}", exc_info=True)
            return {
                "query_list": [],
                "current_queries": [],
                "do_research": False
            }

    def _continue_to_web_research(self, state: OverallState):
        """LangGraph node that sends the search queries to the web research node."""
        if state.get("current_queries") and len(state["current_queries"]) > 0:
            return "web_research"
        else:
            return "finalize_answer"

    def _web_research(self, state: OverallState, config: RunnableConfig = None) -> Dict[str, Any]:  # type: ignore
        """LangGraph node that performs web research using the native Google Search API tool."""
        try:
            # search_tool = CustomSearchTool()
            search_tool = TavilySearch()
            
            all_sources_gathered = []
            all_web_research_results = []
            all_search_queries = []
            
            # Iterate over all current queries
            for idx, query in enumerate(state.get("current_queries", [])):
                try:
                    results = search_tool.run(query)
                    all_search_queries.append(query)
        
                    sources_gathered: List[Dict[str, Any]] = []
                    snippet_blocks: List[str] = []
        
                    # Tavily returns results in a different format - extract the content
                    if isinstance(results, str):
                        # If results is a string, it might be the formatted content
                        web_research_result = results if results.strip() else WebSearchResult.NO_USEFUL_RESULTS.value
                        all_web_research_results.append(web_research_result)
                        continue
                    
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
                        # We need unique IDs across all queries, so use a combination of query index and result index
                        short_url = f"[{len(state.get('sources_gathered', [])) + len(all_sources_gathered) + 1}]"
                        value = url
        
                        sources_gathered.append({
                            "title": title,
                            "short_url": short_url,
                            "value": value,
                            "snippet": snippet,
                        })
        
                        snippet_blocks.append(f"{short_url} {title}: {snippet}")
        
                    web_research_result = "\n".join(snippet_blocks) if snippet_blocks else WebSearchResult.NO_USEFUL_RESULTS.value
                    all_web_research_results.append(web_research_result)
                    all_sources_gathered.extend(sources_gathered)
                    
                except Exception as e:
                    logger.error(f"Error searching for query '{query}': {e}")
                    all_web_research_results.append(WebSearchResult.ERROR.value)

            return {
                "sources_gathered": all_sources_gathered,
                "search_query": all_search_queries,
                "web_research_result": all_web_research_results,
                "current_queries": [],  # Clear current queries after processing
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[web_research node ERROR] {e}", exc_info=True)
            return {
                "sources_gathered": [],
                "search_query": [],
                "web_research_result": [],
                "current_queries": []
            }

    def _reflection(self, state: OverallState, config: RunnableConfig = None) -> ReflectionState:  # type: ignore
        """LangGraph node that identifies knowledge gaps and generates potential follow-up queries."""
        try:
            # Increment the research loop count
            state["research_loop_count"] = state.get("research_loop_count", 0) + 1  # type: ignore

            # Format the prompt
            current_date = get_current_date()
            summaries = "\n\n---\n\n".join(
                [
                    "Query: {query}\n\nSearch Results: {dummy_result}".format(
                        query=query,
                        dummy_result='\n'.join([r for r in result if r not in [WebSearchResult.NO_USEFUL_RESULTS.value, WebSearchResult.ERROR.value]])
                    )
                    for query, result in zip(state["search_query"], state["web_research_result"])
                ]
            )
            formatted_prompt = deepresearch_prompts.reflection_instructions.format(
                current_date=current_date,
                research_topic=get_research_topic(state["messages"]),  # type: ignore
                summaries=summaries,
            )
            
            # Use LLM client for reflection
            response = self.brain.think([{"role": "user", "content": formatted_prompt}])
            
            # Parse response (simplified - in real implementation use structured output)
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

            # Deduplicate queries
            past_queries = set(state.get("search_query", []))
            unique_follow_up_queries = [
                q for q in follow_up_queries 
                if q not in past_queries and q not in state.get("current_queries", [])
            ]

            return {
                "is_sufficient": is_sufficient,
                "knowledge_gap": knowledge_gap,
                "follow_up_queries": unique_follow_up_queries,
                "research_loop_count": state["research_loop_count"],
                "number_of_ran_queries": len(state["search_query"]),  # type: ignore
                "current_queries": unique_follow_up_queries,
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
                "current_queries": [],
            }

    def _evaluate_research(
        self,
        state: ReflectionState,
        config: RunnableConfig = None,  # type: ignore
    ) -> str:
        """LangGraph routing function that determines the next step in the research flow."""
        
        if (
            state["is_sufficient"] 
            or state["research_loop_count"] >= self.config.max_research_loops
            or not state.get("current_queries")  # Stop if no new queries
        ):
            return "finalize_answer"
        else:
            return "web_research"

    def _finalize_answer(self, state: OverallState, config: RunnableConfig = None) -> Dict[str, Any]:  # type: ignore
        """LangGraph node that finalizes the research summary."""
        # Format the prompt
        current_date = get_current_date()
        summaries = "\n\n---\n\n".join(
            [
                "Query: {query}\n\nSearch Results: {dummy_result}".format(
                    query=query,
                    dummy_result='\n'.join([r for r in result if r not in [WebSearchResult.NO_USEFUL_RESULTS.value, WebSearchResult.ERROR.value]])
                )
                for query, result in zip(state["search_query"], state["web_research_result"])
            ]
        )
        formatted_prompt = deepresearch_prompts.answer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),  # type: ignore
            summaries=summaries,
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
