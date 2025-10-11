"""
Base classes for risk management components.

This module defines abstract base classes for risk models and risk management components
that are extended by specific implementations.
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List

class RiskModel(ABC):
    """
    Abstract base class for risk models.
    
    Defines the interface for risk modeling and management components that
    can be used in portfolio optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk model with configuration.
        
        Args:
            config: Configuration dictionary containing model-specific parameters
        """
        self.config = config
        self.covariance_matrix: Optional[pd.DataFrame] = None
        self.returns_data: Optional[pd.DataFrame] = None
    
    @abstractmethod
    def calculate_risk(self, weights: np.ndarray) -> float:
        """
        Calculate portfolio risk based on given weights.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            float: Calculated portfolio risk
        """
        pass
    
    @abstractmethod
    def optimize_weights(self, expected_returns: np.ndarray) -> np.ndarray:
        """
        Optimize portfolio weights based on risk model.
        
        Args:
            expected_returns: Array of expected returns for assets
            
        Returns:
            np.ndarray: Optimized portfolio weights
        """
        pass
    
    def set_covariance_matrix(self, covariance_matrix: pd.DataFrame) -> None:
        """
        Set covariance matrix for risk calculations.
        
        Args:
            covariance_matrix: Covariance matrix of asset returns
        """
        self.covariance_matrix = covariance_matrix
    
    def set_returns_data(self, returns_data: pd.DataFrame) -> None:
        """
        Set returns data for risk calculations.
        
        Args:
            returns_data: DataFrame containing asset returns
        """
        self.returns_data = returns_data
    
    def validate_data(self) -> bool:
        """
        Validate that required data is available for risk calculations.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        if self.covariance_matrix is None or self.returns_data is None:
            return False
            
        # Check covariance matrix dimensions match returns data
        if self.covariance_matrix.shape[0] != self.returns_data.shape[1]:
            return False
            
        return True
    
    def get_risk_contribution(self, weights: np.ndarray) -> pd.Series:
        """
        Calculate risk contribution of each asset in the portfolio.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            pd.Series: Risk contribution of each asset
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for risk contribution calculation")
            
        # Calculate marginal risk contribution
        mrc = self.covariance_matrix.values @ weights
        # Calculate total portfolio risk
        portfolio_risk = np.sqrt(weights.T @ mrc)
        # Calculate risk contribution
        rc = (weights * mrc) / portfolio_risk
        
        return pd.Series(rc, index=self.returns_data.columns)