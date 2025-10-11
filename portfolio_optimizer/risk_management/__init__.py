"""
Risk Management Module for Portfolio Optimization

This module provides implementations of various risk management models used in portfolio optimization.
"""

from .base import RiskModel
from .mean_variance import MeanVarianceModel
from .cvar import CVaRModel

class RiskModelFactory:
    """
    Factory class for creating risk model instances.
    
    This class provides a unified interface for creating different types of risk models
    based on the specified model type. It supports various risk model types including
    mean-variance and CVaR.
    """
    
    @staticmethod
    def create_risk_model(model_type: str, config: dict) -> RiskModel:
        """
        Create a risk model instance of the specified type.
        
        Args:
            model_type: Type of risk model to create ('mean_variance', 'cvar')
            config: Configuration dictionary containing model-specific parameters
            
        Returns:
            RiskModel: Instance of the requested risk model type
            
        Raises:
            ValueError: If an unknown model type is requested
        """
        if model_type.lower() == 'mean_variance':
            return MeanVarianceModel(config)
        elif model_type.lower() == 'cvar':
            return CVaRModel(config)
        else:
            raise ValueError(f"Unknown risk model type: {model_type}")
    
    @staticmethod
    def get_available_models() -> list:
        """
        Get a list of available risk model types.
        
        Returns:
            list: List of available risk model types
        """
        return ['mean_variance', 'cvar']

# Version of the risk management module
__version__ = '0.1.0'

# Export key classes and functions at module level for easier access
__all__ = [
    'RiskModel',
    'RiskModelFactory',
    'MeanVarianceModel',
    'CVaRModel'
]