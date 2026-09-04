# Hierarchical Risk Parity (HRP) Optimizer
"""
This module implements the Hierarchical Risk Parity optimization algorithm.
"""


import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.optimize import minimize
from scipy.spatial.distance import squareform

from .base import BaseOptimizer, OptimizationResult


class HierarchicalRiskParityOptimizer(BaseOptimizer):
    """
    Implementation of the Hierarchical Risk Parity (HRP) optimization algorithm.

    HRP is a risk-based portfolio optimization method that constructs portfolios
    by recursively allocating risk across a hierarchical clustering of assets.
    """

    def __init__(self, returns: pd.DataFrame, covariance_matrix: pd.DataFrame):
        """
        Initialize the HRP optimizer.

        Args:
            returns: Historical returns for assets (n_assets × n_periods)
            covariance_matrix: Asset covariance matrix (n_assets × n_assets)
        """
        super().__init__(returns, covariance_matrix)
        self.linkage_matrix = None
        self.cluster_assignments = None

    def optimize(self, n_clusters: int | None = None,
                linkage_method: str = 'average', **kwargs) -> OptimizationResult:
        """
        Run HRP optimization.

        Args:
            n_clusters: Number of clusters for hierarchical clustering
            linkage_method: Linkage method for hierarchical clustering

        Returns:
            OptimizationResult: Results of the portfolio optimization
        """
        try:
            # Calculate hierarchical clustering
            self.linkage_matrix = self._calculate_linkage(linkage_method)

            # Determine number of clusters if not specified
            if n_clusters is None:
                n_clusters = self._determine_optimal_clusters()

            # Assign assets to clusters
            self.cluster_assignments = self._assign_to_clusters(n_clusters)

            # Cross-cluster weights: inverse-risk across top-level clusters
            cluster_weights = self._calculate_cluster_weights()

            # Intra-cluster weights: equal risk contribution within each cluster
            intra_cluster_weights = self._calculate_intra_cluster_weights()

            # Combine weights to get final portfolio weights
            final_weights = self._combine_weights(cluster_weights, intra_cluster_weights)

            if not self._validate_weights(final_weights):
                raise ValueError("Computed weights violate the sum-to-one / long-only constraints")

            # Calculate performance metrics
            performance = self._calculate_performance_metrics(final_weights)

            # Create method-specific output
            method_specific = {
                'linkage_matrix': self.linkage_matrix.tolist(),
                'cluster_assignments': self.cluster_assignments.tolist(),
                'n_clusters': n_clusters,
                'linkage_method': linkage_method
            }

            return OptimizationResult(
                weights=dict(zip(self.returns.columns, final_weights, strict=True)),
                performance=performance,
                method_specific=method_specific,
                success=True
            )

        except Exception as e:
            return OptimizationResult(
                weights=dict.fromkeys(self.returns.columns, 0.0),
                performance={},
                method_specific={'error': str(e)},
                success=False,
                message=f"Optimization failed: {e!s}"
            )

    def _calculate_linkage(self, method: str) -> np.ndarray:
        """Calculate hierarchical clustering linkage matrix."""
        # Convert covariance matrix to correlation matrix
        correlation_matrix = self._cov_to_corr(self.covariance_matrix)

        # Calculate distance matrix
        distance_matrix = np.sqrt(0.5 * (1 - correlation_matrix))

        # linkage() needs a condensed distance matrix — a square matrix is
        # interpreted as an observation matrix, which silently clusters garbage.
        # Note: 'ward' is only valid on Euclidean observations, so the default
        # method for precomputed distances is 'average'.
        condensed = squareform(distance_matrix, checks=False)
        return linkage(condensed, method=method)

    def _cov_to_corr(self, covariance: pd.DataFrame) -> pd.DataFrame:
        """Convert covariance matrix to correlation matrix."""
        std_devs = np.sqrt(np.diag(covariance))
        # Guard against zero-variance assets (division by zero -> NaN correlations)
        std_devs = np.where(std_devs > 0, std_devs, 1.0)
        correlation = covariance / np.outer(std_devs, std_devs)
        np.fill_diagonal(correlation.values, 1.0)  # Ensure diagonal is exactly 1
        return correlation

    def _determine_optimal_clusters(self) -> int:
        """Determine optimal number of clusters using elbow method."""
        # Simple heuristic: sqrt(n_assets)
        return max(2, int(np.sqrt(self.n_assets)))

    def _assign_to_clusters(self, n_clusters: int) -> np.ndarray:
        """Assign assets to clusters based on linkage matrix."""
        return fcluster(self.linkage_matrix, n_clusters, criterion='maxclust')

    def _calculate_cluster_weights(self) -> dict[int, float]:
        """Calculate cross-cluster weights via inverse-risk allocation.

        Each cluster gets weight proportional to 1/risk (risk = volatility of
        the equal-weighted portfolio inside the cluster), normalized to sum to 1.
        """
        if self.cluster_assignments is None:
            raise RuntimeError("cluster_assignments not computed — call optimize() first")

        # Get indices for each cluster
        cluster_indices: dict[int, list[int]] = {}
        for i, cluster_id in enumerate(self.cluster_assignments):
            cluster_indices.setdefault(cluster_id, []).append(i)

        # Inverse-risk weights across clusters
        inv_risk = {}
        for cluster_id, indices in cluster_indices.items():
            risk = self._calculate_cluster_risk(indices)
            inv_risk[cluster_id] = 1.0 / risk if risk > 0 else 0.0

        total = sum(inv_risk.values())
        if total == 0:
            # Degenerate: all clusters have zero risk — fall back to equal weights
            n = len(inv_risk)
            return dict.fromkeys(inv_risk, 1.0 / n)

        return {cid: w / total for cid, w in inv_risk.items()}

    def _calculate_cluster_risk(self, indices: list[int]) -> float:
        """Calculate risk contribution of a cluster."""
        # Get sub-covariance matrix
        sub_cov = self.covariance_matrix.iloc[indices, indices].values

        # Calculate equal-weighted portfolio for the cluster
        n_assets = len(indices)
        weights = np.ones(n_assets) / n_assets

        # Calculate portfolio variance
        return np.sqrt(weights.T @ sub_cov @ weights)

    def _calculate_intra_cluster_weights(self) -> dict[int, dict[int, float]]:
        """Calculate weights within each cluster."""
        intra_weights = {}

        if self.cluster_assignments is None:
            raise RuntimeError("cluster_assignments not computed — call optimize() first")

        # Get indices for each cluster
        cluster_indices = {}
        for i, cluster_id in enumerate(self.cluster_assignments):
            if cluster_id not in cluster_indices:
                cluster_indices[cluster_id] = []
            cluster_indices[cluster_id].append(i)

        # Calculate equal risk contribution weights within each cluster
        for cluster_id, indices in cluster_indices.items():
            if len(indices) == 1:
                intra_weights[cluster_id] = {indices[0]: 1.0}
            else:
                intra_weights[cluster_id] = self._calculate_erc_weights(indices)

        return intra_weights

    def _calculate_erc_weights(self, indices: list[int]) -> dict[int, float]:
        """Calculate equal risk contribution (ERC) weights within a cluster."""
        # Get sub-covariance matrix
        sub_cov = self.covariance_matrix.iloc[indices, indices].values
        n_assets = len(indices)

        # Objective function for ERC optimization
        def objective(weights):
            # Calculate portfolio variance
            port_var = weights.T @ sub_cov @ weights

            # Calculate marginal contributions to risk
            mctr = (sub_cov @ weights) / np.sqrt(port_var)

            # Calculate risk contributions
            rc = weights * mctr

            # Calculate diversification ratio
            return np.sum((rc - rc.mean())**2)

        # Constraints: fully invested portfolio
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        # Bounds: weights between 0 and 1
        bounds = [(0, 1) for _ in range(n_assets)]

        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets

        # Optimize
        result = minimize(objective, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        if not result.success:
            raise RuntimeError(f"ERC optimization failed: {result.message}")

        return dict(zip(indices, result.x, strict=True))

    def _combine_weights(self, cluster_weights: dict[int, float],
                        intra_cluster_weights: dict[int, dict[int, float]]) -> np.ndarray:
        """Combine cluster and intra-cluster weights to get final portfolio weights.

        final_weight[asset] = cross-cluster weight x intra-cluster (ERC) weight.
        Both factors sum to 1, so the result sums to 1.
        """
        final_weights = np.zeros(self.n_assets)

        for cluster_id, cluster_weight in cluster_weights.items():
            for asset_idx, weight in intra_cluster_weights[cluster_id].items():
                final_weights[asset_idx] = cluster_weight * weight

        return final_weights
