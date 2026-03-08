# Research: Portfolio Optimization UI

## Decision 1: Architecture - FastAPI + Streamlit
- **Decision**: Use a decoupled architecture with a FastAPI backend for optimization and data services, and a Streamlit frontend for the UI.
- **Rationale**: Separates heavy computation and data fetching from the presentation layer. Allows the backend to be reused for CLI or other interfaces. Streamlit provides rapid UI development with Python.
- **Alternatives considered**: Mono-Streamlit (logic and UI in one script), which was rejected because it makes testing and refactoring `/src` into services more complex.

## Decision 2: Refactoring Pattern for `/src`
- **Decision**: Implement a Service Layer pattern where existing logic in `src/data/get_stocks.py` and `src/features/feature_extract.py` is refactored into `IDXDataService` and `FeatureService` classes within a new `portfolio_optimizer.services` package.
- **Rationale**: Ensures the code is modular, testable, and reusable by both the FastAPI backend and the original research scripts.
- **Alternatives considered**: Direct import of scripts (Rejected due to side effects and poor testability).

## Decision 3: Data Ingestion & IDX Suffix Handling
- **Decision**: Implement a ticker normalization utility that automatically appends `.JK` to 4-letter alphanumeric strings if no suffix is provided, while still allowing global suffixes (e.g., `.L`, `.T`).
- **Rationale**: Optimizes for the primary Indonesian market use case while maintaining the "Global support" requirement from clarifications.
- **Alternatives considered**: Strict regex matching for IDX only (Rejected to allow global support).

## Decision 4: Visualization Library
- **Decision**: Use **Plotly** for interactive charts (Pie/Bar) and the hierarchical cluster dendrogram.
- **Rationale**: Native support in Streamlit via `st.plotly_chart` and provides the necessary interactivity for "identifying top-weighted assets" (SC-004) and inspecting HRP clusters.
- **Alternatives considered**: Matplotlib (Static/non-interactive), Altair (Complexity for dendrograms).
