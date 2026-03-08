import streamlit as st
import pandas as pd
from ui.services.api_client import APIClient


def file_uploader_component():
    """Handles CSV/Excel file uploads."""
    uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
            else:
                df = pd.read_excel(uploaded_file, index_col=0, parse_dates=True)
            return df
        except Exception as e:
            st.error(f"Error reading file: {e}")
    return None


def ticker_input_component():
    """Handles manual ticker input with suffix defaulting."""
    tickers_input = st.text_input(
        "Enter Tickers (comma separated)", "BBCA, TLKM, ASII, BBRI"
    )
    lookback = st.selectbox(
        "Lookback Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3
    )

    if st.button("Fetch Data"):
        with st.spinner("Fetching data from Yahoo Finance..."):
            try:
                tickers = [t.strip() for t in tickers_input.split(",")]
                returns_data = APIClient.fetch_market_data(tickers, period=lookback)
                return pd.DataFrame(returns_data)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
    return None
