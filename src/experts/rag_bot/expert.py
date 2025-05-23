from typing import List

from injector import inject
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker

from src.common.config import Config
from src.common.schemas import ChatResponse
from src.base.components import VectorDatabaseInterface, EmbeddingInterface
from src.base.bot import Bot
from src.experts.rag_bot.prompts import RAG_PROMPT
from src.experts.base import BaseExpert


class RAGBotExpert(BaseExpert):
    """
    RAGBotExpert is a class that implements the RAGBotExpert interface.
    """
    @inject
    def __init__(
        self,
        config: Config,
        embedding: EmbeddingInterface,
        vector_database: VectorDatabaseInterface,
        bot: Bot
    ):
        self.config = config
        self.embedding = embedding
        self.vector_database = vector_database
        self.bot = bot
        self.document_chunker = SemanticChunker(self.embedding.embeddings)

    def chunk_document(self, documents: List[Document]):
        """
        Splits documents into semantically meaningful chunks.
        """
        return self.document_chunker.transform_documents(documents)

    def index_documents(self, documents: List[Document]) -> None:
        """
        Indexes documents into the vector database.
        """
        self.vector_database.index_documents(documents)

    async def aindex_documents(self, documents: List[Document]) -> None:
        """
        Asynchronous version of `index_documents`.
        """
        await self.vector_database.aindex_documents(documents)

    def process_document(self, file_path: str) -> None:
        """
        Loads a document from the given file path, chunks it, and indexes it.
        """
        docs = PyPDFLoader(file_path).load()
        doc_chunks = self.chunk_document(docs)
        self.index_documents(doc_chunks)

    def retrieve_context(self, query: str, max_chunks: int = 10) -> List[str]:
        """
        Retrieves relevant document chunks for a given query.
        """
        return self.vector_database.retrieve_context(query, max_chunks)

    def _prepare_context(self, query: str, max_chunks: int = 10) -> str:
        """
        Prepares context string by appending the query to retrieved documents.
        """
        context_chunks = self.retrieve_context(query, max_chunks)
        return RAG_PROMPT.format(context="".join(f'- {chunk}\n' for chunk in context_chunks), query=query)

    def process(self, query: str, conversation_id: str) -> ChatResponse:
        """
        Handles a query using synchronous bot processing.
        """
        context = self._prepare_context(query)
        response = self.bot.call(context, conversation_id)
        return response

    async def aprocess(self, query: str, conversation_id: str) -> ChatResponse:
        """w
        Handles a query using asynchronous bot processing.
        """
        context = self._prepare_context(query)
        response = await self.bot.acall(context, conversation_id)
        return response

    def clear_history(self, conversation_id: str) -> None:
        """
        Clears the conversation history for a specific conversation.
        """
        self.bot.reset_history(conversation_id)
