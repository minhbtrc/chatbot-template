from typing import List, Dict, Any
import os

from injector import inject
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker

from src.common.config import Config
from src.base.components import VectorDatabaseInterface, EmbeddingInterface, MemoryInterface
from src.base.brains import BrainInterface
from src.experts.rag_bot.prompts import RAG_PROMPT
from src.experts.base import BaseExpert
from src.common.logging import logger


class RAGBotExpert(BaseExpert):
    """
    RAGBotExpert is a class that implements the RAG (Retrieval-Augmented Generation) expert interface.
    """
    @inject
    def __init__(
        self,
        config: Config,
        embedding: EmbeddingInterface,
        vector_database: VectorDatabaseInterface,
        memory: MemoryInterface,
        brain: BrainInterface
    ):
        super().__init__(config, memory, brain)
        self.embedding = embedding
        self.vector_database = vector_database
        self.document_chunker = SemanticChunker(self.embedding.embeddings)

    def chunk_document(self, documents: List[Document]):
        """
        Splits documents into semantically meaningful chunks.
        """
        return self.document_chunker.transform_documents(documents)
    
    async def achunk_document(self, documents: List[Document]):
        """
        Splits documents into semantically meaningful chunks.
        """
        return await self.document_chunker.atransform_documents(documents)

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

    def process_document(self, file_path: str, user_id: str, document_id: str) -> None:
        """
        Loads a document from the given file path, chunks it, and indexes it.
        """
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {file_path}")
        
        try:
            logger.info(f"Loading document from: {file_path}")
            docs = PyPDFLoader(file_path).load()
            
            if not docs:
                raise ValueError(f"No content could be extracted from file: {file_path}")
            
            for doc in docs:
                doc.metadata.update({"user_id": user_id, "document_id": document_id}) # type: ignore

            logger.info(f"Successfully loaded {len(docs)} pages from document")
            
            logger.info("Chunking document...")
            doc_chunks = self.chunk_document(docs)
            
            if not doc_chunks:
                raise ValueError("No chunks were created from the document")
            
            logger.info(f"Created {len(doc_chunks)} chunks from document")
            
            logger.info("Indexing document chunks...")
            return self.index_documents(list(doc_chunks))
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    async def aprocess_document(self, file_path: str, user_id: str, document_id: str) -> None:
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {file_path}")
        
        try:
            logger.info(f"Loading document from: {file_path}")
            docs = await PyPDFLoader(file_path).aload()
            
            if not docs:
                raise ValueError(f"No content could be extracted from file: {file_path}")
            
            for doc in docs:
                doc.metadata.update({"user_id": user_id, "document_id": document_id}) # type: ignore

            logger.info(f"Successfully loaded {len(docs)} pages from document")
            
            logger.info("Chunking document...")
            doc_chunks = await self.achunk_document(docs)
            
            if not doc_chunks:
                raise ValueError("No chunks were created from the document")
            
            logger.info(f"Created {len(doc_chunks)} chunks from document")
            
            logger.info("Indexing document chunks...")
            return await self.aindex_documents(list(doc_chunks))
            
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def retrieve_context(self, query: str, max_chunks: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieves relevant document chunks for a given query.
        """
        return self.vector_database.retrieve_context(query, max_chunks, metadata)
    
    async def aretrieve_context(self, query: str, max_chunks: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Asynchronous version of `retrieve_context`.
        """
        return await self.vector_database.aretrieve_context(query, max_chunks, metadata)

    def _prepare_context(self, sentence: str, conversation_id: str, user_id: str, max_chunks: int = 10) -> str:
        """
        Prepares context string by appending the query to retrieved documents.

        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            max_chunks: Maximum number of chunks to retrieve

        """
        context_chunks = self.retrieve_context(sentence, max_chunks, metadata={"user_id": user_id})
        return RAG_PROMPT.format(context="".join(f'- {chunk}\n' for chunk in context_chunks))
    
    async def _aprepare_context(self, sentence: str, user_id: str, max_chunks: int = 10) -> str:
        """
        Asynchronous version of `_prepare_context`.

        Args:
            query: User input
            user_id: ID of the user
            max_chunks: Maximum number of chunks to retrieve
        """
        context_chunks = await self.aretrieve_context(sentence, max_chunks, metadata={"user_id": user_id})
        return RAG_PROMPT.format(context="".join(f'- {chunk}\n' for chunk in context_chunks), query=sentence)
