"""
Base classes for visualization components.

This module defines abstract base classes for visualization components that
can be used to visualize portfolio optimization results.
"""

import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List

class Visualizer(ABC):
    """
    Abstract base class for visualization components.
    
    Defines the interface for visualization components that can be used
    to visualize portfolio optimization results.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize visualizer with configuration.
        
        Args:
            config: Configuration dictionary containing visualizer-specific parameters
        """
        self.config = config
        self.figure_size = config.get('figure_size', (12, 8))
        self.color_scheme = config.get('color_scheme', 'default')
        self.style = config.get('style', 'seaborn')
    
    @abstractmethod
    def plot(self, data: Dict[str, Any], **kwargs) -> plt.Figure:
        """
        Generate a visualization plot.
        
        Args:
            data: Dictionary containing data to visualize
            **kwargs: Additional visualization parameters
            
        Returns:
            plt.Figure: Generated matplotlib figure
        """
        pass
    
    def set_style(self, style: str) -> None:
        """
        Set matplotlib style for visualization.
        
        Args:
            style: Name of matplotlib style to use
        """
        self.style = style
        plt.style.use(style)
    
    def set_figure_size(self, size: tuple) -> None:
        """
        Set default figure size for visualizations.
        
        Args:
            size: Tuple of (width, height) in inches
        """
        self.figure_size = size
    
    def set_color_scheme(self, scheme: str) -> None:
        """
        Set color scheme for visualizations.
        
        Args:
            scheme: Name of color scheme to use
        """
        self.color_scheme = scheme
    
    def save_plot(self, fig: plt.Figure, path: str, dpi: int = 300) -> None:
        """
        Save visualization to file.
        
        Args:
            fig: Matplotlib figure to save
            path: File path to save the figure
            dpi: Resolution in dots per inch
        """
        fig.savefig(path, dpi=dpi, bbox_inches='tight')
    
    def show_plot(self, fig: plt.Figure) -> None:
        """
        Display visualization.
        
        Args:
            fig: Matplotlib figure to display
        """
        plt.show(fig)