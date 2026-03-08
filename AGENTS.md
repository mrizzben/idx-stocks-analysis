# AGENTS.md - Developer & Agent Guidelines

This document provides essential information for developer agents operating in the idx-stocks-analysis repository.

## 1. Project Overview
The idx-stocks-analysis project is a quantitative portfolio optimization system designed for the Indonesian stock market (IDX). It provides a web-based interface (FastAPI + Streamlit) for clustering and optimization algorithms, including Hierarchical Risk Parity (HRP) and Mean-Variance Optimization (Markowitz).

### Directory Structure
- portfolio_optimizer/: Main application package.
  - core/: Core optimization algorithms (HRP, Markowitz, Monte Carlo).
  - services/: Modular services for data ingestion (IDXDataService), feature extraction (FeatureService), and portfolio management (PortfolioService).
  - api/: FastAPI models and endpoints.
  - deprecated/: Legacy modules from previous architectural drafts.
- api/: Entry point for the FastAPI backend.
- ui/: Entry point for the Streamlit dashboard.
- tests/: Comprehensive test suite using pytest.
- notebooks/: Research and exploratory data analysis.

---

## 2. Development & Commands
The project uses uv for dependency management and pytest for testing.

### Environment Setup
bash
# Sync dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate


### Build & Lint
bash
# Run linting
pylint portfolio_optimizer tests

### Testing
bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest tests/integration/test_portfolio_ui.py


---

## 3. Code Style Guidelines

### Python Version
- Targeted for Python 3.12. (Pinned due to dependency compatibility issues with Python 3.13 on macOS).

### Imports
- Standard library imports first.
- Third-party imports second (e.g., numpy, pandas, scipy).
- Local project imports last.
- Imports should be sorted alphabetically within each group.

### Formatting
- Follow PEP 8 conventions.
- Use 4 spaces for indentation.
- Maximum line length: 88-100 characters.

---

## 4. Architecture & Design Patterns
- Service Layer Pattern: Use the services/ directory for business logic to keep API and UI layers thin.
- Base Classes: Use BaseOptimizer and OptimizationResult from core/base.py for consistency.
- Unified Entry Point: The PortfolioService provides a single interface for all optimization strategies.

---

## 5. Best Practices for Agents
- Testing: Always run relevant tests after modifying core logic.
- Documentation: Maintain docstrings using Google style.
- Library-First: Ensure core logic is packaged within portfolio_optimizer/ to allow both API and notebook usage.
