"""
Base classes for data pipeline components.

This module defines abstract base classes for data sources and pipeline components
that are extended by specific implementations.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List

class DataSource(ABC):
    """
    Abstract base class for data sources.
    
    Defines the interface for loading and processing financial data from various sources.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data source with configuration.
        
        Args:
            config: Configuration dictionary containing source-specific parameters
        """
        self.config = config
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
    
    @abstractmethod
    def load_data(self) -> None:
        """Load raw data from the source into a pandas DataFrame."""
        pass
    
    @abstractmethod
    def validate_data(self) -> bool:
        """
        Validate the loaded data.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        pass
    
    def get_returns(self, frequency: str = 'daily') -> pd.DataFrame:
        """
        Calculate returns from processed data.
        
        Args:
            frequency: Frequency of returns ('daily', 'weekly', 'monthly')
            
        Returns:
            pd.DataFrame: Calculated returns
        """
        if self.processed_data is None:
            raise ValueError("No processed data available. Run load_data() first.")
            
        # Convert to appropriate frequency if needed
        if frequency != 'daily':
            data = self._resample_data(self.processed_data, frequency)
        else:
            data = self.processed_data
            
        # Calculate simple returns
        return data.pct_change().dropna()
    
    def get_covariance_matrix(self, frequency: str = 'daily') -> pd.DataFrame:
        """
        Calculate covariance matrix from returns.
        
        Args:
            frequency: Frequency of returns used for covariance calculation
            
        Returns:
            pd.DataFrame: Covariance matrix
        """
        returns = self.get_returns(frequency)
        return returns.cov()
    
    def _resample_data(self, data: pd.DataFrame, frequency: str) -> pd.DataFrame:
        """Resample data to the specified frequency."""
        freq_map = {
            'daily': 'D',
            'weekly': 'W',
            'monthly': 'M',
            'quarterly': 'Q',
            'yearly': 'Y'
        }
        
        if frequency not in freq_map:
            raise ValueError(f"Unsupported frequency: {frequency}. "
                             f"Supported frequencies: {list(freq_map.keys())}")
        
        return data.resample(freq_map[frequency]).last()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the loaded data."""
        if self.processed_data is None:
            raise ValueError("No processed data available. Run load_data() first.")
            
        summary = {
            'shape': self.processed_data.shape,
            'date_range': {
                'start': self.processed_data.index.min().isoformat(),
                'end': self.processed_data.index.max().isoformat()
            },
            'missing_values': self.processed_data.isnull().sum().to_dict(),
            'columns': list(self.processed_data.columns)
        }
        
        return summary