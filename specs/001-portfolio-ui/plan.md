# Implementation Plan: Portfolio Optimization UI

**Branch**: `001-portfolio-ui` | **Date**: 2026-03-07 | **Spec**: [/specs/001-portfolio-ui/spec.md](/specs/001-portfolio-ui/spec.md)
**Input**: Feature specification from `/specs/001-portfolio-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary
Implement a modern web-based utility for portfolio optimization. This involves refactoring existing research code in `src/` into a modular `PortfolioService` and `DataService`, exposing them via a FastAPI backend, and creating an interactive Streamlit frontend that supports CSV uploads and real-time market data fetching from Yahoo Finance (yfinance).

## Technical Context
**Language/Version**: Python 3.13+
**Primary Dependencies**: Streamlit, FastAPI, yfinance, pandas, numpy, scipy, plotly
**Storage**: N/A (In-memory session state; temporary local file storage if needed for uploads)
**Testing**: pytest (Unit and Integration)
**Target Platform**: Containerized Web Application (Docker)
**Project Type**: web-application
**Performance Goals**:
- Data Load (yfinance): < 10s for 20 tickers.
- Optimization calculation: < 1s for 50 assets.
- UI responsiveness: < 500ms for parameter updates.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Principle 1 (Library-First): Refactoring `src/` into importable services in `portfolio_optimizer.services`.
- [x] Principle 2 (CLI Interface): The core logic is library-based; FastAPI exposes the interface.
- [x] Principle 3 (Test-First): Test suite planned for both API and business logic.

## Project Structure

### Documentation (this feature)
```text
specs/001-portfolio-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)
```text
portfolio_optimizer/     # Main package
└── services/            # Refactored logic from /src (Shared Logic)
    ├── data_service.py
    └── portfolio_service.py

api/                     # Backend Process
├── main.py
└── v1/
    ├── endpoints.py
    └── models.py

ui/                      # Frontend Process
└── app.py

docker/                  # Infrastructure
├── api.Dockerfile
├── ui.Dockerfile
└── docker-compose.yml
```

**Structure Decision**: Option 2: Web application (FastAPI + Streamlit). This architecture ensures that the "Heavy Lifting" (Backend) is decoupled from the "Presentation" (Frontend), making the system more robust and easier to extend with new optimization methods or data sources.

## Complexity Tracking
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two-process architecture | Future-proofing for non-Python clients and better separation of concerns. | Mono-Streamlit apps tend to become unmaintainable as logic grows. |
