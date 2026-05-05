# EE 370 Final Project: Root Cause Analysis for Vehicle Telemetry

## Course Information

- **Course**: EE 370 - Introduction to Machine Learning with Python, PyTorch, and AI Agents
- **Institution**: California State University, Long Beach (CSULB)
- **Instructor**: Dr. Mohsen Babaeian
- **Project Weight**: 30% of final grade
- **Duration**: 4-8 weeks

---

## Project Overview

### Problem Statement

Electric vehicles generate thousands of sensor readings per second. When something goes wrong, engineers must sift through this data to find the root cause - a process that traditionally takes hours or days.

Your challenge is to build an **automated Root Cause Analysis (RCA) system** that can:
- Detect when an anomaly occurred
- Identify which component failed first
- Trace the cascade of effects through the vehicle systems
- Explain the findings in a way that engineers can act on

### Real-World Context

This project is based on actual industry problems. Companies monitoring vehicle fleets use similar techniques to:
- Diagnose failures before vehicles are towed
- Predict maintenance needs
- Improve vehicle designs based on failure patterns
- Reduce warranty costs through early detection

### Industry Partner

This project is inspired by real-world industry problems in AI-powered vehicle analytics.

---

## Learning Objectives

By completing this project, you will:

1. **Apply ML algorithms** to real-world time-series data
2. **Implement a multi-step pipeline** integrating multiple techniques
3. **Use causal inference** methods beyond simple correlation
4. **Evaluate and compare** different algorithmic approaches
5. **Communicate technical results** through documentation and visualizations
6. **Work with domain knowledge** in an unfamiliar field (vehicle systems)

### ABET Outcomes Alignment

| Outcome | How This Project Addresses It |
|---------|------------------------------|
| 1. Problem Solving | Apply ML to complex engineering diagnosis problem |
| 2. Design | Design an end-to-end analysis pipeline |
| 3. Communication | Document approach and explain findings |
| 6. Experimentation | Test algorithms on multiple scenarios |
| 7. Modern Tools | Use Python ML libraries and AI assistants |

---

## Technical Requirements

### The 5-Step RCA Pipeline

Your solution must implement these five analysis steps:

#### Step 1: Incident Window Isolation

**Goal**: Identify the time period where the anomaly occurred.

**Requirements**:
- Detect change points or anomaly onset
- Define start/end of analysis window
- Handle cases with no anomaly (control scenario)

**Suggested Approaches**:
- Change-point detection (PELT, Binary Segmentation)
- Z-score thresholding with rolling windows
- Statistical process control (CUSUM)

**Deliverable**: Function that returns (start_index, end_index) for incident window

#### Step 2: Signal Clustering

**Goal**: Group signals that exhibit similar behavior patterns.

**Requirements**:
- Extract meaningful features from time series
- Cluster signals into behavioral groups
- Interpret clusters in domain context

**Suggested Approaches**:
- K-Means on statistical features
- DBSCAN for density-based clustering
- Hierarchical clustering with dendrogram
- DTW-based similarity with k-medoids

**Deliverable**: Dictionary mapping signal_id → cluster_id

#### Step 3: Temporal Relationship Analysis

**Goal**: Determine temporal ordering and causal relationships between signals.

**Requirements**:
- Identify which signals changed first
- Compute lagged correlations
- Test for Granger causality

**Suggested Approaches**:
- Lagged cross-correlation analysis
- Granger causality tests
- Transfer entropy
- Vector autoregression (VAR)

**Deliverable**: 
- First anomaly time for each signal
- Pairwise lag matrix
- Causality evidence scores

#### Step 4: Causal Graph Construction

**Goal**: Build a directed graph representing cause-effect relationships.

**Requirements**:
- Create nodes for relevant signals
- Add directed edges with confidence scores
- Ensure graph is consistent with temporal ordering

**Suggested Approaches**:
- Threshold Granger causality matrix
- PC Algorithm for constraint-based discovery
- LiNGAM for linear non-Gaussian models
- Domain knowledge integration

**Deliverable**: Graph structure with nodes and weighted edges

#### Step 5: Root Cause Ranking & Explanation

**Goal**: Identify and explain the most likely root cause.

**Requirements**:
- Rank all candidate signals by likelihood
- Generate confidence scores
- Provide human-readable explanations

**Suggested Approaches**:
- PageRank on reversed causal graph
- Net causality scoring (causes others - caused by others)
- Feature importance from tree models
- SHAP values for explainability

**Deliverable**:
- Ranked list of candidates with scores
- Natural language explanation for top candidates

---

## Data Specification

### Telemetry Format

Each scenario includes:

1. **telemetry.csv**: Time-series sensor data
   - `timestamp`: ISO 8601 format
   - 44 signal columns (see signals_metadata.json)
   - 10 Hz sampling rate
   - 30 minutes of data per scenario

2. **incident.json**: Scenario metadata
   - Scenario name and difficulty
   - Alert type and severity
   - Affected subsystems

3. **ground_truth.json**: Evaluation reference
   - Actual root cause signal
   - Causal chain with timing
   - Causal graph edges

### Signal Categories

| Subsystem | Signals | Examples |
|-----------|---------|----------|
| Battery | 19 | Cell temperatures, voltages, SOC, SOH |
| Cooling | 8 | Pump flow, coolant temps, fan speed |
| Motor | 10 | Speed, torque, temps, vibration |
| Electrical | 6 | HV bus, isolation, contactors |
| Sensor Health | 1 | Data quality score |

### Scenarios

| ID | Name | Difficulty | Challenge |
|----|------|------------|-----------|
| 01 | Cooling Pump Failure | Easy | Clear cascade |
| 02 | Battery Cell Imbalance | Easy | Gradual drift |
| 03 | Motor Overtemperature | Easy | Sustained load |
| 04 | Radiator Fan Failure | Easy | Thermal cascade |
| 05 | HV Bus Undervoltage | Easy | Electrical issue |
| 06 | Cascading Thermal | Medium | Multiple effects |
| 07 | Intermittent Sensor | Medium | False alarm trap |
| 08 | Motor Bearing Wear | Medium | Gradual onset |
| 09 | Ground Fault | Medium | Fast cascade |
| 10 | Multi-cell Degradation | Medium | Correlated causes |
| 11 | Competing Causes | Hard | Ambiguous timing |
| 12 | Hidden Confounder | Hard | External cause |
| 13 | Delayed Cascade | Hard | Long lag |
| 14 | Noisy Signals | Hard | Signal vs noise |
| 15 | Normal Operation | Control | No fault |

---

## Deliverables

### Code Deliverables

Place in `submission_template/src/`:

```python
# Required files:
step1_window_detection.py    # Incident window isolation
step2_signal_clustering.py   # Signal clustering
step3_temporal_analysis.py   # Temporal relationships
step4_causal_graph.py        # Causal graph construction
step5_ranking_explanation.py # Root cause ranking
pipeline.py                  # End-to-end orchestration

# Supporting files:
utils/
    data_loader.py           # Data loading utilities
    visualization.py         # Plotting functions
    metrics.py               # Evaluation metrics

tests/                       # Unit tests (optional but encouraged)
```

### Notebook Deliverables

Place in `submission_template/notebooks/`:

1. **01_data_exploration.ipynb**: Exploratory data analysis
2. **02_step_by_step_demo.ipynb**: Walkthrough of your approach
3. **03_evaluation_results.ipynb**: Results on all scenarios
4. **04_ablation_studies.ipynb**: (Optional) Algorithm comparisons

### Documentation Deliverables

Place in `submission_template/docs/`:

#### APPROACH.md (Required)

Must include:
- Algorithm selection rationale for each step
- Alternatives you considered and why rejected
- Hyperparameter tuning approach
- Trade-offs and limitations

#### ARCHITECTURE.md (Required)

Must include:
- System diagram of your pipeline
- Data flow description
- Dependencies and libraries used
- Computational complexity analysis

### Results Deliverables

Place in `submission_template/results/`:

1. **scenario_results.json**: Predictions for all 15 scenarios

```json
{
  "scenario_01_easy": {
    "root_cause": "PUMP_COOLANT_FLOW",
    "confidence": 0.92,
    "ranked_candidates": [
      {"signal": "PUMP_COOLANT_FLOW", "score": 0.92},
      {"signal": "COOLANT_FLOW_RATE", "score": 0.78}
    ],
    "causal_graph": {
      "nodes": ["PUMP_COOLANT_FLOW", "COOLANT_FLOW_RATE"],
      "edges": [{"source": "PUMP_COOLANT_FLOW", "target": "COOLANT_FLOW_RATE", "weight": 0.9}]
    },
    "incident_window": {"start_idx": 7500, "end_idx": 15000}
  }
}
```

2. **metrics_summary.csv**: Aggregated metrics
3. **causal_graphs/**: Visualization images
4. **explanations/**: Generated explanations

---

## Evaluation Criteria

### Grading Breakdown

| Component | Weight | Description |
|-----------|--------|-------------|
| Root Cause Accuracy | 30% | Percentage of correct #1 predictions |
| Top-3 Recall | 15% | Correct answer in top 3 |
| Causal Graph Quality | 20% | Precision, Recall, F1 on edges |
| Window Detection | 10% | IoU with actual incident window |
| Code Quality | 15% | Clean, modular, documented |
| Explanation Quality | 10% | Clear, informative explanations |

### Performance Thresholds

| Grade | Root Cause Acc | Top-3 Recall | Graph F1 |
|-------|---------------|--------------|----------|
| A (≥90%) | ≥80% | ≥95% | ≥0.75 |
| B (80-89%) | ≥65% | ≥85% | ≥0.60 |
| C (70-79%) | ≥50% | ≥70% | ≥0.45 |
| D (60-69%) | ≥35% | ≥55% | ≥0.30 |
| F (<60%) | <35% | <55% | <0.30 |

### Baseline Reference

Your solution should beat at least the medium baseline:

| Baseline | Root Cause Acc | Description |
|----------|---------------|-------------|
| Naive Correlation | ~35% | Simple correlation |
| Z-Score Temporal | ~60% | First-to-change ranking |
| Clustering + Granger | ~75% | Target to beat |

---

## Technical Constraints

### Allowed Tools

- **Languages**: Python 3.10+
- **Libraries**: Any open-source library (NumPy, Pandas, Scikit-learn, NetworkX, etc.)
- **AI Assistants**: Permitted for coding help (must understand all code)
- **Environment**: Google Colab or local Python

### Not Allowed

- Hardcoding ground truth values
- Using test data during training
- Submitting code you cannot explain

---

## Timeline

### Suggested Schedule

| Week | Focus | Milestone |
|------|-------|-----------|
| 1-2 | Exploration | Understand data, try baselines |
| 3-4 | Steps 1-3 | Window detection, clustering, temporal |
| 5-6 | Steps 4-5 | Causal graph, ranking |
| 7 | Integration | Complete pipeline, evaluate |
| 8 | Documentation | Write docs, prepare submission |

### Checkpoints

- **Week 2**: Data exploration notebook complete
- **Week 4**: Steps 1-3 implemented and tested
- **Week 6**: Full pipeline running
- **Week 8**: Final submission

---

## Submission Instructions

1. **Package** your `submission_template/` folder
2. **Verify** all required files are present
3. **Run** evaluation script to confirm it works
4. **Submit** via [TBD method]
5. **Due**: [TBD date]

### Submission Checklist

- [ ] All 5 step implementations complete
- [ ] Pipeline runs without errors
- [ ] Results JSON generated for all scenarios
- [ ] APPROACH.md explains algorithm choices
- [ ] ARCHITECTURE.md documents system design
- [ ] Code is clean and commented
- [ ] Notebooks demonstrate your process

---

## Academic Integrity

- AI assistants are permitted for coding assistance
- You must understand and be able to explain all submitted code
- Oral explanations or live demonstrations may be required
- Copying from other students is not permitted
- Cite any external resources used

---

## Getting Help

### Resources

- **Starter Code**: `starter_code/` directory
- **Algorithm Guide**: `reference/RCA_ALGORITHM_GUIDE.md`
- **Domain Primer**: `reference/VEHICLE_DOMAIN_PRIMER.md`
- **Baselines**: Compare your results

### Office Hours

[TBD - Instructor office hours]

### Questions

Post questions on [TBD - course forum/Slack]

---

Good luck! This is a challenging project that will develop skills directly applicable to industry careers in ML and data science.
