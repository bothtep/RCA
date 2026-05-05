#!/usr/bin/env python3
"""
Run all baselines on all scenarios and report results.

This script:
1. Loads all scenario data
2. Runs each baseline on each scenario
3. Computes accuracy metrics
4. Generates a summary report
"""

import json
import os
import sys
from typing import Dict, List
import pandas as pd
import numpy as np

# Import baseline modules
from baseline_1_naive import identify_root_cause as naive_rca
from baseline_2_zscore import identify_root_cause as zscore_rca
from baseline_3_granger import identify_root_cause as granger_rca


def load_scenario(scenario_path: str) -> tuple:
    """Load scenario data and ground truth."""
    telemetry_path = os.path.join(scenario_path, 'telemetry.csv')
    incident_path = os.path.join(scenario_path, 'incident.json')
    ground_truth_path = os.path.join(scenario_path, 'ground_truth.json')
    
    df = pd.read_csv(telemetry_path)
    
    with open(incident_path) as f:
        incident = json.load(f)
    
    with open(ground_truth_path) as f:
        ground_truth = json.load(f)
    
    return df, incident, ground_truth


def evaluate_result(result: dict, ground_truth: dict) -> dict:
    """
    Evaluate a single result against ground truth.
    
    Returns metrics:
    - root_cause_match: 1 if exact match, 0 otherwise
    - top3_match: 1 if ground truth in top 3, 0 otherwise
    - mrr: Mean Reciprocal Rank (1/rank if found, 0 otherwise)
    """
    actual_root_cause = ground_truth.get('root_cause')
    
    # Handle control scenario (no fault)
    if actual_root_cause is None:
        # For control, success is NOT identifying a root cause
        # or having low confidence
        if result.get('root_cause') is None or result.get('confidence', 1.0) < 0.5:
            return {
                'root_cause_match': 1.0,
                'top3_match': 1.0,
                'mrr': 1.0,
                'is_control': True
            }
        else:
            return {
                'root_cause_match': 0.0,
                'top3_match': 0.0,
                'mrr': 0.0,
                'is_control': True
            }
    
    predicted_root_cause = result.get('root_cause')
    candidates = [c['signal'] for c in result.get('ranked_candidates', [])]
    
    # Root cause match
    root_cause_match = 1.0 if predicted_root_cause == actual_root_cause else 0.0
    
    # Top-3 match
    top3 = candidates[:3] if candidates else [predicted_root_cause]
    top3_match = 1.0 if actual_root_cause in top3 else 0.0
    
    # MRR
    mrr = 0.0
    if actual_root_cause in candidates:
        rank = candidates.index(actual_root_cause) + 1
        mrr = 1.0 / rank
    elif predicted_root_cause == actual_root_cause:
        mrr = 1.0
    
    return {
        'root_cause_match': root_cause_match,
        'top3_match': top3_match,
        'mrr': mrr,
        'is_control': False
    }


def run_all_baselines():
    """Run all baselines on all scenarios."""
    # Find data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # Find all scenario directories
    scenarios = []
    for item in sorted(os.listdir(data_dir)):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith('scenario_'):
            scenarios.append((item, item_path))
    
    if not scenarios:
        print("No scenarios found!")
        return
    
    print("=" * 70)
    print("RCA BASELINE EVALUATION")
    print("=" * 70)
    print(f"\nFound {len(scenarios)} scenarios")
    print()
    
    # Define baselines
    baselines = [
        ('Baseline 1: Naive Correlation', naive_rca),
        ('Baseline 2: Z-Score Temporal', zscore_rca),
        ('Baseline 3: Clustering + Granger', granger_rca),
    ]
    
    # Results storage
    all_results = {name: [] for name, _ in baselines}
    
    # Run each baseline on each scenario
    for scenario_name, scenario_path in scenarios:
        print(f"\n{scenario_name}")
        print("-" * 40)
        
        try:
            df, incident, ground_truth = load_scenario(scenario_path)
            actual = ground_truth.get('root_cause', 'None (control)')
            print(f"  Ground truth: {actual}")
        except Exception as e:
            print(f"  Error loading scenario: {e}")
            continue
        
        for baseline_name, baseline_func in baselines:
            try:
                result = baseline_func(df)
                metrics = evaluate_result(result, ground_truth)
                metrics['scenario'] = scenario_name
                metrics['predicted'] = result.get('root_cause')
                metrics['actual'] = ground_truth.get('root_cause')
                all_results[baseline_name].append(metrics)
                
                match_symbol = "✓" if metrics['root_cause_match'] == 1.0 else "✗"
                print(f"  {baseline_name}: {result.get('root_cause', 'None')} {match_symbol}")
                
            except Exception as e:
                print(f"  {baseline_name}: ERROR - {str(e)[:50]}")
                all_results[baseline_name].append({
                    'scenario': scenario_name,
                    'root_cause_match': 0.0,
                    'top3_match': 0.0,
                    'mrr': 0.0,
                    'error': str(e)
                })
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary_data = []
    
    for baseline_name, results in all_results.items():
        if not results:
            continue
        
        n = len(results)
        root_cause_acc = np.mean([r['root_cause_match'] for r in results])
        top3_acc = np.mean([r['top3_match'] for r in results])
        mrr = np.mean([r['mrr'] for r in results])
        
        # By difficulty
        easy = [r for r in results if 'easy' in r.get('scenario', '')]
        medium = [r for r in results if 'medium' in r.get('scenario', '')]
        hard = [r for r in results if 'hard' in r.get('scenario', '')]
        control = [r for r in results if 'control' in r.get('scenario', '')]
        
        print(f"\n{baseline_name}")
        print("-" * 50)
        print(f"  Overall Root Cause Accuracy: {root_cause_acc*100:.1f}%")
        print(f"  Top-3 Recall:                {top3_acc*100:.1f}%")
        print(f"  Mean Reciprocal Rank:        {mrr:.3f}")
        
        if easy:
            print(f"  Easy scenarios:              {np.mean([r['root_cause_match'] for r in easy])*100:.1f}%")
        if medium:
            print(f"  Medium scenarios:            {np.mean([r['root_cause_match'] for r in medium])*100:.1f}%")
        if hard:
            print(f"  Hard scenarios:              {np.mean([r['root_cause_match'] for r in hard])*100:.1f}%")
        if control:
            print(f"  Control scenario:            {np.mean([r['root_cause_match'] for r in control])*100:.1f}%")
        
        summary_data.append({
            'baseline': baseline_name,
            'root_cause_accuracy': root_cause_acc,
            'top3_recall': top3_acc,
            'mrr': mrr
        })
    
    # Save results
    results_dir = os.path.join(script_dir, '..', 'evaluation')
    os.makedirs(results_dir, exist_ok=True)
    
    results_path = os.path.join(results_dir, 'baseline_results.json')
    with open(results_path, 'w') as f:
        json.dump({
            'summary': summary_data,
            'detailed_results': {k: v for k, v in all_results.items()}
        }, f, indent=2, default=str)
    
    print(f"\n\nDetailed results saved to: {results_path}")
    print()
    
    # Student expectations
    print("=" * 70)
    print("STUDENT EXPECTATIONS")
    print("=" * 70)
    print("""
Students should aim to BEAT Baseline 3 (Clustering + Granger) which is
the strongest baseline.

Grade Thresholds:
  A (90%+): >80% root cause accuracy, >95% top-3 recall
  B (80-89%): >65% root cause accuracy, >85% top-3 recall
  C (70-79%): >50% root cause accuracy, >70% top-3 recall
  D (60-69%): >35% root cause accuracy, >55% top-3 recall
  F (<60%): Below D thresholds
""")


if __name__ == "__main__":
    run_all_baselines()
