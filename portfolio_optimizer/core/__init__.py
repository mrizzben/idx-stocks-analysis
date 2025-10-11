"""
Portfolio Optimization Core Module

This module provides the core optimization functionality for the portfolio optimization system.
It implements a factory pattern to create different types of portfolio optimizers.
"""

from .base import BaseOptimizer, OptimizationResult
from .markowitz import MarkowitzOptimizer
from .hrp import HierarchicalRiskParityOptimizer
from .monte_carlo import MonteCarloOptimizer

class OptimizerFactory:
    """
    Factory class for creating portfolio optimizer instances.
    
    This class provides a unified interface for creating different types of portfolio optimizers
    based on the specified optimizer type.
    """
    
    @staticmethod
    def create_optimizer(optimizer_type: str, returns: pd.DataFrame, covariance_matrix: pd.DataFrame):
        """
        Create a portfolio optimizer instance of the specified type.
        
        Args:
            optimizer_type: Type of optimizer to create ('markowitz', 'hrp', 'monte_carlo')
            returns: Historical returns for assets (n_assets × n_periods)
            covariance_matrix: Asset covariance matrix (n_assets × n_assets)
            
        Returns:
            BaseOptimizer: Instance of the requested optimizer type
            
        Raises:
            ValueError: If an unknown optimizer type is requested
        """
        if optimizer_type.lower() == 'markowitz':
            return MarkowitzOptimizer(returns, covariance_matrix)
        elif optimizer_type.lower() == 'hrp':
            return HierarchicalRiskParityOptimizer(returns, covariance_matrix)
        elif optimizer_type.lower() == 'monte_carlo':
            return MonteCarloOptimizer(returns, covariance_matrix)
        else:
            raise ValueError(f"Unknown optimizer type: {optimizer_type}")
    
    @staticmethod
    def get_available_optimizers() -> List[str]:
        """
        Get a list of available optimizer types.
        
        Returns:
            List[str]: List of available optimizer types
        """
        return ['markowitz', 'hrp', 'monte_carlo']

# Version of the core optimization module
__version__ = '0.1.0'

# Export key classes and functions at module level for easier access
__all__ = [
    'BaseOptimizer',
    'OptimizationResult',
    'OptimizerFactory',
    'MarkowitzOptimizer',
    'HierarchicalRiskParityOptimizer',
    'MonteCarloOptimizer'
]