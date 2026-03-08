# UI Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir streamlit pandas numpy plotly requests openpyxl

# Copy project files
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
