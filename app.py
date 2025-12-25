
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
import statsmodels.api as sm

# Import from src
from src.features.feature_extract import log_rate
# Import configuration
from config import KOMPAS100_TICKERS

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
tickers_input = st.sidebar.text_area("Enter Stock Tickers (comma separated)",
                                     ", ".join(KOMPAS100_TICKERS))

# Helper function to load data
@st.cache_data
def load_data(tickers, start, end):
    tickers_list = [t.strip() for t in tickers.split(',')]
    if not tickers_list:
        return None
    try:
        data = yf.download(tickers_list, start=start, end=end)['Adj Close']
        return data
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        return None

# Load data
if st.sidebar.button("Load Data"):
    with st.spinner("Downloading stock data..."):
        data = load_data(tickers_input, start_date, end_date)
        if data is not None:
            st.session_state['data'] = data
            st.success("Data loaded successfully!")

if 'data' in st.session_state:
    df = st.session_state['data']

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
    returns_df['Returns'] = returns_mean
    returns_df['Volatility'] = returns_volatility


    # Calculate Correlation
    st.header("Clustering Analysis")

    # Format the data as a numpy array to feed into the K-Means algorithm
    X = np.asarray([np.asarray(returns_df['Returns']),np.asarray(returns_df['Volatility'])]).T

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
    ax_elbow.set_title('Elbow Curve')
    st.pyplot(fig_elbow)

    # K-Means Clustering
    k_clusters = st.sidebar.slider("Number of Clusters (K-Means)", 2, 10, 5)

    # Using sklearn for KMeans as scipy vq is not imported and slightly different API
    kmeans = KMeans(n_clusters=k_clusters)
    kmeans.fit(X)
    labels = kmeans.predict(X)
    centroids = kmeans.cluster_centers_

    details = [(name,cluster) for name, cluster in zip(returns_df.index, labels)]

    fig_cluster, ax_cluster = plt.subplots(figsize=(10, 8))
    ax_cluster.scatter(X[:,0],X[:,1], c=labels, cmap='rainbow', alpha=0.7, s=100)
    ax_cluster.scatter(centroids[:,0],centroids[:,1], marker='x', s=100, c='black')
    ax_cluster.set_xlabel('Annualized Returns')
    ax_cluster.set_ylabel('Annualized Volatility')
    ax_cluster.set_title('K-Means Clustering')

    for i, txt in enumerate(returns_df.index):
        ax_cluster.annotate(txt, (X[i,0], X[i,1]))

    st.pyplot(fig_cluster)

    st.write("Cluster Details:")
    cluster_df = pd.DataFrame(details, columns=['Ticker', 'Cluster'])
    st.dataframe(cluster_df.sort_values(by='Cluster'))

    # Hierarchical Clustering
    st.subheader("Hierarchical Clustering")

    fig_dendro, ax_dendro = plt.subplots(figsize=(12, 6))
    linked = linkage(X, 'ward')
    dendrogram(linked, labels=returns_df.index, ax=ax_dendro, leaf_rotation=90)
    st.pyplot(fig_dendro)

    # Optimization (Simple Mean-Variance for selected cluster)
    st.header("Portfolio Optimization")
    selected_cluster = st.selectbox("Select Cluster to Optimize", sorted(cluster_df['Cluster'].unique()))

    cluster_tickers = cluster_df[cluster_df['Cluster'] == selected_cluster]['Ticker'].tolist()

    if cluster_tickers:
        st.write(f"Optimizing portfolio for cluster {selected_cluster} with tickers: {', '.join(cluster_tickers)}")

        cluster_data = df[cluster_tickers]

        # Calculate expected returns and sample covariance
        # Using simple returns for optimization logic as it's standard for MPT simulation code below
        # (Portfolio return = sum(w * r))
        mu = cluster_data.pct_change().mean() * 252
        S = cluster_data.pct_change().cov() * 252

        # Efficient Frontier Simulation
        st.subheader("Efficient Frontier Simulation")

        num_portfolios = 5000
        results = np.zeros((3, num_portfolios))

        for i in range(num_portfolios):
            weights = np.random.random(len(cluster_tickers))
            weights /= np.sum(weights)

            portfolio_return = np.sum(weights * mu)
            portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(S, weights)))

            results[0,i] = portfolio_return
            results[1,i] = portfolio_std_dev
            results[2,i] = results[0,i] / results[1,i] # Sharpe Ratio

        fig_ef, ax_ef = plt.subplots(figsize=(10, 6))
        sc = ax_ef.scatter(results[1,:], results[0,:], c=results[2,:], cmap='YlGnBu', marker='o')
        ax_ef.set_xlabel('Volatility')
        ax_ef.set_ylabel('Returns')
        plt.colorbar(sc, label='Sharpe Ratio')
        st.pyplot(fig_ef)

        # Max Sharpe Ratio Portfolio
        max_sharpe_idx = np.argmax(results[2])
        st.write("Maximum Sharpe Ratio Portfolio:")
        st.write(f"Return: {results[0,max_sharpe_idx]:.2f}")
        st.write(f"Volatility: {results[1,max_sharpe_idx]:.2f}")
        st.write(f"Sharpe Ratio: {results[2,max_sharpe_idx]:.2f}")
