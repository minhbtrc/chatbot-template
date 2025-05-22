RAG_PROMPT="""You are a helpful expert assistant. Use the following context to answer the question at the end.
Answer only based on the context. If the answer is not present, say "I don't know based on the given context."

Context:
{context}

Question:
{query}
"""