#!/usr/bin/env python3
"""
Baseline 3: Clustering + Granger Causality Root Cause Identification

This is a STRONG baseline that students should aim to beat.
It uses:
1. Signal clustering to group similar behaviors
2. Granger causality tests to determine causal relationships
3. Net causality scoring to rank root causes

Expected Performance: ~70-80% accuracy on root cause identification
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def extract_signal_features(signal: np.ndarray) -> np.ndarray:
    """
    Extract statistical features from a signal for clustering.
    
    Returns array of features:
    - mean, std, min, max, range
    - skewness, kurtosis
    - trend (slope of linear fit)
    - autocorrelation at lag 1
    - number of zero crossings
    """
    features = []
    
    # Basic statistics
    features.append(np.mean(signal))
    features.append(np.std(signal))
    features.append(np.min(signal))
    features.append(np.max(signal))
    features.append(np.ptp(signal))  # range
    
    # Higher moments
    features.append(stats.skew(signal))
    features.append(stats.kurtosis(signal))
    
    # Trend
    x = np.arange(len(signal))
    slope, _ = np.polyfit(x, signal, 1)
    features.append(slope)
    
    # Autocorrelation at lag 1
    if len(signal) > 1:
        autocorr = np.corrcoef(signal[:-1], signal[1:])[0, 1]
        features.append(autocorr if not np.isnan(autocorr) else 0)
    else:
        features.append(0)
    
    # Zero crossings (relative to mean)
    mean_centered = signal - np.mean(signal)
    zero_crossings = np.sum(np.diff(np.sign(mean_centered)) != 0)
    features.append(zero_crossings)
    
    return np.array(features)


def cluster_signals(df: pd.DataFrame, n_clusters: int = 5) -> Dict[str, int]:
    """
    Cluster signals based on their statistical features.
    Uses simple k-means clustering.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # Get numeric columns
    numeric_cols = [col for col in df.columns if col != 'timestamp' 
                    and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]]
    
    # Extract features for each signal
    feature_matrix = []
    for col in numeric_cols:
        features = extract_signal_features(df[col].values)
        feature_matrix.append(features)
    
    feature_matrix = np.array(feature_matrix)
    
    # Handle NaN values
    feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(feature_matrix)
    
    # Cluster
    n_clusters = min(n_clusters, len(numeric_cols))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(features_scaled)
    
    return {col: int(label) for col, label in zip(numeric_cols, cluster_labels)}


def simple_granger_test(x: np.ndarray, y: np.ndarray, max_lag: int = 10) -> float:
    """
    Simplified Granger causality test.
    Returns a causality score (lower p-value = stronger causality).
    
    Tests if x Granger-causes y.
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    
    # Ensure sufficient data
    if len(x) < max_lag + 10 or len(y) < max_lag + 10:
        return 1.0  # No evidence of causality
    
    # Prepare lagged data
    n = len(y) - max_lag
    
    # Model 1: y predicted by its own lags only
    y_lags = np.column_stack([y[max_lag-i-1:n+max_lag-i-1] for i in range(max_lag)])
    y_target = y[max_lag:]
    
    model1 = LinearRegression()
    model1.fit(y_lags, y_target)
    mse1 = mean_squared_error(y_target, model1.predict(y_lags))
    
    # Model 2: y predicted by its own lags AND x lags
    x_lags = np.column_stack([x[max_lag-i-1:n+max_lag-i-1] for i in range(max_lag)])
    combined_lags = np.column_stack([y_lags, x_lags])
    
    model2 = LinearRegression()
    model2.fit(combined_lags, y_target)
    mse2 = mean_squared_error(y_target, model2.predict(combined_lags))
    
    # F-test approximation
    if mse2 >= mse1 or mse2 == 0:
        return 1.0  # x doesn't help predict y
    
    # Simplified: return ratio of improvement
    improvement = (mse1 - mse2) / mse1
    
    # Convert to pseudo p-value (lower = stronger causality)
    p_value = 1.0 - improvement
    
    return max(0.0, min(1.0, p_value))


def compute_granger_matrix(df: pd.DataFrame, 
                           signals: List[str],
                           max_lag: int = 10) -> np.ndarray:
    """
    Compute pairwise Granger causality matrix.
    
    Returns matrix where M[i,j] is the p-value for "signal i causes signal j"
    """
    n_signals = len(signals)
    granger_matrix = np.ones((n_signals, n_signals))
    
    for i, sig_i in enumerate(signals):
        for j, sig_j in enumerate(signals):
            if i != j:
                p_value = simple_granger_test(
                    df[sig_i].values,
                    df[sig_j].values,
                    max_lag=max_lag
                )
                granger_matrix[i, j] = p_value
    
    return granger_matrix


def compute_net_causality(granger_matrix: np.ndarray, 
                          signals: List[str],
                          p_threshold: float = 0.1) -> List[Tuple[str, float]]:
    """
    Compute net causality score for each signal.
    
    Net causality = (signals it causes) - (signals that cause it)
    Weighted by strength of evidence (1 - p_value).
    """
    n_signals = len(signals)
    scores = []
    
    for i, sig in enumerate(signals):
        # Signals this one causes (row i)
        causes_others = np.sum([1 - granger_matrix[i, j] 
                                for j in range(n_signals) 
                                if j != i and granger_matrix[i, j] < p_threshold])
        
        # Signals that cause this one (column i)
        caused_by_others = np.sum([1 - granger_matrix[j, i] 
                                   for j in range(n_signals) 
                                   if j != i and granger_matrix[j, i] < p_threshold])
        
        net_score = causes_others - caused_by_others
        scores.append((sig, net_score))
    
    # Sort by net causality (highest first = most likely root cause)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores


def build_causal_graph(granger_matrix: np.ndarray,
                       signals: List[str],
                       p_threshold: float = 0.1) -> Dict:
    """
    Build causal graph from Granger matrix.
    """
    edges = []
    
    for i, sig_i in enumerate(signals):
        for j, sig_j in enumerate(signals):
            if i != j and granger_matrix[i, j] < p_threshold:
                edges.append({
                    'source': sig_i,
                    'target': sig_j,
                    'weight': float(1 - granger_matrix[i, j])
                })
    
    return {
        'nodes': signals,
        'edges': edges
    }


def identify_root_cause(df: pd.DataFrame,
                        max_lag: int = 10,
                        p_threshold: float = 0.1,
                        top_k: int = 5) -> dict:
    """
    Main function to identify root causes using clustering + Granger causality.
    
    Args:
        df: DataFrame with telemetry data
        max_lag: Maximum lag for Granger test
        p_threshold: P-value threshold for significant causality
        top_k: Number of top candidates to return
    
    Returns:
        Dictionary with root cause analysis results
    """
    # Get numeric columns
    numeric_cols = [col for col in df.columns if col != 'timestamp' 
                    and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]]
    
    # Filter to signals that show some variation
    active_signals = [col for col in numeric_cols if df[col].std() > 0]
    
    # Limit to top signals by variance for computational efficiency
    variances = [(col, df[col].var()) for col in active_signals]
    variances.sort(key=lambda x: x[1], reverse=True)
    selected_signals = [col for col, _ in variances[:20]]  # Max 20 signals
    
    if len(selected_signals) < 2:
        return {
            'method': 'clustering_granger',
            'root_cause': selected_signals[0] if selected_signals else None,
            'confidence': 0.5,
            'ranked_candidates': [],
            'causal_graph': {'nodes': [], 'edges': []}
        }
    
    # Cluster signals
    cluster_assignments = cluster_signals(df[['timestamp'] + selected_signals].copy())
    
    # Compute Granger causality matrix
    granger_matrix = compute_granger_matrix(df, selected_signals, max_lag=max_lag)
    
    # Compute net causality scores
    net_causality = compute_net_causality(granger_matrix, selected_signals, p_threshold)
    
    # Build causal graph
    causal_graph = build_causal_graph(granger_matrix, selected_signals, p_threshold)
    
    # Root cause is signal with highest net causality
    root_cause_signal = net_causality[0][0] if net_causality else None
    root_cause_score = net_causality[0][1] if net_causality else 0.0
    
    # Confidence based on:
    # 1. How much higher the top signal scores vs. second
    # 2. Absolute magnitude of the score
    if len(net_causality) > 1:
        gap = net_causality[0][1] - net_causality[1][1]
        confidence = min(0.95, 0.5 + gap * 0.1 + abs(root_cause_score) * 0.05)
    else:
        confidence = 0.6
    
    results = {
        'method': 'clustering_granger',
        'root_cause': root_cause_signal,
        'confidence': confidence,
        'ranked_candidates': [
            {
                'signal': sig,
                'net_causality_score': float(score),
                'cluster': cluster_assignments.get(sig, -1)
            }
            for sig, score in net_causality[:top_k]
        ],
        'cluster_assignments': cluster_assignments,
        'causal_graph': causal_graph
    }
    
    return results


def main():
    """Example usage of the clustering + Granger baseline."""
    import json
    import os
    
    # Example: run on scenario 01
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenario_01_easy')
    
    if os.path.exists(data_path):
        # Load data
        df = pd.read_csv(os.path.join(data_path, 'telemetry.csv'))
        
        print("Running Clustering + Granger Baseline...")
        print("(This may take a moment...)")
        
        # Run RCA
        results = identify_root_cause(df)
        
        print("\nClustering + Granger Baseline Results")
        print("=" * 50)
        print(f"Identified Root Cause: {results['root_cause']}")
        print(f"Confidence: {results['confidence']:.3f}")
        print("\nTop 5 Candidates (by net causality):")
        for i, candidate in enumerate(results['ranked_candidates'], 1):
            print(f"  {i}. {candidate['signal']}")
            print(f"     Net causality: {candidate['net_causality_score']:.3f}")
            print(f"     Cluster: {candidate['cluster']}")
        
        print(f"\nCausal Graph: {len(results['causal_graph']['edges'])} edges identified")
        
        # Load ground truth for comparison
        with open(os.path.join(data_path, 'ground_truth.json')) as f:
            ground_truth = json.load(f)
        
        print(f"\nActual Root Cause: {ground_truth['root_cause']}")
        print(f"Match: {results['root_cause'] == ground_truth['root_cause']}")
    else:
        print(f"Data path not found: {data_path}")
        print("Please run from the project directory or generate data first.")


if __name__ == "__main__":
    main()
