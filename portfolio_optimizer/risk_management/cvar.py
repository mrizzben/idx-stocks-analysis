"""
Conditional Value at Risk (CVaR) Implementation

This module implements the Conditional Value at Risk (CVaR) model for portfolio optimization.
"""

import numpy as np
import pandas as pd
from .base import RiskModel
from typing import Dict, Any

class CVaRModel(RiskModel):
    """
    Implementation of the Conditional Value at Risk (CVaR) model for portfolio optimization.
    
    This model focuses on minimizing the expected loss in the tail of the loss distribution,
    providing protection against extreme market events.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CVaR risk model with configuration.
        
        Args:
            config: Configuration dictionary containing model-specific parameters.
                   Expected keys:
                   - alpha: Confidence level for CVaR calculation (default: 0.05)
                   - risk_aversion: Risk aversion parameter (default: 1.0)
                   - max_iterations: Maximum iterations for optimization (default: 1000)
                   - tolerance: Convergence tolerance (default: 1e-8)
        """
        super().__init__(config)
        self.alpha = config.get('alpha', 0.05)
        self.risk_aversion = config.get('risk_aversion', 1.0)
        self.max_iterations = config.get('max_iterations', 1000)
        self.tolerance = config.get('tolerance', 1e-8)
        self.loss_threshold = None
    
    def calculate_risk(self, weights: np.ndarray) -> float:
        """
        Calculate portfolio CVaR using historical simulation.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            float: Calculated portfolio CVaR
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for risk calculation")
            
        # Calculate portfolio returns
        portfolio_returns = self.returns_data.values @ weights
        
        # Calculate Value at Risk (VaR)
        var = np.percentile(portfolio_returns, 100 * (1 - self.alpha))
        
        # Calculate CVaR as average of returns below VaR
        tail_losses = portfolio_returns[portfolio_returns <= var]
        cvar = -np.mean(tail_losses)
        
        return cvar
    
    def optimize_weights(self, expected_returns: np.ndarray) -> np.ndarray:
        """
        Optimize portfolio weights using CVaR minimization.
        
        Args:
            expected_returns: Array of expected returns for assets
            
        Returns:
            np.ndarray: Optimized portfolio weights
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for weight optimization")
            
        n_assets = len(expected_returns)
        returns_matrix = self.returns_data.values
        
        # Initialize weights equally
        weights = np.ones(n_assets) / n_assets
        
        # Optimization using Rockafellar-Uryasev algorithm
        for _ in range(self.max_iterations):
            # Calculate portfolio returns
            portfolio_returns = returns_matrix @ weights
            
            # Calculate loss threshold (VaR)
            self.loss_threshold = np.percentile(portfolio_returns, 100 * (1 - self.alpha))
            
            # Calculate gradient of CVaR
            tail_mask = portfolio_returns <= self.loss_threshold
            tail_returns = returns_matrix[tail_mask]
            
            if len(tail_returns) == 0:
                gradient = np.zeros(n_assets)
            else:
                gradient = -np.mean(tail_returns, axis=0) / (1 - self.alpha)
            
            # Update weights using gradient descent
            new_weights = weights - self.risk_aversion * gradient
            
            # Apply constraints (non-negative weights that sum to 1)
            new_weights = np.clip(new_weights, 0, 1)
            new_weights /= np.sum(new_weights)
            
            # Check for convergence
            if np.linalg.norm(new_weights - weights) < self.tolerance:
                break
                
            weights = new_weights
        
        return weights
    
    def set_alpha(self, alpha: float) -> None:
        """
        Update the confidence level for CVaR calculation.
        
        Args:
            alpha: New confidence level (between 0 and 1)
        """
        if not 0 < alpha < 1:
            raise ValueError("Alpha must be between 0 and 1")
        self.alpha = alpha
    
    def set_risk_aversion(self, risk_aversion: float) -> None:
        """
        Update the risk aversion parameter.
        
        Args:
            risk_aversion: New risk aversion value
        """
        self.risk_aversion = risk_aversion
    
    def get_var(self, weights: np.ndarray) -> float:
        """
        Calculate Value at Risk (VaR) for the portfolio.
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            float: Calculated portfolio VaR
        """
        if not self.validate_data():
            raise ValueError("Invalid or missing data for VaR calculation")
            
        # Calculate portfolio returns
        portfolio_returns = self.returns_data.values @ weights
        
        # Calculate Value at Risk (VaR)
        var = np.percentile(portfolio_returns, 100 * (1 - self.alpha))
        
        return -var