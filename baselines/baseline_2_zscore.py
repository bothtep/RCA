#!/usr/bin/env python3
"""
Baseline 2: Z-Score + Temporal Order Root Cause Identification

This is a MEDIUM baseline that uses:
1. Z-score anomaly detection to find abnormal signals
2. Temporal ordering to rank by which signal changed first

Expected Performance: ~55-65% accuracy on root cause identification
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from datetime import datetime


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string."""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def compute_rolling_zscore(signal: pd.Series, window: int = 100) -> pd.Series:
    """
    Compute rolling z-score for a signal.
    Uses a rolling window to establish local baseline.
    """
    rolling_mean = signal.rolling(window=window, min_periods=1).mean()
    rolling_std = signal.rolling(window=window, min_periods=1).std()
    
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, np.nan).fillna(signal.std())
    
    z_scores = (signal - rolling_mean) / rolling_std
    return z_scores


def detect_first_anomaly(signal: pd.Series, 
                         threshold: float = 3.0,
                         min_duration: int = 5) -> Optional[int]:
    """
    Detect the first sustained anomaly in a signal.
    
    Args:
        signal: Time series data
        threshold: Z-score threshold for anomaly
        min_duration: Minimum consecutive samples to count as anomaly
    
    Returns:
        Index of first anomaly, or None if no anomaly found
    """
    z_scores = compute_rolling_zscore(signal)
    anomaly_mask = np.abs(z_scores) > threshold
    
    # Find sustained anomalies
    count = 0
    for i, is_anomaly in enumerate(anomaly_mask):
        if is_anomaly:
            count += 1
            if count >= min_duration:
                return i - min_duration + 1
        else:
            count = 0
    
    return None


def compute_signal_severity(signal: pd.Series, 
                            first_anomaly_idx: int) -> float:
    """
    Compute anomaly severity based on max deviation after first anomaly.
    """
    if first_anomaly_idx is None:
        return 0.0
    
    anomaly_segment = signal.iloc[first_anomaly_idx:]
    baseline_segment = signal.iloc[:first_anomaly_idx] if first_anomaly_idx > 0 else signal
    
    baseline_mean = baseline_segment.mean()
    baseline_std = baseline_segment.std()
    
    if baseline_std == 0:
        return 0.0
    
    max_deviation = np.max(np.abs(anomaly_segment - baseline_mean)) / baseline_std
    return float(max_deviation)


def zscore_temporal_rca(df: pd.DataFrame,
                        z_threshold: float = 3.0,
                        min_anomaly_duration: int = 5) -> List[Dict]:
    """
    Z-score based RCA with temporal ordering.
    
    Args:
        df: DataFrame with telemetry data
        z_threshold: Z-score threshold for anomaly detection
        min_anomaly_duration: Minimum samples for sustained anomaly
    
    Returns:
        List of signal analysis results, sorted by first anomaly time
    """
    # Get numeric columns only
    numeric_cols = [col for col in df.columns if col != 'timestamp' 
                    and df[col].dtype in [np.float64, np.int64, np.float32, np.int32]]
    
    results = []
    
    for col in numeric_cols:
        first_anomaly_idx = detect_first_anomaly(
            df[col], 
            threshold=z_threshold,
            min_duration=min_anomaly_duration
        )
        
        if first_anomaly_idx is not None:
            severity = compute_signal_severity(df[col], first_anomaly_idx)
            
            results.append({
                'signal': col,
                'first_anomaly_idx': first_anomaly_idx,
                'first_anomaly_time': df['timestamp'].iloc[first_anomaly_idx] if 'timestamp' in df.columns else None,
                'severity': severity,
                'max_zscore': float(np.max(np.abs(compute_rolling_zscore(df[col]))))
            })
    
    # Sort by first anomaly time (earliest first)
    results.sort(key=lambda x: x['first_anomaly_idx'])
    
    return results


def build_temporal_causal_chain(signal_results: List[Dict], 
                                 max_signals: int = 10) -> List[Dict]:
    """
    Build a causal chain based on temporal ordering.
    Earlier anomalies are assumed to cause later ones.
    """
    chain = []
    
    for i, result in enumerate(signal_results[:max_signals]):
        chain.append({
            'signal': result['signal'],
            'order': i + 1,
            'first_anomaly_idx': result['first_anomaly_idx'],
            'severity': result['severity']
        })
    
    return chain


def identify_root_cause(df: pd.DataFrame,
                        z_threshold: float = 3.0,
                        top_k: int = 5) -> dict:
    """
    Main function to identify root causes using z-score + temporal ordering.
    
    Args:
        df: DataFrame with telemetry data
        z_threshold: Z-score threshold for anomaly detection
        top_k: Number of top candidates to return
    
    Returns:
        Dictionary with root cause analysis results
    """
    # Run temporal analysis
    signal_results = zscore_temporal_rca(df, z_threshold=z_threshold)
    
    if not signal_results:
        return {
            'method': 'zscore_temporal',
            'root_cause': None,
            'confidence': 0.0,
            'ranked_candidates': [],
            'causal_chain': [],
            'causal_graph': {'nodes': [], 'edges': []}
        }
    
    # Root cause is the first signal to show anomaly
    root_cause = signal_results[0]
    
    # Build causal chain
    causal_chain = build_temporal_causal_chain(signal_results)
    
    # Build simple causal graph (chain structure)
    nodes = [r['signal'] for r in signal_results[:top_k]]
    edges = []
    for i in range(len(nodes) - 1):
        edges.append({
            'source': nodes[i],
            'target': nodes[i + 1],
            'weight': 0.8 - i * 0.1  # Decreasing confidence for later edges
        })
    
    # Calculate confidence based on:
    # 1. How much earlier the root cause is vs. others
    # 2. Severity of the anomaly
    time_gap = 0
    if len(signal_results) > 1:
        time_gap = signal_results[1]['first_anomaly_idx'] - signal_results[0]['first_anomaly_idx']
    
    confidence = min(0.9, 0.5 + (time_gap / 100) * 0.2 + (root_cause['severity'] / 10) * 0.2)
    
    results = {
        'method': 'zscore_temporal',
        'window': {
            'start_idx': root_cause['first_anomaly_idx'] - 50 if root_cause['first_anomaly_idx'] > 50 else 0,
            'end_idx': len(df) - 1
        },
        'root_cause': root_cause['signal'],
        'confidence': confidence,
        'root_cause_time': root_cause['first_anomaly_time'],
        'ranked_candidates': [
            {
                'signal': r['signal'],
                'first_anomaly_idx': r['first_anomaly_idx'],
                'severity': r['severity'],
                'score': r['severity'] / (r['first_anomaly_idx'] + 1) * 1000  # Earlier + severe = higher score
            }
            for r in signal_results[:top_k]
        ],
        'causal_chain': causal_chain[:top_k],
        'causal_graph': {
            'nodes': nodes,
            'edges': edges
        }
    }
    
    return results


def main():
    """Example usage of the z-score temporal baseline."""
    import json
    import os
    
    # Example: run on scenario 01
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenario_01_easy')
    
    if os.path.exists(data_path):
        # Load data
        df = pd.read_csv(os.path.join(data_path, 'telemetry.csv'))
        
        # Run RCA
        results = identify_root_cause(df)
        
        print("Z-Score Temporal Baseline Results")
        print("=" * 50)
        print(f"Identified Root Cause: {results['root_cause']}")
        print(f"First Anomaly Time: {results.get('root_cause_time', 'N/A')}")
        print(f"Confidence: {results['confidence']:.3f}")
        print("\nCausal Chain:")
        for item in results['causal_chain'][:5]:
            print(f"  {item['order']}. {item['signal']} (severity: {item['severity']:.2f})")
        
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
