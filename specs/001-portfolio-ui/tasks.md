# Tasks: Portfolio Optimization UI

**Branch**: `001-portfolio-ui`
**Implementation Plan**: `/Users/rizz/idx-stocks-analysis/specs/001-portfolio-ui/plan.md`
**User Stories**: `/Users/rizz/idx-stocks-analysis/specs/001-portfolio-ui/spec.md`

## Phase 1: Setup

- [X] T001 Initialize project structure for `api/`, `ui/`, and `services/`
- [X] T002 Configure `uv` dependencies in `pyproject.toml` (FastAPI, Streamlit, Plotly, yfinance)
- [X] T003 [P] Create base Pydantic models for API request/response in `api/v1/models.py`
- [X] T004 Create FastAPI application entry point in `api/main.py`

## Phase 2: Foundational (Logic Refactoring)

*Goal: Refactor existing research code in `/src` into modular services.*

- [X] T005 [P] Create `IDXDataService` in `portfolio_optimizer/services/data_service.py` by refactoring `src/data/get_stocks.py`
- [X] T006 [P] Create `FeatureService` in `portfolio_optimizer/services/feature_service.py` by refactoring `src/features/feature_extract.py`
- [X] T007 [P] Create `PortfolioService` in `portfolio_optimizer/services/portfolio_service.py` as a wrapper for `portfolio_optimizer.core.hrp`
- [X] T008 [P] Implement ticker normalization utility (IDX suffix handling) in `portfolio_optimizer/services/utils.py`
- [X] T009 Write unit tests for refactored services in `tests/unit/test_services.py`

## Phase 3: [US1] Portfolio Weight Generation (P1)

*Goal: Support CSV upload, ticker input, and HRP optimization with weights display.*

- [X] T010 [US1] Implement `POST /fetch-data` endpoint in `api/v1/endpoints.py` using `IDXDataService`
- [X] T011 [US1] Implement `POST /optimize` endpoint in `api/v1/endpoints.py` using `PortfolioService`
- [X] T012 [P] [US1] Create basic Streamlit layout with sidebar and main panel in `ui/app.py`
- [X] T013 [US1] Implement CSV/Excel file uploader component in `ui/components/data_ingestion.py`
- [X] T014 [US1] Implement Ticker Input component with suffix defaulting in `ui/components/data_ingestion.py`
- [X] T015 [US1] Create Plotly Pie/Bar chart component for weights in `ui/components/visualizations.py`
- [X] T016 [US1] Connect UI to FastAPI backend via API client in `ui/services/api_client.py`
- [X] T028 [US1] Implement session state management for data persistence in `ui/app.py`

**Independent Test Criteria**: 
- Valid CSV upload displays weight breakdown.
- Ticker input (e.g., "BBCA") correctly fetches data and generates weights.
- weights total exactly 100%.

## Phase 4: [US2] Risk Metric Visualization (P2)

*Goal: Display Sharpe Ratio and Volatility metrics.*

- [X] T017 [US2] Update `OptimizationResult` model to include risk metrics in `api/v1/models.py`
- [X] T018 [US2] Update `PortfolioService` to calculate Sharpe Ratio and Volatility in `services/portfolio_service.py`
- [X] T019 [P] [US2] Create metrics display component (st.metric) in `ui/components/visualizations.py`
- [X] T020 [US2] Implement interactive risk-free rate input in Streamlit sidebar `ui/app.py`

**Independent Test Criteria**:
- Sharpe Ratio and Volatility are visible after optimization.
- Changing the risk-free rate slider updates the Sharpe Ratio without re-fetching data.

## Phase 5: [US3] Optimization Method Comparison (P3)

*Goal: Compare HRP with Equal Weight benchmark.*

- [X] T021 [US3] Add "Equal Weight" strategy to `PortfolioService` in `services/portfolio_service.py`
- [X] T022 [US3] Implement strategy selection dropdown in Streamlit sidebar `ui/app.py`
- [X] T023 [US3] Update Plotly component to support comparison overlays in `ui/components/visualizations.py`

**Independent Test Criteria**:
- Selecting "Equal Weight" displays uniform weight distribution.
- Metrics update accordingly when toggling between HRP and Equal Weight.

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T024 Implement error handling for invalid file formats and API timeouts in `ui/app.py`
- [X] T025 Add loading spinners (`st.spinner`) for data fetching and optimization tasks
- [X] T026 [P] Finalize `quickstart.md` with verified launch commands
- [X] T027 Run full integration test suite in `tests/integration/test_portfolio_ui.py`
- [X] T029 [P] Validate UI performance with 100 tickers in `tests/integration/test_portfolio_ui.py`
- [X] T030 Create Dockerfiles for API and UI in `docker/`
- [X] T031 Orchestrate multi-container setup in `docker/docker-compose.yml`

## Dependencies & Strategy

### Story Completion Order
1. [US1] (MVP)
2. [US2]
3. [US3]

### Implementation Strategy
- **Foundational**: Complete Phase 2 first to ensure `/src` logic is available as services.
- **MVP**: Phase 1 + Phase 2 + Phase 3 delivers the core utility.
- **Incremental**: Phase 4 and Phase 5 add analytical depth.
- **Parallelism**: Service refactoring (T005-T008) and UI skeleton (T012) can proceed concurrently once models (T003) are defined.
