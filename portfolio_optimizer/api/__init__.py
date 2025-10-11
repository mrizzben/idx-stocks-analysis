"""
Portfolio Optimization API Module

This package contains the API interface for portfolio optimization services.
"""

from flask import Flask, request, jsonify
import logging
import traceback
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioOptimizationAPI:
    """
    REST API interface for portfolio optimization services.
    
    This class provides a Flask-based API for portfolio optimization functionality,
    exposing endpoints for different optimization methods and handling request
    processing, validation, and response formatting.
    """
    
    def __init__(self, optimizer_engine):
        """
        Initialize the API interface.
        
        Args:
            optimizer_engine: Instance of the portfolio optimization engine
        """
        self.app = Flask(__name__)
        self.optimizer_engine = optimizer_engine
        self._register_routes()
        
    def _register_routes(self):
        """Register API routes and endpoints."""
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint to verify API availability."""
            return jsonify({
                'status': 'healthy',
                'components': {
                    'optimizer': True,
                    'data_pipeline': True,
                    'risk_management': True
                }
            })
        
        @self.app.route('/api/optimize', methods=['POST'])
        def optimize_portfolio():
            """Endpoint for portfolio optimization requests."""
            try:
                # Get request data
                request_data = request.get_json()
                
                # Validate input data
                if not request_data or not isinstance(request_data, dict):
                    return jsonify({
                        'error': 'Invalid input data',
                        'message': 'Request body must be a JSON object'
                    }), 400
                
                # Extract optimization parameters
                optimization_type = request_data.get('type', 'mean_variance')
                assets = request_data.get('assets')
                returns_data = request_data.get('returns')
                covariance_matrix = request_data.get('covariance')
                constraints = request_data.get('constraints', {})
                risk_free_rate = request_data.get('risk_free_rate', 0.0)
                
                # Validate required parameters
                if not assets:
                    return jsonify({
                        'error': 'Missing assets',
                        'message': 'Asset list is required'
                    }), 400
                
                if not returns_data:
                    return jsonify({
                        'error': 'Missing returns data',
                        'message': 'Expected returns data is required'
                    }), 400
                
                # Call optimization engine
                result = self.optimizer_engine.optimize(
                    optimization_type=optimization_type,
                    assets=assets,
                    expected_returns=returns_data,
                    covariance_matrix=covariance_matrix,
                    constraints=constraints,
                    risk_free_rate=risk_free_rate
                )
                
                # Return optimization result
                return jsonify({
                    'success': True,
                    'result': result
                })
                
            except Exception as e:
                # Log the error with traceback
                logger.error(f"Error in portfolio optimization: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Return error response
                return jsonify({
                    'error': 'Internal server error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/backtest', methods=['POST'])
        def backtest_strategy():
            """Endpoint for portfolio backtesting requests."""
            try:
                # Get request data
                request_data = request.get_json()
                
                # Validate input data
                if not request_data or not isinstance(request_data, dict):
                    return jsonify({
                        'error': 'Invalid input data',
                        'message': 'Request body must be a JSON object'
                    }), 400
                
                # Extract backtesting parameters
                portfolio_config = request_data.get('portfolio_config')
                historical_data = request_data.get('historical_data')
                rebalance_frequency = request_data.get('rebalance_frequency', 'monthly')
                transaction_costs = request_data.get('transaction_costs', 0.0)
                
                # Validate required parameters
                if not portfolio_config:
                    return jsonify({
                        'error': 'Missing portfolio configuration',
                        'message': 'Portfolio configuration is required'
                    }), 400
                
                if not historical_data:
                    return jsonify({
                        'error': 'Missing historical data',
                        'message': 'Historical data is required'
                    }), 400
                
                # Call backtesting functionality
                result = self.optimizer_engine.backtest(
                    portfolio_config=portfolio_config,
                    historical_data=historical_data,
                    rebalance_frequency=rebalance_frequency,
                    transaction_costs=transaction_costs
                )
                
                # Return backtesting result
                return jsonify({
                    'success': True,
                    'result': result
                })
                
            except Exception as e:
                # Log the error with traceback
                logger.error(f"Error in backtesting: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Return error response
                return jsonify({
                    'error': 'Internal server error',
                    'message': str(e)
                }), 500
        
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        Run the Flask application.
        
        Args:
            host: Host address for the server
            port: Port number for the server
            debug: Whether to run in debug mode
        """
        self.app.run(host=host, port=port, debug=debug)