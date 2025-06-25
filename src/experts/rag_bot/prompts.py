RAG_PROMPT="""You are a helpful expert assistant. Use the following context to answer the question at the end.
Answer only based on the context. If the answer is not present, say "I don't know based on the given context."

Context:
{context}

Conversation:
"""

LLM_AS_JUDGE_PROMPT = """
Evaluate the following AI assistant response comprehensively. You will assess both faithfulness to the context and overall quality.

Query: {query}

Context Used:
{context}

Generated Response:
{response}

Please evaluate the response on these specific criteria:

1. FAITHFULNESS (How well does the response stick to the provided context?)
- 1.0 = Completely faithful, all information supported by context
- 0.8 = Mostly faithful, minor unsupported details
- 0.6 = Generally faithful, some unsupported information
- 0.4 = Partially faithful, significant unsupported content
- 0.2 = Mostly unfaithful, contradicts or ignores context
- 0.0 = Completely unfaithful, no relation to context

2. QUALITY (How good is the response overall?)
- Accuracy: Is the information correct?
- Relevance: Does it address the query?
- Completeness: Is the answer comprehensive?
- Clarity: Is it well-structured and understandable?
- Helpfulness: Would this help the user?

3. OVERALL RATING (1-5 scale)
- 5 = Excellent (Highly faithful, accurate, complete, clear)
- 4 = Good (Mostly faithful, accurate, minor issues)
- 3 = Average (Generally acceptable, some problems)
- 2 = Below Average (Significant issues with faithfulness or quality)
- 1 = Poor (Major problems, unhelpful or inaccurate)

Respond in the following JSON format:
{{
    "faithfulness_score": <number between 0.0-1.0>,
    "quality_score": <number between 0.0-1.0>,
    "overall_rating": <number between 1-5>,
    "rationale": "<detailed explanation covering faithfulness, quality, and reasoning for scores>"
}}
"""


GENERATION_EVALUATION_PROMPT = """
Given the following document chunk, generate {num_questions} diverse questions that can be answered using the information in this chunk.

Document chunk:
{document_chunk}

Please create questions with different difficulty levels and types:
- 2 easy factual questions (direct facts from the text)
- 2 medium inferential questions (require connecting information)
- 1 hard conceptual question (require understanding concepts)

For each question, also specify:
- The exact snippet from the document that answers the question
- The difficulty level (easy/medium/hard)
- The question type (factual/inferential/conceptual)

Please respond in the following JSON format:
{{
    "questions": [
        {{
            "question": "Your question here",
            "answer_snippet": "Exact text from document that answers the question",
            "difficulty": "easy/medium/hard",
            "type": "factual/inferential/conceptual"
        }}
    ]
}}
"""