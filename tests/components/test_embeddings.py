import unittest
from typing import List
from unittest.mock import patch, MagicMock

from src.common.config import Config
from src.base.components.embeddings import create_embedding
from src.base.components.embeddings.variants.azure_openai_embedding import AzureOpenAIEmbedding

class TestEmbeddings(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Config()
        self.mock_config.embedding_type = "azureopenai"
        self.mock_config.azure_embedding_model_key = "mock_key"
        self.mock_config.azure_embedding_model_endpoint = "mock_endpoint"
        self.mock_config.azure_embedding_model_deployment = "mock_deployment"
        self.mock_config.azure_embedding_model_version = "2024-02-15-preview"

    @patch('src.base.components.embeddings.variants.azure_openai_embedding.AzureOpenAIEmbeddings')
    def test_embedding_factory(self, mock_embeddings: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance
        embedding = create_embedding(self.mock_config)
        assert embedding is not None
        assert isinstance(embedding, AzureOpenAIEmbedding)

    def test_embedding_factory_invalid_type(self) -> None:
        config = Config()
        config.embedding_type = "invalid"
        with self.assertRaises(ValueError):
            create_embedding(config)

    @patch('src.base.components.embeddings.variants.azure_openai_embedding.AzureOpenAIEmbeddings')
    def test_process_return_type(self, mock_embeddings: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_embeddings.return_value = mock_instance
        
        embedding = create_embedding(self.mock_config)
        result = embedding.process("test text")
        assert isinstance(result, List)
        assert all(isinstance(x, float) for x in result)
        mock_instance.embed_query.assert_called_once_with("test text")

    @patch('src.base.components.embeddings.variants.azure_openai_embedding.AzureOpenAIEmbeddings')
    def test_process_documents_return_type(self, mock_embeddings: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_embeddings.return_value = mock_instance
        
        embedding = create_embedding(self.mock_config)
        documents = ["test text 1", "test text 2"]
        result = embedding.process_documents(documents)
        assert isinstance(result, List)
        assert all(isinstance(doc_embedding, List) for doc_embedding in result)
        assert all(isinstance(x, float) for doc_embedding in result for x in doc_embedding)
        mock_instance.embed_documents.assert_called_once_with(documents)
