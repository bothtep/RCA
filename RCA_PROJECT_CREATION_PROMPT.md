# AI Agent Prompt: Create Complete RCA Student Project Package

## Purpose
This prompt instructs an AI agent to generate a complete, production-ready student project package for a Root Cause Analysis (RCA) system. The project is designed for EE 370 (Introduction to Machine Learning) at CSULB, taught by Dr. Mohsen Babaeian. The project serves dual purposes:
1. **Educational**: Teach students end-to-end ML pipeline development
2. **Industry realism**: Mirror real-world constraints and workflows in an applied ML setting

---

## Target Audience Profile

### Students
- **Level**: Undergraduate Junior/Senior (Electrical Engineering)
- **Prerequisites**: 
  - Basic Python programming
  - Linear algebra (matrices, vectors)
  - Probability and statistics fundamentals
- **Tools Proficiency**: Google Colab, NumPy, Pandas, Matplotlib, Scikit-learn, PyTorch
- **AI Agent Experience**: Students are trained to use AI agents for development assistance
- **Team Structure**: Individual or teams of 2-3 students (flexible)
- **Timeline**: 4-8 weeks for project completion
- **Evaluation**: This is a final project worth 30% of course grade

### Key Constraint
Students are NOT familiar with:
- Data pipelines (Kafka, message queues)
- Databases (VictoriaMetrics, PostgreSQL)
- Containerization (Docker, Kubernetes)
- Automotive/vehicle telemetry domain

Therefore, ALL data must be provided as flat files (CSV/JSON) with comprehensive documentation.

---

## The RCA Problem Definition

### Business Context
An industry team is developing an AI-powered platform for vehicle telemetry analysis. A critical feature is **Root Cause Analysis (RCA)** — automatically identifying the root cause of vehicle failures/anomalies from time-series sensor data.

### Technical Problem Statement
Given time-series telemetry data from vehicle sensors surrounding a failure event, build an ML system that:
1. Identifies the incident window
2. Groups related signals by behavior
3. Discovers temporal/causal relationships
4. Constructs a causal graph
5. Ranks and explains the most likely root causes

### The 5-Step RCA Pipeline

#### STEP 1: Incident Window Isolation
**Goal**: Extract the relevant slice of telemetry around the failure moment (t0 ± context window)

**Why It Matters**: RCA is only meaningful when analyzing the few minutes where signals "went weird"

**Technical Approaches**:
| Algorithm | Description | When to Use | Python Library |
|-----------|-------------|-------------|----------------|
| **PELT (Pruned Exact Linear Time)** | Optimal change-point detection | Multiple change points | `ruptures` |
| **Binary Segmentation** | Fast approximate change-point | Large datasets | `ruptures` |
| **BOCPD (Bayesian Online CPD)** | Online/streaming detection | Real-time scenarios | `bayesian_changepoint_detection` |
| **Z-Score Thresholding** | Simple statistical anomaly | Baseline approach | `scipy.stats` |
| **Rolling Statistics** | Moving average deviation | Gradual changes | `pandas` |

**Implementation Details**:
```python
# Example: PELT change-point detection
import ruptures as rpt
import numpy as np

def detect_incident_window(signal: np.ndarray, model: str = "rbf", penalty: float = 10) -> list:
    """
    Detect change points in a signal using PELT algorithm.
    
    Args:
        signal: 1D numpy array of signal values
        model: Cost function model ('rbf', 'l2', 'l1', 'normal', 'ar')
        penalty: Penalty value for adding change points (higher = fewer points)
    
    Returns:
        List of change point indices
    """
    algo = rpt.Pelt(model=model).fit(signal)
    change_points = algo.predict(pen=penalty)
    return change_points
```

**Expected Output**: 
- Start timestamp of incident window
- End timestamp of incident window
- Confidence score (0-1)
- Detected change points within window

#### STEP 2: Cluster Related Signals (Group Behaviors)
**Goal**: Group signals that exhibit similar patterns during the failure

**Why It Matters**: A vehicle has hundreds of signals; clustering reduces dimensionality to meaningful behavioral groups

**Technical Approaches**:
| Algorithm | Description | When to Use | Python Library |
|-----------|-------------|-------------|----------------|
| **K-Means** | Centroid-based clustering | Known number of clusters | `sklearn.cluster` |
| **DBSCAN** | Density-based clustering | Unknown clusters, noise | `sklearn.cluster` |
| **Hierarchical/Agglomerative** | Tree-based clustering | Need dendrogram | `sklearn.cluster` |
| **DTW + K-Medoids** | Time-series specific | Temporal misalignment | `tslearn` |
| **Spectral Clustering** | Graph-based | Non-convex shapes | `sklearn.cluster` |

**Feature Engineering for Clustering**:
```python
def extract_signal_features(signal: np.ndarray) -> dict:
    """
    Extract statistical features from a signal for clustering.
    """
    return {
        'mean': np.mean(signal),
        'std': np.std(signal),
        'min': np.min(signal),
        'max': np.max(signal),
        'range': np.ptp(signal),
        'skewness': scipy.stats.skew(signal),
        'kurtosis': scipy.stats.kurtosis(signal),
        'trend': np.polyfit(range(len(signal)), signal, 1)[0],  # slope
        'autocorr_lag1': np.corrcoef(signal[:-1], signal[1:])[0, 1],
        'zero_crossings': np.sum(np.diff(np.sign(signal - np.mean(signal))) != 0),
        'energy': np.sum(signal ** 2),
        'entropy': scipy.stats.entropy(np.histogram(signal, bins=20)[0] + 1e-10)
    }
```

**Expected Output**:
- Cluster assignments for each signal
- Cluster centroids/representatives
- Cluster quality metrics (silhouette score, Davies-Bouldin index)
- Behavioral labels (e.g., "thermal group", "electrical group")

#### STEP 3: Temporal Relationships & Correlation
**Goal**: Understand which changes LED or LAGGED others

**Why It Matters**: RCA is fundamentally about SEQUENCE — "A happened before B" is not the same as "A and B happened together"

**Technical Approaches**:
| Algorithm | Description | When to Use | Python Library |
|-----------|-------------|-------------|----------------|
| **Lagged Cross-Correlation** | Correlation at time offsets | Finding lead/lag | `numpy`, `scipy.signal` |
| **Granger Causality** | Statistical causality test | Time-series causation | `statsmodels` |
| **Transfer Entropy** | Information-theoretic causality | Non-linear relationships | `pyinform`, `dit` |
| **Dynamic Time Warping** | Similarity with time shifts | Misaligned series | `dtaidistance`, `tslearn` |
| **Vector Autoregression (VAR)** | Multivariate time-series | System dynamics | `statsmodels` |

**Implementation Details**:
```python
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np

def compute_granger_causality(signal_a: np.ndarray, signal_b: np.ndarray, max_lag: int = 10) -> dict:
    """
    Test if signal_a Granger-causes signal_b.
    
    Returns:
        Dictionary with p-values for each lag
    """
    data = np.column_stack([signal_b, signal_a])  # Note: [effect, cause] order
    results = grangercausalitytests(data, maxlag=max_lag, verbose=False)
    
    p_values = {}
    for lag, result in results.items():
        # Use F-test p-value
        p_values[lag] = result[0]['ssr_ftest'][1]
    
    return p_values

def compute_lagged_correlation(signal_a: np.ndarray, signal_b: np.ndarray, max_lag: int = 50) -> tuple:
    """
    Compute cross-correlation and find optimal lag.
    
    Returns:
        (optimal_lag, max_correlation, correlation_array)
    """
    correlation = np.correlate(signal_a - np.mean(signal_a), 
                                signal_b - np.mean(signal_b), 
                                mode='full')
    correlation = correlation / (len(signal_a) * np.std(signal_a) * np.std(signal_b))
    
    lags = np.arange(-len(signal_a) + 1, len(signal_a))
    
    # Find max correlation within lag bounds
    valid_indices = np.where(np.abs(lags) <= max_lag)[0]
    max_idx = valid_indices[np.argmax(np.abs(correlation[valid_indices]))]
    
    return lags[max_idx], correlation[max_idx], correlation
```

**Expected Output**:
- Pairwise lag values (which signal leads which)
- Correlation strengths at optimal lags
- Granger causality p-values matrix
- Temporal ordering of signals (first to change → last to change)

#### STEP 4: Build & Score a Causal Graph
**Goal**: Convert signal relationships into a directed graph representing "A caused B"

**Why It Matters**: Humans think in causes, not correlation matrices. A causal graph is interpretable.

**Technical Approaches**:
| Algorithm | Description | When to Use | Python Library |
|-----------|-------------|-------------|----------------|
| **PC Algorithm** | Constraint-based causal discovery | Linear relationships | `causal-learn`, `pgmpy` |
| **FCI Algorithm** | PC with latent variables | Hidden confounders | `causal-learn` |
| **LiNGAM** | Linear Non-Gaussian Acyclic Model | Non-Gaussian data | `lingam` |
| **NOTEARS** | Continuous optimization DAG | Differentiable approach | `causalnex` |
| **GES (Greedy Equivalence Search)** | Score-based search | BIC/AIC optimization | `causal-learn` |

**Graph Scoring Criteria**:
```python
def score_causal_edge(source_signal: str, target_signal: str, evidence: dict) -> float:
    """
    Score a causal edge based on multiple evidence types.
    
    Evidence dictionary should contain:
        - correlation: lagged correlation value
        - granger_pvalue: Granger causality p-value
        - temporal_order: 1 if source changes before target, 0 otherwise
        - domain_match: 1 if domain knowledge supports this edge, 0 otherwise
        - deviation_magnitude: how much signals deviated from normal
    """
    weights = {
        'correlation': 0.25,
        'granger': 0.25,
        'temporal': 0.30,
        'domain': 0.10,
        'deviation': 0.10
    }
    
    score = 0.0
    
    # Correlation component (higher correlation = higher score)
    score += weights['correlation'] * min(abs(evidence.get('correlation', 0)), 1.0)
    
    # Granger component (lower p-value = higher score)
    granger_p = evidence.get('granger_pvalue', 1.0)
    score += weights['granger'] * (1.0 - min(granger_p, 1.0))
    
    # Temporal order component
    score += weights['temporal'] * evidence.get('temporal_order', 0)
    
    # Domain knowledge component
    score += weights['domain'] * evidence.get('domain_match', 0)
    
    # Deviation magnitude component (normalized)
    score += weights['deviation'] * min(evidence.get('deviation_magnitude', 0) / 3.0, 1.0)
    
    return score
```

**Expected Output**:
- Directed Acyclic Graph (DAG) as adjacency matrix or edge list
- Edge weights/confidence scores
- Graph visualization
- Identified root nodes (no incoming edges)

#### STEP 5: Rank Root Causes & Generate Explanations
**Goal**: Produce a sorted, human-readable list of most likely root causes with explanations

**Why It Matters**: Engineers need actionable ranked list, not raw probabilities

**Technical Approaches**:
| Algorithm | Description | When to Use | Python Library |
|-----------|-------------|-------------|----------------|
| **XGBoost Feature Importance** | Gradient boosted ranking | Large feature sets | `xgboost` |
| **SHAP Values** | Explainable AI | Model interpretability | `shap` |
| **PageRank on Causal Graph** | Graph centrality | Identifying key nodes | `networkx` |
| **Random Forest Importance** | Ensemble feature ranking | Robust importance | `sklearn` |
| **Attention Weights** | Neural network explanation | Deep learning models | `pytorch` |

**Implementation Details**:
```python
import shap
import xgboost as xgb
import networkx as nx

def rank_root_causes_pagerank(causal_graph: nx.DiGraph) -> list:
    """
    Rank nodes using reverse PageRank (sources are most important).
    """
    # Reverse graph so sources have high PageRank
    reversed_graph = causal_graph.reverse()
    pagerank = nx.pagerank(reversed_graph, alpha=0.85)
    
    # Sort by PageRank score descending
    ranked = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    return ranked

def explain_with_shap(model, X_test, feature_names: list) -> dict:
    """
    Generate SHAP explanations for feature contributions.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Average absolute SHAP values per feature
    mean_shap = np.abs(shap_values).mean(axis=0)
    
    explanations = {}
    for i, name in enumerate(feature_names):
        explanations[name] = {
            'importance': mean_shap[i],
            'contribution_direction': 'positive' if shap_values[:, i].mean() > 0 else 'negative'
        }
    
    return explanations

def generate_natural_language_explanation(root_cause: str, evidence: dict) -> str:
    """
    Generate human-readable explanation for a root cause.
    """
    template = (
        f"Root Cause: {root_cause}\n"
        f"Confidence: {evidence['confidence']:.1%}\n"
        f"Evidence:\n"
        f"  - First anomaly detected at: {evidence['first_anomaly_time']}\n"
        f"  - Deviation from normal: {evidence['deviation']:.2f} standard deviations\n"
        f"  - Correlated downstream effects: {', '.join(evidence['downstream_signals'])}\n"
        f"  - Temporal precedence: This signal changed {evidence['lead_time']:.1f} seconds before cascade\n"
    )
    return template
```

**Expected Output**:
- Ranked list of root causes with confidence scores
- Natural language explanations for each
- SHAP/feature importance plots
- Evidence summary for each candidate

---

## Synthetic Data Generation Specification

### Overview
Generate realistic vehicle telemetry data that mimics real-world failure scenarios. Data must be provided as flat files (CSV/JSON) with comprehensive documentation.

### Data Structure

#### 1. Signal Metadata File (`signals_metadata.json`)
```json
{
  "signals": [
    {
      "signal_id": "TEMP_BATTERY_CELL_01",
      "display_name": "Battery Cell 1 Temperature",
      "unit": "°C",
      "subsystem": "battery",
      "normal_range": {"min": 20, "max": 45},
      "critical_range": {"min": -10, "max": 60},
      "sampling_rate_hz": 10,
      "description": "Temperature sensor on battery cell 1",
      "related_signals": ["TEMP_BATTERY_CELL_02", "CURRENT_BATTERY", "VOLTAGE_CELL_01"]
    }
  ]
}
```

#### 2. Telemetry Data Files (`scenario_XX/telemetry.csv`)
```csv
timestamp,TEMP_BATTERY_CELL_01,TEMP_BATTERY_CELL_02,CURRENT_BATTERY,VOLTAGE_CELL_01,...
2024-01-15T10:00:00.000Z,25.3,25.1,45.2,3.92,...
2024-01-15T10:00:00.100Z,25.4,25.1,45.5,3.91,...
```

#### 3. Incident Metadata (`scenario_XX/incident.json`)
```json
{
  "scenario_id": "SCENARIO_001",
  "scenario_name": "Battery Thermal Runaway - Cooling Pump Failure",
  "difficulty": "easy",
  "incident_timestamp": "2024-01-15T10:15:30.000Z",
  "alert_type": "THERMAL_WARNING",
  "alert_severity": "critical",
  "affected_subsystems": ["battery", "cooling"],
  "data_window": {
    "start": "2024-01-15T10:00:00.000Z",
    "end": "2024-01-15T10:30:00.000Z"
  },
  "ground_truth": {
    "root_cause": "PUMP_COOLANT_FLOW",
    "root_cause_display": "Coolant Pump Failure",
    "causal_chain": [
      "PUMP_COOLANT_FLOW",
      "COOLANT_FLOW_RATE",
      "TEMP_BATTERY_CELL_01",
      "TEMP_BATTERY_CELL_02",
      "VOLTAGE_CELL_01",
      "SOC_BATTERY"
    ],
    "root_cause_timestamp": "2024-01-15T10:12:45.000Z",
    "cascade_duration_seconds": 165
  }
}
```

#### 4. Ground Truth Causal Graph (`scenario_XX/causal_graph.json`)
```json
{
  "nodes": ["PUMP_COOLANT_FLOW", "COOLANT_FLOW_RATE", "TEMP_BATTERY_CELL_01", ...],
  "edges": [
    {"source": "PUMP_COOLANT_FLOW", "target": "COOLANT_FLOW_RATE", "lag_seconds": 2.5, "strength": 0.95},
    {"source": "COOLANT_FLOW_RATE", "target": "TEMP_BATTERY_CELL_01", "lag_seconds": 15.0, "strength": 0.88}
  ]
}
```

### Signal Categories (Subsystems)

Generate signals from these vehicle subsystems:

#### Battery Subsystem (12-15 signals)
| Signal ID | Description | Unit | Normal Range |
|-----------|-------------|------|--------------|
| TEMP_BATTERY_CELL_01 to _08 | Cell temperatures | °C | 20-45 |
| VOLTAGE_CELL_01 to _08 | Cell voltages | V | 3.2-4.2 |
| CURRENT_BATTERY | Pack current | A | -200 to 200 |
| SOC_BATTERY | State of charge | % | 10-90 |
| SOH_BATTERY | State of health | % | 80-100 |

#### Cooling/Thermal Subsystem (8-10 signals)
| Signal ID | Description | Unit | Normal Range |
|-----------|-------------|------|--------------|
| PUMP_COOLANT_FLOW | Pump flow rate | L/min | 5-20 |
| COOLANT_FLOW_RATE | Measured flow | L/min | 5-20 |
| TEMP_COOLANT_IN | Inlet temperature | °C | 15-35 |
| TEMP_COOLANT_OUT | Outlet temperature | °C | 20-45 |
| FAN_SPEED_RADIATOR | Fan RPM | RPM | 0-5000 |
| VALVE_THERMAL_POSITION | Thermal valve | % | 0-100 |

#### Motor/Drivetrain Subsystem (10-12 signals)
| Signal ID | Description | Unit | Normal Range |
|-----------|-------------|------|--------------|
| MOTOR_SPEED_RPM | Motor speed | RPM | 0-15000 |
| MOTOR_TORQUE | Torque output | Nm | 0-400 |
| TEMP_MOTOR_STATOR | Stator temp | °C | 30-120 |
| TEMP_MOTOR_ROTOR | Rotor temp | °C | 30-130 |
| CURRENT_MOTOR_PHASE_A/B/C | Phase currents | A | -300 to 300 |
| VIBRATION_MOTOR_X/Y/Z | Vibration axes | g | 0-2 |

#### Electrical Subsystem (6-8 signals)
| Signal ID | Description | Unit | Normal Range |
|-----------|-------------|------|--------------|
| VOLTAGE_HV_BUS | HV bus voltage | V | 300-420 |
| CURRENT_HV_BUS | HV bus current | A | -250 to 250 |
| VOLTAGE_LV_BUS | 12V bus | V | 11.5-14.5 |
| ISOLATION_RESISTANCE | Isolation | kΩ | >500 |
| CONTACTOR_STATE_POS/NEG | Contactor status | bool | 0/1 |

#### Sensor Health (5-6 signals)
| Signal ID | Description | Unit | Normal Range |
|-----------|-------------|------|--------------|
| SENSOR_STATUS_TEMP_XX | Sensor health | enum | 0=OK, 1=WARN, 2=FAIL |
| DATA_QUALITY_SCORE | Overall quality | % | 95-100 |

### Scenario Specifications (15 Scenarios)

Generate these specific failure scenarios with varying difficulty:

#### Easy Scenarios (5) — Single Root Cause, Clear Causation
| ID | Name | Root Cause | Cascade | Duration |
|----|------|------------|---------|----------|
| S01 | Cooling Pump Failure | PUMP_COOLANT_FLOW drops | Coolant→Temps→Voltage | 3 min |
| S02 | Battery Cell Imbalance | VOLTAGE_CELL_03 drifts | Voltage→Current→SOC | 10 min |
| S03 | Motor Overtemperature | TEMP_MOTOR_STATOR rises | Stator→Rotor→Power limit | 5 min |
| S04 | Radiator Fan Failure | FAN_SPEED_RADIATOR = 0 | Fan→Coolant→Battery temp | 8 min |
| S05 | HV Bus Undervoltage | VOLTAGE_HV_BUS drops | HV→Motor limit→Torque | 2 min |

#### Medium Scenarios (5) — Longer Cascades, More Signals
| ID | Name | Root Cause | Complexity |
|----|------|------------|------------|
| S06 | Cascading Thermal Event | Valve stuck + Fan degraded | 2 root causes combine |
| S07 | Intermittent Sensor Fault | TEMP_BATTERY_CELL_05 glitches | Noise handling required |
| S08 | Gradual Motor Bearing Wear | VIBRATION_MOTOR_X increases | Slow drift over window |
| S09 | Electrical Ground Fault | ISOLATION_RESISTANCE drops | Fast cascade (30s) |
| S10 | Multi-cell Battery Degradation | 3 cells degrade together | Correlated multi-source |

#### Hard Scenarios (4) — Ambiguous, Multi-Cause, Noise
| ID | Name | Root Cause | Challenge |
|----|------|------------|-----------|
| S11 | Competing Root Causes | Pump AND Fan fail near-simultaneously | Which caused which? |
| S12 | Hidden Confounder | External temperature spike causes multiple effects | No sensor for actual cause |
| S13 | Delayed Cascade | Root cause → 5 minute delay → Effects | Long lag detection |
| S14 | Noisy Signals + Real Fault | 20% signal noise + actual failure | Signal vs. noise |

#### Control Scenario (1) — No Fault
| ID | Name | Description | Challenge |
|----|------|-------------|-----------|
| S15 | Normal Operation | No actual failure, random variations | Avoid false positives |

### Data Generation Parameters

For each scenario, generate data with these characteristics:

```python
DATA_GENERATION_CONFIG = {
    "sampling_rate_hz": 10,
    "window_duration_minutes": 30,
    "signals_count": 45,  # Total across all subsystems
    
    # Normal operation baseline
    "noise_level_percent": 2.0,  # Signal noise as % of range
    "drift_rate_per_hour": 0.5,  # Slow natural drift
    
    # Anomaly injection
    "anomaly_types": {
        "step_change": {"magnitude_std": 3.0},  # Sudden jump
        "ramp": {"rate_per_minute": 0.5},  # Gradual increase
        "spike": {"magnitude_std": 5.0, "duration_samples": 10},
        "oscillation": {"frequency_hz": 0.5, "amplitude_std": 2.0},
        "dropout": {"probability": 0.01}  # Missing values
    },
    
    # Causal propagation
    "propagation_delay_seconds": {"min": 1.0, "max": 30.0},
    "propagation_attenuation": 0.85,  # Downstream effect is 85% of cause
    
    # Ground truth precision
    "root_cause_timestamp_precision_ms": 100
}
```

### Data Quality Requirements
- **No missing values in core signals** (except intentional dropouts in S14)
- **Timestamps are monotonically increasing**
- **All signals normalized to realistic physical ranges**
- **Ground truth is unambiguous for Easy/Medium scenarios**
- **Causal chains are physically plausible**

---

## Baseline Implementations

Provide three baseline implementations for students to compare against:

### Baseline 1: Naive Correlation (Weak Baseline)
```python
"""
Baseline 1: Simple correlation-based root cause identification.
Does NOT consider temporal order — just finds highest correlated signal to alert.
Expected performance: ~30-40% accuracy
"""

def naive_correlation_baseline(telemetry_df, alert_signal):
    correlations = {}
    for col in telemetry_df.columns:
        if col != alert_signal and col != 'timestamp':
            corr = telemetry_df[col].corr(telemetry_df[alert_signal])
            correlations[col] = abs(corr)
    
    ranked = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    return [signal for signal, _ in ranked[:5]]
```

### Baseline 2: Z-Score + Temporal Order (Medium Baseline)
```python
"""
Baseline 2: Z-score anomaly detection with temporal ordering.
Identifies anomalous signals and ranks by which changed first.
Expected performance: ~55-65% accuracy
"""

def zscore_temporal_baseline(telemetry_df, window_before_alert_minutes=5):
    # Calculate z-scores
    z_scores = (telemetry_df - telemetry_df.mean()) / telemetry_df.std()
    
    # Find first anomaly time for each signal (|z| > 3)
    first_anomaly_times = {}
    for col in z_scores.columns:
        if col == 'timestamp':
            continue
        anomaly_mask = abs(z_scores[col]) > 3
        if anomaly_mask.any():
            first_idx = anomaly_mask.idxmax()
            first_anomaly_times[col] = telemetry_df.loc[first_idx, 'timestamp']
    
    # Rank by earliest anomaly
    ranked = sorted(first_anomaly_times.items(), key=lambda x: x[1])
    return [signal for signal, _ in ranked[:5]]
```

### Baseline 3: Clustering + Granger (Strong Baseline)
```python
"""
Baseline 3: Cluster signals, then use Granger causality on cluster representatives.
Expected performance: ~70-80% accuracy
Students should aim to beat this.
"""

def clustering_granger_baseline(telemetry_df, n_clusters=5):
    from sklearn.cluster import KMeans
    from statsmodels.tsa.stattools import grangercausalitytests
    
    # Extract features and cluster
    features = extract_all_features(telemetry_df)
    kmeans = KMeans(n_clusters=n_clusters)
    clusters = kmeans.fit_predict(features)
    
    # Get cluster representatives (closest to centroid)
    representatives = get_cluster_representatives(telemetry_df, clusters, kmeans)
    
    # Granger causality between representatives
    causality_scores = compute_pairwise_granger(representatives)
    
    # Rank by "most causal" (causes others but not caused by others)
    return rank_by_net_causality(causality_scores)
```

---

## Evaluation Framework

### Metrics

#### 1. Root Cause Accuracy (Primary Metric)
```python
def root_cause_accuracy(predicted_root_cause: str, ground_truth_root_cause: str) -> float:
    """Binary: 1.0 if exact match, 0.0 otherwise"""
    return 1.0 if predicted_root_cause == ground_truth_root_cause else 0.0
```

#### 2. Top-K Recall
```python
def top_k_recall(predicted_ranked_list: list, ground_truth_root_cause: str, k: int = 3) -> float:
    """1.0 if ground truth is in top-k predictions, 0.0 otherwise"""
    return 1.0 if ground_truth_root_cause in predicted_ranked_list[:k] else 0.0
```

#### 3. Mean Reciprocal Rank (MRR)
```python
def mean_reciprocal_rank(predicted_ranked_list: list, ground_truth_root_cause: str) -> float:
    """1/rank if found, 0 otherwise"""
    try:
        rank = predicted_ranked_list.index(ground_truth_root_cause) + 1
        return 1.0 / rank
    except ValueError:
        return 0.0
```

#### 4. Causal Graph Edge F1
```python
def causal_graph_f1(predicted_edges: set, ground_truth_edges: set) -> dict:
    """Precision, Recall, F1 for causal graph edges"""
    true_positives = len(predicted_edges & ground_truth_edges)
    precision = true_positives / len(predicted_edges) if predicted_edges else 0
    recall = true_positives / len(ground_truth_edges) if ground_truth_edges else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return {'precision': precision, 'recall': recall, 'f1': f1}
```

#### 5. Incident Window IoU (Intersection over Union)
```python
def window_iou(predicted_start, predicted_end, actual_start, actual_end) -> float:
    """How well did they identify the incident window?"""
    intersection_start = max(predicted_start, actual_start)
    intersection_end = min(predicted_end, actual_end)
    intersection = max(0, intersection_end - intersection_start)
    
    union = (predicted_end - predicted_start) + (actual_end - actual_start) - intersection
    return intersection / union if union > 0 else 0
```

### Scoring Rubric

| Component | Weight | Criteria |
|-----------|--------|----------|
| **Root Cause Accuracy** | 30% | % of scenarios with correct #1 root cause |
| **Top-3 Recall** | 15% | % of scenarios with correct root cause in top 3 |
| **Causal Graph F1** | 20% | Average F1 across all scenarios |
| **Window Detection IoU** | 10% | Average IoU across all scenarios |
| **Code Quality** | 15% | Modularity, documentation, testing |
| **Explanation Quality** | 10% | Clarity of generated explanations |

### Expected Performance Thresholds

| Grade | Root Cause Acc | Top-3 Recall | Graph F1 |
|-------|---------------|--------------|----------|
| A (90%+) | >80% | >95% | >0.75 |
| B (80-89%) | >65% | >85% | >0.60 |
| C (70-79%) | >50% | >70% | >0.45 |
| D (60-69%) | >35% | >55% | >0.30 |
| F (<60%) | <35% | <55% | <0.30 |

---

## Deliverables Specification

### Required Student Deliverables

#### 1. Source Code (`/src/`)
```
src/
├── __init__.py
├── step1_window_detection.py
├── step2_signal_clustering.py
├── step3_temporal_analysis.py
├── step4_causal_graph.py
├── step5_ranking_explanation.py
├── pipeline.py              # End-to-end orchestration
├── utils/
│   ├── data_loader.py
│   ├── visualization.py
│   └── metrics.py
└── tests/
    ├── test_step1.py
    ├── test_step2.py
    └── test_integration.py
```

#### 2. Jupyter Notebooks (`/notebooks/`)
```
notebooks/
├── 01_data_exploration.ipynb
├── 02_step_by_step_demo.ipynb
├── 03_evaluation_results.ipynb
└── 04_ablation_studies.ipynb
```

#### 3. Documentation (`/docs/`)
```
docs/
├── APPROACH.md             # Algorithm selection rationale
├── ARCHITECTURE.md         # System design
├── RESULTS.md              # Performance analysis
└── FUTURE_WORK.md          # Limitations and improvements
```

#### 4. Results (`/results/`)
```
results/
├── scenario_results.json   # Predictions for all scenarios
├── metrics_summary.csv     # Aggregated metrics
├── causal_graphs/          # Generated graphs (PNG/JSON)
└── explanations/           # Generated explanations
```

### Documentation Requirements

#### APPROACH.md Must Include:
1. **Algorithm Selection**: Why they chose each algorithm for each step
2. **Alternatives Considered**: What else they evaluated and why they rejected it
3. **Hyperparameter Tuning**: How they selected parameters
4. **Trade-offs**: What compromises they made and why

#### ARCHITECTURE.md Must Include:
1. **System Diagram**: Visual representation of their pipeline
2. **Data Flow**: How data moves through each step
3. **Dependencies**: What libraries and why
4. **Computational Complexity**: Big-O analysis of their approach

---

## Project Package File Structure

Create this complete file structure:

```
Student Project Folder/
├── README.md                           # Project overview and getting started
├── PROJECT_DESCRIPTION.md              # Formal project requirements
├── GRADING_RUBRIC.md                   # Detailed scoring criteria
│
├── data/
│   ├── signals_metadata.json           # Signal definitions
│   ├── domain_knowledge.json           # Subsystem relationships
│   │
│   ├── scenario_01_easy/
│   │   ├── telemetry.csv               # Time-series data
│   │   ├── incident.json               # Scenario metadata
│   │   └── ground_truth.json           # Causal graph + root cause
│   │
│   ├── scenario_02_easy/
│   │   └── ...
│   │
│   ├── ... (scenarios 01-15)
│   │
│   └── scenario_15_control/
│       └── ...
│
├── baselines/
│   ├── baseline_1_naive.py             # Weak baseline
│   ├── baseline_2_zscore.py            # Medium baseline
│   ├── baseline_3_granger.py           # Strong baseline
│   └── run_baselines.py                # Execute all baselines
│
├── evaluation/
│   ├── evaluate.py                     # Main evaluation script
│   ├── metrics.py                      # Metric implementations
│   └── expected_results.json           # Baseline performance for comparison
│
├── starter_code/
│   ├── data_loader.py                  # Load and parse data files
│   ├── visualization.py                # Plotting utilities
│   ├── pipeline_template.py            # Skeleton pipeline structure
│   └── sample_notebook.ipynb           # Getting started notebook
│
├── reference/
│   ├── RCA_ALGORITHM_GUIDE.md          # Detailed algorithm explanations
│   ├── VEHICLE_DOMAIN_PRIMER.md        # Vehicle systems overview
│   ├── SIGNAL_REFERENCE.md             # Complete signal documentation
│   └── PAPER_REFERENCES.md             # Academic papers for each technique
│
└── submission_template/
    ├── src/                            # Where students put code
    ├── notebooks/                      # Where students put notebooks
    ├── docs/                           # Where students put documentation
    └── results/                        # Where students put outputs
```

---

## Detailed File Content Specifications

### README.md Content
```markdown
# Root Cause Analysis (RCA) Project
## EE 370 Final Project - Fall 2024

### Overview
Build an end-to-end ML system that identifies root causes of vehicle failures from sensor telemetry data.

### Quick Start
1. Clone this repository
2. Open `starter_code/sample_notebook.ipynb` in Google Colab
3. Run all cells to verify data loading works
4. Read `PROJECT_DESCRIPTION.md` for full requirements

### Project Structure
[File tree here]

### Timeline
- Week 1-2: Data exploration, algorithm research
- Week 3-4: Steps 1-3 implementation
- Week 5-6: Steps 4-5 implementation
- Week 7-8: Integration, testing, documentation

### Submission
Submit via [TBD] by [TBD date]
```

### PROJECT_DESCRIPTION.md Content
Follow the format from the sample course document but focused on RCA:
- Problem statement
- Learning objectives aligned to ABET outcomes
- Technical requirements for each step
- Deliverables checklist
- Grading breakdown

### VEHICLE_DOMAIN_PRIMER.md Content
- Explain battery electric vehicle architecture
- Describe each subsystem and how they interact
- Common failure modes in EVs
- Physical relationships between signals (e.g., "when pump fails, flow drops, temperature rises")

---

## Data Generation Implementation Notes

### Signal Generation Algorithm
```python
def generate_scenario_data(config: dict) -> pd.DataFrame:
    """
    Generate synthetic telemetry data for a scenario.
    
    Steps:
    1. Generate baseline normal operation for all signals
    2. Inject root cause anomaly at specified time
    3. Propagate effects through causal graph with delays
    4. Add realistic noise
    5. Return complete dataframe
    """
    
    # 1. Normal operation baseline
    n_samples = config['duration_minutes'] * 60 * config['sampling_rate_hz']
    timestamps = pd.date_range(
        start=config['start_time'],
        periods=n_samples,
        freq=f"{1000//config['sampling_rate_hz']}ms"
    )
    
    data = {'timestamp': timestamps}
    for signal in config['signals']:
        data[signal['id']] = generate_normal_signal(
            n_samples, 
            signal['normal_mean'], 
            signal['normal_std'],
            signal['noise_level']
        )
    
    # 2. Inject root cause
    root_cause_idx = timestamp_to_index(config['root_cause_time'], timestamps)
    data[config['root_cause_signal']] = inject_anomaly(
        data[config['root_cause_signal']],
        start_idx=root_cause_idx,
        anomaly_type=config['anomaly_type'],
        magnitude=config['anomaly_magnitude']
    )
    
    # 3. Propagate through causal graph
    for edge in config['causal_edges']:
        source_data = data[edge['source']]
        lag_samples = int(edge['lag_seconds'] * config['sampling_rate_hz'])
        attenuation = edge['attenuation']
        
        # Apply lagged, attenuated effect to target
        data[edge['target']] = propagate_effect(
            data[edge['target']],
            source_data,
            lag_samples,
            attenuation
        )
    
    # 4. Add noise
    for signal_id in data:
        if signal_id != 'timestamp':
            noise_level = config['signals_map'][signal_id]['noise_level']
            data[signal_id] = add_gaussian_noise(data[signal_id], noise_level)
    
    return pd.DataFrame(data)
```

### Causal Graph Definition for Each Scenario
Define explicit causal graphs that data generation follows:

```python
SCENARIO_01_CAUSAL_GRAPH = {
    "root_cause": "PUMP_COOLANT_FLOW",
    "edges": [
        {"source": "PUMP_COOLANT_FLOW", "target": "COOLANT_FLOW_RATE", "lag": 2.0, "attn": 0.95},
        {"source": "COOLANT_FLOW_RATE", "target": "TEMP_COOLANT_OUT", "lag": 10.0, "attn": 0.85},
        {"source": "TEMP_COOLANT_OUT", "target": "TEMP_BATTERY_CELL_01", "lag": 15.0, "attn": 0.80},
        {"source": "TEMP_BATTERY_CELL_01", "target": "TEMP_BATTERY_CELL_02", "lag": 5.0, "attn": 0.90},
        {"source": "TEMP_BATTERY_CELL_01", "target": "VOLTAGE_CELL_01", "lag": 30.0, "attn": 0.70},
        # ... more edges
    ]
}
```

---

## Quality Assurance Checklist

Before finalizing the package, verify:

### Data Quality
- [ ] All CSV files load without errors in Pandas
- [ ] No NaN values except intentional (S14)
- [ ] Timestamps are monotonic and properly formatted
- [ ] Signal values are within physical ranges
- [ ] Ground truth is correct for each scenario

### Code Quality
- [ ] All Python files pass `python -m py_compile`
- [ ] Baselines run without errors
- [ ] Evaluation script produces expected output
- [ ] Starter notebook runs in Google Colab

### Documentation Quality
- [ ] README provides clear getting-started path
- [ ] All algorithms are explained at appropriate level
- [ ] Domain primer is understandable to non-automotive students
- [ ] Grading rubric leaves no ambiguity

### Pedagogical Quality
- [ ] Difficulty progression is appropriate
- [ ] Easy scenarios are solvable with course knowledge
- [ ] Hard scenarios require creativity/research
- [ ] Control scenario prevents trivial solutions

---

## Additional Context for AI Agent

### Course Context
- This is for EE 370 at CSULB
- Students have completed weeks 1-13 of the syllabus
- They know: supervised/unsupervised learning, neural networks, PyTorch, AI agents
- They use Google Colab for all work
- AI assistance is explicitly permitted
- 30% of final grade depends on this project

### Startup Context
- The problem is real — simplified version of production RCA
- Students should be told this is a real industry problem

### What Makes a Great Solution
1. **Goes beyond baselines** — doesn't just copy baseline code
2. **Novel combinations** — creatively combines techniques
3. **Robust to noise** — handles S14 well
4. **Clear explanations** — produces interpretable outputs
5. **Well-documented** — code and decisions are explained
6. **Tested** — includes unit tests and validation

---

## Execution Instructions for AI Agent

1. **Create all directories** as specified in file structure
2. **Generate all data files** following the specifications
3. **Implement all baseline code** that runs correctly
4. **Write all documentation** in clear, student-friendly language
5. **Create evaluation script** that matches grading rubric
6. **Generate starter notebook** that demonstrates data loading and basic visualization
7. **Verify everything works** end-to-end

**Total estimated files**: ~50 files
**Total estimated lines of code**: ~3000 lines
**Total estimated documentation**: ~5000 words

---

## End of Prompt

This prompt contains all specifications needed to generate a complete RCA student project package. The AI agent should create production-ready materials suitable for undergraduate engineering students with ML background.
