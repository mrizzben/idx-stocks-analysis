"""
API Data Source Implementation

This module implements a data source that retrieves financial data from REST APIs.
"""

import pandas as pd
import requests
from datetime import datetime
from .base import DataSource
from typing import Dict, Any, Optional

class APIDataSource(DataSource):
    """
    Implementation of DataSource for retrieving financial data from REST APIs.
    
    This class provides functionality to fetch financial time series data from
    RESTful APIs and convert them into pandas DataFrames for further processing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize API data source with configuration.
        
        Args:
            config: Configuration dictionary containing API-specific parameters.
                   Expected keys:
                   - url: Base URL of the API endpoint
                   - endpoint: Specific endpoint path
                   - api_key: API authentication key (optional)
                   - headers: Custom request headers (optional)
                   - params: Default request parameters (optional)
                   - date_field: Name of the field containing dates (default: 'date')
                   - asset_fields: Dictionary mapping asset names to field names
                   - date_format: Format of date strings (optional)
        """
        super().__init__(config)
        self.url = config['url']
        self.endpoint = config.get('endpoint', '')
        self.api_key = config.get('api_key')
        self.headers = config.get('headers', {})
        self.params = config.get('params', {})
        self.date_field = config.get('date_field', 'date')
        self.asset_fields = config['asset_fields']
        self.date_format = config.get('date_format')
        
        # Add API key to headers if provided
        if self.api_key:
            self.headers['Authorization'] = f"Bearer {self.api_key}"
    
    def load_data(self) -> None:
        """Load raw data from API endpoint into a pandas DataFrame."""
        try:
            # Construct full URL
            full_url = f"{self.url.rstrip('/')}/{self.endpoint.lstrip('/')}"
            
            # Make API request
            response = requests.get(
                full_url,
                headers=self.headers,
                params=self.params
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Convert to pandas DataFrame
            self.raw_data = pd.DataFrame(data)
            
            # Validate required date field exists
            if self.date_field not in self.raw_data.columns:
                raise ValueError(f"Date field '{self.date_field}' not found in API response")
                
            # Convert date field
            if self.date_format:
                self.raw_data[self.date_field] = pd.to_datetime(
                    self.raw_data[self.date_field],
                    format=self.date_format
                )
            else:
                self.raw_data[self.date_field] = pd.to_datetime(
                    self.raw_data[self.date_field]
                )
                
            # Set date as index
            self.raw_data = self.raw_data.set_index(self.date_field)
            
            # Select and rename asset fields
            self.processed_data = self.raw_data[list(self.asset_fields.keys())]
            self.processed_data.columns = list(self.asset_fields.values())
            
        except Exception as e:
            raise RuntimeError(f"Error loading API data: {str(e)}")
    
    def validate_data(self) -> bool:
        """
        Validate the loaded data.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        if self.raw_data is None or self.processed_data is None:
            return False
            
        # Check for non-empty data
        if self.raw_data.empty or self.processed_data.empty:
            return False
            
        # Check for valid numeric data in asset columns
        for col in self.processed_data.columns:
            if not pd.api.types.is_numeric_dtype(self.processed_data[col]):
                return False
                
        return True
    
    def update_params(self, new_params: Dict[str, Any]) -> None:
        """
        Update request parameters for subsequent API calls.
        
        Args:
            new_params: Dictionary of parameters to update
        """
        self.params.update(new_params)