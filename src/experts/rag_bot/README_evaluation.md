# RAG Evaluation System

This module provides comprehensive evaluation capabilities for your RAG (Retrieval-Augmented Generation) system, allowing you to assess both retrieval and generation performance.

## Overview

The RAG evaluator is designed based on best practices from the ZenML documentation and provides:

- **Retrieval Evaluation**: Measures how well the system retrieves relevant documents
- **Generation Evaluation**: Assesses the quality and faithfulness of generated responses
- **End-to-End Evaluation**: Comprehensive evaluation of the entire RAG pipeline
- **Batch Evaluation**: Efficient evaluation of multiple test cases
- **Detailed Reporting**: Comprehensive reports with metrics, latencies, and failure analysis

## Features

### Evaluation Metrics

1. **Retrieval Relevance** (`retrieval_relevance_at_k`)
   - Measures if expected context appears in top-K retrieved documents
   - Binary metric: 1.0 if found, 0.0 if not found
   - Configurable K value (default: 5)

2. **Generation Faithfulness** (`generation_faithfulness`)
   - Uses LLM to evaluate if generated response is faithful to retrieved context
   - Scale: 0.0 to 1.0
   - Ensures responses don't hallucinate information not in context

3. **Response Quality** (`response_quality`)
   - Uses LLM to evaluate overall quality of generated responses
   - Considers clarity, completeness, accuracy, and helpfulness
   - Scale: 0.0 to 1.0

### Evaluation Types

1. **Manual Evaluation**: Using handcrafted test cases with known expected outcomes
2. **Automated Evaluation**: Using synthetically generated test cases
3. **Retrieval-Only Evaluation**: Focus on retrieval component performance
4. **Generation-Only Evaluation**: Focus on generation component performance
5. **End-to-End Evaluation**: Complete pipeline evaluation

## Usage

### Basic Setup

```python
from src.experts.rag_bot.evaluator import RAGEvaluator, create_evaluator
from src.experts.rag_bot.expert import RAGBotExpert

# Create evaluator (assumes you have components set up)
evaluator = create_evaluator(
    config=config,
    embedding=embedding,
    vector_database=vector_database,
    llm=llm
)
```

### Single Query Evaluation

```python
# Evaluate a single query end-to-end
result = evaluator.evaluate_end_to_end(
    rag_expert=rag_expert,
    query="How do I configure the vector database?",
    expected_context="vector database configuration",
    user_id="test_user",
    conversation_id="eval_session"
)

print(f"Retrieval Score: {result.retrieval_score}")
print(f"Generation Score: {result.generation_score}")
print(f"Response: {result.generated_response}")
```

### Batch Evaluation

```python
# Define test cases
test_cases = [
    {
        "query": "How do I get started?",
        "expected_context": "getting started",
        "expected_response": None
    },
    {
        "query": "What features are available?",
        "expected_context": "features",
        "expected_response": None
    }
]

# Run batch evaluation
results = evaluator.evaluate_batch(
    rag_expert=rag_expert,
    test_cases=test_cases,
    user_id="batch_eval_user"
)

# Generate comprehensive report
report = evaluator.generate_report(results)
print(f"Failure rate: {report['summary']['failure_rate_retrieval']:.1f}%")
```

### Retrieval-Only Evaluation

```python
# Evaluate only retrieval performance
result = evaluator.evaluate_retrieval(
    query="How do I deploy this application?",
    expected_context="deployment guide",
    max_chunks=10,
    metadata={"user_id": "test_user"}
)

print(f"Retrieved {len(result.retrieved_context)} chunks")
print(f"Relevance score: {result.retrieval_score}")
```

### Generation-Only Evaluation

```python
# Evaluate only generation performance
retrieved_context = ["Context chunk 1", "Context chunk 2"]
generated_response = "Based on the context..."

result = evaluator.evaluate_generation(
    query="Your question here",
    retrieved_context=retrieved_context,
    generated_response=generated_response
)

print(f"Faithfulness score: {result.generation_score}")
```

## Predefined Test Cases

The module includes `MANUAL_TEST_CASES` with predefined scenarios:

```python
from src.experts.rag_bot.evaluator import MANUAL_TEST_CASES

# Use predefined test cases
results = evaluator.evaluate_batch(
    rag_expert=rag_expert,
    test_cases=MANUAL_TEST_CASES,
    user_id="manual_eval"
)
```

## Custom Metrics

You can add custom evaluation metrics by extending `BaseEvaluationMetric`:

```python
class CustomMetric(BaseEvaluationMetric):
    def calculate(self, evaluation_result: EvaluationResult) -> float:
        # Your custom evaluation logic here
        return score
    
    def get_name(self) -> str:
        return "custom_metric"

# Add to evaluator
evaluator.add_metric(CustomMetric())
```

## Report Structure

The evaluation report includes:

```json
{
  "summary": {
    "total_evaluations": 5,
    "failed_retrievals": 1,
    "low_quality_generations": 0,
    "failure_rate_retrieval": 20.0,
    "failure_rate_generation": 0.0
  },
  "metrics": {
    "retrieval_relevance_at_5_score": {
      "average": 0.8,
      "min": 0.0,
      "max": 1.0,
      "count": 5
    },
    "generation_faithfulness_score": {
      "average": 0.85,
      "min": 0.7,
      "max": 1.0,
      "count": 5
    }
  },
  "latency": {
    "retrieval": {"average": 0.12, "min": 0.08, "max": 0.18},
    "generation": {"average": 1.45, "min": 0.98, "max": 2.1}
  },
  "failure_cases": {
    "retrieval_failures": [...],
    "generation_failures": [...]
  }
}
```

## Running Evaluations

### Command Line Usage

You can run the evaluation example script:

```bash
cd src/experts/rag_bot
python evaluation_example.py
```

### Integration with Your Pipeline

```python
# In your existing pipeline
def evaluate_rag_performance():
    # Setup your RAG expert as usual
    rag_expert = create_rag_expert()
    
    # Create evaluator
    evaluator = create_evaluator(...)
    
    # Run evaluation
    results = evaluator.evaluate_batch(rag_expert, test_cases)
    report = evaluator.generate_report(results)
    
    # Log or save results
    logger.info(f"RAG performance: {report['summary']}")
    
    return report
```

## Best Practices

### 1. Test Case Design
- Create diverse test cases covering different query types
- Include edge cases and known difficult scenarios
- Balance between factual and inferential questions

### 2. Evaluation Frequency
- Run evaluations after significant changes
- Monitor performance over time
- Set up automated evaluation pipelines

### 3. Interpreting Results
- Focus on trends rather than absolute scores
- Analyze failure cases to identify improvement areas
- Consider both retrieval and generation performance

### 4. Performance Optimization
- Use retrieval-only evaluation for faster iteration
- Batch evaluations for efficiency
- Cache evaluation results when possible

## Troubleshooting

### Common Issues

1. **No documents indexed**: Ensure your vector database has documents before evaluation
2. **Low retrieval scores**: Check if expected context strings match actual document content
3. **High latency**: Consider optimizing vector database configuration or model settings

### Debugging

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Inspect individual evaluation results
for result in results:
    print(f"Query: {result.query}")
    print(f"Retrieved: {result.retrieved_context}")
    print(f"Generated: {result.generated_response}")
    print("---")
```

## Advanced Usage

### Synthetic Data Generation

For automated evaluation at scale, consider generating synthetic test cases:

1. Extract representative document chunks
2. Use LLM to generate questions for each chunk
3. Create large-scale evaluation datasets
4. Run comprehensive evaluations across the dataset

### Comparative Evaluation

Use the evaluator to compare different:
- Embedding models
- Vector database configurations
- Retrieval strategies
- Generation models

### Performance Monitoring

Integrate evaluation into your deployment pipeline:
- Set performance thresholds
- Alert on degradation
- Track metrics over time
- A/B test improvements

## Integration with ZenML

This evaluator is designed to align with ZenML best practices:

- Modular metric design
- Comprehensive reporting
- Support for both manual and automated evaluation
- Scalable batch processing

For production deployments, consider integrating with ZenML pipelines for:
- Automated evaluation runs
- Experiment tracking
- Model performance monitoring
- Continuous integration

## Contributing

To add new evaluation metrics or improve existing ones:

1. Extend `BaseEvaluationMetric`
2. Implement `calculate()` and `get_name()` methods
3. Add appropriate tests
4. Update documentation

The evaluation system is designed to be extensible and adapt to your specific RAG use cases. 