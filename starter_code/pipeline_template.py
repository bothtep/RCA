#!/usr/bin/env python3
"""
RCA Pipeline Template

This is a template/skeleton for students to implement their RCA solution.
Each step corresponds to one of the 5 RCA pipeline stages.

Students should:
1. Fill in the implementation for each step
2. Choose appropriate algorithms
3. Tune parameters
4. Document their design decisions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class RCAResult:
    """Data class to hold RCA results."""
    root_cause: str
    confidence: float
    ranked_candidates: List[Dict]
    causal_chain: List[Dict]
    causal_graph: Dict
    incident_window: Tuple[int, int]
    explanations: Dict


class RCAPipeline:
    """
    Root Cause Analysis Pipeline
    
    This class implements the 5-step RCA pipeline:
    1. Incident Window Isolation
    2. Signal Clustering
    3. Temporal Analysis
    4. Causal Graph Construction
    5. Root Cause Ranking & Explanation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the RCA pipeline.
        
        Args:
            config: Configuration dictionary for algorithm parameters
        """
        self.config = config or {}
        
        # Default parameters - students should tune these
        self.window_context_seconds = self.config.get('window_context_seconds', 300)
        self.zscore_threshold = self.config.get('zscore_threshold', 3.0)
        self.n_clusters = self.config.get('n_clusters', 5)
        self.max_lag_samples = self.config.get('max_lag_samples', 100)
        self.causality_threshold = self.config.get('causality_threshold', 0.1)
    
    def run(self, df: pd.DataFrame, incident_metadata: Optional[Dict] = None) -> RCAResult:
        """
        Run the complete RCA pipeline.
        
        Args:
            df: Telemetry DataFrame
            incident_metadata: Optional incident information
        
        Returns:
            RCAResult with analysis results
        """
        # Step 1: Incident Window Isolation
        window_start, window_end = self.step1_isolate_window(df, incident_metadata)
        window_df = df.iloc[window_start:window_end].reset_index(drop=True)
        
        # Step 2: Signal Clustering
        clusters = self.step2_cluster_signals(window_df)
        
        # Step 3: Temporal Analysis
        temporal_results = self.step3_temporal_analysis(window_df)
        
        # Step 4: Causal Graph Construction
        causal_graph = self.step4_build_causal_graph(window_df, temporal_results)
        
        # Step 5: Root Cause Ranking & Explanation
        ranked_causes, explanations = self.step5_rank_and_explain(
            window_df, temporal_results, causal_graph, clusters
        )
        
        # Compile results
        result = RCAResult(
            root_cause=ranked_causes[0]['signal'] if ranked_causes else None,
            confidence=ranked_causes[0]['score'] if ranked_causes else 0.0,
            ranked_candidates=ranked_causes[:10],
            causal_chain=self._extract_causal_chain(ranked_causes, temporal_results),
            causal_graph=causal_graph,
            incident_window=(window_start, window_end),
            explanations=explanations
        )
        
        return result
    
    def step1_isolate_window(self, 
                             df: pd.DataFrame, 
                             incident_metadata: Optional[Dict] = None) -> Tuple[int, int]:
        """
        Step 1: Incident Window Isolation
        
        Identify the time window where the incident/anomaly occurred.
        
        Suggested Algorithms:
        - Change-point detection (PELT, Binary Segmentation)
        - Z-score thresholding
        - Rolling statistics deviation
        
        Args:
            df: Full telemetry DataFrame
            incident_metadata: Optional dict with incident timestamp
        
        Returns:
            (start_index, end_index) of incident window
        """
        # TODO: Implement incident window detection
        # 
        # Students should implement one or more of:
        # 1. Change-point detection using ruptures library
        # 2. Z-score based anomaly detection
        # 3. Rolling mean/std deviation detection
        #
        # Example skeleton:
        # 
        # import ruptures as rpt
        # 
        # # Combine signals into single feature
        # numeric_cols = [c for c in df.columns if c != 'timestamp']
        # signal_matrix = df[numeric_cols].values
        # 
        # # Detect change points
        # algo = rpt.Pelt(model="rbf").fit(signal_matrix)
        # change_points = algo.predict(pen=10)
        # 
        # # Extract window around first change point
        # ...
        
        # Placeholder: return full range
        return 0, len(df)
    
    def step2_cluster_signals(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Step 2: Signal Clustering
        
        Group signals that exhibit similar patterns.
        
        Suggested Algorithms:
        - K-Means clustering on signal features
        - DBSCAN for density-based clustering
        - Hierarchical clustering
        - DTW-based clustering for time series
        
        Args:
            df: Telemetry DataFrame (incident window)
        
        Returns:
            Dictionary mapping signal names to cluster IDs
        """
        # TODO: Implement signal clustering
        #
        # Students should:
        # 1. Extract features from each signal (mean, std, trend, etc.)
        # 2. Normalize features
        # 3. Apply clustering algorithm
        # 4. Optionally: interpret clusters (thermal, electrical, etc.)
        #
        # Example skeleton:
        #
        # from sklearn.cluster import KMeans
        # from sklearn.preprocessing import StandardScaler
        #
        # features = []
        # signal_names = []
        # for col in df.columns:
        #     if col != 'timestamp':
        #         feat = extract_features(df[col])
        #         features.append(feat)
        #         signal_names.append(col)
        #
        # scaler = StandardScaler()
        # features_scaled = scaler.fit_transform(features)
        #
        # kmeans = KMeans(n_clusters=self.n_clusters)
        # labels = kmeans.fit_predict(features_scaled)
        #
        # return {name: label for name, label in zip(signal_names, labels)}
        
        # Placeholder: assign all to cluster 0
        return {col: 0 for col in df.columns if col != 'timestamp'}
    
    def step3_temporal_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Step 3: Temporal Relationships & Correlation
        
        Analyze temporal relationships between signals.
        
        Suggested Algorithms:
        - Lagged cross-correlation
        - Granger causality tests
        - Transfer entropy
        - Dynamic Time Warping
        
        Args:
            df: Telemetry DataFrame (incident window)
        
        Returns:
            Dictionary with temporal analysis results:
            - first_anomaly_times: when each signal first showed anomaly
            - lag_matrix: pairwise lag values
            - correlation_matrix: pairwise correlations at optimal lag
            - granger_matrix: pairwise Granger causality p-values
        """
        # TODO: Implement temporal analysis
        #
        # Students should:
        # 1. Detect first anomaly time for each signal
        # 2. Compute lagged cross-correlations
        # 3. Run Granger causality tests
        # 4. Determine temporal ordering
        #
        # Example skeleton:
        #
        # from statsmodels.tsa.stattools import grangercausalitytests
        #
        # results = {
        #     'first_anomaly_times': {},
        #     'lag_matrix': {},
        #     'granger_matrix': {}
        # }
        #
        # signals = [c for c in df.columns if c != 'timestamp']
        #
        # # First anomaly times
        # for sig in signals:
        #     z_scores = (df[sig] - df[sig].mean()) / df[sig].std()
        #     anomaly_mask = abs(z_scores) > self.zscore_threshold
        #     if anomaly_mask.any():
        #         results['first_anomaly_times'][sig] = anomaly_mask.idxmax()
        #
        # # Granger causality
        # for sig_a in signals:
        #     for sig_b in signals:
        #         if sig_a != sig_b:
        #             # Test if sig_a causes sig_b
        #             ...
        #
        # return results
        
        # Placeholder: empty results
        return {
            'first_anomaly_times': {},
            'lag_matrix': {},
            'granger_matrix': {}
        }
    
    def step4_build_causal_graph(self, 
                                  df: pd.DataFrame,
                                  temporal_results: Dict) -> Dict:
        """
        Step 4: Build & Score Causal Graph
        
        Construct a directed graph representing causal relationships.
        
        Suggested Algorithms:
        - PC Algorithm
        - FCI Algorithm
        - LiNGAM
        - GES (Greedy Equivalence Search)
        - Simple: threshold Granger matrix
        
        Args:
            df: Telemetry DataFrame
            temporal_results: Results from step 3
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        # TODO: Implement causal graph construction
        #
        # Students should:
        # 1. Use temporal analysis results
        # 2. Apply causal discovery algorithm OR
        # 3. Build graph from significant Granger relationships
        # 4. Score edges based on evidence
        #
        # Example skeleton:
        #
        # nodes = [c for c in df.columns if c != 'timestamp']
        # edges = []
        #
        # granger = temporal_results.get('granger_matrix', {})
        # first_times = temporal_results.get('first_anomaly_times', {})
        #
        # for (src, tgt), p_value in granger.items():
        #     if p_value < self.causality_threshold:
        #         # Check temporal order
        #         src_time = first_times.get(src, float('inf'))
        #         tgt_time = first_times.get(tgt, float('inf'))
        #         
        #         if src_time < tgt_time:  # src changed first
        #             edges.append({
        #                 'source': src,
        #                 'target': tgt,
        #                 'weight': 1 - p_value
        #             })
        #
        # return {'nodes': nodes, 'edges': edges}
        
        # Placeholder: empty graph
        return {
            'nodes': [c for c in df.columns if c != 'timestamp'],
            'edges': []
        }
    
    def step5_rank_and_explain(self,
                                df: pd.DataFrame,
                                temporal_results: Dict,
                                causal_graph: Dict,
                                clusters: Dict) -> Tuple[List[Dict], Dict]:
        """
        Step 5: Rank Root Causes & Generate Explanations
        
        Produce ranked list of root cause candidates with explanations.
        
        Suggested Algorithms:
        - PageRank on causal graph
        - Net causality scoring
        - XGBoost feature importance
        - SHAP values
        
        Args:
            df: Telemetry DataFrame
            temporal_results: Results from step 3
            causal_graph: Graph from step 4
            clusters: Cluster assignments from step 2
        
        Returns:
            Tuple of:
            - List of ranked candidates with scores
            - Dictionary of explanations
        """
        # TODO: Implement root cause ranking and explanation
        #
        # Students should:
        # 1. Compute ranking score for each signal
        # 2. Consider: temporal order, graph position, severity
        # 3. Generate human-readable explanations
        #
        # Example skeleton:
        #
        # import networkx as nx
        #
        # # Build NetworkX graph
        # G = nx.DiGraph()
        # for edge in causal_graph['edges']:
        #     G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        #
        # # PageRank (reversed for root cause)
        # if G.edges():
        #     reversed_G = G.reverse()
        #     pagerank = nx.pagerank(reversed_G)
        #     ranked = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        # else:
        #     # Fall back to first anomaly time
        #     first_times = temporal_results.get('first_anomaly_times', {})
        #     ranked = sorted(first_times.items(), key=lambda x: x[1])
        #
        # # Convert to expected format
        # ranked_candidates = [
        #     {'signal': sig, 'score': score}
        #     for sig, score in ranked
        # ]
        #
        # # Generate explanations
        # explanations = {}
        # for candidate in ranked_candidates[:5]:
        #     sig = candidate['signal']
        #     explanations[sig] = self._generate_explanation(sig, ...)
        #
        # return ranked_candidates, explanations
        
        # Placeholder: rank by variance
        signals = [c for c in df.columns if c != 'timestamp']
        ranked = [(sig, df[sig].var()) for sig in signals]
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        ranked_candidates = [
            {'signal': sig, 'score': score}
            for sig, score in ranked
        ]
        
        explanations = {}
        
        return ranked_candidates, explanations
    
    def _extract_causal_chain(self, 
                              ranked_causes: List[Dict],
                              temporal_results: Dict) -> List[Dict]:
        """Extract causal chain from results."""
        chain = []
        first_times = temporal_results.get('first_anomaly_times', {})
        
        for i, cause in enumerate(ranked_causes[:10]):
            chain.append({
                'signal': cause['signal'],
                'order': i + 1,
                'first_anomaly_idx': first_times.get(cause['signal'])
            })
        
        return chain
    
    def _generate_explanation(self, signal: str, evidence: Dict) -> str:
        """Generate natural language explanation for a root cause candidate."""
        # TODO: Implement explanation generation
        template = f"""
Root Cause Candidate: {signal}

Evidence:
- First anomaly detected at: [timestamp]
- Deviation from normal: [X] standard deviations
- Downstream effects: [list of affected signals]
- Temporal precedence: This signal changed [X] seconds before cascade

Conclusion: [Summary of why this is likely the root cause]
"""
        return template


def main():
    """Example usage of the RCA pipeline."""
    import sys
    sys.path.insert(0, '.')
    from data_loader import load_scenario, list_scenarios
    
    # Load example scenario
    scenarios = list_scenarios()
    if not scenarios:
        print("No scenarios found. Please generate data first.")
        return
    
    scenario_name = scenarios[0]
    print(f"Loading scenario: {scenario_name}")
    
    df, incident, ground_truth = load_scenario(scenario_name)
    
    # Initialize and run pipeline
    pipeline = RCAPipeline()
    result = pipeline.run(df, incident)
    
    # Display results
    print("\n" + "=" * 50)
    print("RCA PIPELINE RESULTS")
    print("=" * 50)
    print(f"\nIdentified Root Cause: {result.root_cause}")
    print(f"Confidence: {result.confidence:.3f}")
    
    print("\nTop 5 Candidates:")
    for i, candidate in enumerate(result.ranked_candidates[:5], 1):
        print(f"  {i}. {candidate['signal']}: {candidate['score']:.3f}")
    
    print(f"\nGround Truth: {ground_truth.get('root_cause')}")
    print(f"Match: {result.root_cause == ground_truth.get('root_cause')}")


if __name__ == "__main__":
    main()
