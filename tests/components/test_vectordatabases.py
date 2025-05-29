import unittest
from typing import List

from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from src.common.config import Config
from src.base.components.vector_databases import create_vector_database, ChromaVectorDatabase
from src.base.components.embeddings import BaseEmbedding


class TestVectorDatabases(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Config()
        self.mock_config.vector_database_type = "chroma"
        self.mock_config.vector_database_chroma_path = "/tmp/test_chroma"
        self.mock_embeddings = MagicMock(spec=BaseEmbedding)
        self.mock_embeddings.embeddings = MagicMock()
        self.mock_embeddings.embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.mock_embeddings.embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    @patch('chromadb.PersistentClient')
    def test_create_vector_database_chroma(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        assert isinstance(vector_database, ChromaVectorDatabase)
    
    def test_create_vector_database_invalid_type(self) -> None:
        config = Config()
        config.vector_database_type = "invalid"
        with self.assertRaises(ValueError):
            create_vector_database(config, self.mock_embeddings)

    @patch('src.base.components.vector_databases.variants.chromadb.Chroma')
    def test_retrieve_context_return_type(self, mock_chroma: MagicMock) -> None:
        # Mock the Chroma client and retriever
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            Document(page_content="test document 1"),
            Document(page_content="test document 2")
        ]
        mock_chroma.return_value.as_retriever.return_value = mock_retriever
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # Test retrieve_context with empty metadata to avoid filter issues
        result = vector_database.retrieve_context("test query", n_results=2, metadata={})
        assert isinstance(result, List)
        assert all(isinstance(x, str) for x in result)

    @patch('src.base.components.vector_databases.variants.chromadb.Chroma')
    def test_index_documents_return_type(self, mock_chroma: MagicMock) -> None:
        # Mock the add_documents method to return document IDs
        mock_chroma.return_value.add_documents.return_value = ['id0', 'id1']
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # Test index_documents - it should return List[str] of document IDs
        documents = [Document(page_content="test document 1"), Document(page_content="test document 2")]
        result = vector_database.index_documents(documents)
        assert isinstance(result, List)
        assert all(isinstance(x, str) for x in result)
        assert result == ['id0', 'id1']

    @patch('src.base.components.vector_databases.variants.chromadb.Chroma')
    def test_delete_document_return_type(self, mock_chroma: MagicMock) -> None:
        mock_chroma.return_value.delete.return_value = None
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # Test delete_document
        result = vector_database.delete_document("test_doc_id")
        assert result is None
