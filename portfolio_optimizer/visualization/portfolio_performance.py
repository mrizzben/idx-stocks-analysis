"""
Portfolio Performance Visualization

This module implements visualization for portfolio performance metrics.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .base import Visualizer
from typing import Dict, Any

class PortfolioPerformanceVisualizer(Visualizer):
    """
    Visualizer for portfolio performance metrics.
    
    Creates visualizations showing portfolio performance over time, including
    cumulative returns, drawdowns, and performance comparisons against benchmarks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the portfolio performance visualizer.
        
        Args:
            config: Configuration dictionary containing visualizer-specific parameters.
                   Expected keys:
                   - date_format: Date format for x-axis labels (default: '%Y-%m-%d')
                   - show_grid: Whether to show grid lines (default: True)
                   - legend_position: Position of legend (default: 'upper left')
        """
        super().__init__(config)
        self.date_format = config.get('date_format', '%Y-%m-%d')
        self.show_grid = config.get('show_grid', True)
        self.legend_position = config.get('legend_position', 'upper left')
    
    def plot_cumulative_returns(self, data: Dict[str, Any], **kwargs) -> plt.Figure:
        """
        Generate cumulative returns visualization.
        
        Args:
            data: Dictionary containing data to visualize. Expected keys:
                - 'returns': Array or Series of portfolio returns
                - 'benchmark_returns': Array or Series of benchmark returns (optional)
            **kwargs: Additional visualization parameters:
                - title: Plot title
                - xlabel: X-axis label
                - ylabel: Y-axis label
                - portfolio_label: Label for portfolio returns (default: 'Portfolio')
                - benchmark_label: Label for benchmark returns (default: 'Benchmark')
                - show_legend: Whether to show a legend (default: True)
                
        Returns:
            plt.Figure: Generated matplotlib figure
        """
        # Extract data
        returns = data.get('returns')
        if returns is None:
            raise ValueError("Portfolio returns data is required for visualization")
        
        # Handle different input types
        if isinstance(returns, pd.Series):
            dates = returns.index
            returns_array = returns.values
        else:
            dates = pd.date_range(start='2020-01-01', periods=len(returns), freq='D')
            returns_array = np.array(returns)
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + returns_array)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Plot portfolio returns
        ax.plot(dates, cumulative_returns, label=kwargs.get('portfolio_label', 'Portfolio'))
        
        # Plot benchmark returns if provided
        benchmark_returns = data.get('benchmark_returns')
        if benchmark_returns is not None:
            if isinstance(benchmark_returns, pd.Series):
                benchmark_dates = benchmark_returns.index
                benchmark_array = benchmark_returns.values
            else:
                benchmark_dates = dates  # Assume same dates as portfolio
                benchmark_array = np.array(benchmark_returns)
            
            benchmark_cumulative = np.cumprod(1 + benchmark_array)
            ax.plot(benchmark_dates, benchmark_cumulative, 
                   label=kwargs.get('benchmark_label', 'Benchmark'))
        
        # Format plot
        ax.set_title(kwargs.get('title', 'Cumulative Portfolio Returns'))
        ax.set_xlabel(kwargs.get('xlabel', 'Date'))
        ax.set_ylabel(kwargs.get('ylabel', 'Cumulative Return'))
        
        # Format date axis
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(self.date_format))
        fig.autofmt_xdate()
        
        # Show grid if requested
        if self.show_grid:
            ax.grid(True)
        
        # Show legend if requested
        if kwargs.get('show_legend', True):
            ax.legend(loc=self.legend_position)
        
        # Apply style
        plt.style.use(self.style)
        
        return fig
    
    def plot_drawdown(self, data: Dict[str, Any], **kwargs) -> plt.Figure:
        """
        Generate drawdown visualization.
        
        Args:
            data: Dictionary containing data to visualize. Expected keys:
                - 'returns': Array or Series of portfolio returns
            **kwargs: Additional visualization parameters:
                - title: Plot title
                - xlabel: X-axis label
                - ylabel: Y-axis label
                - area_color: Color for drawdown area (default: 'red')
                - area_alpha: Transparency for drawdown area (default: 0.3)
                
        Returns:
            plt.Figure: Generated matplotlib figure
        """
        # Extract data
        returns = data.get('returns')
        if returns is None:
            raise ValueError("Portfolio returns data is required for visualization")
        
        # Handle different input types
        if isinstance(returns, pd.Series):
            dates = returns.index
            returns_array = returns.values
        else:
            dates = pd.date_range(start='2020-01-01', periods=len(returns), freq='D')
            returns_array = np.array(returns)
        
        # Calculate cumulative returns and drawdown
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Plot drawdown area
        area_color = kwargs.get('area_color', 'red')
        area_alpha = kwargs.get('area_alpha', 0.3)
        ax.fill_between(dates, drawdown, 0, color=area_color, alpha=area_alpha)
        ax.plot(dates, drawdown, color=area_color, alpha=0.8)
        
        # Format plot
        ax.set_title(kwargs.get('title', 'Portfolio Drawdown'))
        ax.set_xlabel(kwargs.get('xlabel', 'Date'))
        ax.set_ylabel(kwargs.get('ylabel', 'Drawdown (%)'))
        
        # Format date axis
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(self.date_format))
        fig.autofmt_xdate()
        
        # Show grid if requested
        if self.show_grid:
            ax.grid(True)
        
        # Apply style
        plt.style.use(self.style)
        
        return fig