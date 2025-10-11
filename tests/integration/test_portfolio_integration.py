import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.core.hrp import HRP
from portfolio_optimizer.data_pipeline.csv_data_source import CSVDataSource
from portfolio_optimizer.risk_management.mean_variance import MeanVarianceRiskModel
from portfolio_optimizer.visualization.portfolio_weights import PortfolioWeightsVisualizer

@pytest.fixture
def sample_data():
    # Create synthetic financial data
    dates = pd.date_range('2023-01-01', periods=100)
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    data = pd.DataFrame(np.random.randn(100, 4), index=dates, columns=assets)
    return data

def test_data_to_optimization_integration(sample_data):
    """Test integration between data pipeline and optimization engine"""
    risk_model = MeanVarianceRiskModel()
    optimizer = MarkowitzOptimizer(risk_model=risk_model)
    
    # Test data pipeline integration
    data_source = CSVDataSource()
    data_source.data = sample_data
    
    # Get processed data from pipeline
    processed_data = data_source.get_data()
    
    # Run optimization
    weights = optimizer.optimize(processed_data)
    
    # Validate results
    assert isinstance(weights, dict)
    assert len(weights) == len(sample_data.columns)
    assert np.isclose(sum(weights.values()), 1.0)
    
    # Test risk model integration
    risk_metrics = risk_model.calculate_risk_metrics(processed_data)
    assert 'volatility' in risk_metrics
    assert 'correlation' in risk_metrics

def test_optimization_to_visualization_integration(sample_data):
    """Test integration between optimization and visualization components"""
    optimizer = HRP()
    visualizer = PortfolioWeightsVisualizer()
    
    # Run optimization
    weights = optimizer.optimize(sample_data)
    
    # Generate visualization
    fig = visualizer.visualize(weights)
    
    # Validate visualization
    assert fig is not None
    assert len(fig.data) > 0

def test_full_pipeline_integration(tmpdir):
    """Test full pipeline from data loading to visualization"""
    # Setup temporary CSV file
    data_path = tmpdir.join("test_data.csv")
    sample_data = pd.DataFrame({
        'AAPL': np.random.randn(100),
        'GOOGL': np.random.randn(100)
    })
    sample_data.to_csv(data_path)
    
    # Initialize components
    data_source = CSVDataSource(file_path=str(data_path))
    optimizer = MarkowitzOptimizer()
    visualizer = PortfolioWeightsVisualizer()
    
    # Execute full pipeline
    raw_data = data_source.load_data()
    processed_data = data_source.preprocess_data(raw_data)
    weights = optimizer.optimize(processed_data)
    fig = visualizer.visualize(weights)
    
    # Validate pipeline
    assert not raw_data.empty
    assert len(processed_data) == len(raw_data)
    assert isinstance(weights, dict)
    assert len(fig.data) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])