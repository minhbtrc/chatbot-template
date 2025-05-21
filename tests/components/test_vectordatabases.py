import unittest
from typing import List
from unittest.mock import patch, MagicMock

from src.common.config import Config
from src.base.components.vector_databases import create_vector_database
from src.base.components.vector_databases.variants.chromadb import ChromaVectorDatabase


class TestVectorDatabases(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Config()
        self.mock_config.vector_database_type = "chroma"
        self.mock_config.vector_database_chroma_path = "/tmp/test_chroma"

    @patch('chromadb.PersistentClient')
    def test_create_vector_database_chroma(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config)
        assert isinstance(vector_database, ChromaVectorDatabase)
    
    def test_create_vector_database_invalid_type(self) -> None:
        config = Config()
        config.vector_database_type = "invalid"
        with self.assertRaises(ValueError):
            create_vector_database(config)

    @patch('chromadb.PersistentClient')
    def test_retrieve_context_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["test document 1", "test document 2"]]
        }
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config)
        
        # First index some documents
        documents = ["test document 1", "test document 2"]
        vector_database.index_documents(documents)
        
        # Test retrieve_context
        result = vector_database.retrieve_context("test query", n_results=2)
        assert isinstance(result, List)
        assert all(isinstance(x, str) for x in result)

    @patch('chromadb.PersistentClient')
    def test_index_documents_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config)
        
        # Test index_documents (should return None)
        documents = ["test document 1", "test document 2"]
        result = vector_database.index_documents(documents)
        assert result is None

    @patch('chromadb.PersistentClient')
    def test_delete_document_return_type(self, mock_client: MagicMock) -> None:
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_database = create_vector_database(self.mock_config)
        
        # First index a document
        documents = ["test document to delete"]
        vector_database.index_documents(documents)
        
        # Test delete_document (should return None)
        result = vector_database.delete_document("test document to delete")
        assert result is None
