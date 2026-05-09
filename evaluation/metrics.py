#!/usr/bin/env python3
"""
Evaluation Metrics for RCA Project

This module provides standard metrics for evaluating student RCA solutions.
Students can use these functions to evaluate their own implementations.
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional


def root_cause_accuracy(predicted: str, actual: str) -> float:
    """
    Binary root cause accuracy.
    
    Args:
        predicted: Predicted root cause signal name
        actual: Actual root cause signal name
    
    Returns:
        1.0 if exact match, 0.0 otherwise
    """
    if actual is None:
        # Control scenario - should not predict any root cause
        return 1.0 if predicted is None else 0.0
    return 1.0 if predicted == actual else 0.0


def top_k_recall(predicted_ranked: List[str], actual: str, k: int = 3) -> float:
    """
    Check if actual root cause is in top-k predictions.
    
    Args:
        predicted_ranked: List of predicted signals, ranked by likelihood
        actual: Actual root cause signal name
        k: Number of top predictions to consider
    
    Returns:
        1.0 if actual in top-k, 0.0 otherwise
    """
    if actual is None:
        return 1.0 if not predicted_ranked else 0.0
    return 1.0 if actual in predicted_ranked[:k] else 0.0


def mean_reciprocal_rank(predicted_ranked: List[str], actual: str) -> float:
    """
    Compute Mean Reciprocal Rank (MRR).
    
    MRR = 1/rank if the actual root cause is found in predictions, else 0.
    
    Args:
        predicted_ranked: List of predicted signals, ranked by likelihood
        actual: Actual root cause signal name
    
    Returns:
        1/rank if found, 0.0 otherwise
    """
    if actual is None:
        return 1.0 if not predicted_ranked else 0.0
    
    try:
        rank = predicted_ranked.index(actual) + 1
        return 1.0 / rank
    except ValueError:
        return 0.0


def causal_graph_precision(predicted_edges: Set[Tuple[str, str]], 
                           actual_edges: Set[Tuple[str, str]]) -> float:
    """
    Precision for causal graph edges.
    
    Precision = (True Positives) / (Predicted Positives)
    
    Args:
        predicted_edges: Set of (source, target) tuples for predicted edges
        actual_edges: Set of (source, target) tuples for ground truth edges
    
    Returns:
        Precision score (0.0 to 1.0)
    """
    if not predicted_edges:
        return 0.0
    
    true_positives = len(predicted_edges & actual_edges)
    return true_positives / len(predicted_edges)


def causal_graph_recall(predicted_edges: Set[Tuple[str, str]], 
                        actual_edges: Set[Tuple[str, str]]) -> float:
    """
    Recall for causal graph edges.
    
    Recall = (True Positives) / (Actual Positives)
    
    Args:
        predicted_edges: Set of (source, target) tuples for predicted edges
        actual_edges: Set of (source, target) tuples for ground truth edges
    
    Returns:
        Recall score (0.0 to 1.0)
    """
    if not actual_edges:
        return 1.0 if not predicted_edges else 0.0
    
    true_positives = len(predicted_edges & actual_edges)
    return true_positives / len(actual_edges)


def causal_graph_f1(predicted_edges: Set[Tuple[str, str]], 
                    actual_edges: Set[Tuple[str, str]]) -> Dict[str, float]:
    """
    Compute Precision, Recall, and F1 for causal graph edges.
    
    Args:
        predicted_edges: Set of (source, target) tuples for predicted edges
        actual_edges: Set of (source, target) tuples for ground truth edges
    
    Returns:
        Dictionary with 'precision', 'recall', 'f1' scores
    """
    precision = causal_graph_precision(predicted_edges, actual_edges)
    recall = causal_graph_recall(predicted_edges, actual_edges)
    
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


def window_iou(predicted_start: int, predicted_end: int,
               actual_start: int, actual_end: int) -> float:
    """
    Intersection over Union for incident window detection.
    
    Args:
        predicted_start: Predicted start index of incident window
        predicted_end: Predicted end index of incident window
        actual_start: Actual start index of incident window
        actual_end: Actual end index of incident window
    
    Returns:
        IoU score (0.0 to 1.0)
    """
    # Calculate intersection
    intersection_start = max(predicted_start, actual_start)
    intersection_end = min(predicted_end, actual_end)
    intersection = max(0, intersection_end - intersection_start)
    
    # Calculate union
    predicted_length = predicted_end - predicted_start
    actual_length = actual_end - actual_start
    union = predicted_length + actual_length - intersection
    
    if union <= 0:
        return 0.0
    
    return intersection / union


def explanation_quality_score(explanation: str, 
                              required_elements: List[str]) -> float:
    """
    Score the quality of a generated explanation.
    
    Checks if explanation contains required elements like:
    - Root cause identification
    - Temporal sequence
    - Confidence level
    - Evidence description
    
    Args:
        explanation: Generated natural language explanation
        required_elements: List of keywords/phrases that should appear
    
    Returns:
        Score based on proportion of required elements present
    """
    if not explanation:
        return 0.0
    
    explanation_lower = explanation.lower()
    found = sum(1 for elem in required_elements if elem.lower() in explanation_lower)
    
    return found / len(required_elements) if required_elements else 0.0


def compute_all_metrics(result: Dict, ground_truth: Dict) -> Dict[str, float]:
    """
    Compute all evaluation metrics for a single result.
    
    Args:
        result: Dictionary with prediction results containing:
            - root_cause: predicted root cause signal
            - ranked_candidates: list of dicts with 'signal' key
            - causal_graph: dict with 'edges' list
            - window: dict with 'start_idx' and 'end_idx'
        ground_truth: Dictionary with ground truth containing:
            - root_cause: actual root cause signal
            - causal_graph: dict with 'edges' list
    
    Returns:
        Dictionary with all computed metrics
    """
    # Extract predictions
    predicted_root = result.get('root_cause')
    predicted_ranked = [c['signal'] for c in result.get('ranked_candidates', [])]
    
    # Extract ground truth
    actual_root = ground_truth.get('root_cause')
    
    # Root cause metrics
    rc_accuracy = root_cause_accuracy(predicted_root, actual_root)
    top1 = top_k_recall(predicted_ranked, actual_root, k=1)
    top3 = top_k_recall(predicted_ranked, actual_root, k=3)
    top5 = top_k_recall(predicted_ranked, actual_root, k=5)
    mrr = mean_reciprocal_rank(predicted_ranked, actual_root)
    
    # Causal graph metrics
    pred_edges = set()
    if 'causal_graph' in result and 'edges' in result['causal_graph']:
        for e in result['causal_graph']['edges']:
            pred_edges.add((e['source'], e['target']))
    
    actual_edges = set()
    if 'causal_graph' in ground_truth and 'edges' in ground_truth['causal_graph']:
        for e in ground_truth['causal_graph']['edges']:
            actual_edges.add((e['source'], e['target']))
    
    graph_metrics = causal_graph_f1(pred_edges, actual_edges)
    
    return {
        'root_cause_accuracy': rc_accuracy,
        'top_1_recall': top1,
        'top_3_recall': top3,
        'top_5_recall': top5,
        'mrr': mrr,
        'graph_precision': graph_metrics['precision'],
        'graph_recall': graph_metrics['recall'],
        'graph_f1': graph_metrics['f1']
    }


def aggregate_metrics(all_metrics: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Aggregate metrics across multiple scenarios.
    
    Args:
        all_metrics: List of metric dictionaries from compute_all_metrics
    
    Returns:
        Dictionary with mean values for each metric
    """
    if not all_metrics:
        return {}
    
    keys = all_metrics[0].keys()
    aggregated = {}
    
    for key in keys:
        values = [m[key] for m in all_metrics if key in m]
        aggregated[f'mean_{key}'] = np.mean(values) if values else 0.0
        aggregated[f'std_{key}'] = np.std(values) if values else 0.0
    
    return aggregated


def print_metrics_report(metrics: Dict[str, float], title: str = "Evaluation Report"):
    """
    Print a formatted metrics report.
    
    Args:
        metrics: Dictionary of metric name -> value
        title: Report title
    """
    print("=" * 60)
    print(title)
    print("=" * 60)
    
    # Group metrics by category
    rc_metrics = {k: v for k, v in metrics.items() if 'root_cause' in k or 'top_' in k or 'mrr' in k}
    graph_metrics = {k: v for k, v in metrics.items() if 'graph' in k}
    other_metrics = {k: v for k, v in metrics.items() if k not in rc_metrics and k not in graph_metrics}
    
    if rc_metrics:
        print("\nRoot Cause Identification:")
        print("-" * 40)
        for key, value in sorted(rc_metrics.items()):
            print(f"  {key}: {value:.4f}")
    
    if graph_metrics:
        print("\nCausal Graph Quality:")
        print("-" * 40)
        for key, value in sorted(graph_metrics.items()):
            print(f"  {key}: {value:.4f}")
    
    if other_metrics:
        print("\nOther Metrics:")
        print("-" * 40)
        for key, value in sorted(other_metrics.items()):
            print(f"  {key}: {value:.4f}")
    
    print("=" * 60)


# Grading thresholds
GRADE_THRESHOLDS = {
    'A': {'root_cause_accuracy': 0.80, 'top_3_recall': 0.95, 'graph_f1': 0.75},
    'B': {'root_cause_accuracy': 0.65, 'top_3_recall': 0.85, 'graph_f1': 0.60},
    'C': {'root_cause_accuracy': 0.50, 'top_3_recall': 0.70, 'graph_f1': 0.45},
    'D': {'root_cause_accuracy': 0.35, 'top_3_recall': 0.55, 'graph_f1': 0.30},
}


def compute_grade(metrics: Dict[str, float]) -> str:
    """
    Compute letter grade based on metrics.
    
    Args:
        metrics: Dictionary with at least 'root_cause_accuracy' and 'top_3_recall'
    
    Returns:
        Letter grade (A, B, C, D, or F)
    """
    rc_acc = metrics.get('mean_root_cause_accuracy', metrics.get('root_cause_accuracy', 0))
    top3 = metrics.get('mean_top_3_recall', metrics.get('top_3_recall', 0))
    
    for grade in ['A', 'B', 'C', 'D']:
        thresholds = GRADE_THRESHOLDS[grade]
        if rc_acc >= thresholds['root_cause_accuracy'] and top3 >= thresholds['top_3_recall']:
            return grade
    
    return 'F'


if __name__ == "__main__":
    # Example usage
    print("RCA Evaluation Metrics Module")
    print("-" * 40)
    print("\nAvailable functions:")
    print("  - root_cause_accuracy(predicted, actual)")
    print("  - top_k_recall(predicted_ranked, actual, k)")
    print("  - mean_reciprocal_rank(predicted_ranked, actual)")
    print("  - causal_graph_f1(predicted_edges, actual_edges)")
    print("  - window_iou(pred_start, pred_end, actual_start, actual_end)")
    print("  - compute_all_metrics(result, ground_truth)")
    print("  - aggregate_metrics(all_metrics)")
    print("  - compute_grade(metrics)")
    
    print("\n\nGrade Thresholds:")
    for grade, thresholds in GRADE_THRESHOLDS.items():
        print(f"  {grade}: {thresholds}")
