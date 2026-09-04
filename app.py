import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import yaml
import yfinance as yf
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans

# Import from portfolio_optimizer
from portfolio_optimizer.core.financial_metrics import log_rate
from portfolio_optimizer.core.hrp import HierarchicalRiskParityOptimizer
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer

# Load configuration (path resolved relative to this file, not the cwd)
_config_path = Path(__file__).resolve().parent / "config.yaml"
try:
    with open(_config_path) as _f:
        config = yaml.safe_load(_f)
    KOMPAS100_TICKERS = config["tickers"]
except (OSError, KeyError, TypeError):
    st.error(f"Could not load {_config_path}. Check the file is present and valid.")
    st.stop()
    KOMPAS100_TICKERS = []  # unreachable after st.stop(); placates type checker

# Set page config
st.set_page_config(page_title="Portfolio Optimization", layout="wide")

# Title and Introduction
st.title("IDX Stocks Portfolio Optimization using Hierarchical Clustering")
st.markdown("""
This app implements a quantitative study on portfolio optimization using data science techniques.
It focuses on creating optimal portfolios through clustering analysis (k-means and agglomerative hierarchical clustering)
combined with modern portfolio optimization methods (mean-variance and hierarchical risk parity).
""")

# Sidebar controls
st.sidebar.header("Configuration")
start_date = st.sidebar.date_input("Start Date", dt.date(2010, 1, 1))
end_date = st.sidebar.date_input("End Date", dt.date.today())
tickers_input = st.sidebar.text_area(
    "Enter Stock Tickers (comma separated)", ", ".join(KOMPAS100_TICKERS)
)


# Helper function to load data
@st.cache_data
def load_data(tickers, start, end):
    tickers_list = [t.strip() for t in tickers.split(",")]
    if not tickers_list:
        return None
    try:
        data = yf.download(tickers_list, start=start, end=end, auto_adjust=False)["Adj Close"]  # type: ignore[reportOptionalSubscript]
        return data
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        return None


# Load data
if st.sidebar.button("Load Data"):
    with st.spinner("Downloading stock data..."):
        data = load_data(tickers_input, start_date, end_date)
        if data is not None:
            st.session_state["data"] = data
            st.success("Data loaded successfully!")

if "data" in st.session_state:
    df = st.session_state["data"]

    # Data Overview
    st.header("Data Overview")
    st.write("Adjusted Close Prices")
    st.dataframe(df.head())

    st.subheader("Price History")
    # Normalize for better visualization
    df_norm = df / df.iloc[0]
    st.line_chart(df_norm)

    # Returns calculation using log_rate from src
    # Note: original app used pct_change (simple returns).
    # log_rate returns log returns.
    # For mean-variance, usually simple returns are used, but for clustering log returns are fine.
    # To keep consistency with visual output we might want to stick to what works for clustering.
    # We will use log_rate here to show we are using the src function.

    # However, calculating annualized stats from log returns needs care if comparing to simple returns.
    # For approximation, for small returns, log returns ~ simple returns.

    returns_log = log_rate(df)

    returns_mean = returns_log.mean() * 252
    returns_volatility = returns_log.std() * np.sqrt(252)

    returns_df = pd.DataFrame()
    returns_df["Returns"] = returns_mean
    returns_df["Volatility"] = returns_volatility

    # Calculate Correlation
    st.header("Clustering Analysis")

    # Format the data as a numpy array to feed into the K-Means algorithm
    X = np.asarray(
        [np.asarray(returns_df["Returns"]), np.asarray(returns_df["Volatility"])]
    ).T

    # Elbow Method
    st.subheader("Elbow Curve to find optimal K")
    distorsions = []
    for k in range(2, 20):
        k_means = KMeans(n_clusters=k)
        k_means.fit(X)
        distorsions.append(k_means.inertia_)

    fig_elbow, ax_elbow = plt.subplots(figsize=(10, 5))
    ax_elbow.plot(range(2, 20), distorsions)
    ax_elbow.grid(True)
    ax_elbow.set_title("Elbow Curve")
    st.pyplot(fig_elbow)

    # K-Means Clustering
    k_clusters = st.sidebar.slider("Number of Clusters (K-Means)", 2, 10, 5)

    # Using sklearn for KMeans as scipy vq is not imported and slightly different API
    kmeans = KMeans(n_clusters=k_clusters)
    kmeans.fit(X)
    labels = kmeans.predict(X)
    centroids = kmeans.cluster_centers_

    details = [
        (name, cluster) for name, cluster in zip(returns_df.index, labels, strict=True)
    ]

    fig_cluster, ax_cluster = plt.subplots(figsize=(10, 8))
    ax_cluster.scatter(X[:, 0], X[:, 1], c=labels, cmap="rainbow", alpha=0.7, s=100)
    ax_cluster.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=100, c="black")
    ax_cluster.set_xlabel("Annualized Returns")
    ax_cluster.set_ylabel("Annualized Volatility")
    ax_cluster.set_title("K-Means Clustering")

    for i, txt in enumerate(returns_df.index):
        ax_cluster.annotate(txt, (X[i, 0], X[i, 1]))

    st.pyplot(fig_cluster)

    st.write("Cluster Details:")
    cluster_df = pd.DataFrame(details, columns=["Ticker", "Cluster"])  # type: ignore[reportArgumentType]
    st.dataframe(cluster_df.sort_values(by="Cluster"))

    # Hierarchical Clustering
    st.subheader("Hierarchical Clustering")

    fig_dendro, ax_dendro = plt.subplots(figsize=(12, 6))
    linked = linkage(X, "ward")
    dendrogram(linked, labels=returns_df.index, ax=ax_dendro, leaf_rotation=90)
    st.pyplot(fig_dendro)

    # Optimization (Simple Mean-Variance for selected cluster)
    st.header("Portfolio Optimization")
    selected_cluster = st.selectbox(
        "Select Cluster to Optimize", sorted(cluster_df["Cluster"].unique())
    )

    cluster_tickers = cluster_df[cluster_df["Cluster"] == selected_cluster][
        "Ticker"
    ].tolist()

    if cluster_tickers:
        st.write(
            f"Optimizing portfolio for cluster {selected_cluster} with tickers: {', '.join(cluster_tickers)}"
        )

        cluster_data = df[cluster_tickers]

        # Prepare data for optimization
        # Note: portfolio_optimizer modules typically expect simple returns for calculating final stats
        # but check documentation if log returns are preferred. Markowitz usually uses arithmetic mean/cov.
        returns_simple = cluster_data.pct_change().dropna()
        cov_matrix = returns_simple.cov() * 252

        st.subheader("Mean-Variance Optimization")

        # Initialize Optimizer
        optimizer = MarkowitzOptimizer(returns_simple, cov_matrix)

        # Calculate Efficient Frontier
        ef_points = optimizer._calculate_efficient_frontier(n_points=50)

        fig_ef, ax_ef = plt.subplots(figsize=(10, 6))
        ax_ef.plot(
            ef_points["risk"], ef_points["returns"], "b-", label="Efficient Frontier"
        )
        ax_ef.set_xlabel("Volatility")
        ax_ef.set_ylabel("Expected Return")
        ax_ef.set_title("Efficient Frontier")
        ax_ef.legend()
        st.pyplot(fig_ef)

        # Max Sharpe Optimization
        st.write("### Maximum Sharpe Ratio Portfolio")
        result_sharpe = optimizer.optimize(method="max_sharpe")

        if result_sharpe.success:
            st.write(
                f"Expected Return: {result_sharpe.performance['expected_return']:.4f}"
            )
            st.write(f"Volatility: {result_sharpe.performance['volatility']:.4f}")
            st.write(f"Sharpe Ratio: {result_sharpe.performance['sharpe_ratio']:.4f}")

            # Plot Weights
            weights_df = pd.Series(result_sharpe.weights).sort_values(ascending=False)
            fig_weights, ax_weights = plt.subplots(figsize=(10, 6))
            weights_df.plot(kind="bar", ax=ax_weights)
            ax_weights.set_title("Portfolio Weights (Max Sharpe)")
            st.pyplot(fig_weights)
        else:
            st.error(f"Optimization failed: {result_sharpe.message}")

        # Min Variance Optimization
        st.write("### Minimum Variance Portfolio")
        result_min_var = optimizer.optimize(method="min_variance")

        if result_min_var.success:
            st.write(
                f"Expected Return: {result_min_var.performance['expected_return']:.4f}"
            )
            st.write(f"Volatility: {result_min_var.performance['volatility']:.4f}")
            st.write(f"Sharpe Ratio: {result_min_var.performance['sharpe_ratio']:.4f}")

        st.subheader("Hierarchical Risk Parity (HRP) Optimization")

        # Initialize HRP Optimizer
        hrp_optimizer = HierarchicalRiskParityOptimizer(returns_simple, cov_matrix)
        result_hrp = hrp_optimizer.optimize()

        if result_hrp.success:
            st.write(
                f"Expected Return: {result_hrp.performance['expected_return']:.4f}"
            )
            st.write(f"Volatility: {result_hrp.performance['volatility']:.4f}")
            st.write(f"Sharpe Ratio: {result_hrp.performance['sharpe_ratio']:.4f}")

            # Plot Weights
            weights_hrp_df = pd.Series(result_hrp.weights).sort_values(ascending=False)
            fig_weights_hrp, ax_weights_hrp = plt.subplots(figsize=(10, 6))
            weights_hrp_df.plot(kind="bar", ax=ax_weights_hrp)
            ax_weights_hrp.set_title("Portfolio Weights (HRP)")
            st.pyplot(fig_weights_hrp)
