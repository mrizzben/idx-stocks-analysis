"""
Mean-Variance Risk Model Implementation

This module implements the classic mean-variance risk model for portfolio optimization.
"""

import numpy as np
import pandas as pd
from .base import RiskModel
from typing import Dict, Any

class MeanVarianceModel(RiskModel):
    """
    Implementation of the Mean-Variance risk model for portfolio optimization.
    
    This model uses the traditional Markowitz approach to calculate portfolio risk
    based on the covariance matrix of asset returns.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Mean-Variance risk model with configuration.
        
        Args:
            config: Configuration dictionary containing model-specific parameters.
                   Expected keys:
                   - risk_aversion: Risk aversion parameter (default: 1.0)
                   - annualization_factor: Factor to annualize risk (default: 252)
        """
        super().__init__(config)
        self.risk_aversion = config.get('risk_aversion', 1.0)
        self.annualization_factor = config.get('annualization_factor', 252)
    
    def calculate_risk(self, weights: np.ndarray) -> float:
        """
        Calculate portfolio risk using the mean-variance approach.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            float: Annualized portfolio risk (volatility)
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for risk calculation")
            
        # Calculate portfolio variance
        portfolio_variance = weights.T @ self.covariance_matrix.values @ weights
        
        # Calculate annualized portfolio risk (volatility)
        annualized_risk = np.sqrt(portfolio_variance * self.annualization_factor)
        
        return annualized_risk
    
    def optimize_weights(self, expected_returns: np.ndarray) -> np.ndarray:
        """
        Optimize portfolio weights using mean-variance optimization.
        
        Args:
            expected_returns: Array of expected returns for assets
            
        Returns:
            np.ndarray: Optimized portfolio weights
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for weight optimization")
            
        # Calculate optimal weights using Markowitz solution
        inv_cov_matrix = np.linalg.inv(self.covariance_matrix.values)
        ones = np.ones(len(expected_returns))
        
        # Calculate optimal portfolio weights
        numerator = inv_cov_matrix @ expected_returns
        denominator = ones.T @ inv_cov_matrix @ expected_returns
        
        # Calculate weights based on risk aversion
        optimal_weights = (self.risk_aversion * numerator) / denominator
        
        return optimal_weights
    
    def set_risk_aversion(self, risk_aversion: float) -> None:
        """
        Update the risk aversion parameter.
        
        Args:
            risk_aversion: New risk aversion value
        """
        self.risk_aversion = risk_aversion
    
    def set_annualization_factor(self, factor: int) -> None:
        """
        Update the annualization factor.
        
        Args:
            factor: New annualization factor
        """
        self.annualization_factor = factor