# Root Cause Analysis (RCA) Project

## EE 370 Final Project - Machine Learning for Vehicle Telemetry Analysis

### Overview

This project challenges you to build an end-to-end **Root Cause Analysis (RCA)** system that automatically identifies the root cause of vehicle failures from sensor telemetry data.

This is a real industry problem - simplified from production systems used in electric vehicle monitoring. Companies like Tesla, Rivian, and specialized fleet operators use similar approaches to diagnose vehicle issues remotely.

### Quick Start

1. **Clone/Download** this project folder
2. **Open** `starter_code/sample_notebook.ipynb` in Google Colab or Jupyter
3. **Run** all cells to verify data loading works
4. **Read** `PROJECT_DESCRIPTION.md` for full requirements
5. **Start** implementing your solution!

### Project Structure

```
├── README.md                    # This file
├── PROJECT_DESCRIPTION.md       # Full project requirements
├── GRADING_RUBRIC.md           # Detailed grading criteria
│
├── data/                        # Scenario data
│   ├── signals_metadata.json    # Signal definitions
│   ├── domain_knowledge.json    # Domain relationships
│   ├── scenario_01_easy/        # Easy scenarios (1-5)
│   ├── scenario_06_medium/      # Medium scenarios (6-10)
│   ├── scenario_11_hard/        # Hard scenarios (11-14)
│   └── scenario_15_control/     # Control scenario (no fault)
│
├── baselines/                   # Reference implementations
│   ├── baseline_1_naive.py      # Weak baseline (~35% accuracy)
│   ├── baseline_2_zscore.py     # Medium baseline (~60% accuracy)
│   ├── baseline_3_granger.py    # Strong baseline (~75% accuracy)
│   └── run_baselines.py         # Run all baselines
│
├── evaluation/                  # Evaluation tools
│   ├── evaluate.py              # Main evaluation script
│   ├── metrics.py               # Metric implementations
│   └── expected_results.json    # Baseline performance reference
│
├── starter_code/                # Helper code for students
│   ├── data_loader.py           # Load scenario data
│   ├── visualization.py         # Plotting utilities
│   ├── pipeline_template.py     # RCA pipeline skeleton
│   └── sample_notebook.ipynb    # Getting started notebook
│
├── reference/                   # Learning materials
│   ├── RCA_ALGORITHM_GUIDE.md   # Algorithm explanations
│   ├── VEHICLE_DOMAIN_PRIMER.md # Vehicle systems overview
│   └── SIGNAL_REFERENCE.md      # Signal documentation
│
└── submission_template/         # Where to put your solution
    ├── src/                     # Your code
    ├── notebooks/               # Your notebooks
    ├── docs/                    # Your documentation
    └── results/                 # Your outputs
```

### The Challenge

Given 30 minutes of vehicle telemetry data (44 signals sampled at 10 Hz), identify:

1. **When** the incident started
2. **Which** signal is the root cause
3. **How** the failure cascaded through the system
4. **Why** you believe this is the root cause

### The 5-Step RCA Pipeline

Your solution should implement these 5 steps:

| Step | Goal | Example Algorithms |
|------|------|-------------------|
| 1. Window Isolation | Find when the anomaly started | PELT, Z-score |
| 2. Signal Clustering | Group related behaviors | K-Means, DBSCAN |
| 3. Temporal Analysis | Who changed first? | Lagged correlation, Granger |
| 4. Causal Graph | Build cause-effect model | PC Algorithm, LiNGAM |
| 5. Root Cause Ranking | Identify and explain | PageRank, SHAP |

### Scenarios

| Difficulty | Count | Description |
|------------|-------|-------------|
| Easy | 5 | Single root cause, clear cascade |
| Medium | 5 | Longer chains, more signals involved |
| Hard | 4 | Ambiguous cases, competing causes |
| Control | 1 | No fault - avoid false positives |

### Evaluation

Your solution will be evaluated on:

- **Root Cause Accuracy** (30%) - Did you identify the correct root cause?
- **Top-3 Recall** (15%) - Was the correct answer in your top 3?
- **Causal Graph Quality** (20%) - How well did you capture relationships?
- **Code Quality** (15%) - Is your code clean and documented?
- **Explanation Quality** (10%) - Are your explanations clear?
- **Window Detection** (10%) - Did you find the right time window?

### Grade Thresholds

| Grade | Root Cause Accuracy | Top-3 Recall |
|-------|--------------------:|-------------:|
| A | ≥80% | ≥95% |
| B | ≥65% | ≥85% |
| C | ≥50% | ≥70% |
| D | ≥35% | ≥55% |

### Resources

- **Starter Notebook**: `starter_code/sample_notebook.ipynb`
- **Algorithm Guide**: `reference/RCA_ALGORITHM_GUIDE.md`
- **Domain Primer**: `reference/VEHICLE_DOMAIN_PRIMER.md`
- **Baselines**: Run `python baselines/run_baselines.py` to see baseline performance

### Submission

Place your solution in the `submission_template/` folder:

```
submission_template/
├── src/                    # Your Python code
├── notebooks/              # Your Jupyter notebooks
├── docs/
│   ├── APPROACH.md         # Your algorithm choices
│   └── ARCHITECTURE.md     # Your system design
└── results/
    └── scenario_results.json  # Your predictions
```

### Timeline Suggestion

- **Week 1-2**: Data exploration, algorithm research
- **Week 3-4**: Implement Steps 1-3
- **Week 5-6**: Implement Steps 4-5
- **Week 7-8**: Integration, testing, documentation

### Tips for Success

1. **Start with easy scenarios** - Get those working first
2. **Visualize everything** - Use the plotting utilities
3. **Beat the baselines** - Compare your results to reference implementations
4. **Document decisions** - Explain why you chose each algorithm
5. **Test incrementally** - Don't wait until the end to evaluate

### Getting Help

- Use AI assistants (ChatGPT, Claude, Copilot) for coding help
- You must understand and be able to explain all code you submit
- Reference the algorithm guide for implementation details

Good luck! This is a challenging but rewarding project that mirrors real industry problems.

---

*This project is inspired by real-world industry problems in AI-powered vehicle analytics.*
