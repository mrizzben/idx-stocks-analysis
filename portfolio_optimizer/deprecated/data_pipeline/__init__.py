"""
Data Pipeline Module for Portfolio Optimization

This module provides a factory pattern implementation for creating data source instances
based on the specified data source type. It supports various data sources including
CSV files and REST APIs.
"""

from .base import DataSource
from .csv_data_source import CSVDataSource
from .api_data_source import APIDataSource

class DataSourceFactory:
    """
    Factory class for creating data source instances.
    
    This class provides a unified interface for creating different types of data sources
    based on the specified source type. It supports various data source types including
    CSV files and REST APIs.
    """
    
    @staticmethod
    def create_data_source(source_type: str, config: dict) -> DataSource:
        """
        Create a data source instance of the specified type.
        
        Args:
            source_type: Type of data source to create ('csv', 'api')
            config: Configuration dictionary containing source-specific parameters
            
        Returns:
            DataSource: Instance of the requested data source type
            
        Raises:
            ValueError: If an unknown source type is requested
        """
        if source_type.lower() == 'csv':
            return CSVDataSource(config)
        elif source_type.lower() == 'api':
            return APIDataSource(config)
        else:
            raise ValueError(f"Unknown data source type: {source_type}")
    
    @staticmethod
    def get_available_sources() -> list:
        """
        Get a list of available data source types.
        
        Returns:
            list: List of available data source types
        """
        return ['csv', 'api']

# Version of the data pipeline module
__version__ = '0.1.0'

# Export key classes and functions at module level for easier access
__all__ = [
    'DataSource',
    'DataSourceFactory',
    'CSVDataSource',
    'APIDataSource'
]