"""
Base classes for the application.

This module provides base classes that can be used across the application.
"""

import logging
from typing import Any


class BaseObject:
    """Base class for objects in the application.
    
    Provides common functionality like logging.
    """
    
    def __init__(self):
        """Initialize the base object with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Make the object callable, to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement __call__") 