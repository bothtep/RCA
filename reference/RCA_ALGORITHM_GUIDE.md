# RCA Algorithm Guide

This guide provides detailed explanations of algorithms you can use for each step of the RCA pipeline.

---

## Step 1: Incident Window Isolation

### Goal
Identify the time window where the anomaly/failure occurred.

### Algorithm Options

#### 1.1 Change-Point Detection with PELT

**What it does**: Finds points where statistical properties of the signal change.

**Library**: `ruptures`

```python
import ruptures as rpt
import numpy as np

def detect_change_points_pelt(signal, model='rbf', penalty=10):
    """
    Detect change points using PELT algorithm.
    
    Args:
        signal: 1D numpy array
        model: Cost function ('rbf', 'l2', 'l1', 'normal')
        penalty: Penalty for adding change points (higher = fewer points)
    
    Returns:
        List of change point indices
    """
    algo = rpt.Pelt(model=model).fit(signal)
    change_points = algo.predict(pen=penalty)
    return change_points[:-1]  # Remove last point (always len(signal))
```

**Pros**: Optimal detection, handles multiple change points
**Cons**: Can be slow on long signals
**Parameter Tuning**: Start with penalty=10, increase if too many points detected

#### 1.2 Z-Score Threshold Detection

**What it does**: Flags points exceeding N standard deviations from mean.

```python
import numpy as np
import pandas as pd

def detect_anomalies_zscore(signal, threshold=3.0, window=100):
    """
    Detect anomalies using rolling z-score.
    
    Args:
        signal: Pandas Series
        threshold: Number of std deviations
        window: Rolling window size for baseline
    
    Returns:
        Boolean mask of anomalies
    """
    rolling_mean = signal.rolling(window=window, min_periods=1).mean()
    rolling_std = signal.rolling(window=window, min_periods=1).std()
    
    z_scores = (signal - rolling_mean) / rolling_std
    return np.abs(z_scores) > threshold
```

**Pros**: Simple, intuitive, fast
**Cons**: Doesn't handle gradual changes well
**Parameter Tuning**: threshold=3 is standard; window depends on sampling rate

#### 1.3 CUSUM (Cumulative Sum)

**What it does**: Detects shifts in mean by tracking cumulative deviations.

```python
def cusum_detection(signal, threshold=5.0, drift=0.5):
    """
    CUSUM change detection.
    
    Args:
        signal: 1D array (normalized)
        threshold: Detection threshold
        drift: Allowed drift before flagging
    
    Returns:
        Index of detected change
    """
    s_pos = np.zeros(len(signal))
    s_neg = np.zeros(len(signal))
    
    for i in range(1, len(signal)):
        s_pos[i] = max(0, s_pos[i-1] + signal[i] - drift)
        s_neg[i] = max(0, s_neg[i-1] - signal[i] - drift)
        
        if s_pos[i] > threshold or s_neg[i] > threshold:
            return i
    
    return None
```

**Pros**: Good for shift detection, interpretable
**Cons**: Needs normalized data, sensitive to parameters

---

## Step 2: Signal Clustering

### Goal
Group signals that exhibit similar behavior patterns.

### Algorithm Options

#### 2.1 K-Means on Statistical Features

**What it does**: Clusters signals based on extracted statistical features.

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from scipy import stats

def extract_features(signal):
    """Extract statistical features from a signal."""
    return np.array([
        np.mean(signal),
        np.std(signal),
        np.min(signal),
        np.max(signal),
        stats.skew(signal),
        stats.kurtosis(signal),
        np.polyfit(range(len(signal)), signal, 1)[0],  # trend
    ])

def cluster_signals_kmeans(df, n_clusters=5):
    """
    Cluster signals using K-Means on features.
    
    Returns:
        Dict mapping signal_id to cluster_id
    """
    signals = [c for c in df.columns if c != 'timestamp']
    
    features = np.array([extract_features(df[s].values) for s in signals])
    features = np.nan_to_num(features)
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_scaled)
    
    return dict(zip(signals, labels))
```

**Pros**: Fast, easy to interpret
**Cons**: Must choose k; sensitive to feature selection
**Parameter Tuning**: Use elbow method or silhouette score for k

#### 2.2 DBSCAN (Density-Based)

**What it does**: Finds clusters of arbitrary shape, identifies outliers.

```python
from sklearn.cluster import DBSCAN

def cluster_signals_dbscan(features, eps=0.5, min_samples=2):
    """
    DBSCAN clustering.
    
    Args:
        features: Feature matrix (signals x features)
        eps: Maximum distance between points in cluster
        min_samples: Minimum points to form cluster
    
    Returns:
        Cluster labels (-1 = noise)
    """
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(features_scaled)
    
    return labels
```

**Pros**: No need to specify k, finds outliers
**Cons**: Sensitive to eps parameter
**Parameter Tuning**: Use k-distance graph to find eps

#### 2.3 Dynamic Time Warping (DTW) + K-Medoids

**What it does**: Clusters time series allowing for temporal shifts.

```python
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

def cluster_signals_dtw(df, n_clusters=5):
    """
    Cluster signals using DTW distance.
    """
    signals = [c for c in df.columns if c != 'timestamp']
    
    # Format data for tslearn (n_samples, n_timestamps, n_features)
    X = np.array([df[s].values for s in signals])
    X = X.reshape(len(signals), -1, 1)
    
    scaler = TimeSeriesScalerMeanVariance()
    X_scaled = scaler.fit_transform(X)
    
    model = TimeSeriesKMeans(n_clusters=n_clusters, metric="dtw", random_state=42)
    labels = model.fit_predict(X_scaled)
    
    return dict(zip(signals, labels))
```

**Pros**: Handles temporal misalignment
**Cons**: Computationally expensive
**When to Use**: When signals have similar patterns at different times

---

## Step 3: Temporal Relationship Analysis

### Goal
Determine which signals changed first and their causal relationships.

### Algorithm Options

#### 3.1 Lagged Cross-Correlation

**What it does**: Finds time lag at which two signals are most correlated.

```python
import numpy as np

def lagged_correlation(x, y, max_lag=100):
    """
    Compute lagged cross-correlation.
    
    Args:
        x, y: 1D arrays (same length)
        max_lag: Maximum lag to consider
    
    Returns:
        optimal_lag: Lag where correlation is strongest
        max_corr: Correlation at optimal lag
    """
    # Normalize
    x = (x - np.mean(x)) / np.std(x)
    y = (y - np.mean(y)) / np.std(y)
    
    n = len(x)
    correlations = np.zeros(2 * max_lag + 1)
    
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = np.corrcoef(x[:lag], y[-lag:])[0, 1]
        elif lag > 0:
            corr = np.corrcoef(x[lag:], y[:-lag])[0, 1]
        else:
            corr = np.corrcoef(x, y)[0, 1]
        
        correlations[lag + max_lag] = corr if not np.isnan(corr) else 0
    
    best_idx = np.argmax(np.abs(correlations))
    optimal_lag = best_idx - max_lag
    max_corr = correlations[best_idx]
    
    return optimal_lag, max_corr
```

**Interpretation**: Positive lag means x leads y; negative means y leads x

#### 3.2 Granger Causality

**What it does**: Tests if one signal helps predict another (statistical causality).

```python
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np

def granger_causality_test(x, y, max_lag=10):
    """
    Test if x Granger-causes y.
    
    Args:
        x: Potential cause signal
        y: Potential effect signal
        max_lag: Maximum lag to test
    
    Returns:
        min_pvalue: Minimum p-value across lags
        best_lag: Lag with strongest evidence
    """
    # Stack data: [effect, cause]
    data = np.column_stack([y, x])
    
    try:
        results = grangercausalitytests(data, maxlag=max_lag, verbose=False)
        
        # Extract p-values (using F-test)
        p_values = {lag: results[lag][0]['ssr_ftest'][1] 
                    for lag in results.keys()}
        
        best_lag = min(p_values, key=p_values.get)
        min_pvalue = p_values[best_lag]
        
        return min_pvalue, best_lag
    except:
        return 1.0, 0
```

**Important**: Low p-value (< 0.05) suggests x Granger-causes y

#### 3.3 Transfer Entropy

**What it does**: Measures information transfer between signals (non-linear causality).

```python
def transfer_entropy(source, target, k=1, bins=10):
    """
    Estimate transfer entropy from source to target.
    
    Args:
        source, target: 1D arrays
        k: Embedding dimension
        bins: Number of bins for discretization
    
    Returns:
        Transfer entropy value (higher = more information transfer)
    """
    from scipy.stats import entropy
    
    # Discretize
    source_d = np.digitize(source, np.linspace(source.min(), source.max(), bins))
    target_d = np.digitize(target, np.linspace(target.min(), target.max(), bins))
    
    # Create lagged versions
    n = len(source) - k
    target_future = target_d[k:]
    target_past = target_d[:n]
    source_past = source_d[:n]
    
    # Compute joint and marginal entropies
    # H(Y_future | Y_past, X_past) vs H(Y_future | Y_past)
    # TE = H(Y_f | Y_p) - H(Y_f | Y_p, X_p)
    
    # Simplified estimation using histograms
    # (For production, use specialized libraries like pyinform)
    
    # This is a simplified placeholder
    return 0.0  # Replace with actual implementation
```

---

## Step 4: Causal Graph Construction

### Goal
Build a directed graph representing cause-effect relationships.

### Algorithm Options

#### 4.1 Thresholded Granger Matrix

**What it does**: Creates edges where Granger causality is significant.

```python
import networkx as nx

def build_graph_from_granger(granger_matrix, signals, p_threshold=0.05):
    """
    Build causal graph from Granger causality matrix.
    
    Args:
        granger_matrix: Dict of (source, target) -> p_value
        signals: List of signal names
        p_threshold: Significance threshold
    
    Returns:
        NetworkX DiGraph
    """
    G = nx.DiGraph()
    G.add_nodes_from(signals)
    
    for (source, target), p_value in granger_matrix.items():
        if p_value < p_threshold:
            G.add_edge(source, target, weight=1 - p_value)
    
    return G
```

#### 4.2 PC Algorithm

**What it does**: Constraint-based causal discovery using conditional independence tests.

```python
# Using causal-learn library
def pc_algorithm(df):
    """
    PC Algorithm for causal discovery.
    
    Requires: pip install causal-learn
    """
    from causallearn.search.ConstraintBased.PC import pc
    
    # Prepare data
    signals = [c for c in df.columns if c != 'timestamp']
    data = df[signals].values
    
    # Run PC algorithm
    cg = pc(data, alpha=0.05, indep_test='fisherz')
    
    # Convert to NetworkX
    G = nx.DiGraph()
    G.add_nodes_from(signals)
    
    # Add edges from PC output
    # (cg.G contains the graph)
    
    return G
```

**Note**: PC algorithm returns CPDAG (may have undirected edges)

#### 4.3 LiNGAM

**What it does**: Finds linear causal structure assuming non-Gaussian noise.

```python
def lingam_discovery(df):
    """
    LiNGAM causal discovery.
    
    Requires: pip install lingam
    """
    import lingam
    
    signals = [c for c in df.columns if c != 'timestamp']
    data = df[signals].values
    
    model = lingam.DirectLiNGAM()
    model.fit(data)
    
    # Build graph from adjacency matrix
    G = nx.DiGraph()
    G.add_nodes_from(signals)
    
    adj_matrix = model.adjacency_matrix_
    for i, source in enumerate(signals):
        for j, target in enumerate(signals):
            if adj_matrix[i, j] != 0:
                G.add_edge(source, target, weight=abs(adj_matrix[i, j]))
    
    return G
```

---

## Step 5: Root Cause Ranking

### Goal
Identify and rank the most likely root causes.

### Algorithm Options

#### 5.1 PageRank on Reversed Graph

**What it does**: Ranks nodes by influence, reversed so sources rank high.

```python
import networkx as nx

def rank_by_pagerank(G):
    """
    Rank root causes using PageRank on reversed graph.
    
    Args:
        G: Causal graph (DiGraph)
    
    Returns:
        List of (node, score) tuples, sorted descending
    """
    # Reverse graph: sources become sinks
    G_reversed = G.reverse()
    
    # PageRank
    pagerank = nx.pagerank(G_reversed, alpha=0.85)
    
    # Sort by score
    ranked = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    
    return ranked
```

**Interpretation**: High PageRank = influences many other nodes

#### 5.2 Net Causality Score

**What it does**: Scores nodes by (outgoing influence) - (incoming influence).

```python
def net_causality_score(G):
    """
    Compute net causality score for each node.
    
    Net causality = out_degree - in_degree (weighted)
    """
    scores = {}
    
    for node in G.nodes():
        out_weight = sum(G[node][succ]['weight'] for succ in G.successors(node))
        in_weight = sum(G[pred][node]['weight'] for pred in G.predecessors(node))
        scores[node] = out_weight - in_weight
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked
```

#### 5.3 SHAP Values for Explanation

**What it does**: Explains model predictions in terms of feature contributions.

```python
import shap
import xgboost as xgb

def explain_with_shap(X, y, feature_names):
    """
    Train model and explain with SHAP.
    
    Args:
        X: Feature matrix
        y: Target (e.g., anomaly indicator)
        feature_names: List of feature names
    
    Returns:
        Dict of feature -> mean absolute SHAP value
    """
    model = xgb.XGBClassifier()
    model.fit(X, y)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    # Mean absolute SHAP value per feature
    importance = np.abs(shap_values).mean(axis=0)
    
    return dict(zip(feature_names, importance))
```

---

## Recommended Pipeline Combinations

### Simple but Effective
1. Window: Z-score threshold
2. Clustering: K-Means
3. Temporal: Lagged correlation
4. Graph: Threshold edges by lag
5. Ranking: First to change

### Moderate Complexity
1. Window: PELT change-point
2. Clustering: DBSCAN
3. Temporal: Granger causality
4. Graph: Threshold Granger matrix
5. Ranking: Net causality

### Advanced
1. Window: PELT + CUSUM ensemble
2. Clustering: DTW + hierarchical
3. Temporal: Granger + Transfer entropy
4. Graph: PC algorithm + temporal constraints
5. Ranking: PageRank + SHAP

---

## Library Installation

```bash
# Core
pip install numpy pandas matplotlib scikit-learn

# Change-point detection
pip install ruptures

# Time series clustering
pip install tslearn

# Causality
pip install statsmodels
pip install causal-learn  # PC algorithm
pip install lingam        # LiNGAM

# Graphs
pip install networkx

# Explainability
pip install shap xgboost
```

---

## Further Reading

1. **Change-Point Detection**: Truong et al., "Selective review of offline change point detection methods" (2020)
2. **Granger Causality**: Granger, "Investigating Causal Relations by Econometric Models" (1969)
3. **PC Algorithm**: Spirtes et al., "Causation, Prediction, and Search" (2000)
4. **LiNGAM**: Shimizu et al., "A Linear Non-Gaussian Acyclic Model for Causal Discovery" (2006)
5. **SHAP**: Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions" (2017)
