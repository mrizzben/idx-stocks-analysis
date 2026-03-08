# Feature Specification: Portfolio Optimization UI

**Feature Branch**: `001-portfolio-ui`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "the current repo is an implementation of hierarchical risk parity portfolio, it has the code but lacks the ui for a user friendly utility"

## Clarifications

### Session 2026-03-07
- Q: Should the UI focus exclusively on Indonesian stocks (IDX) or support global markets? → A: Global support with IDX defaults.
- Q: How should existing code in /src be utilized for the UI utility? → A: Full integration: Refactor /src into modules used by the UI.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Portfolio Weight Generation (Priority: P1)

A quantitative analyst wants to quickly generate an optimized portfolio using the Hierarchical Risk Parity (HRP) algorithm without writing code. They have a CSV file containing historical stock returns and want to see the resulting asset weights immediately.

**Why this priority**: This is the core value proposition of the utility—making the existing optimization logic accessible to non-technical users or for rapid prototyping.

**Independent Test**: Can be fully tested by uploading a valid returns CSV and verifying that a table or chart of weights is displayed.

**Acceptance Scenarios**:

1. **Given** a valid CSV file of historical returns, **When** the user uploads it and clicks "Optimize", **Then** the system displays a breakdown of asset weights totaling 100%.
2. **Given** an invalid file format (e.g., PDF), **When** the user attempts to upload it, **Then** the system displays a clear error message and prevents optimization.

---

### User Story 2 - Risk Metric Visualization (Priority: P2)

An investor wants to understand the risk profile of the optimized portfolio. They need to see key metrics like the Sharpe Ratio and Volatility alongside the weights to decide if the portfolio fits their risk tolerance.

**Why this priority**: Weights alone are not enough for financial decision-making; risk metrics provide the necessary context.

**Independent Test**: Can be tested by running an optimization and verifying that Sharpe Ratio and Volatility are calculated and displayed correctly based on the provided data.

**Acceptance Scenarios**:

1. **Given** an optimized portfolio, **When** the results are displayed, **Then** the system also shows the annualized volatility and Sharpe ratio.
2. **Given** a risk-free rate input field, **When** the user changes the value, **Then** the Sharpe ratio is automatically recalculated in the display.

---

### User Story 3 - Optimization Method Comparison (Priority: P3)

A portfolio manager wants to compare the HRP results with a standard Equal Weight benchmark to see the "alpha" or risk reduction provided by the clustering-based approach.

**Why this priority**: Comparative analysis helps validate the choice of HRP over simpler strategies.

**Independent Test**: Can be tested by toggling between "HRP" and "Equal Weight" and verifying that the displayed weights and metrics update accordingly.

**Acceptance Scenarios**:

1. **Given** an uploaded dataset, **When** the user selects "Equal Weight" instead of "HRP", **Then** the system displays weights distributed evenly across all assets in the dataset.

---

### Edge Cases

- **What happens when the uploaded CSV has missing data?**: The system should either drop rows with missing values or provide a warning/imputation strategy rather than crashing.
- **How does system handle a single-asset dataset?**: The UI should inform the user that optimization requires at least two assets to calculate correlations/risk parity.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web-based user interface (e.g., Streamlit) for interacting with the portfolio optimizer.
- **FR-002**: System MUST allow users to upload market data in CSV or Excel format containing historical returns or prices.
- **FR-003**: System MUST provide a hybrid data ingestion model supporting both local file uploads (CSV/Excel) and direct market data fetching via ticker symbol using an API (e.g., Yahoo Finance). The system SHOULD default to the Indonesia Stock Exchange (IDX) for ticker searches if no suffix is provided.
- **FR-004**: System MUST display optimization results using both a tabular format (for precise weights) and a visual format (e.g., Pie or Bar chart).
- **FR-005**: System MUST allow configuration of optimization parameters: strategy (HRP/Equal Weight), lookback window, and risk-free rate.
- **FR-006**: System MUST persist the current session state so that changing a visualization setting does not trigger a full recalculation of the optimization.
- **FR-007**: System MUST refactor existing scripts in `/src` into modular, testable services (e.g., data collection in `/src/data`, feature extraction in `/src/features`) that are directly imported and used by the UI utility.

### Key Entities *(include if feature involves data)*

- **Portfolio**: Represents the collection of assets, their historical data, and the resulting optimized weights.
- **Optimization Strategy**: Defines the algorithm (HRP, Markowitz, etc.) and its specific parameters.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the journey from data upload to weight visualization in under 30 seconds for a 50-asset dataset.
- **SC-002**: 100% of successful optimizations must result in a total portfolio weight of exactly 1.0 (100%).
- **SC-003**: The UI must handle up to 100 stocks in a single optimization without browser lag or interface non-responsiveness.
- **SC-004**: Non-technical users can identify the top-weighted asset without looking at the raw data tables.
- **SC-005**: 100% of data fetching and preprocessing logic in the UI is powered by the refactored modules in `/src`, ensuring parity between research scripts and the user utility.

## Assumptions

- The underlying HRP logic in `portfolio_optimizer/core/hrp.py` is stable and returns correct results.
- The UI will be used locally or in a trusted internal environment, so complex authentication is not required for the initial version.
- Users have basic familiarity with CSV structures required for financial analysis.
