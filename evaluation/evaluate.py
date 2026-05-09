#!/usr/bin/env python3
"""
Main Evaluation Script for RCA Student Projects

This script evaluates a student's RCA solution against all scenarios
and produces a comprehensive report with grades.

Usage:
    python evaluate.py <path_to_student_results.json>
    
Or import and use programmatically:
    from evaluate import evaluate_submission
    report = evaluate_submission(results_dict)
"""

import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

from metrics import (
    compute_all_metrics,
    aggregate_metrics,
    print_metrics_report,
    compute_grade,
    GRADE_THRESHOLDS
)


def load_all_ground_truths(data_dir: str) -> Dict[str, Dict]:
    """Load ground truth for all scenarios."""
    ground_truths = {}
    
    for item in sorted(os.listdir(data_dir)):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith('scenario_'):
            gt_path = os.path.join(item_path, 'ground_truth.json')
            if os.path.exists(gt_path):
                with open(gt_path) as f:
                    ground_truths[item] = json.load(f)
    
    return ground_truths


def evaluate_submission(student_results: Dict, 
                        ground_truths: Dict,
                        verbose: bool = True) -> Dict:
    """
    Evaluate a student submission against ground truth.
    
    Args:
        student_results: Dictionary mapping scenario names to prediction results
        ground_truths: Dictionary mapping scenario names to ground truth
        verbose: Print detailed output
    
    Returns:
        Evaluation report dictionary
    """
    all_metrics = []
    evaluated_scenario_metrics = []
    scenario_details = []
    
    # Evaluate each scenario
    for scenario_name, gt in ground_truths.items():
        if scenario_name not in student_results:
            if verbose:
                print(f"WARNING: No results for {scenario_name}")
            scenario_details.append({
                'scenario': scenario_name,
                'status': 'missing',
                'metrics': None
            })
            continue
        
        result = student_results[scenario_name]
        metrics = compute_all_metrics(result, gt)
        all_metrics.append(metrics)
        evaluated_scenario_metrics.append((scenario_name, metrics))
        
        # Determine correctness
        actual = gt.get('root_cause')
        predicted = result.get('root_cause')
        is_correct = (predicted == actual) if actual else (predicted is None)
        
        scenario_details.append({
            'scenario': scenario_name,
            'status': 'evaluated',
            'actual_root_cause': actual,
            'predicted_root_cause': predicted,
            'is_correct': is_correct,
            'metrics': metrics
        })
        
        if verbose:
            symbol = "✓" if is_correct else "✗"
            print(f"{scenario_name}: {predicted} vs {actual} {symbol}")
    
    # Aggregate metrics
    aggregated = aggregate_metrics(all_metrics)
    
    # Compute by difficulty
    easy_metrics = [m for name, m in evaluated_scenario_metrics if 'easy' in name]
    medium_metrics = [m for name, m in evaluated_scenario_metrics if 'medium' in name]
    hard_metrics = [m for name, m in evaluated_scenario_metrics if 'hard' in name]
    
    # Compute grade
    grade = compute_grade(aggregated)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'n_scenarios_evaluated': len(all_metrics),
        'n_scenarios_total': len(ground_truths),
        'overall_metrics': aggregated,
        'grade': grade,
        'by_difficulty': {
            'easy': aggregate_metrics(easy_metrics) if easy_metrics else {},
            'medium': aggregate_metrics(medium_metrics) if medium_metrics else {},
            'hard': aggregate_metrics(hard_metrics) if hard_metrics else {}
        },
        'scenario_details': scenario_details,
        'thresholds': GRADE_THRESHOLDS
    }
    
    return report


def print_evaluation_report(report: Dict):
    """Print a formatted evaluation report."""
    print("\n" + "=" * 70)
    print("ROOT CAUSE ANALYSIS - EVALUATION REPORT")
    print("=" * 70)
    
    print(f"\nTimestamp: {report['timestamp']}")
    print(f"Scenarios Evaluated: {report['n_scenarios_evaluated']} / {report['n_scenarios_total']}")
    
    # Overall metrics
    print("\n" + "-" * 70)
    print("OVERALL METRICS")
    print("-" * 70)
    
    om = report['overall_metrics']
    print(f"  Root Cause Accuracy:  {om.get('mean_root_cause_accuracy', 0)*100:.1f}%")
    print(f"  Top-3 Recall:         {om.get('mean_top_3_recall', 0)*100:.1f}%")
    print(f"  Top-5 Recall:         {om.get('mean_top_5_recall', 0)*100:.1f}%")
    print(f"  Mean Reciprocal Rank: {om.get('mean_mrr', 0):.3f}")
    print(f"  Graph F1 Score:       {om.get('mean_graph_f1', 0):.3f}")
    
    # By difficulty
    print("\n" + "-" * 70)
    print("BY DIFFICULTY")
    print("-" * 70)
    
    for difficulty in ['easy', 'medium', 'hard']:
        dm = report['by_difficulty'].get(difficulty, {})
        if dm:
            acc = dm.get('mean_root_cause_accuracy', 0) * 100
            print(f"  {difficulty.capitalize():8} scenarios: {acc:.1f}% accuracy")
    
    # Grade
    print("\n" + "-" * 70)
    print("FINAL GRADE")
    print("-" * 70)
    
    grade = report['grade']
    print(f"\n  {'*' * 20}")
    print(f"  *  GRADE: {grade}  {'  ' if len(grade) == 1 else ''}     *")
    print(f"  {'*' * 20}")
    
    # Grade explanation
    print("\n  Grade Thresholds:")
    for g, thresh in GRADE_THRESHOLDS.items():
        print(f"    {g}: RC Acc >= {thresh['root_cause_accuracy']*100:.0f}%, Top-3 >= {thresh['top_3_recall']*100:.0f}%")
    
    # Scenario breakdown
    print("\n" + "-" * 70)
    print("SCENARIO BREAKDOWN")
    print("-" * 70)
    
    correct = sum(1 for s in report['scenario_details'] if s.get('is_correct'))
    total = len(report['scenario_details'])
    
    print(f"\n  Correct: {correct} / {total}")
    print("\n  Details:")
    
    for s in report['scenario_details']:
        if s['status'] == 'missing':
            print(f"    {s['scenario']}: MISSING")
        else:
            symbol = "✓" if s['is_correct'] else "✗"
            actual = s['actual_root_cause'] or 'None (control)'
            predicted = s['predicted_root_cause'] or 'None'
            print(f"    {s['scenario']}: {symbol}")
            print(f"      Predicted: {predicted}")
            print(f"      Actual:    {actual}")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point for evaluation script."""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # Check for student results file argument
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
    else:
        # Default: look for results in submission template
        results_path = os.path.join(script_dir, '..', 'submission_template', 
                                     'results', 'scenario_results.json')
    
    print("RCA Evaluation Script")
    print("-" * 40)
    
    # Load ground truths
    print(f"Loading ground truths from: {data_dir}")
    ground_truths = load_all_ground_truths(data_dir)
    print(f"Found {len(ground_truths)} scenarios")
    
    # Check for student results
    if os.path.exists(results_path):
        print(f"Loading student results from: {results_path}")
        with open(results_path) as f:
            student_results = json.load(f)
        
        # Run evaluation
        print("\nEvaluating submission...")
        report = evaluate_submission(student_results, ground_truths, verbose=True)
        
        # Print report
        print_evaluation_report(report)
        
        # Save report
        report_path = os.path.join(os.path.dirname(results_path), 'evaluation_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReport saved to: {report_path}")
        
    else:
        print(f"\nNo student results found at: {results_path}")
        print("\nTo evaluate your solution:")
        print("  1. Save your results as JSON with scenario names as keys")
        print("  2. Each scenario should have: root_cause, ranked_candidates, causal_graph")
        print("  3. Run: python evaluate.py <your_results.json>")
        print("\nExpected results format:")
        print(json.dumps({
            "scenario_01_easy": {
                "root_cause": "PUMP_COOLANT_FLOW",
                "ranked_candidates": [
                    {"signal": "PUMP_COOLANT_FLOW", "score": 0.95},
                    {"signal": "COOLANT_FLOW_RATE", "score": 0.85}
                ],
                "causal_graph": {
                    "nodes": ["PUMP_COOLANT_FLOW", "COOLANT_FLOW_RATE"],
                    "edges": [{"source": "PUMP_COOLANT_FLOW", "target": "COOLANT_FLOW_RATE", "weight": 0.9}]
                }
            }
        }, indent=2))


if __name__ == "__main__":
    main()
