from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import time

from injector import inject

from src.common.config import Config
from src.base.components import VectorDatabaseInterface, EmbeddingInterface
from src.base.brains import BrainInterface
from src.common.logging import logger

from .prompts import LLM_AS_JUDGE_PROMPT

if TYPE_CHECKING:
    from src.experts.rag_bot.expert import RAGBotExpert


@dataclass
class EvaluationResult:
    """
    Data class for storing evaluation results.
    """
    query: str
    expected_context: Optional[str] = None
    expected_doc_id: Optional[str] = None
    expected_snippet: Optional[str] = None
    retrieved_context: Optional[List[str]] = field(default_factory=list)
    retrieved_doc_ids: Optional[List[str]] = field(default_factory=list)
    retrieval_scores: Optional[List[float]] = field(default_factory=list)
    generated_response: Optional[str] = None
    expected_response: Optional[str] = None
    retrieval_score: Optional[float] = None
    generation_score: Optional[float] = None
    generation_rating: Optional[int] = None
    generation_rationale: Optional[str] = None
    faithfulness_score: Optional[float] = None
    quality_score: Optional[float] = None
    retrieval_latency: Optional[float] = None
    generation_latency: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        if self.retrieved_context is None:
            self.retrieved_context = []
        if self.retrieved_doc_ids is None:
            self.retrieved_doc_ids = []
        if self.retrieval_scores is None:
            self.retrieval_scores = []
        if self.metadata is None:
            self.metadata = {}


class BaseEvaluationMetric(ABC):
    """
    Base class for evaluation metrics.
    """
    
    @abstractmethod
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        """
        Calculate the metric score for the given evaluation result.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the metric.
        """
        pass


class TopKAccuracyMetric(BaseEvaluationMetric):
    """
    Metric to evaluate if expected document is found in top-K retrieved results.
    """
    
    def __init__(self, k: int = 5):
        self.k = k
    
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        """
        Calculate if the expected document/context is found in the top-k retrieved results.
        Returns 1.0 if found, 0.0 if not found.
        """
        if not evaluation_result.expected_context and not evaluation_result.expected_doc_id:
            return 0.0
        
        if not evaluation_result.retrieved_context and not evaluation_result.retrieved_doc_ids:
            return 0.0
        
        # Check by document ID if available
        if evaluation_result.expected_doc_id and evaluation_result.retrieved_doc_ids:
            top_k_doc_ids = evaluation_result.retrieved_doc_ids[:self.k]
            if evaluation_result.expected_doc_id in top_k_doc_ids:
                return 1.0
        
        # Check by content if no doc IDs available
        if evaluation_result.expected_context and evaluation_result.retrieved_context:
            expected = evaluation_result.expected_context.lower()
            top_k_contexts = evaluation_result.retrieved_context[:self.k]
            for context in top_k_contexts:
                if expected in context.lower():
                    return 1.0
        
        return 0.0
    
    def get_name(self) -> str:
        return f"top_{self.k}_accuracy"


class MeanReciprocalRankMetric(BaseEvaluationMetric):
    """
    Mean Reciprocal Rank (MRR) metric - rewards correct documents appearing higher in ranking.
    """
    
    def __init__(self, k: int = 10):
        self.k = k
    
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        """
        Calculate MRR score. Returns 1/rank if found, 0 if not found in top-k.
        """
        if not evaluation_result.expected_context and not evaluation_result.expected_doc_id:
            return 0.0
        
        if not evaluation_result.retrieved_context and not evaluation_result.retrieved_doc_ids:
            return 0.0
        
        # Check by document ID if available
        if evaluation_result.expected_doc_id and evaluation_result.retrieved_doc_ids:
            top_k_doc_ids = evaluation_result.retrieved_doc_ids[:self.k]
            for rank, doc_id in enumerate(top_k_doc_ids, 1):
                if doc_id == evaluation_result.expected_doc_id:
                    return 1.0 / rank
        
        # Check by content if no doc IDs available
        if evaluation_result.expected_context and evaluation_result.retrieved_context:
            expected = evaluation_result.expected_context.lower()
            top_k_contexts = evaluation_result.retrieved_context[:self.k]
            for rank, context in enumerate(top_k_contexts, 1):
                if expected in context.lower():
                    return 1.0 / rank
        
        return 0.0
    
    def get_name(self) -> str:
        return f"mrr_at_{self.k}"


class RecallAtKMetric(BaseEvaluationMetric):
    """
    Recall@K metric - measures how many correct documents appear in top-K.
    """
    
    def __init__(self, k: int = 5):
        self.k = k
    
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        """
        Calculate Recall@K. For single expected document, this is equivalent to Top-K accuracy.
        """
        # For now, implement as Top-K accuracy since we typically have one expected document
        # This can be extended for multiple expected documents
        return TopKAccuracyMetric(self.k).calculate(evaluation_result)
    
    def get_name(self) -> str:
        return f"recall_at_{self.k}"


class LLMAsJudgeMetric(BaseEvaluationMetric):
    """
    Comprehensive LLM-as-a-Judge metric that evaluates both faithfulness and quality.
    Provides detailed scoring (1-5) with rationale, and separate scores for faithfulness and quality.
    """
    @inject
    def __init__(self, brain: BrainInterface):
        self.brain = brain
    
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        """
        Use LLM to comprehensively evaluate the generated response.
        Returns overall normalized score (0.0 to 1.0) and stores detailed metrics.
        """
        if not evaluation_result.generated_response or not evaluation_result.retrieved_context:
            return 0.0
        
        judge_prompt = LLM_AS_JUDGE_PROMPT.format(
            context="\n".join(evaluation_result.retrieved_context),
            response=evaluation_result.generated_response,
            query=evaluation_result.query
        )
        
        try:
            messages = [{"role": "user", "content": judge_prompt}]
            result = self.brain.think(messages)
            response_text = result.get("content", "").strip()
            
            # Try to parse JSON response
            try:
                parsed_result = json.loads(response_text)
                faithfulness = float(parsed_result.get("faithfulness_score", 0.0))
                quality = float(parsed_result.get("quality_score", 0.0))
                rating = int(parsed_result.get("overall_rating", 1))
                rationale = parsed_result.get("rationale", "No rationale provided")
            except (json.JSONDecodeError, ValueError, TypeError):
                # Fallback: try to extract values from text
                import re
                faithfulness_match = re.search(r'"faithfulness_score":\s*([\d.]+)', response_text)
                quality_match = re.search(r'"quality_score":\s*([\d.]+)', response_text)
                rating_match = re.search(r'"overall_rating":\s*(\d)', response_text)
                
                faithfulness = float(faithfulness_match.group(1)) if faithfulness_match else 0.0
                quality = float(quality_match.group(1)) if quality_match else 0.0
                rating = int(rating_match.group(1)) if rating_match else 1
                rationale = "Extracted from partial response"
            
            # Clamp values to valid ranges
            faithfulness = max(0.0, min(1.0, faithfulness))
            quality = max(0.0, min(1.0, quality))
            rating = max(1, min(5, rating))
            
            # Store detailed results in the evaluation result
            evaluation_result.generation_rating = rating
            evaluation_result.generation_rationale = rationale
            evaluation_result.faithfulness_score = faithfulness
            evaluation_result.quality_score = quality
            
            # Return overall normalized score (average of faithfulness and quality)
            overall_score = (faithfulness + quality) / 2.0
            return overall_score
            
        except Exception as e:
            logger.warning(f"Failed to get LLM judge evaluation: {e}")
            evaluation_result.generation_rating = 1
            evaluation_result.generation_rationale = f"Evaluation failed: {str(e)}"
            evaluation_result.faithfulness_score = 0.0
            evaluation_result.quality_score = 0.0
            return 0.0
    
    def get_name(self) -> str:
        return "llm_as_judge"


class RAGEvaluator:
    """
    Comprehensive evaluator for RAG (Retrieval-Augmented Generation) systems.
    """
    
    @inject
    def __init__(
        self,
        config: Config,
        embedding: EmbeddingInterface,
        vector_database: VectorDatabaseInterface,
        brain: BrainInterface
    ):
        self.config = config
        self.embedding = embedding
        self.vector_database = vector_database
        self.metrics: List[BaseEvaluationMetric] = [
            TopKAccuracyMetric(k=1),
            TopKAccuracyMetric(k=3),
            TopKAccuracyMetric(k=5),
            MeanReciprocalRankMetric(k=10),
            RecallAtKMetric(k=5),
            LLMAsJudgeMetric(brain)
        ]
    
    def add_metric(self, metric: BaseEvaluationMetric) -> None:
        """
        Add a custom evaluation metric.
        """
        self.metrics.append(metric)
    
    def evaluate_retrieval(
        self, 
        query: str, 
        expected_context: Optional[str] = None,
        expected_doc_id: Optional[str] = None,
        expected_snippet: Optional[str] = None,
        max_chunks: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate retrieval performance for a single query.
        """
        if metadata is None:
            metadata = {}
        
        logger.info(f"Evaluating retrieval for query: {query}")
        
        # Measure retrieval latency
        start_time = time.time()
        retrieved_context = self.vector_database.retrieve_context(
            query, max_chunks, metadata
        )
        retrieval_latency = time.time() - start_time
        
        # Create evaluation result
        result = EvaluationResult(
            query=query,
            expected_context=expected_context,
            expected_doc_id=expected_doc_id,
            expected_snippet=expected_snippet,
            retrieved_context=retrieved_context,
            retrieval_latency=retrieval_latency,
            metadata=metadata
        )
        
        # Calculate retrieval metrics
        for metric in self.metrics:
            if any(keyword in metric.get_name() for keyword in ["top_", "mrr", "recall", "failure", "retrieval"]):
                score = metric.calculate(result)
                setattr(result, f"{metric.get_name()}_score", score)
                
                # Set main retrieval score for backwards compatibility
                if "top_5_accuracy" in metric.get_name():
                    result.retrieval_score = score
        
        logger.info(f"Retrieval evaluation completed for query: {query}")
        return result
    
    def evaluate_generation(
        self,
        query: str,
        retrieved_context: List[str],
        generated_response: str,
        expected_response: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate generation performance for a single query.
        """
        logger.info(f"Evaluating generation for query: {query}")
        
        # Create evaluation result
        result = EvaluationResult(
            query=query,
            retrieved_context=retrieved_context,
            generated_response=generated_response,
            expected_response=expected_response
        )
        
        # Calculate generation metrics
        for metric in self.metrics:
            if "llm_as_judge" in metric.get_name():
                score = metric.calculate(result)
                setattr(result, f"{metric.get_name()}_score", score)
                
                # Set main generation score for backwards compatibility
                result.generation_score = score
        
        logger.info(f"Generation evaluation completed for query: {query}")
        return result
    
    def evaluate_end_to_end(
        self,
        rag_expert: "RAGBotExpert",
        query: str,
        expected_context: Optional[str] = None,
        expected_doc_id: Optional[str] = None,
        expected_snippet: Optional[str] = None,
        expected_response: Optional[str] = None,
        user_id: str = "test_user",
        conversation_id: str = "test_conversation",
        max_chunks: int = 10
    ) -> EvaluationResult:
        """
        Evaluate both retrieval and generation performance end-to-end.
        """
        logger.info(f"Starting end-to-end evaluation for query: {query}")
        
        # Measure retrieval
        start_time = time.time()
        metadata = {"user_id": user_id}
        retrieved_context = rag_expert.retrieve_context(query, max_chunks, metadata)
        retrieval_latency = time.time() - start_time
        
        # Measure generation
        start_time = time.time()
        response = rag_expert.process(query, conversation_id, user_id)
        generation_latency = time.time() - start_time
        
        # Create comprehensive evaluation result
        result = EvaluationResult(
            query=query,
            expected_context=expected_context,
            expected_doc_id=expected_doc_id,
            expected_snippet=expected_snippet,
            retrieved_context=retrieved_context,
            generated_response=response.response,
            expected_response=expected_response,
            retrieval_latency=retrieval_latency,
            generation_latency=generation_latency,
            metadata={"user_id": user_id, "conversation_id": conversation_id}
        )
        
        # Calculate all metrics
        for metric in self.metrics:
            score = metric.calculate(result)
            metric_name = metric.get_name()
            setattr(result, f"{metric_name}_score", score)
            
            # Set main scores for backwards compatibility
            if "top_5_accuracy" in metric_name:
                result.retrieval_score = score
            elif "llm_as_judge" in metric_name:
                result.generation_score = score
        
        logger.info(f"End-to-end evaluation completed for query: {query}")
        return result
    
    def evaluate_batch(
        self,
        rag_expert: "RAGBotExpert",
        test_cases: List[Dict[str, Any]],
        user_id: str = "test_user"
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple test cases in batch.
        
        Args:
            rag_expert: The RAG expert to evaluate
            test_cases: List of test cases, each containing 'query', 'expected_context', 'expected_doc_id', etc.
            user_id: User ID for the evaluation
        """
        logger.info(f"Starting batch evaluation with {len(test_cases)} test cases")
        
        results: List[EvaluationResult] = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Evaluating test case {i+1}/{len(test_cases)}")
            
            conversation_id = f"eval_conversation_{i}"
            result = self.evaluate_end_to_end(
                rag_expert=rag_expert,
                query=test_case["query"],
                expected_context=test_case.get("expected_context"),
                expected_doc_id=test_case.get("expected_doc_id"),
                expected_snippet=test_case.get("expected_snippet"),
                expected_response=test_case.get("expected_response"),
                user_id=user_id,
                conversation_id=conversation_id
            )
            results.append(result)
            
            # Clear conversation history for next test
            rag_expert.clear_history(conversation_id, user_id)
        
        logger.info(f"Batch evaluation completed")
        return results
    
    def generate_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate a comprehensive evaluation report.
        """
        if not results:
            return {"error": "No evaluation results provided"}
        
        # Calculate aggregate metrics
        total_results = len(results)
        
        # Get all metric names from the first result
        metric_names: List[str] = []
        for attr_name in dir(results[0]):
            if attr_name.endswith("_score") and not attr_name.startswith("_"):
                metric_names.append(attr_name)
        
        # Calculate averages and counts
        aggregate_metrics = {}
        for metric_name in metric_names:
            scores = [getattr(result, metric_name) for result in results if hasattr(result, metric_name) and getattr(result, metric_name) is not None]
            if scores:
                aggregate_metrics[metric_name] = {
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "count": len(scores)
                }
        
        # Add separate faithfulness and quality metrics
        faithfulness_scores = [r.faithfulness_score for r in results if r.faithfulness_score is not None]
        quality_scores = [r.quality_score for r in results if r.quality_score is not None]
        
        if faithfulness_scores:
            aggregate_metrics["faithfulness"] = {
                "average": sum(faithfulness_scores) / len(faithfulness_scores),
                "min": min(faithfulness_scores),
                "max": max(faithfulness_scores),
                "count": len(faithfulness_scores)
            }
        
        if quality_scores:
            aggregate_metrics["quality"] = {
                "average": sum(quality_scores) / len(quality_scores),
                "min": min(quality_scores),
                "max": max(quality_scores),
                "count": len(quality_scores)
            }
        
        # Calculate latencies
        retrieval_latencies = [r.retrieval_latency for r in results if r.retrieval_latency is not None]
        generation_latencies = [r.generation_latency for r in results if r.generation_latency is not None]
        
        # Identify failure cases using the new metrics
        failed_retrievals = [r for r in results if hasattr(r, 'top_5_accuracy_score') and getattr(r, 'top_5_accuracy_score', 0) == 0.0]
        low_quality_generations = [r for r in results if hasattr(r, 'llm_as_judge_score') and getattr(r, 'llm_as_judge_score', 0) < 0.5]
        
        # Collect detailed LLM judge feedback
        llm_judge_feedback: List[Dict[str, Any]] = []
        for result in results:
            if hasattr(result, 'generation_rating') and hasattr(result, 'generation_rationale'):
                llm_judge_feedback.append({
                    "query": result.query,
                    "rating": result.generation_rating,
                    "rationale": result.generation_rationale,
                    "faithfulness": result.faithfulness_score,
                    "quality": result.quality_score,
                    "response_preview": result.generated_response[:100] + "..." if result.generated_response and len(result.generated_response) > 100 else result.generated_response
                })
        
        report = {
            "summary": {
                "total_evaluations": total_results,
                "failed_retrievals": len(failed_retrievals),
                "low_quality_generations": len(low_quality_generations),
                "failure_rate_retrieval": len(failed_retrievals) / total_results * 100 if total_results > 0 else 0,
                "failure_rate_generation": len(low_quality_generations) / total_results * 100 if total_results > 0 else 0
            },
            "metrics": aggregate_metrics,
            "latency": {
                "retrieval": {
                    "average": sum(retrieval_latencies) / len(retrieval_latencies) if retrieval_latencies else 0,
                    "min": min(retrieval_latencies) if retrieval_latencies else 0,
                    "max": max(retrieval_latencies) if retrieval_latencies else 0
                },
                "generation": {
                    "average": sum(generation_latencies) / len(generation_latencies) if generation_latencies else 0,
                    "min": min(generation_latencies) if generation_latencies else 0,
                    "max": max(generation_latencies) if generation_latencies else 0
                }
            },
            "failure_cases": {
                "retrieval_failures": [
                    {
                        "query": r.query, 
                        "expected_context": r.expected_context,
                        "expected_doc_id": r.expected_doc_id,
                        "retrieved_context": r.retrieved_context[:2] if r.retrieved_context else []
                    }
                    for r in failed_retrievals[:5]  # Show first 5 failures
                ],
                "generation_failures": [
                    {
                        "query": r.query, 
                        "generated_response": r.generated_response[:200] + "..." if r.generated_response and len(r.generated_response) > 200 else r.generated_response,
                        "llm_rating": getattr(r, 'generation_rating', None),
                        "llm_rationale": getattr(r, 'generation_rationale', None),
                        "faithfulness": getattr(r, 'faithfulness_score', None),
                        "quality": getattr(r, 'quality_score', None)
                    }
                    for r in low_quality_generations[:5]  # Show first 5 failures
                ]
            },
            "llm_judge_feedback": llm_judge_feedback[:10]  # Show first 10 detailed feedbacks
        }
        
        return report


# Enhanced test cases with more detailed ground truth
ENHANCED_TEST_CASES = [
    {
        "query": "How do I get started with the chatbot?",
        "expected_context": "chatbot setup",
        "expected_doc_id": "setup_guide",
        "expected_snippet": "getting started with chatbot configuration"
    },
    {
        "query": "What are the main features of this system?",
        "expected_context": "features",
        "expected_doc_id": "features_overview",
        "expected_snippet": "main system features and capabilities"
    },
    {
        "query": "How do I configure the vector database?",
        "expected_context": "vector database configuration",
        "expected_doc_id": "vector_db_config",
        "expected_snippet": "vector database setup and configuration"
    },
    {
        "query": "What embedding models are supported?",
        "expected_context": "embedding models",
        "expected_doc_id": "embedding_guide",
        "expected_snippet": "supported embedding models and configuration"
    },
    {
        "query": "How do I deploy this application?",
        "expected_context": "deployment",
        "expected_doc_id": "deployment_guide",
        "expected_snippet": "application deployment instructions"
    }
]

# Legacy test cases for backward compatibility
MANUAL_TEST_CASES = [
    {
        "query": "How do I get started with the chatbot?",
        "expected_context": "chatbot setup",
        "expected_response": None
    },
    {
        "query": "What are the main features of this system?",
        "expected_context": "features",
        "expected_response": None
    },
    {
        "query": "How do I configure the vector database?",
        "expected_context": "vector database configuration",
        "expected_response": None
    },
    {
        "query": "What embedding models are supported?",
        "expected_context": "embedding models",
        "expected_response": None
    },
    {
        "query": "How do I deploy this application?",
        "expected_context": "deployment",
        "expected_response": None
    }
]


def create_evaluator(
    config: Config,
    embedding: EmbeddingInterface,
    vector_database: VectorDatabaseInterface,
    brain: BrainInterface
) -> RAGEvaluator:
    """
    Factory function to create a RAG evaluator.
    """
    return RAGEvaluator(config, embedding, vector_database, brain) 