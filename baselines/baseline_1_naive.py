#!/usr/bin/env python3
"""
Baseline 1: Naive Correlation-Based Root Cause Identification

This is a WEAK baseline that students should easily beat.
It does NOT consider temporal order - just finds the signal most correlated 
with anomalous behavior.

Expected Performance: ~30-40% accuracy on root cause identification
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def detect_anomaly_window(df: pd.DataFrame, threshold_std: float = 3.0) -> Tuple[int, int]:
    """
    Simple anomaly window detection using z-score threshold.
    Returns start and end indices of the anomalous period.
    """
    # Calculate z-scores for all numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    z_scores = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
    
    # Find any point where any signal exceeds threshold
    anomaly_mask = (np.abs(z_scores) > threshold_std).any(axis=1)
    
    if not anomaly_mask.any():
        return 0, len(df) - 1
    
    # Find first and last anomaly indices
    anomaly_indices = np.where(anomaly_mask)[0]
    start_idx = max(0, anomaly_indices[0] - 100)  # Include some context
    end_idx = min(len(df) - 1, anomaly_indices[-1] + 100)
    
    return start_idx, end_idx


def compute_signal_deviation(signal: pd.Series) -> float:
    """
    Compute how much a signal deviates from its normal behavior.
    Uses the max absolute z-score as the deviation metric.
    """
    if signal.std() == 0:
        return 0.0
    z_scores = (signal - signal.mean()) / signal.std()
    return np.max(np.abs(z_scores))


def naive_correlation_rca(df: pd.DataFrame, 
                          alert_signal: Optional[str] = None) -> List[Tuple[str, float]]:
    """
    Naive correlation-based root cause analysis.
    
    If alert_signal is provided, ranks signals by correlation with it.
    Otherwise, ranks signals by their deviation from normal.
    
    Args:
        df: DataFrame with telemetry data (timestamp column + signal columns)
        alert_signal: Optional signal that triggered the alert
    
    Returns:
        List of (signal_name, score) tuples, sorted by score descending
    """
    # Get numeric columns only (exclude timestamp)
    numeric_cols = [col for col in df.columns if col != 'timestamp' 
                    and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]]
    
    if alert_signal and alert_signal in numeric_cols:
        # Method 1: Correlation with alert signal
        scores = {}
        alert_data = df[alert_signal]
        
        for col in numeric_cols:
            if col != alert_signal:
                corr = np.abs(df[col].corr(alert_data))
                scores[col] = corr if not np.isnan(corr) else 0.0
    else:
        # Method 2: Rank by deviation from normal
        scores = {}
        for col in numeric_cols:
            scores[col] = compute_signal_deviation(df[col])
    
    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return ranked


def identify_root_cause(df: pd.DataFrame, 
                        alert_signal: Optional[str] = None,
                        top_k: int = 5) -> dict:
    """
    Main function to identify root causes using naive correlation.
    
    Args:
        df: DataFrame with telemetry data
        alert_signal: Optional signal that triggered the alert
        top_k: Number of top candidates to return
    
    Returns:
        Dictionary with root cause analysis results
    """
    # Detect anomaly window
    start_idx, end_idx = detect_anomaly_window(df)
    window_df = df.iloc[start_idx:end_idx]
    
    # Run naive RCA
    ranked_signals = naive_correlation_rca(window_df, alert_signal)
    
    # Prepare results
    results = {
        'method': 'naive_correlation',
        'window': {
            'start_idx': start_idx,
            'end_idx': end_idx
        },
        'root_cause': ranked_signals[0][0] if ranked_signals else None,
        'confidence': ranked_signals[0][1] if ranked_signals else 0.0,
        'ranked_candidates': [
            {'signal': sig, 'score': float(score)} 
            for sig, score in ranked_signals[:top_k]
        ],
        'causal_graph': {
            'nodes': [sig for sig, _ in ranked_signals[:top_k]],
            'edges': []  # Naive method doesn't build causal graph
        }
    }
    
    return results


def main():
    """Example usage of the naive baseline."""
    import json
    import os
    
    # Example: run on scenario 01
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenario_01_easy')
    
    if os.path.exists(data_path):
        # Load data
        df = pd.read_csv(os.path.join(data_path, 'telemetry.csv'))
        
        # Run RCA
        results = identify_root_cause(df)
        
        print("Naive Correlation Baseline Results")
        print("=" * 50)
        print(f"Identified Root Cause: {results['root_cause']}")
        print(f"Confidence: {results['confidence']:.3f}")
        print("\nTop 5 Candidates:")
        for i, candidate in enumerate(results['ranked_candidates'], 1):
            print(f"  {i}. {candidate['signal']}: {candidate['score']:.3f}")
        
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
