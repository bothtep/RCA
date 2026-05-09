#!/usr/bin/env python3
"""
Visualization Utilities for RCA Project

This module provides plotting functions to visualize telemetry data,
anomalies, and RCA results.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_signal(df: pd.DataFrame, 
                signal_id: str,
                ax: Optional[plt.Axes] = None,
                highlight_window: Optional[Tuple[int, int]] = None,
                title: Optional[str] = None,
                show_anomaly_threshold: bool = True) -> plt.Axes:
    """
    Plot a single signal over time.
    
    Args:
        df: DataFrame with 'timestamp' and signal columns
        signal_id: Column name to plot
        ax: Matplotlib axes (creates new if None)
        highlight_window: (start_idx, end_idx) to highlight
        title: Plot title
        show_anomaly_threshold: Show ±3σ threshold lines
    
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 4))
    
    # Plot signal
    if 'timestamp' in df.columns:
        x = df['timestamp']
    else:
        x = df.index
    
    ax.plot(x, df[signal_id], linewidth=0.8, color='steelblue')
    
    # Highlight window
    if highlight_window:
        start_idx, end_idx = highlight_window
        ax.axvspan(x.iloc[start_idx], x.iloc[end_idx], 
                   alpha=0.2, color='red', label='Anomaly Window')
    
    # Anomaly thresholds
    if show_anomaly_threshold:
        mean = df[signal_id].mean()
        std = df[signal_id].std()
        ax.axhline(mean + 3*std, color='red', linestyle='--', 
                   alpha=0.5, label='+3σ')
        ax.axhline(mean - 3*std, color='red', linestyle='--', 
                   alpha=0.5, label='-3σ')
        ax.axhline(mean, color='gray', linestyle='-', alpha=0.3)
    
    # Formatting
    ax.set_xlabel('Time')
    ax.set_ylabel(signal_id)
    ax.set_title(title or signal_id)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    if 'timestamp' in df.columns:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    return ax


def plot_multiple_signals(df: pd.DataFrame,
                          signal_ids: List[str],
                          figsize: Tuple[int, int] = (14, 3),
                          title: str = "Signal Overview") -> plt.Figure:
    """
    Plot multiple signals in subplots.
    
    Args:
        df: DataFrame with signal data
        signal_ids: List of signal column names
        figsize: Figure size per subplot (width, height)
        title: Overall figure title
    
    Returns:
        Matplotlib figure
    """
    n_signals = len(signal_ids)
    fig, axes = plt.subplots(n_signals, 1, 
                             figsize=(figsize[0], figsize[1] * n_signals),
                             sharex=True)
    
    if n_signals == 1:
        axes = [axes]
    
    for ax, signal_id in zip(axes, signal_ids):
        plot_signal(df, signal_id, ax=ax, show_anomaly_threshold=False)
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_correlation_matrix(df: pd.DataFrame,
                            signal_ids: Optional[List[str]] = None,
                            figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Plot correlation matrix heatmap.
    
    Args:
        df: DataFrame with signal data
        signal_ids: Subset of signals (uses all numeric if None)
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    if signal_ids is None:
        signal_ids = df.select_dtypes(include=[np.number]).columns.tolist()
        signal_ids = [s for s in signal_ids if s != 'timestamp']
    
    corr_matrix = df[signal_ids].corr()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
    
    # Labels
    ax.set_xticks(range(len(signal_ids)))
    ax.set_yticks(range(len(signal_ids)))
    ax.set_xticklabels(signal_ids, rotation=90, fontsize=8)
    ax.set_yticklabels(signal_ids, fontsize=8)
    
    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Correlation')
    
    ax.set_title('Signal Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_causal_graph(causal_graph: Dict,
                      figsize: Tuple[int, int] = (12, 8),
                      title: str = "Causal Graph") -> plt.Figure:
    """
    Plot a causal graph.
    
    Args:
        causal_graph: Dict with 'nodes' and 'edges' lists
        figsize: Figure size
        title: Plot title
    
    Returns:
        Matplotlib figure
    """
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX not installed. Install with: pip install networkx")
        return None
    
    # Create graph
    G = nx.DiGraph()
    
    nodes = causal_graph.get('nodes', [])
    edges = causal_graph.get('edges', [])
    
    G.add_nodes_from(nodes)
    
    for edge in edges:
        G.add_edge(edge['source'], edge['target'], 
                   weight=edge.get('weight', 1.0))
    
    # Layout
    if len(nodes) <= 5:
        pos = nx.shell_layout(G)
    else:
        pos = nx.spring_layout(G, k=2, iterations=50)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=2000, 
                           node_color='lightblue', edgecolors='black')
    
    # Draw edges
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray',
                           width=[w * 2 for w in edge_weights],
                           arrows=True, arrowsize=20,
                           connectionstyle="arc3,rad=0.1")
    
    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
    
    # Edge labels (weights)
    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax, font_size=7)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    
    return fig


def plot_anomaly_detection(df: pd.DataFrame,
                           signal_id: str,
                           anomaly_indices: List[int],
                           figsize: Tuple[int, int] = (14, 5)) -> plt.Figure:
    """
    Plot signal with anomaly points highlighted.
    
    Args:
        df: DataFrame with signal data
        signal_id: Signal to plot
        anomaly_indices: List of indices where anomalies detected
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot full signal
    if 'timestamp' in df.columns:
        x = df['timestamp']
    else:
        x = df.index
    
    ax.plot(x, df[signal_id], linewidth=0.8, color='steelblue', label='Signal')
    
    # Highlight anomalies
    if anomaly_indices:
        anomaly_x = x.iloc[anomaly_indices]
        anomaly_y = df[signal_id].iloc[anomaly_indices]
        ax.scatter(anomaly_x, anomaly_y, color='red', s=50, 
                   zorder=5, label='Anomaly')
    
    ax.set_xlabel('Time')
    ax.set_ylabel(signal_id)
    ax.set_title(f'Anomaly Detection: {signal_id}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if 'timestamp' in df.columns:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_ranked_causes(ranked_candidates: List[Dict],
                       actual_root_cause: Optional[str] = None,
                       figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot bar chart of ranked root cause candidates.
    
    Args:
        ranked_candidates: List of dicts with 'signal' and 'score' keys
        actual_root_cause: Ground truth root cause to highlight
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    signals = [c['signal'] for c in ranked_candidates[:10]]
    scores = [c.get('score', c.get('confidence', 0)) for c in ranked_candidates[:10]]
    
    # Color bars
    colors = ['green' if s == actual_root_cause else 'steelblue' for s in signals]
    
    bars = ax.barh(range(len(signals)), scores, color=colors)
    ax.set_yticks(range(len(signals)))
    ax.set_yticklabels(signals)
    ax.invert_yaxis()  # Highest at top
    
    ax.set_xlabel('Score')
    ax.set_title('Ranked Root Cause Candidates', fontsize=14, fontweight='bold')
    
    # Add legend
    if actual_root_cause:
        ax.legend([plt.Rectangle((0,0),1,1, fc='green'),
                   plt.Rectangle((0,0),1,1, fc='steelblue')],
                  ['Actual Root Cause', 'Candidate'])
    
    plt.tight_layout()
    return fig


def plot_causal_chain_timeline(causal_chain: List[Dict],
                               df: pd.DataFrame,
                               figsize: Tuple[int, int] = (14, 8)) -> plt.Figure:
    """
    Plot signals in causal chain with their temporal ordering.
    
    Args:
        causal_chain: List of dicts with 'signal' and timing info
        df: DataFrame with signal data
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    n_signals = len(causal_chain)
    fig, axes = plt.subplots(n_signals, 1, figsize=figsize, sharex=True)
    
    if n_signals == 1:
        axes = [axes]
    
    colors = plt.cm.viridis(np.linspace(0, 0.8, n_signals))
    
    for i, (chain_item, ax, color) in enumerate(zip(causal_chain, axes, colors)):
        signal_id = chain_item['signal']
        
        if signal_id in df.columns:
            if 'timestamp' in df.columns:
                x = df['timestamp']
            else:
                x = df.index
            
            ax.plot(x, df[signal_id], linewidth=1, color=color)
            ax.set_ylabel(signal_id, fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Add order number
            ax.text(0.02, 0.95, f"#{chain_item.get('order', i+1)}", 
                    transform=ax.transAxes, fontsize=10, fontweight='bold',
                    verticalalignment='top')
    
    fig.suptitle('Causal Chain Timeline', fontsize=14, fontweight='bold')
    
    if 'timestamp' in df.columns:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def create_scenario_summary_plot(df: pd.DataFrame,
                                 incident: Dict,
                                 ground_truth: Dict,
                                 figsize: Tuple[int, int] = (16, 12)) -> plt.Figure:
    """
    Create a comprehensive summary plot for a scenario.
    
    Args:
        df: Telemetry DataFrame
        incident: Incident metadata
        ground_truth: Ground truth data
    
    Returns:
        Matplotlib figure
    """
    fig = plt.figure(figsize=figsize)
    
    # Get root cause and related signals
    root_cause = ground_truth.get('root_cause')
    causal_chain = ground_truth.get('causal_chain', [])
    
    # Subplot layout
    if causal_chain:
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1])
        
        # Root cause signal
        ax1 = fig.add_subplot(gs[0, :])
        if root_cause and root_cause in df.columns:
            plot_signal(df, root_cause, ax=ax1, 
                       title=f"Root Cause: {root_cause}")
        
        # First few signals in chain
        for i, chain_item in enumerate(causal_chain[1:4]):  # Skip root cause, show next 3
            row = 1 + i // 2
            col = i % 2
            if row < 3:
                ax = fig.add_subplot(gs[row, col])
                signal = chain_item['signal']
                if signal in df.columns:
                    plot_signal(df, signal, ax=ax, 
                               title=f"#{chain_item.get('order', i+2)}: {signal}",
                               show_anomaly_threshold=False)
    else:
        # No causal chain - show overview
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Scenario: {incident.get('scenario_name', 'Unknown')}\n"
                         f"Difficulty: {incident.get('difficulty', 'Unknown')}\n"
                         f"Root Cause: {root_cause or 'None (control)'}",
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
    
    title = f"Scenario Summary: {incident.get('scenario_name', 'Unknown')}"
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


# Example usage
if __name__ == "__main__":
    print("RCA Visualization Module")
    print("-" * 40)
    print("\nAvailable plotting functions:")
    print("  - plot_signal(df, signal_id)")
    print("  - plot_multiple_signals(df, signal_ids)")
    print("  - plot_correlation_matrix(df)")
    print("  - plot_causal_graph(causal_graph)")
    print("  - plot_anomaly_detection(df, signal_id, anomaly_indices)")
    print("  - plot_ranked_causes(ranked_candidates)")
    print("  - plot_causal_chain_timeline(causal_chain, df)")
    print("  - create_scenario_summary_plot(df, incident, ground_truth)")
