# RCA Project Grading Rubric

## Overview

This document provides detailed grading criteria for the Root Cause Analysis project. Total points: 100.

---

## 1. Root Cause Identification Accuracy (30 points)

### Primary Metric: Percentage of scenarios where the #1 predicted root cause matches ground truth

| Points | Accuracy | Interpretation |
|--------|----------|----------------|
| 30 | ≥80% (12+/15) | Excellent - consistently identifies root causes |
| 25 | ≥65% (10/15) | Good - solid performance across difficulties |
| 20 | ≥50% (8/15) | Satisfactory - gets most easy/medium scenarios |
| 15 | ≥35% (5/15) | Needs improvement - limited success |
| 10 | ≥20% (3/15) | Poor - mostly incorrect |
| 0 | <20% | Failing - below random baseline |

### By Difficulty Breakdown
- Easy scenarios (5): Should get 4-5 correct
- Medium scenarios (5): Should get 3-4 correct
- Hard scenarios (4): Should get 1-2 correct
- Control scenario (1): Should NOT identify a root cause

---

## 2. Top-3 Recall (15 points)

### Metric: Percentage of scenarios where correct root cause is in top 3 predictions

| Points | Top-3 Recall | Interpretation |
|--------|--------------|----------------|
| 15 | ≥95% (14-15/15) | Excellent - almost always in top 3 |
| 12 | ≥85% (13/15) | Good - rarely misses |
| 9 | ≥70% (10-11/15) | Satisfactory |
| 6 | ≥55% (8-9/15) | Needs improvement |
| 3 | ≥40% (6/15) | Poor |
| 0 | <40% | Failing |

---

## 3. Causal Graph Quality (20 points)

### Metrics: Precision, Recall, and F1 score on causal graph edges

| Points | Graph F1 | Interpretation |
|--------|----------|----------------|
| 20 | ≥0.75 | Excellent - captures most real relationships |
| 16 | ≥0.60 | Good - reasonable graph structure |
| 12 | ≥0.45 | Satisfactory - some correct edges |
| 8 | ≥0.30 | Needs improvement |
| 4 | ≥0.15 | Poor |
| 0 | <0.15 | Failing |

### Evaluation Criteria
- **Precision**: Of edges you predicted, how many are correct?
- **Recall**: Of true edges, how many did you find?
- **F1**: Harmonic mean of precision and recall

---

## 4. Incident Window Detection (10 points)

### Metric: Intersection over Union (IoU) of predicted vs. actual incident window

| Points | Average IoU | Interpretation |
|--------|-------------|----------------|
| 10 | ≥0.70 | Excellent - precise window detection |
| 8 | ≥0.55 | Good |
| 6 | ≥0.40 | Satisfactory |
| 4 | ≥0.25 | Needs improvement |
| 2 | ≥0.10 | Poor |
| 0 | <0.10 | Failing |

---

## 5. Code Quality (15 points)

### Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Modularity** | 4 | Code organized into logical modules |
| **Documentation** | 4 | Functions have docstrings, README clear |
| **Readability** | 3 | Clear variable names, consistent style |
| **Testing** | 2 | Unit tests or validation checks |
| **Reproducibility** | 2 | Runs without errors on new environment |

### Detailed Rubric

**Modularity (4 points)**
- 4: Each pipeline step in separate file, clean interfaces
- 3: Most steps separated, some mixing
- 2: Partial separation
- 1: Monolithic code with some structure
- 0: All code in one file, no organization

**Documentation (4 points)**
- 4: All functions documented, APPROACH.md and ARCHITECTURE.md complete
- 3: Most functions documented, docs mostly complete
- 2: Some documentation
- 1: Minimal documentation
- 0: No documentation

**Readability (3 points)**
- 3: PEP 8 compliant, descriptive names, clear logic
- 2: Mostly readable, some issues
- 1: Hard to follow in places
- 0: Unreadable code

**Testing (2 points)**
- 2: Unit tests for key functions
- 1: Some validation checks
- 0: No testing

**Reproducibility (2 points)**
- 2: Runs cleanly on fresh environment
- 1: Runs with minor fixes
- 0: Does not run

---

## 6. Explanation Quality (10 points)

### Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Completeness** | 4 | All required elements present |
| **Clarity** | 3 | Easy to understand |
| **Evidence** | 3 | Supported by data/analysis |

### Required Explanation Elements

- Root cause identification
- Confidence level
- Temporal sequence (what happened first)
- Evidence summary (why this signal?)
- Downstream effects

### Rubric

**Completeness (4 points)**
- 4: All 5 elements present for all scenarios
- 3: Most elements present
- 2: Some elements missing
- 1: Minimal explanation
- 0: No explanation

**Clarity (3 points)**
- 3: A non-expert could understand
- 2: Technical but clear
- 1: Hard to follow
- 0: Incomprehensible

**Evidence (3 points)**
- 3: Each claim backed by specific data
- 2: Some evidence provided
- 1: Vague justifications
- 0: No evidence

---

## Grade Calculation

### Formula

```
Final Score = (
    Root Cause Accuracy Points +
    Top-3 Recall Points +
    Causal Graph Points +
    Window Detection Points +
    Code Quality Points +
    Explanation Quality Points
)
```

### Letter Grade Mapping

| Score | Letter Grade |
|-------|--------------|
| 90-100 | A |
| 80-89 | B |
| 70-79 | C |
| 60-69 | D |
| <60 | F |

---

## Bonus Points (up to 10)

### Innovation Bonus (up to 5 points)
- Novel algorithm combination
- Creative use of domain knowledge
- Significant improvement over baselines
- Interesting ablation studies

### Documentation Bonus (up to 3 points)
- Exceptional clarity
- Helpful visualizations
- Thorough analysis of failures

### Performance Bonus (up to 2 points)
- Achieving A-grade on hard scenarios specifically

---

## Common Deductions

| Issue | Deduction |
|-------|-----------|
| Code doesn't run | Up to -20 |
| Missing scenario results | -2 per missing |
| Hardcoded ground truth | -50 (academic integrity) |
| No documentation | -10 |
| Plagiarism | -100 (fail + academic action) |

---

## Evaluation Process

1. **Automated Scoring** (70%)
   - Run evaluation script on scenario_results.json
   - Compute all metrics automatically

2. **Manual Review** (30%)
   - Code quality assessment
   - Documentation review
   - Explanation quality evaluation

3. **Optional Interview**
   - May be requested to explain code
   - Demonstrate understanding of algorithms

---

## Example Grade Calculations

### Example A: Strong Submission
- Root Cause: 80% (12/15) → 30 pts
- Top-3: 93% (14/15) → 15 pts
- Graph F1: 0.72 → 18 pts
- Window IoU: 0.65 → 8 pts
- Code Quality → 14 pts
- Explanations → 8 pts
- **Total: 93 pts (A)**

### Example B: Good Submission
- Root Cause: 60% (9/15) → 22 pts
- Top-3: 80% (12/15) → 10 pts
- Graph F1: 0.55 → 14 pts
- Window IoU: 0.50 → 7 pts
- Code Quality → 12 pts
- Explanations → 7 pts
- **Total: 72 pts (C+)**

### Example C: Needs Improvement
- Root Cause: 40% (6/15) → 17 pts
- Top-3: 60% (9/15) → 7 pts
- Graph F1: 0.35 → 10 pts
- Window IoU: 0.30 → 5 pts
- Code Quality → 8 pts
- Explanations → 4 pts
- **Total: 51 pts (F)**

---

## Frequently Asked Questions

**Q: Can I get an A without getting all hard scenarios correct?**
A: Yes. A grade requires ≥80% accuracy overall (12/15). Getting all easy (5), all medium (5), and 2 hard scenarios would achieve this.

**Q: What if my causal graph has extra edges?**
A: Extra edges hurt precision but don't affect recall. Balance is important.

**Q: Is partial credit given for close answers?**
A: Top-3 recall provides partial credit for close rankings. Graph F1 provides partial credit for partially correct graphs.

**Q: How is the control scenario evaluated?**
A: You should NOT identify a root cause (or have very low confidence). Correctly handling control adds to accuracy.

**Q: Can I use external libraries?**
A: Yes, any open-source library is allowed. Document what you use.

---

*This rubric is designed to reward both technical performance and engineering practices. The goal is to build skills that transfer to industry.*
