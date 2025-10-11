# Hierarchical Risk Parity (HRP) Optimizer
"""
This module implements the Hierarchical Risk Parity optimization algorithm.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.optimize import minimize
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
    
    def optimize(self, n_clusters: Optional[int] = None, 
                linkage_method: str = 'ward') -> OptimizationResult:
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
            
            # Calculate cluster weights using recursive bisection
            cluster_weights = self._calculate_cluster_weights()
            
            # Calculate intra-cluster weights
            intra_cluster_weights = self._calculate_intra_cluster_weights()
            
            # Combine weights to get final portfolio weights
            final_weights = self._combine_weights(cluster_weights, intra_cluster_weights)
            
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
                weights=dict(zip(self.returns.columns, final_weights)),
                performance=performance,
                method_specific=method_specific,
                success=True
            )
            
        except Exception as e:
            return OptimizationResult(
                weights={asset: 0.0 for asset in self.returns.columns},
                performance={},
                method_specific={'error': str(e)},
                success=False,
                message=f"Optimization failed: {str(e)}"
            )
    
    def _calculate_linkage(self, method: str) -> np.ndarray:
        """Calculate hierarchical clustering linkage matrix."""
        # Convert covariance matrix to correlation matrix
        correlation_matrix = self._cov_to_corr(self.covariance_matrix)
        
        # Calculate distance matrix
        distance_matrix = np.sqrt(0.5 * (1 - correlation_matrix))
        
        # Calculate linkage matrix
        return linkage(distance_matrix, method=method)
    
    def _cov_to_corr(self, covariance: pd.DataFrame) -> pd.DataFrame:
        """Convert covariance matrix to correlation matrix."""
        std_devs = np.sqrt(np.diag(covariance))
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
    
    def _calculate_cluster_weights(self) -> Dict[int, float]:
        """Calculate weights for each cluster using recursive bisection."""
        # Get unique clusters
        unique_clusters = np.unique(self.cluster_assignments)
        
        # Initialize cluster weights
        cluster_weights = {}
        
        # Recursive bisection function
        def recursive_bisection(cluster_indices):
            if len(cluster_indices) == 1:
                return {cluster_indices[0]: 1.0}
            
            # Split cluster into two sub-clusters
            mid = len(cluster_indices) // 2
            left_cluster = cluster_indices[:mid]
            right_cluster = cluster_indices[mid:]
            
            # Calculate risk contribution of each sub-cluster
            left_risk = self._calculate_cluster_risk(left_cluster)
            right_risk = self._calculate_cluster_risk(right_cluster)
            
            # Calculate weights based on inverse risk
            total_risk = left_risk + right_risk
            left_weight = right_risk / total_risk
            right_weight = left_weight
            
            # Recursively calculate weights within each sub-cluster
            left_weights = recursive_bisection(left_cluster)
            right_weights = recursive_bisection(right_cluster)
            
            # Combine weights
            combined_weights = {}
            for idx, weight in left_weights.items():
                combined_weights[idx] = weight * left_weight
            for idx, weight in right_weights.items():
                combined_weights[idx] = weight * right_weight
                
            return combined_weights
        
        # Get indices for each cluster
        cluster_indices = {}
        for i, cluster_id in enumerate(self.cluster_assignments):
            if cluster_id not in cluster_indices:
                cluster_indices[cluster_id] = []
            cluster_indices[cluster_id].append(i)
        
        # Calculate weights for each cluster
        for cluster_id, indices in cluster_indices.items():
            cluster_weights[cluster_id] = recursive_bisection(indices)
            
        return cluster_weights
    
    def _calculate_cluster_risk(self, indices: List[int]) -> float:
        """Calculate risk contribution of a cluster."""
        # Get sub-covariance matrix
        sub_cov = self.covariance_matrix.iloc[indices, indices].values
        
        # Calculate equal-weighted portfolio for the cluster
        n_assets = len(indices)
        weights = np.ones(n_assets) / n_assets
        
        # Calculate portfolio variance
        return np.sqrt(weights.T @ sub_cov @ weights)
    
    def _calculate_intra_cluster_weights(self) -> Dict[int, Dict[int, float]]:
        """Calculate weights within each cluster."""
        intra_weights = {}
        
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
    
    def _calculate_erc_weights(self, indices: List[int]) -> Dict[int, float]:
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
            
        return {idx: weight for idx, weight in zip(indices, result.x)}
    
    def _combine_weights(self, cluster_weights: Dict[int, float], 
                        intra_cluster_weights: Dict[int, Dict[int, float]]) -> np.ndarray:
        """Combine cluster and intra-cluster weights to get final portfolio weights."""
        final_weights = np.zeros(self.n_assets)
        
        for cluster_id, cluster_weight in cluster_weights.items():
            if isinstance(cluster_weight, dict):  # If cluster_weight is actually intra-cluster weights
                for asset_idx, weight in cluster_weight.items():
                    final_weights[asset_idx] = weight
            else:
                for asset_idx, weight in intra_cluster_weights[cluster_id].items():
                    final_weights[asset_idx] = weight * cluster_weight
                    
        return final_weights