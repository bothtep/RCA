#!/usr/bin/env python3
"""
Data Loader Utilities for RCA Project

This module provides functions to load and preprocess the scenario data.
Students should use these functions to load data in their implementations.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np


def get_project_root() -> str:
    """Get the root directory of the project."""
    current = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current)


def get_data_dir() -> str:
    """Get the data directory path."""
    return os.path.join(get_project_root(), 'data')


def list_scenarios() -> List[str]:
    """
    List all available scenarios.
    
    Returns:
        List of scenario directory names sorted by number
    """
    data_dir = get_data_dir()
    scenarios = []
    
    for item in sorted(os.listdir(data_dir)):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith('scenario_'):
            scenarios.append(item)
    
    return scenarios


def load_scenario(scenario_name: str) -> Tuple[pd.DataFrame, Dict, Dict]:
    """
    Load all data for a specific scenario.
    
    Args:
        scenario_name: Name of scenario directory (e.g., 'scenario_01_easy')
    
    Returns:
        Tuple of (telemetry_df, incident_metadata, ground_truth)
    """
    data_dir = get_data_dir()
    scenario_path = os.path.join(data_dir, scenario_name)
    
    if not os.path.exists(scenario_path):
        raise FileNotFoundError(f"Scenario not found: {scenario_name}")
    
    # Load telemetry
    telemetry_path = os.path.join(scenario_path, 'telemetry.csv')
    df = pd.read_csv(telemetry_path)
    
    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Load incident metadata
    incident_path = os.path.join(scenario_path, 'incident.json')
    with open(incident_path) as f:
        incident = json.load(f)
    
    # Load ground truth
    ground_truth_path = os.path.join(scenario_path, 'ground_truth.json')
    with open(ground_truth_path) as f:
        ground_truth = json.load(f)
    
    return df, incident, ground_truth


def load_telemetry(scenario_name: str) -> pd.DataFrame:
    """
    Load only telemetry data for a scenario.
    
    Args:
        scenario_name: Name of scenario directory
    
    Returns:
        DataFrame with telemetry data
    """
    df, _, _ = load_scenario(scenario_name)
    return df


def load_signals_metadata() -> Dict:
    """
    Load the signals metadata file.
    
    Returns:
        Dictionary with signal definitions
    """
    data_dir = get_data_dir()
    metadata_path = os.path.join(data_dir, 'signals_metadata.json')
    
    with open(metadata_path) as f:
        return json.load(f)


def load_domain_knowledge() -> Dict:
    """
    Load the domain knowledge file.
    
    Returns:
        Dictionary with domain knowledge (causal relationships, failure patterns, etc.)
    """
    data_dir = get_data_dir()
    knowledge_path = os.path.join(data_dir, 'domain_knowledge.json')
    
    with open(knowledge_path) as f:
        return json.load(f)


def get_signal_info(signal_id: str) -> Optional[Dict]:
    """
    Get metadata for a specific signal.
    
    Args:
        signal_id: Signal identifier (e.g., 'TEMP_BATTERY_CELL_01')
    
    Returns:
        Signal metadata dictionary or None if not found
    """
    metadata = load_signals_metadata()
    
    for signal in metadata['signals']:
        if signal['signal_id'] == signal_id:
            return signal
    
    return None


def get_signals_by_subsystem(subsystem: str) -> List[str]:
    """
    Get all signal IDs belonging to a specific subsystem.
    
    Args:
        subsystem: Subsystem name ('battery', 'cooling', 'motor', 'electrical', 'sensor_health')
    
    Returns:
        List of signal IDs
    """
    metadata = load_signals_metadata()
    
    return [s['signal_id'] for s in metadata['signals'] 
            if s.get('subsystem') == subsystem]


def get_numeric_signals(df: pd.DataFrame) -> List[str]:
    """
    Get list of numeric signal columns from a DataFrame.
    
    Excludes 'timestamp' column.
    
    Args:
        df: Telemetry DataFrame
    
    Returns:
        List of numeric column names
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [col for col in numeric_cols if col != 'timestamp']


def normalize_signals(df: pd.DataFrame, 
                      method: str = 'zscore') -> pd.DataFrame:
    """
    Normalize numeric signals in a DataFrame.
    
    Args:
        df: Telemetry DataFrame
        method: 'zscore' (standard normalization) or 'minmax' (0-1 scaling)
    
    Returns:
        DataFrame with normalized values (timestamp preserved)
    """
    result = df.copy()
    numeric_cols = get_numeric_signals(df)
    
    if method == 'zscore':
        for col in numeric_cols:
            mean = result[col].mean()
            std = result[col].std()
            if std > 0:
                result[col] = (result[col] - mean) / std
    elif method == 'minmax':
        for col in numeric_cols:
            min_val = result[col].min()
            max_val = result[col].max()
            if max_val > min_val:
                result[col] = (result[col] - min_val) / (max_val - min_val)
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return result


def get_incident_window(df: pd.DataFrame, 
                        incident_metadata: Dict,
                        context_before_seconds: float = 300,
                        context_after_seconds: float = 300) -> pd.DataFrame:
    """
    Extract data around the incident timestamp.
    
    Args:
        df: Full telemetry DataFrame
        incident_metadata: Incident metadata with 'incident_timestamp'
        context_before_seconds: Seconds of context before incident
        context_after_seconds: Seconds of context after incident
    
    Returns:
        Subset of DataFrame around incident
    """
    incident_ts = incident_metadata.get('incident_timestamp')
    
    if incident_ts is None:
        # Control scenario - return full data
        return df
    
    incident_time = pd.to_datetime(incident_ts)
    
    start_time = incident_time - pd.Timedelta(seconds=context_before_seconds)
    end_time = incident_time + pd.Timedelta(seconds=context_after_seconds)
    
    mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
    return df[mask].reset_index(drop=True)


def resample_data(df: pd.DataFrame, 
                  target_freq: str = '1S') -> pd.DataFrame:
    """
    Resample time series data to a different frequency.
    
    Args:
        df: Telemetry DataFrame with 'timestamp' column
        target_freq: Target frequency (e.g., '1S' for 1 second, '100ms' for 100ms)
    
    Returns:
        Resampled DataFrame
    """
    df_indexed = df.set_index('timestamp')
    resampled = df_indexed.resample(target_freq).mean()
    return resampled.reset_index()


def load_all_scenarios() -> Dict[str, Tuple[pd.DataFrame, Dict, Dict]]:
    """
    Load all scenarios into memory.
    
    Returns:
        Dictionary mapping scenario names to (df, incident, ground_truth) tuples
    """
    all_data = {}
    
    for scenario_name in list_scenarios():
        try:
            df, incident, ground_truth = load_scenario(scenario_name)
            all_data[scenario_name] = (df, incident, ground_truth)
        except Exception as e:
            print(f"Warning: Failed to load {scenario_name}: {e}")
    
    return all_data


# For convenience when running as script
if __name__ == "__main__":
    print("RCA Data Loader")
    print("=" * 50)
    
    # List available scenarios
    scenarios = list_scenarios()
    print(f"\nAvailable scenarios ({len(scenarios)}):")
    for s in scenarios:
        print(f"  - {s}")
    
    # Load example scenario
    if scenarios:
        print(f"\nLoading first scenario: {scenarios[0]}")
        df, incident, ground_truth = load_scenario(scenarios[0])
        
        print(f"\nTelemetry shape: {df.shape}")
        print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Signals: {len(get_numeric_signals(df))}")
        
        print(f"\nIncident: {incident['scenario_name']}")
        print(f"Difficulty: {incident['difficulty']}")
        print(f"Root cause: {ground_truth.get('root_cause', 'None (control)')}")
    
    # Show signal metadata summary
    metadata = load_signals_metadata()
    print(f"\n\nSignal Metadata:")
    print(f"  Total signals: {len(metadata['signals'])}")
    print(f"  Subsystems: {metadata['subsystems']}")
