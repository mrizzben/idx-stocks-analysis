import streamlit as st
import pandas as pd
import plotly.express as px


def weights_pie_chart(weights: dict):
    """Displays a pie chart of portfolio weights."""
    weights_df = pd.DataFrame(list(weights.items()), columns=["Asset", "Weight"])
    fig = px.pie(
        weights_df,
        values="Weight",
        names="Asset",
        hole=0.4,
        title="Portfolio Allocation",
    )
    st.plotly_chart(fig, use_container_width=True)


def performance_metrics_display(metrics: dict):
    """Displays key risk/return metrics."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Return", f"{metrics.get('Expected Return', 0) * 100:.2f}%")
    col2.metric("Volatility", f"{metrics.get('Volatility', 0) * 100:.2f}%")
    col3.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")


def weight_breakdown_table(weights: dict):
    """Displays a sorted table of weights."""
    weights_df = pd.DataFrame(list(weights.items()), columns=["Asset", "Weight"])
    st.table(weights_df.sort_values("Weight", ascending=False))


def weights_comparison_chart(weights_hrp: dict, weights_ew: dict):
    """Displays a bar chart comparing two sets of weights."""
    df_hrp = pd.DataFrame(list(weights_hrp.items()), columns=["Asset", "Weight"])
    df_hrp["Strategy"] = "HRP"

    df_ew = pd.DataFrame(list(weights_ew.items()), columns=["Asset", "Weight"])
    df_ew["Strategy"] = "Equal Weight"

    df = pd.concat([df_hrp, df_ew])
    fig = px.bar(
        df,
        x="Asset",
        y="Weight",
        color="Strategy",
        barmode="group",
        title="HRP vs Equal Weight",
    )
    st.plotly_chart(fig, use_container_width=True)
