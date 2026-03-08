"""
CSV Data Source Implementation

This module implements a data source that reads financial data from CSV files.
"""

import pandas as pd
import os
from .base import DataSource
from typing import Dict, Any

class CSVDataSource(DataSource):
    """
    Implementation of DataSource for reading financial data from CSV files.
    
    This class provides functionality to load financial time series data from
    CSV files into pandas DataFrames for further processing and analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CSV data source with configuration.
        
        Args:
            config: Configuration dictionary containing CSV-specific parameters.
                   Expected keys:
                   - file_path: Path to the CSV file
                   - date_column: Name of the column containing dates (default: 'Date')
                   - date_format: Format of date strings (optional)
                   - index_column: Whether to set the date column as index (default: True)
                   - asset_columns: List of columns to use as assets (optional, default: all columns except date)
        """
        super().__init__(config)
        self.file_path = config['file_path']
        self.date_column = config.get('date_column', 'Date')
        self.date_format = config.get('date_format')
        self.index_column = config.get('index_column', True)
        self.asset_columns = config.get('asset_columns')
        
        # Validate file existence
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file not found at {self.file_path}")
    
    def load_data(self) -> None:
        """Load raw data from CSV file into a pandas DataFrame."""
        try:
            # Read CSV file
            self.raw_data = pd.read_csv(self.file_path)
            
            # Convert date column if specified
            if self.date_column in self.raw_data.columns:
                if self.date_format:
                    self.raw_data[self.date_column] = pd.to_datetime(
                        self.raw_data[self.date_column], 
                        format=self.date_format
                    )
                else:
                    self.raw_data[self.date_column] = pd.to_datetime(
                        self.raw_data[self.date_column]
                    )
                    
                # Set as index if specified
                if self.index_column:
                    self.raw_data = self.raw_data.set_index(self.date_column)
            
            # Select asset columns if specified
            if self.asset_columns:
                self.processed_data = self.raw_data[self.asset_columns]
            else:
                # Use all columns except date column
                self.processed_data = self.raw_data.drop(columns=[self.date_column]) \
                    if self.date_column in self.raw_data.columns else self.raw_data
            
        except Exception as e:
            raise RuntimeError(f"Error loading CSV data: {str(e)}")
    
    def validate_data(self) -> bool:
        """
        Validate the loaded data.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        if self.raw_data is None:
            return False
            
        # Check for non-empty data
        if self.raw_data.empty:
            return False
            
        # Check for at least one asset column
        if self.processed_data is None or self.processed_data.empty:
            return False
            
        # Check for valid numeric data in asset columns
        for col in self.processed_data.columns:
            if not pd.api.types.is_numeric_dtype(self.processed_data[col]):
                return False
                
        return True