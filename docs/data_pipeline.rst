Data Pipeline Module
====================

The data pipeline module handles market data ingestion and preprocessing.

CSV Data Source
---------------
.. autoclass:: portfolio_optimizer.data_pipeline.csv_data_source.CSVDataSource
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.data_pipeline.csv_data_source import CSVDataSource

data_source = CSVDataSource(file_path="data/returns.csv")
raw_data = data_source.load_data()
processed_data = data_source.preprocess_data(raw_data)
```

API Data Source
---------------
.. autoclass:: portfolio_optimizer.data_pipeline.api_data_source.APIDataSource
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.data_pipeline.api_data_source import APIDataSource

data_source = APIDataSource(api_endpoint="https://api.example.com/market-data")
raw_data = data_source.fetch_data()
processed_data = data_source.preprocess_data(raw_data)
```

Key Features
------------
- Abstract base class for consistent data source interface
- CSV file support with date parsing and missing value handling
- API data source with request configuration and error handling
- Data preprocessing with normalization and outlier detection
- Configurable data validation rules