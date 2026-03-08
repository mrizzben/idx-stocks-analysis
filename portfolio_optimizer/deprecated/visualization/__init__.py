"""
Portfolio Optimization Visualization Module

This package contains visualization components for portfolio optimization results.
"""

from .base import Visualizer
from .portfolio_weights import PortfolioWeightsVisualizer
from .portfolio_performance import PortfolioPerformanceVisualizer

class VisualizerFactory:
    """
    Factory class for creating visualizer instances.
    
    This class provides a unified interface for creating different types of visualizers
    based on the specified visualizer type. It supports various visualization types
    including portfolio weights and performance visualizers.
    """
    
    @staticmethod
    def create_visualizer(visualizer_type: str, config: dict) -> Visualizer:
        """
        Create a visualizer instance of the specified type.
        
        Args:
            visualizer_type: Type of visualizer to create ('portfolio_weights', 'portfolio_performance')
            config: Configuration dictionary containing visualizer-specific parameters
            
        Returns:
            Visualizer: Instance of the requested visualizer type
            
        Raises:
            ValueError: If an unknown visualizer type is requested
        """
        if visualizer_type.lower() == 'portfolio_weights':
            return PortfolioWeightsVisualizer(config)
        elif visualizer_type.lower() == 'portfolio_performance':
            return PortfolioPerformanceVisualizer(config)
        else:
            raise ValueError(f"Unknown visualizer type: {visualizer_type}")
    
    @staticmethod
    def get_available_visualizers() -> list:
        """
        Get a list of available visualizer types.
        
        Returns:
            list: List of available visualizer types
        """
        return ['portfolio_weights', 'portfolio_performance']

# Version of the visualization module
__version__ = '0.1.0'

# Export key classes and functions at module level for easier access
__all__ = [
    'Visualizer',
    'VisualizerFactory',
    'PortfolioWeightsVisualizer',
    'PortfolioPerformanceVisualizer'
]