"""
Portfolio Weights Visualization

This module implements visualization for portfolio weights distribution.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .base import Visualizer
from typing import Dict, Any

class PortfolioWeightsVisualizer(Visualizer):
    """
    Visualizer for portfolio weights distribution.
    
    Creates visualizations showing the allocation of weights across different assets
    in a portfolio, with options for both absolute weights and relative proportions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the portfolio weights visualizer.
        
        Args:
            config: Configuration dictionary containing visualizer-specific parameters.
                   Expected keys:
                   - show_values: Whether to show numerical values on the chart (default: True)
                   - value_format: Format string for value display (default: '{:.1%}')
                   - sort_weights: Whether to sort weights by magnitude (default: True)
        """
        super().__init__(config)
        self.show_values = config.get('show_values', True)
        self.value_format = config.get('value_format', '{:.1%}')
        self.sort_weights = config.get('sort_weights', True)
    
    def plot(self, data: Dict[str, Any], **kwargs) -> plt.Figure:
        """
        Generate portfolio weights visualization.
        
        Args:
            data: Dictionary containing data to visualize. Expected keys:
                - 'weights': Array or Series of portfolio weights
                - 'assets': List of asset names (optional if weights is a Series)
            **kwargs: Additional visualization parameters:
                - title: Plot title
                - xlabel: X-axis label
                - ylabel: Y-axis label
                - color: Bar color (single color or list)
                - horizontal: Whether to create a horizontal bar chart (default: True)
                - show_legend: Whether to show a legend (default: False)
                
        Returns:
            plt.Figure: Generated matplotlib figure
        """
        # Extract data
        weights = data.get('weights')
        if weights is None:
            raise ValueError("Portfolio weights data is required for visualization")
        
        # Handle different input types
        if isinstance(weights, pd.Series):
            assets = weights.index.tolist()
            weights_array = weights.values
        elif 'assets' in data:
            assets = data['assets']
            weights_array = np.array(weights)
        else:
            assets = [f'Asset {i+1}' for i in range(len(weights))]
            weights_array = np.array(weights)
        
        # Sort weights if requested
        if self.sort_weights:
            sort_idx = np.argsort(weights_array)[::-1]
            weights_array = weights_array[sort_idx]
            assets = [assets[i] for i in sorted(sort_idx)]
        
        # Get visualization parameters
        title = kwargs.get('title', 'Portfolio Weights Distribution')
        xlabel = kwargs.get('xlabel', 'Assets')
        ylabel = kwargs.get('ylabel', 'Weight')
        color = kwargs.get('color', 'skyblue')
        horizontal = kwargs.get('horizontal', True)
        show_legend = kwargs.get('show_legend', False)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Plot weights
        if horizontal:
            bars = ax.barh(assets, weights_array, color=color)
            ax.set_xlim(0, max(weights_array) * 1.1)
            ax.invert_yaxis()
        else:
            bars = ax.bar(assets, weights_array, color=color)
            ax.set_ylim(0, max(weights_array) * 1.1)
        
        # Format plot
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Show values if requested
        if self.show_values:
            for bar in bars:
                width = bar.get_width()
                height = bar.get_height()
                
                if horizontal:
                    ax.text(width * 1.01, bar.get_y() + height/2, 
                           self.value_format.format(width), va='center')
                else:
                    ax.text(bar.get_x() + width/2, height * 1.01,
                           self.value_format.format(height), ha='center')
        
        # Show legend if requested
        if show_legend:
            ax.legend()
        
        # Apply style
        plt.style.use(self.style)
        
        return fig