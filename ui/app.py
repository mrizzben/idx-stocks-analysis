import streamlit as st
import pandas as pd
from ui.services.api_client import APIClient
from ui.components.data_ingestion import file_uploader_component, ticker_input_component
from ui.components.visualizations import (
    weights_pie_chart,
    performance_metrics_display,
    weight_breakdown_table,
    weights_comparison_chart,
)

st.set_page_config(page_title="IDX Portfolio Optimizer", layout="wide")

st.title("🇮🇩 Indonesian Stock Market Portfolio Optimizer")
st.markdown(
    "Optimize your portfolio using Hierarchical Risk Parity (HRP) or Equal Weight strategies."
)

# T028: Session state management for persistence
if "returns_df" not in st.session_state:
    st.session_state.returns_df = None
if "optimization_result" not in st.session_state:
    st.session_state.optimization_result = None
if "benchmark_result" not in st.session_state:
    st.session_state.benchmark_result = None

# Sidebar for configuration
st.sidebar.header("Configuration")

# Data Ingestion Method
data_source = st.sidebar.radio(
    "Data Source", ["Fetch from Yahoo Finance", "Upload CSV/Excel"]
)

if data_source == "Fetch from Yahoo Finance":
    df = ticker_input_component()
    if df is not None:
        st.session_state.returns_df = df
        st.success("Data fetched successfully!")
else:
    df = file_uploader_component()
    if df is not None:
        st.session_state.returns_df = df
        st.success("File uploaded successfully!")

# Optimization Parameters
st.sidebar.markdown("---")
strategy = st.sidebar.selectbox(
    "Optimization Strategy", ["HRP", "Equal Weight", "Markowitz", "Monte Carlo"]
)
rf_rate = st.sidebar.slider("Risk-Free Rate (%)", 0.0, 15.0, 6.5) / 100.0

if st.sidebar.button("Optimize Portfolio"):
    if st.session_state.returns_df is not None:
        with st.spinner("Running optimization..."):
            try:
                # Convert DF to dict for API
                returns_dict = st.session_state.returns_df.to_dict(orient="list")
                result = APIClient.optimize(
                    strategy=strategy.lower().replace(" ", "_"),
                    returns_data=returns_dict,
                    risk_free_rate=rf_rate,
                )

                # If HRP, also get Equal Weight for comparison
                if strategy == "HRP":
                    benchmark = APIClient.optimize(
                        strategy="equal_weight",
                        returns_data=returns_dict,
                        risk_free_rate=rf_rate,
                    )
                    st.session_state.benchmark_result = benchmark
                else:
                    st.session_state.benchmark_result = None

                st.session_state.optimization_result = result
                st.success("Optimization complete!")
            except Exception as e:
                st.error(f"Optimization failed: {e}")
    else:
        st.warning("Please fetch or upload data first.")

# Main Panel Display
if st.session_state.optimization_result:
    res = st.session_state.optimization_result
    bench = st.session_state.get("benchmark_result")

    if res.get("status") == "success" and res.get("data", {}).get("success"):
        data = res.get("data", {})
        weights = data.get("weights", {})
        metrics = data.get("performance", {})

        # Display Metrics
        performance_metrics_display(metrics)

        # Display Weights Chart
        st.subheader("Portfolio Allocation")
        if bench and bench.get("status") == "success":
            weights_comparison_chart(weights, bench.get("data", {}).get("weights", {}))
        else:
            weights_pie_chart(weights)

        # Display Weights Table
        st.subheader("Weight Breakdown")
        weight_breakdown_table(weights)
    else:
        error_msg = res.get("message") or res.get("data", {}).get("message")
        st.error(f"Optimization Error: {error_msg}")

elif st.session_state.returns_df is not None:
    st.subheader("Historical Returns (Preview)")
    st.dataframe(st.session_state.returns_df.head())
else:
    st.info("👋 Welcome! Use the sidebar to load data and start optimizing.")
