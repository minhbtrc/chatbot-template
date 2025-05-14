"""
MongoDB client module.
"""

from typing import Dict, Any, List, Optional

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

from infrastructure.config import Config
from infrastructure.logging import logger


class MongoDBClient:
    """MongoDB client for database operations."""
    
    def __init__(self, config: Config):
        """
        Initialize the MongoDB client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = self._create_client()
        self.db = self._get_database()
        self.collection = self._get_collection()
        
        logger.info(f"Connected to MongoDB database: {self.config.mongo_database}")
    
    def _create_client(self) -> MongoClient:
        """
        Create a MongoDB client.
        
        Returns:
            MongoDB client
        """
        # Use connection string from config
        return MongoClient(self.config.mongo_uri)
    
    def _get_database(self) -> Database:
        """
        Get the MongoDB database.
        
        Returns:
            MongoDB database
        """
        return self.client[self.config.mongo_database]
    
    def _get_collection(self) -> Collection:
        """
        Get the MongoDB collection.
        
        Returns:
            MongoDB collection
        """
        return self.db[self.config.mongo_collection]
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a document into the collection.
        
        Args:
            document: Document to insert
            
        Returns:
            Inserted document ID
        """
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a document in the collection.
        
        Args:
            query: Query to execute
            
        Returns:
            Matching document or None
        """
        return self.collection.find_one(query)
    
    def find_many(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find multiple documents in the collection.
        
        Args:
            query: Query to execute
            
        Returns:
            List of matching documents
        """
        return list(self.collection.find(query))
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a document in the collection.
        
        Args:
            query: Query to find the document
            update: Update to apply
            
        Returns:
            True if a document was updated, False otherwise
        """
        result = self.collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    def delete_one(self, query: Dict[str, Any]) -> bool:
        """
        Delete a document from the collection.
        
        Args:
            query: Query to find the document
            
        Returns:
            True if a document was deleted, False otherwise
        """
        result = self.collection.delete_one(query)
        return result.deleted_count > 0
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed") 