#!/usr/bin/env python3
"""
Step 3: Temporal Relationship Analysis

This module implements temporal relationship analysis for the RCA pipeline.
It determines which signals changed first and identifies causal relationships
between signals using lagged correlation and Granger causality tests.

Author: Student Implementation
Course: EE 370 - Introduction to Machine Learning with Python
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

# Suppress statsmodels warnings for cleaner output
warnings.filterwarnings('ignore')


@dataclass
class TemporalAnalysisResult:
    """Data class to hold temporal analysis results."""
    first_anomaly_times: Dict[str, int]  # signal -> index of first anomaly
    lag_matrix: Dict[Tuple[str, str], int]  # (signal_a, signal_b) -> optimal lag
    correlation_matrix: Dict[Tuple[str, str], float]  # (signal_a, signal_b) -> correlation at optimal lag
    granger_matrix: Dict[Tuple[str, str], float]  # (signal_a, signal_b) -> p-value
    temporal_order: List[str]  # signals ordered by first anomaly time


class TemporalAnalyzer:
    """
    Temporal Relationship Analyzer
    
    Implements algorithms for determining temporal ordering and causal
    relationships between signals in vehicle telemetry data.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the temporal analyzer.
        
        Args:
            config: Configuration dictionary for algorithm parameters
        """
        self.config = config or {}
        
        # Default parameters
        self.zscore_threshold = self.config.get('zscore_threshold', 3.0)
        self.max_lag_samples = self.config.get('max_lag_samples', 100)
        self.granger_max_lag = self.config.get('granger_max_lag', 10)
        self.granger_significance = self.config.get('granger_significance', 0.05)
        self.min_samples_for_granger = self.config.get('min_samples_for_granger', 50)
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Perform complete temporal analysis on telemetry data.
        
        Args:
            df: Telemetry DataFrame (should be incident window)
        
        Returns:
            Dictionary with temporal analysis results
        """
        # Get signal columns
        signals = [c for c in df.columns if c != 'timestamp']
        
        # Step 3.1: Detect first anomaly time for each signal
        first_anomaly_times = self.detect_first_anomalies(df)
        
        # Step 3.2: Compute lagged cross-correlations
        lag_matrix, correlation_matrix = self.compute_lagged_correlations(df, signals)
        
        # Step 3.3: Run Granger causality tests
        granger_matrix = self.compute_granger_causality(df, signals)
        
        # Step 3.4: Determine temporal ordering
        temporal_order = self.determine_temporal_order(first_anomaly_times)
        
        return {
            'first_anomaly_times': first_anomaly_times,
            'lag_matrix': lag_matrix,
            'correlation_matrix': correlation_matrix,
            'granger_matrix': granger_matrix,
            'temporal_order': temporal_order
        }
    
    def detect_first_anomalies(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Detect the first anomaly time for each signal.
        
        Uses rolling z-score to identify when each signal first deviates
        significantly from its baseline behavior.
        
        Args:
            df: Telemetry DataFrame
        
        Returns:
            Dictionary mapping signal names to index of first anomaly
        """
        first_anomaly_times = {}
        signals = [c for c in df.columns if c != 'timestamp']
        
        # Use first 10% of data as baseline (or at least 100 samples)
        baseline_size = max(int(len(df) * 0.1), 100)
        baseline_size = min(baseline_size, len(df) // 3)  # Don't use more than 1/3
        
        for signal in signals:
            signal_data = df[signal].values
            
            # Calculate baseline statistics
            baseline = signal_data[:baseline_size]
            baseline_mean = np.mean(baseline)
            baseline_std = np.std(baseline)
            
            if baseline_std < 1e-10:
                # Signal has no variance in baseline - skip
                first_anomaly_times[signal] = None
                continue
            
            # Compute z-scores for entire signal
            z_scores = (signal_data - baseline_mean) / baseline_std
            
            # Find first point exceeding threshold
            anomaly_mask = np.abs(z_scores) > self.zscore_threshold
            
            if np.any(anomaly_mask):
                first_anomaly_idx = int(np.argmax(anomaly_mask))
                first_anomaly_times[signal] = first_anomaly_idx
            else:
                # No anomaly detected - mark as very late
                first_anomaly_times[signal] = len(df)
        
        return first_anomaly_times
    
    def compute_lagged_correlations(self, 
                                     df: pd.DataFrame,
                                     signals: List[str]) -> Tuple[Dict, Dict]:
        """
        Compute lagged cross-correlations between all signal pairs.
        
        For each pair of signals, finds the lag at which they are most
        correlated, which helps identify temporal relationships.
        
        Args:
            df: Telemetry DataFrame
            signals: List of signal names to analyze
        
        Returns:
            Tuple of (lag_matrix, correlation_matrix)
            - lag_matrix: (signal_a, signal_b) -> optimal lag (positive = a leads b)
            - correlation_matrix: (signal_a, signal_b) -> correlation at optimal lag
        """
        lag_matrix = {}
        correlation_matrix = {}
        
        for i, signal_a in enumerate(signals):
            for j, signal_b in enumerate(signals):
                if i >= j:
                    # Skip diagonal and lower triangle (symmetric info)
                    continue
                
                data_a = df[signal_a].values
                data_b = df[signal_b].values
                
                # Remove NaN values
                valid_mask = ~(np.isnan(data_a) | np.isnan(data_b))
                if np.sum(valid_mask) < self.min_samples_for_granger:
                    continue
                
                data_a = data_a[valid_mask]
                data_b = data_b[valid_mask]
                
                # Compute lagged correlation
                optimal_lag, max_corr = self._lagged_correlation(
                    data_a, data_b, self.max_lag_samples
                )
                
                lag_matrix[(signal_a, signal_b)] = optimal_lag
                correlation_matrix[(signal_a, signal_b)] = max_corr
                
                # Store reverse relationship
                lag_matrix[(signal_b, signal_a)] = -optimal_lag
                correlation_matrix[(signal_b, signal_a)] = max_corr
        
        return lag_matrix, correlation_matrix
    
    def _lagged_correlation(self, 
                            x: np.ndarray,
                            y: np.ndarray,
                            max_lag: int) -> Tuple[int, float]:
        """
        Compute lagged cross-correlation between two signals.
        
        Args:
            x: First signal (1D array)
            y: Second signal (1D array)
            max_lag: Maximum lag to consider
        
        Returns:
            Tuple of (optimal_lag, max_correlation)
            - optimal_lag: Lag where correlation is strongest
            - max_correlation: Correlation value at optimal lag
            
        Interpretation:
            - Positive lag: x leads y (x changes before y)
            - Negative lag: y leads x (y changes before x)
        """
        n = len(x)
        
        # Normalize signals
        x_norm = (x - np.mean(x)) / (np.std(x) + 1e-10)
        y_norm = (y - np.mean(y)) / (np.std(y) + 1e-10)
        
        correlations = np.zeros(2 * max_lag + 1)
        
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                # y leads x
                min_len = min(len(x_norm[:lag]), len(y_norm[-lag:]))
                if min_len > 0:
                    corr = np.corrcoef(
                        x_norm[:lag][:min_len],
                        y_norm[-lag:][:min_len]
                    )[0, 1]
                else:
                    corr = 0
            elif lag > 0:
                # x leads y
                min_len = min(len(x_norm[lag:]), len(y_norm[:-lag]))
                if min_len > 0:
                    corr = np.corrcoef(
                        x_norm[lag:][:min_len],
                        y_norm[:-lag][:min_len]
                    )[0, 1]
                else:
                    corr = 0
            else:
                # Zero lag
                corr = np.corrcoef(x_norm, y_norm)[0, 1]
            
            correlations[lag + max_lag] = corr if not np.isnan(corr) else 0
        
        # Find best lag
        best_idx = np.argmax(np.abs(correlations))
        optimal_lag = best_idx - max_lag
        max_corr = correlations[best_idx]
        
        return optimal_lag, max_corr
    
    def compute_granger_causality(self,
                                   df: pd.DataFrame,
                                   signals: List[str]) -> Dict[Tuple[str, str], float]:
        """
        Compute Granger causality tests between signal pairs.
        
        Granger causality tests whether one time series helps predict
        another, providing statistical evidence for causal relationships.
        
        Args:
            df: Telemetry DataFrame
            signals: List of signal names to analyze
        
        Returns:
            Dictionary mapping (cause, effect) -> p-value
            Lower p-value indicates stronger evidence that first causes second
        """
        granger_matrix = {}
        
        # Import statsmodels here to avoid dependency if not used
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
        except ImportError:
            print("Warning: statsmodels not installed. Skipping Granger causality tests.")
            print("Install with: pip install statsmodels")
            return granger_matrix
        
        for signal_cause in signals:
            for signal_effect in signals:
                if signal_cause == signal_effect:
                    continue
                
                # Get data
                data_cause = df[signal_cause].values
                data_effect = df[signal_effect].values
                
                # Remove NaN values
                valid_mask = ~(np.isnan(data_cause) | np.isnan(data_effect))
                if np.sum(valid_mask) < self.min_samples_for_granger * 2:
                    granger_matrix[(signal_cause, signal_effect)] = 1.0
                    continue
                
                data_cause = data_cause[valid_mask]
                data_effect = data_effect[valid_mask]
                
                # Run Granger test
                p_value, best_lag = self._granger_test(
                    data_cause, data_effect, self.granger_max_lag
                )
                
                granger_matrix[(signal_cause, signal_effect)] = p_value
        
        return granger_matrix
    
    def _granger_test(self,
                      cause: np.ndarray,
                      effect: np.ndarray,
                      max_lag: int) -> Tuple[float, int]:
        """
        Perform Granger causality test.
        
        Tests whether 'cause' Granger-causes 'effect'.
        
        Args:
            cause: Potential cause signal
            effect: Potential effect signal
            max_lag: Maximum lag to test
        
        Returns:
            Tuple of (min_pvalue, best_lag)
            - min_pvalue: Minimum p-value across tested lags
            - best_lag: Lag with strongest evidence
        """
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            
            # Stack data: [effect, cause] (note the order!)
            data = np.column_stack([effect, cause])
            
            # Handle edge cases
            if len(data) < max_lag + 10:
                return 1.0, 0
            
            # Run Granger tests
            results = grangercausalitytests(data, maxlag=max_lag, verbose=False)
            
            # Extract p-values (using F-test statistic)
            p_values = {}
            for lag, result in results.items():
                try:
                    p_value = result[0]['ssr_ftest'][1]
                    p_values[lag] = p_value
                except (KeyError, IndexError):
                    p_values[lag] = 1.0
            
            # Find best lag
            if p_values:
                best_lag = min(p_values, key=p_values.get)
                min_pvalue = p_values[best_lag]
            else:
                best_lag = 0
                min_pvalue = 1.0
            
            return min_pvalue, best_lag
            
        except Exception as e:
            # Return non-significant result on error
            return 1.0, 0
    
    def determine_temporal_order(self,
                                  first_anomaly_times: Dict[str, int]) -> List[str]:
        """
        Determine temporal ordering of signals based on first anomaly times.
        
        Args:
            first_anomaly_times: Dictionary mapping signals to first anomaly index
        
        Returns:
            List of signals ordered by first anomaly time (earliest first)
        """
        # Filter out None values and sort by anomaly time
        valid_times = {
            sig: time for sig, time in first_anomaly_times.items()
            if time is not None
        }
        
        sorted_signals = sorted(valid_times.keys(), key=lambda s: valid_times[s])
        
        return sorted_signals
    
    def get_causality_evidence(self,
                                granger_matrix: Dict[Tuple[str, str], float],
                                significance: float = 0.05) -> List[Dict]:
        """
        Extract significant causal relationships from Granger matrix.
        
        Args:
            granger_matrix: Granger causality p-values
            significance: P-value threshold for significance
        
        Returns:
            List of causal relationships with evidence scores
        """
        evidence = []
        
        for (cause, effect), p_value in granger_matrix.items():
            if p_value < significance:
                evidence.append({
                    'cause': cause,
                    'effect': effect,
                    'p_value': p_value,
                    'confidence': 1 - p_value,
                    'significant': True
                })
        
        # Sort by confidence (highest first)
        evidence.sort(key=lambda x: x['confidence'], reverse=True)
        
        return evidence


def analyze_temporal_relationships(df: pd.DataFrame,
                                    config: Optional[Dict] = None) -> Dict:
    """
    Convenience function to perform temporal analysis.
    
    Args:
        df: Telemetry DataFrame (incident window)
        config: Optional configuration dictionary
    
    Returns:
        Dictionary with temporal analysis results
    """
    analyzer = TemporalAnalyzer(config)
    return analyzer.analyze(df)


def main():
    """Example usage of temporal analysis."""
    import sys
    sys.path.insert(0, '..')
    from data_loader import load_scenario, list_scenarios
    
    # Load example scenario
    scenarios = list_scenarios()
    if not scenarios:
        print("No scenarios found. Please generate data first.")
        return
    
    scenario_name = scenarios[0]
    print(f"Loading scenario: {scenario_name}")
    
    df, incident, ground_truth = load_scenario(scenario_name)
    
    # Get incident window if available
    from step1_window_detection import detect_incident_window
    start_idx, end_idx = detect_incident_window(df)
    window_df = df.iloc[start_idx:end_idx].reset_index(drop=True)
    
    print(f"Analyzing window: {start_idx} to {end_idx} ({len(window_df)} samples)")
    
    # Run temporal analysis
    results = analyze_temporal_relationships(window_df)
    
    # Display results
    print("\n" + "=" * 60)
    print("TEMPORAL RELATIONSHIP ANALYSIS RESULTS")
    print("=" * 60)
    
    print("\n1. First Anomaly Times (top 10 earliest):")
    sorted_times = sorted(
        [(sig, t) for sig, t in results['first_anomaly_times'].items() if t is not None],
        key=lambda x: x[1]
    )
    for sig, time in sorted_times[:10]:
        print(f"  {sig}: index {time}")
    
    print("\n2. Temporal Order (first 10 signals):")
    for i, sig in enumerate(results['temporal_order'][:10], 1):
        time = results['first_anomaly_times'][sig]
        print(f"  {i}. {sig} (anomaly at index {time})")
    
    print("\n3. Significant Granger Causal Relationships (p < 0.05):")
    analyzer = TemporalAnalyzer()
    evidence = analyzer.get_causality_evidence(results['granger_matrix'])
    
    if evidence:
        for rel in evidence[:10]:
            print(f"  {rel['cause']} → {rel['effect']} (p={rel['p_value']:.4f}, confidence={rel['confidence']:.2f})")
    else:
        print("  No significant relationships found.")
    
    print("\n4. Strongest Lagged Correlations:")
    corr_items = list(results['correlation_matrix'].items())
    corr_items.sort(key=lambda x: abs(x[1]), reverse=True)
    for (sig_a, sig_b), corr in corr_items[:10]:
        lag = results['lag_matrix'][(sig_a, sig_b)]
        leader = sig_a if lag > 0 else sig_b
        print(f"  {sig_a} ↔ {sig_b}: r={corr:.3f} (lag={lag}, {leader} leads)")
    
    print("\n" + "=" * 60)
    print(f"Ground Truth Root Cause: {ground_truth.get('root_cause', 'N/A')}")
    
    # Check if earliest signal matches ground truth
    if results['temporal_order']:
        earliest = results['temporal_order'][0]
        print(f"Earliest Anomaly: {earliest}")
        print(f"Match: {earliest == ground_truth.get('root_cause')}")


if __name__ == "__main__":
    main()
