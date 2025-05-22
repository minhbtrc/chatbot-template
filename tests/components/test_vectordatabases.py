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

    @patch('chromadb.PersistentClient')
    def test_retrieve_context_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["test document 1"], ["test document 2"]]
        }
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # First index some documents
        documents = [Document(page_content="test document 1"), Document(page_content="test document 2")]
        vector_database.index_documents(documents)
        
        # Test retrieve_context
        result = vector_database.retrieve_context("test query", n_results=2)
        assert isinstance(result, List)
        assert all(isinstance(x, str) for x in result)

    @patch('chromadb.PersistentClient')
    def test_index_documents_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # Test index_document
        documents = [Document(page_content="test document 1"), Document(page_content="test document 2")]
        result = vector_database.index_documents(documents)
        assert result is None

    @patch('chromadb.PersistentClient')
    def test_delete_document_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config, self.mock_embeddings)
        
        # First index a document
        documents = [Document(page_content="test document to delete")]
        vector_database.index_documents(documents)
        
        # Test delete_document
        result = vector_database.delete_document("test_doc_id")
        assert result is None
