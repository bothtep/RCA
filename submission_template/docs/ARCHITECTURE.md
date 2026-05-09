# Architecture Document

*Replace this template with your actual architecture documentation.*

## System Overview

[Insert system diagram here]

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Input     │────▶│  Pipeline   │────▶│   Output    │
│  (CSV/JSON) │     │  (5 steps)  │     │  (Results)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Data Flow

1. **Input**: Telemetry CSV + Incident JSON
2. **Step 1**: Window detection
3. **Step 2**: Clustering
4. **Step 3**: Temporal analysis
5. **Step 4**: Graph construction
6. **Step 5**: Ranking + explanation
7. **Output**: Results JSON

## Module Structure

```
src/
├── step1_window_detection.py    # [Brief description]
├── step2_signal_clustering.py   # [Brief description]
├── step3_temporal_analysis.py   # [Brief description]
├── step4_causal_graph.py        # [Brief description]
├── step5_ranking_explanation.py # [Brief description]
├── pipeline.py                  # [Brief description]
└── utils/
    ├── data_loader.py           # [Brief description]
    └── visualization.py         # [Brief description]
```

## Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| numpy | X.X.X | [purpose] |
| pandas | X.X.X | [purpose] |
| [lib] | X.X.X | [purpose] |

## Computational Complexity

| Step | Time Complexity | Space Complexity |
|------|-----------------|------------------|
| 1 | O(...) | O(...) |
| 2 | O(...) | O(...) |
| 3 | O(...) | O(...) |
| 4 | O(...) | O(...) |
| 5 | O(...) | O(...) |

## Key Design Decisions

### Decision 1: [Topic]
- **Choice**: [What you chose]
- **Rationale**: [Why]

### Decision 2: [Topic]
- **Choice**: [What you chose]
- **Rationale**: [Why]
