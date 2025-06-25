from typing import List, Dict, Any, Optional
import os

from injector import inject
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker

from src.common.config import Config
from src.base.components import VectorDatabaseInterface, EmbeddingInterface, MemoryInterface
from src.base.brains import BrainInterface
from src.experts.rag_bot.prompts import RAG_PROMPT
from src.experts.rag_bot.synthetic_data_generator import SyntheticDataGenerator, SyntheticTestCase
from src.experts.base import BaseExpert
from src.common.logging import logger


class RAGBotExpert(BaseExpert):
    """
    RAGBotExpert is a class that implements the RAG (Retrieval-Augmented Generation) expert interface.
    Now includes optional synthetic dataset generation during document ingestion.
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
        
        # Initialize synthetic data generator if enabled
        self.synthetic_generator: Optional[SyntheticDataGenerator] = None
        if config.enable_synthetic_dataset_generation:
            self.synthetic_generator = SyntheticDataGenerator(brain, vector_database)
            logger.info("Synthetic dataset generation enabled for RAG document processing")
            
            # Ensure export directory exists
            if config.synthetic_dataset_export_path:
                os.makedirs(config.synthetic_dataset_export_path, exist_ok=True)

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

    def _generate_synthetic_dataset(
        self, 
        doc_chunks: List[Document], 
        user_id: str, 
        document_id: str, 
        file_path: str
    ) -> Optional[List[SyntheticTestCase]]:
        """
        Generate synthetic test cases from document chunks.
        
        Args:
            doc_chunks: List of document chunks
            user_id: User ID for metadata
            document_id: Document ID for metadata
            file_path: Original file path for metadata
            
        Returns:
            List of generated test cases or None if generation is disabled/failed
        """
        if not self.synthetic_generator:
            return None
            
        try:
            logger.info(f"Generating synthetic dataset for document: {document_id}")
            
            # Limit chunks if configured
            max_chunks = self.config.synthetic_max_chunks_per_document or len(doc_chunks)
            chunks_to_process = doc_chunks[:max_chunks]
            
            # Generate synthetic test cases
            test_cases = self.synthetic_generator.generate_questions_from_document_chunks(
                document_chunks=chunks_to_process,
                questions_per_chunk=self.config.synthetic_questions_per_chunk or 3,
                max_chunks=max_chunks
            )
            
            if test_cases:
                # Add additional metadata
                for test_case in test_cases:
                    test_case.metadata.update({
                        "source_file_path": file_path,
                        "document_processing_user_id": user_id,
                        "document_processing_document_id": document_id,
                        "total_chunks_in_document": len(doc_chunks),
                        "chunks_processed_for_synthesis": len(chunks_to_process)
                    })
                
                # Export the test cases
                if self.config.synthetic_dataset_export_path:
                    export_filename = f"{document_id}_{user_id}_synthetic_dataset.json"
                    export_path = os.path.join(self.config.synthetic_dataset_export_path, export_filename)
                    
                    self.synthetic_generator.export_test_cases(test_cases, export_path)
                    logger.info(f"Synthetic dataset exported to: {export_path}")
                
                logger.info(f"Generated {len(test_cases)} synthetic test cases for document {document_id}")
                return test_cases
            else:
                logger.warning(f"No synthetic test cases generated for document {document_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate synthetic dataset for document {document_id}: {str(e)}")
            return None

    def process_document(self, file_path: str, user_id: str, document_id: str) -> Optional[List[SyntheticTestCase]]:
        """
        Loads a document from the given file path, chunks it, indexes it, and optionally generates synthetic dataset.
        
        Returns:
            List of generated synthetic test cases if synthetic generation is enabled, None otherwise
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
            
            # Generate synthetic dataset before indexing (optional)
            synthetic_test_cases = None
            if self.config.enable_synthetic_dataset_generation:
                synthetic_test_cases = self._generate_synthetic_dataset(
                    doc_chunks=list(doc_chunks),
                    user_id=user_id,
                    document_id=document_id,
                    file_path=file_path
                )
            
            logger.info("Indexing document chunks...")
            self.index_documents(list(doc_chunks))
            
            return synthetic_test_cases
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    async def aprocess_document(self, file_path: str, user_id: str, document_id: str) -> Optional[List[SyntheticTestCase]]:
        """
        Async version of process_document with synthetic dataset generation.
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
            
            # Generate synthetic dataset before indexing (optional)
            synthetic_test_cases = None
            if self.config.enable_synthetic_dataset_generation:
                synthetic_test_cases = self._generate_synthetic_dataset(
                    doc_chunks=list(doc_chunks),
                    user_id=user_id,
                    document_id=document_id,
                    file_path=file_path
                )
            
            logger.info("Indexing document chunks...")
            await self.aindex_documents(list(doc_chunks))
            
            return synthetic_test_cases
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def get_synthetic_dataset_for_document(self, user_id: str, document_id: str) -> Optional[List[SyntheticTestCase]]:
        """
        Load previously generated synthetic dataset for a specific document.
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            List of synthetic test cases if found, None otherwise
        """
        if not self.synthetic_generator or not self.config.synthetic_dataset_export_path:
            return None
            
        try:
            export_filename = f"{document_id}_{user_id}_synthetic_dataset.json"
            export_path = os.path.join(self.config.synthetic_dataset_export_path, export_filename)
            
            if os.path.exists(export_path):
                return self.synthetic_generator.load_test_cases(export_path)
            else:
                logger.warning(f"No synthetic dataset found for document {document_id} and user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load synthetic dataset for document {document_id}: {str(e)}")
            return None

    def list_available_synthetic_datasets(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available synthetic datasets, optionally filtered by user_id.
        
        Args:
            user_id: Optional user ID to filter datasets
            
        Returns:
            List of dictionaries containing dataset metadata
        """
        if not self.config.synthetic_dataset_export_path or not os.path.exists(self.config.synthetic_dataset_export_path):
            return []
            
        try:
            datasets: List[Dict[str, Any]] = []
            for filename in os.listdir(self.config.synthetic_dataset_export_path):
                if filename.endswith("_synthetic_dataset.json"):
                    # Parse filename: {document_id}_{user_id}_synthetic_dataset.json
                    parts = filename.replace("_synthetic_dataset.json", "").split("_")
                    if len(parts) >= 2:
                        file_user_id = parts[-1]
                        file_document_id = "_".join(parts[:-1])
                        
                        if user_id is None or file_user_id == user_id:
                            file_path = os.path.join(self.config.synthetic_dataset_export_path, filename)
                            file_stats = os.stat(file_path)
                            
                            datasets.append({
                                "document_id": file_document_id,
                                "user_id": file_user_id,
                                "filename": filename,
                                "file_path": file_path,
                                "created_timestamp": file_stats.st_ctime,
                                "file_size": file_stats.st_size
                            })
            
            return sorted(datasets, key=lambda x: x["created_timestamp"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list synthetic datasets: {str(e)}")
            return []

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

    def _prepare_context(self, sentence: str, conversation_id: str, user_id: str, max_chunks: int = 10, **kwargs: Any) -> str:
        """
        Prepares context string by appending the query to retrieved documents.

        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            max_chunks: Maximum number of chunks to retrieve
            **kwargs: Additional keyword arguments for compatibility

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
