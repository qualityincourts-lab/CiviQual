#!/usr/bin/env python3
"""
WATSON Visualization Engine

Provides chart generation capabilities for Lean Six Sigma analysis.

Copyright (c) 2025 A Step in the Right Direction LLC
All Rights Reserved.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats

from statistics_engine import StatisticsEngine


class VisualizationEngine:
    """Visualization engine for Watson charts."""
    
    # ==========================================================================
    # Brand Colors (Quality in Courts)
    # ==========================================================================
    BRAND_BURGUNDY = '#6d132a'  # Primary brand - logo, titles, spec limits
    BRAND_GOLD = '#dcad73'      # Secondary brand - accents, highlights
    
    # ==========================================================================
    # Colorblind Accessible Chart Palette
    # Modified Wong palette avoiding red/orange to prevent brand color confusion
    # ==========================================================================
    BLUE = '#0072B2'       # Primary data series
    TEAL = '#009E73'       # Secondary data, control limits
    SKY_BLUE = '#56B4E9'   # Histogram fills, tertiary data
    YELLOW = '#F0E442'     # Highlights, warnings (use sparingly)
    PINK = '#CC79A7'       # Additional data series
    INDIGO = '#332288'     # Extended palette
    CYAN = '#88CCEE'       # Extended palette
    OLIVE = '#999933'      # Extended palette
    
    # Semantic aliases
    BLACK = '#000000'      # Primary text, center lines
    GRAY = '#999999'       # Secondary text, zone lines
    LIGHT_GRAY = '#E5E5E5' # Backgrounds
    WHITE = '#ffffff'
    
    # Legacy aliases for compatibility
    GREEN = '#009E73'      # Alias for TEAL
    ORANGE = '#dcad73'     # Redirected to BRAND_GOLD (avoid in charts)
    VERMILLION = '#6d132a' # Redirected to BRAND_BURGUNDY (out-of-control)
    PURPLE = '#CC79A7'     # Alias for PINK
    
    # Chart color cycle (colorblind-safe, brand-aligned)
    COLOR_CYCLE = ['#0072B2', '#009E73', '#56B4E9', '#CC79A7', 
                   '#332288', '#F0E442', '#88CCEE', '#999933']
    
    def __init__(self):
        """Initialize the visualization engine."""
        self.stats_engine = StatisticsEngine()
        self.temp_dir = Path(tempfile.gettempdir()) / 'watson_charts'
        self.temp_dir.mkdir(exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'figure.titlesize': 14,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': self.GRAY,
            'axes.labelcolor': self.BLACK,
            'text.color': self.BLACK,
            'axes.prop_cycle': plt.cycler(color=self.COLOR_CYCLE)
        })
    
    def generate_four_up(self, data, column_name, lsl=None, usl=None, target=None, percentile=80):
        """
        Generate Watson 4-Up Chart.
        
        The 4-Up Chart provides four complementary views:
        1. Statistical Summary (histogram with statistics)
        2. Probability Plot (normality assessment)
        3. I-Chart (Individuals control chart)
        4. Capability Analysis (Cp=1.0 natural tolerance based on data)
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            lsl: Lower specification limit (not used in 4-Up - for standalone capability)
            usl: Upper specification limit (not used in 4-Up - for standalone capability)
            target: Target value (not used in 4-Up - for standalone capability)
            percentile: Percentile line to display on probability plot
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 2:
            return None
        
        # Create figure with 2x2 grid
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle(f'Watson 4-Up Chart: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)
        
        # Calculate statistics
        stats_dict = self.stats_engine.descriptive_stats(data)
        
        # Quadrant 1: Statistical Summary (Histogram)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_statistical_summary(ax1, data, stats_dict)
        
        # Quadrant 2: Probability Plot
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_probability(ax2, data, percentile)
        
        # Quadrant 3: I-Chart
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_ichart(ax3, data, column_name)
        
        # Quadrant 4: Capability Analysis (always Cp=1.0 natural tolerance)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_capability(ax4, data, column_name)
        
        # Save figure
        output_path = self.temp_dir / 'four_up_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def _plot_statistical_summary(self, ax, data, stats_dict):
        """Plot statistical summary with histogram and statistics."""
        # Histogram
        n_bins = min(int(np.sqrt(len(data))), 30)
        n, bins, patches = ax.hist(data, bins=n_bins, color=self.SKY_BLUE, 
                                   edgecolor=self.BLUE, alpha=0.8)
        
        # Add normal curve overlay
        x = np.linspace(data.min(), data.max(), 100)
        mean, std = stats_dict['mean'], stats_dict['std']
        y = stats.norm.pdf(x, mean, std)
        y = y * len(data) * (bins[1] - bins[0])  # Scale to histogram
        ax.plot(x, y, color=self.BLACK, linewidth=2, label='Normal Fit')
        
        # Add mean line
        ax.axvline(mean, color=self.TEAL, linestyle='--', linewidth=2, label=f'Mean: {mean:.2f}')
        
        # Statistics text box
        stats_text = (
            f"N = {stats_dict['n']}\n"
            f"Mean = {stats_dict['mean']:.4f}\n"
            f"StDev = {stats_dict['std']:.4f}\n"
            f"Median = {stats_dict['median']:.4f}\n"
            f"Min = {stats_dict['min']:.4f}\n"
            f"Max = {stats_dict['max']:.4f}"
        )
        
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.9))
        
        ax.set_title('Statistical Summary', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.legend(loc='upper left', fontsize=8)
    
    def _plot_boxplot(self, ax, data, column_name):
        """Plot box and whisker diagram."""
        bp = ax.boxplot(data, vert=True, patch_artist=True)
        
        # Customize colors (colorblind-friendly, brand-aligned)
        bp['boxes'][0].set_facecolor(self.SKY_BLUE)
        bp['boxes'][0].set_edgecolor(self.BLUE)
        bp['boxes'][0].set_alpha(0.7)
        bp['medians'][0].set_color(self.BLACK)
        bp['medians'][0].set_linewidth(2)
        bp['whiskers'][0].set_color(self.BLUE)
        bp['whiskers'][1].set_color(self.BLUE)
        bp['caps'][0].set_color(self.BLUE)
        bp['caps'][1].set_color(self.BLUE)
        
        for flier in bp['fliers']:
            flier.set(marker='o', markerfacecolor=self.PINK, markersize=6,
                     markeredgecolor=self.BLUE)
        
        # Add quartile labels
        q1 = np.percentile(data, 25)
        median = np.percentile(data, 50)
        q3 = np.percentile(data, 75)
        
        ax.annotate(f'Q1: {q1:.2f}', xy=(1.15, q1), xycoords=('axes fraction', 'data'),
                   fontsize=8, color=self.BLACK)
        ax.annotate(f'Median: {median:.2f}', xy=(1.15, median), xycoords=('axes fraction', 'data'),
                   fontsize=8, color=self.BLACK)
        ax.annotate(f'Q3: {q3:.2f}', xy=(1.15, q3), xycoords=('axes fraction', 'data'),
                   fontsize=8, color=self.BLACK)
        
        ax.set_title('Box and Whisker Plot', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_ylabel('Value')
        ax.set_xticklabels([column_name])
    
    def _plot_probability(self, ax, data, percentile):
        """Plot probability plot with normal distribution confidence band."""
        sorted_data = np.sort(data)
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        # Calculate plotting positions (Blom's formula for normal probability plots)
        plotting_positions = (np.arange(1, n + 1) - 0.375) / (n + 0.25)
        
        # Convert to theoretical quantiles (z-scores) for Y-axis positioning
        theoretical_quantiles = stats.norm.ppf(plotting_positions)
        
        # Expected values if data were perfectly normal
        expected_values = mean + std * theoretical_quantiles
        
        # Plot the fitted normal line (diagonal on probability scale)
        z_range = np.linspace(-3.2, 3.2, 100)
        x_fit = mean + std * z_range
        ax.plot(x_fit, z_range, color=self.BLACK, linewidth=2, zorder=2)
        
        # Calculate 95% confidence band for the fit
        # Using order statistic variance approximation
        se_multiplier = 1.0 / stats.norm.pdf(theoretical_quantiles)
        se = std * np.sqrt(plotting_positions * (1 - plotting_positions) / n) * se_multiplier
        
        # Clip extreme standard errors
        se = np.clip(se, 0, 3 * std)
        
        # Confidence band bounds (in data units)
        lower_bound = expected_values - 1.96 * se
        upper_bound = expected_values + 1.96 * se
        
        # Fill the confidence band
        ax.fill_betweenx(theoretical_quantiles, lower_bound, upper_bound, 
                        color=self.BLUE, alpha=0.15, zorder=1,
                        label='95% CI')
        
        # Plot data points (x = actual data, y = theoretical z-score)
        ax.scatter(sorted_data, theoretical_quantiles, color=self.BLUE, s=25, alpha=0.8,
                  edgecolors='white', linewidth=0.5, zorder=3)
        
        # Anderson-Darling test for normality
        ad_result = stats.anderson(data, dist='norm')
        ad_stat = ad_result.statistic
        crit_values = ad_result.critical_values
        
        # Determine p-value range
        if ad_stat < crit_values[0]:
            p_text = "p > 0.15"
        elif ad_stat < crit_values[1]:
            p_text = "p > 0.10"
        elif ad_stat < crit_values[2]:
            p_text = "p > 0.05"
        elif ad_stat < crit_values[3]:
            p_text = "p > 0.025"
        elif ad_stat < crit_values[4]:
            p_text = "p > 0.01"
        else:
            p_text = "p < 0.01"
        
        # Set probability scale ticks on Y-axis (percentage labels at z-score positions)
        prob_ticks = [0.1, 1, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 99.9]
        z_ticks = [stats.norm.ppf(p/100) for p in prob_ticks]
        ax.set_yticks(z_ticks)
        ax.set_yticklabels([f'{p:.1f}' if p < 1 or p > 99 else f'{int(p)}' for p in prob_ticks])
        ax.set_ylim(stats.norm.ppf(0.001), stats.norm.ppf(0.999))
        
        # Statistics box
        stats_text = f'Mean: {mean:.2f}\nStDev: {std:.2f}\nN: {n}\nAD: {ad_stat:.3f}\n{p_text}'
        ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=8,
               verticalalignment='bottom', horizontalalignment='right',
               fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.9))
        
        ax.set_title('Probability Plot (Normal - 95% CI)', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Value')
        ax.set_ylabel('Percent')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=8)
    
    def _plot_ichart(self, ax, data, column_name):
        """Plot I-Chart (Individuals Control Chart)."""
        limits = self.stats_engine.control_chart_limits(data)
        flagged = self.stats_engine.detect_special_causes(data)
        
        x = np.arange(1, len(data) + 1)
        
        # Plot data points
        ax.plot(x, data, color=self.BLUE, marker='o', markersize=5,
               linewidth=1, markerfacecolor=self.BLUE, markeredgecolor='white')
        
        # Highlight flagged points (out-of-control = brand burgundy)
        if flagged['all']:
            flagged_x = [i + 1 for i in flagged['all']]
            flagged_y = [data[i] for i in flagged['all']]
            ax.scatter(flagged_x, flagged_y, color=self.BRAND_BURGUNDY, s=100, zorder=5,
                      marker='o', edgecolors='#4a0919', linewidth=2)
        
        # Control limits (center = black, UCL/LCL = teal)
        ax.axhline(limits['center'], color=self.BLACK, linewidth=2, 
                  label=f'Center: {limits["center"]:.2f}')
        ax.axhline(limits['ucl'], color=self.TEAL, linewidth=1.5, linestyle='--',
                  label=f'UCL: {limits["ucl"]:.2f}')
        ax.axhline(limits['lcl'], color=self.TEAL, linewidth=1.5, linestyle='--',
                  label=f'LCL: {limits["lcl"]:.2f}')
        
        # Zone lines (lighter)
        ax.axhline(limits['zone_a_upper'], color=self.GRAY, linewidth=0.5, linestyle=':')
        ax.axhline(limits['zone_a_lower'], color=self.GRAY, linewidth=0.5, linestyle=':')
        ax.axhline(limits['zone_b_upper'], color=self.GRAY, linewidth=0.5, linestyle=':')
        ax.axhline(limits['zone_b_lower'], color=self.GRAY, linewidth=0.5, linestyle=':')
        
        ax.set_title('I-Chart (Individuals Control Chart)', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Observation')
        ax.set_ylabel('Value')
        ax.legend(loc='upper right', fontsize=8)
        
        # Add stability note
        n_flagged = len(flagged['all'])
        stability_text = f'Flagged Points: {n_flagged}'
        if n_flagged == 0:
            stability_text += '\nProcess appears STABLE'
            text_color = self.TEAL
        else:
            stability_text += '\nSpecial causes detected'
            text_color = self.BRAND_BURGUNDY
        
        ax.text(0.02, 0.02, stability_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='bottom', color=text_color,
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.9))
    
    def _plot_capability(self, ax, data, column_name):
        """Plot capability analysis chart for 4-Up - always shows Cp=1.0 natural tolerance."""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        # Cp=1.0 natural tolerance limits (always shown)
        nat_lsl = mean - 3 * std
        nat_usl = mean + 3 * std
        
        # Create histogram (sky blue fill, blue outline)
        n_bins = min(int(np.sqrt(len(data))), 20)
        n, bins, patches = ax.hist(data, bins=n_bins, color=self.SKY_BLUE, 
                                   edgecolor=self.BLUE, alpha=0.7, density=True)
        
        # Add normal curve (black)
        x = np.linspace(mean - 4*std, mean + 4*std, 100)
        y = stats.norm.pdf(x, mean, std)
        ax.plot(x, y, color=self.BLACK, linewidth=2, label='Normal Fit')
        
        # Always show Cp=1.0 natural tolerance limits (brand burgundy = spec limits)
        ax.axvline(nat_lsl, color=self.BRAND_BURGUNDY, linewidth=2, linestyle='-',
                  label=f'LSL (Cp=1): {nat_lsl:.2f}')
        ax.axvline(nat_usl, color=self.BRAND_BURGUNDY, linewidth=2, linestyle='-',
                  label=f'USL (Cp=1): {nat_usl:.2f}')
        
        # Shade outside natural tolerance (pink for out-of-spec area)
        ax.axvspan(ax.get_xlim()[0], nat_lsl, alpha=0.15, color=self.PINK)
        ax.axvspan(nat_usl, ax.get_xlim()[1], alpha=0.15, color=self.PINK)
        
        # Add mean line (teal for target)
        ax.axvline(mean, color=self.TEAL, linewidth=2, linestyle='-.',
                  label=f'Mean: {mean:.2f}')
        
        # Statistics text - Cp=1.0 baseline
        stats_text = f"N = {len(data)}\nMean = {mean:.4f}\nStDev = {std:.4f}"
        stats_text += f"\n─────────"
        stats_text += f"\nCp=1.0 Limits:"
        stats_text += f"\nLSL = {nat_lsl:.2f}"
        stats_text += f"\nUSL = {nat_usl:.2f}"
        stats_text += f"\n6σ = {6*std:.4f}"
        
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right',
               fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.9))
        
        ax.set_title('Capability (Cp=1.0 Natural Tolerance)', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.legend(loc='upper left', fontsize=7)
    
    def generate_ichart(self, data, column_name, rules=None):
        """
        Generate standalone I-Chart.
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            rules: dict specifying which Western Electric rules to apply
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 2:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(f'I-Chart: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        self._plot_ichart(ax, data, column_name)
        
        output_path = self.temp_dir / 'ichart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_imr_chart(self, data, column_name, rules=None):
        """
        Generate I-MR Chart (Individuals and Moving Range).
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            rules: dict specifying which rules to apply
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 3:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[1, 1])
        fig.suptitle(f'I-MR Chart: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        # I-Chart on top
        self._plot_ichart(ax1, data, column_name)
        ax1.set_title('Individuals Chart', fontweight='bold', color=self.BRAND_BURGUNDY)
        
        # MR Chart on bottom
        mr = np.abs(np.diff(data))
        mr_bar = np.mean(mr)
        
        # MR control limits (D4 = 3.267 for n=2)
        d4 = 3.267
        mr_ucl = d4 * mr_bar
        
        x = np.arange(2, len(data) + 1)
        
        ax2.plot(x, mr, color=self.BLUE, marker='o', markersize=5,
                linewidth=1, markerfacecolor=self.BLUE, markeredgecolor='white')
        
        ax2.axhline(mr_bar, color=self.GREEN, linewidth=2,
                   label=f'MR-bar: {mr_bar:.2f}')
        ax2.axhline(mr_ucl, color=self.BRAND_BURGUNDY, linewidth=1.5, linestyle='--',
                   label=f'UCL: {mr_ucl:.2f}')
        ax2.axhline(0, color=self.GRAY, linewidth=0.5)
        
        ax2.set_title('Moving Range Chart', fontweight='bold', color=self.BRAND_BURGUNDY)
        ax2.set_xlabel('Observation')
        ax2.set_ylabel('Moving Range')
        ax2.legend(loc='upper right', fontsize=8)
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'imr_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_mr_chart(self, data, column_name):
        """
        Generate standalone Moving Range Chart.
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 3:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.suptitle(f'Moving Range Chart: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        # Calculate moving ranges
        mr = np.abs(np.diff(data))
        mr_bar = np.mean(mr)
        
        # MR control limits (D4 = 3.267 for n=2, D3 = 0 for n=2)
        d4 = 3.267
        mr_ucl = d4 * mr_bar
        mr_lcl = 0  # D3 = 0 for n=2
        
        x = np.arange(2, len(data) + 1)
        
        # Plot MR values
        ax.plot(x, mr, color=self.BLUE, marker='o', markersize=6,
                linewidth=1.5, markerfacecolor=self.BLUE, markeredgecolor='white',
                label='Moving Range')
        
        # Center line (MR-bar)
        ax.axhline(mr_bar, color=self.BLACK, linewidth=2,
                   label=f'MR-bar: {mr_bar:.4f}')
        
        # Control limits
        ax.axhline(mr_ucl, color=self.TEAL, linewidth=1.5, linestyle='--',
                   label=f'UCL: {mr_ucl:.4f}')
        ax.axhline(mr_lcl, color=self.TEAL, linewidth=1.5, linestyle='--',
                   label=f'LCL: {mr_lcl:.4f}')
        
        # Flag out-of-control points
        for i, (xi, mri) in enumerate(zip(x, mr)):
            if mri > mr_ucl:
                ax.plot(xi, mri, 'o', color=self.BRAND_BURGUNDY, markersize=10,
                       markerfacecolor='none', markeredgewidth=2)
        
        ax.set_xlabel('Observation')
        ax.set_ylabel('Moving Range')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Add statistics box
        stats_text = (f'MR-bar = {mr_bar:.4f}\n'
                     f'UCL = {mr_ucl:.4f}\n'
                     f'LCL = {mr_lcl:.4f}\n'
                     f'n = {len(mr)}')
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'mr_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_capability_chart(self, data, column_name, lsl=None, usl=None, target=None,
                                    show_cp_one=False, cp_one_lsl=None, cp_one_usl=None):
        """
        Generate standalone Capability Analysis Chart.
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            lsl: Lower specification limit
            usl: Upper specification limit
            target: Target value
            show_cp_one: Whether to show Cp=1.0 natural tolerance limits
            cp_one_lsl: Calculated Cp=1.0 lower limit (mean - 3σ)
            cp_one_usl: Calculated Cp=1.0 upper limit (mean + 3σ)
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 2:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.suptitle(f'Capability Analysis: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        # Create histogram
        n_bins = min(int(np.sqrt(len(data))), 25)
        n, bins, patches = ax.hist(data, bins=n_bins, color=self.BLUE, 
                                   edgecolor='white', alpha=0.7, density=True)
        
        # Add normal curve
        x_range = max(data) - min(data)
        x = np.linspace(min(data) - 0.3*x_range, max(data) + 0.3*x_range, 200)
        y = stats.norm.pdf(x, mean, std)
        ax.plot(x, y, color=self.BLACK, linewidth=2.5, label='Normal Fit')
        
        # Add Cp=1.0 natural tolerance limits if requested
        if show_cp_one and cp_one_lsl is not None and cp_one_usl is not None:
            ax.axvline(cp_one_lsl, color=self.SKY_BLUE, linewidth=2, linestyle=':',
                      label=f'Cp=1.0 LSL: {cp_one_lsl:.2f}')
            ax.axvline(cp_one_usl, color=self.SKY_BLUE, linewidth=2, linestyle=':',
                      label=f'Cp=1.0 USL: {cp_one_usl:.2f}')
            # Light shading for natural tolerance zone
            ax.axvspan(cp_one_lsl, cp_one_usl, alpha=0.05, color=self.SKY_BLUE)
        
        # Add specification limits
        if lsl is not None:
            ax.axvline(lsl, color=self.BRAND_BURGUNDY, linewidth=2.5, linestyle='-',
                      label=f'LSL: {lsl:.2f}')
            # Shade out-of-spec region
            x_min = ax.get_xlim()[0]
            ax.axvspan(x_min, lsl, alpha=0.15, color=self.BRAND_BURGUNDY)
        
        if usl is not None:
            ax.axvline(usl, color=self.BRAND_BURGUNDY, linewidth=2.5, linestyle='-',
                      label=f'USL: {usl:.2f}')
            # Shade out-of-spec region
            x_max = ax.get_xlim()[1]
            ax.axvspan(usl, x_max, alpha=0.15, color=self.BRAND_BURGUNDY)
        
        if target is not None:
            ax.axvline(target, color=self.GREEN, linewidth=2.5, linestyle='--',
                      label=f'Target: {target:.2f}')
        
        # Add mean line
        ax.axvline(mean, color=self.PURPLE, linewidth=2, linestyle='-.',
                  label=f'Mean: {mean:.2f}')
        
        # Calculate and display capability indices
        stats_text = f"Process Statistics\n"
        stats_text += f"══════════════════\n"
        stats_text += f"N = {len(data)}\n"
        stats_text += f"Mean = {mean:.4f}\n"
        stats_text += f"StDev = {std:.4f}\n"
        stats_text += f"6σ = {6*std:.4f}\n"
        
        if lsl is not None and usl is not None and std > 0:
            cp = (usl - lsl) / (6 * std)
            cpu = (usl - mean) / (3 * std)
            cpl = (mean - lsl) / (3 * std)
            cpk = min(cpu, cpl)
            
            # PPM calculations
            ppm_below = stats.norm.cdf(lsl, mean, std) * 1e6
            ppm_above = (1 - stats.norm.cdf(usl, mean, std)) * 1e6
            ppm_total = ppm_below + ppm_above
            
            stats_text += f"\nCapability Indices\n"
            stats_text += f"══════════════════\n"
            stats_text += f"Cp = {cp:.3f}\n"
            stats_text += f"Cpk = {cpk:.3f}\n"
            stats_text += f"Cpu = {cpu:.3f}\n"
            stats_text += f"Cpl = {cpl:.3f}\n"
            stats_text += f"\nExpected Defects\n"
            stats_text += f"══════════════════\n"
            stats_text += f"PPM Total: {ppm_total:.0f}\n"
            
            # Add capability rating
            if cpk >= 1.33:
                stats_text += f"\n✓ CAPABLE"
            elif cpk >= 1.0:
                stats_text += f"\n⚠ MARGINAL"
            else:
                stats_text += f"\n✗ NOT CAPABLE"
        
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right',
               fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.95))
        
        ax.set_xlabel('Value', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'capability_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_multi_probability_plot(self, datasets, labels, title="Probability Plot Comparison"):
        """
        Generate probability plot with multiple data series.
        Uses probability scale on Y-axis with 95% confidence bands.
        
        Args:
            datasets: List of data arrays to compare
            labels: List of labels for each dataset
            title: Chart title
            
        Returns:
            str: Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = self.COLOR_CYCLE
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p']
        
        # Statistics table data
        stats_rows = []
        
        for i, (data, label) in enumerate(zip(datasets, labels)):
            data = np.array(data)
            data = data[~np.isnan(data)]
            
            if len(data) < 2:
                continue
            
            sorted_data = np.sort(data)
            n = len(data)
            mean = np.mean(data)
            std = np.std(data, ddof=1)
            
            # Calculate plotting positions (Blom's formula)
            plotting_positions = (np.arange(1, n + 1) - 0.375) / (n + 0.25)
            theoretical_quantiles = stats.norm.ppf(plotting_positions)
            
            color = colors[i % len(colors)]
            marker = markers[i % len(markers)]
            
            # Plot the fitted normal line
            z_range = np.linspace(-3.2, 3.2, 100)
            x_fit = mean + std * z_range
            ax.plot(x_fit, z_range, color=color, linewidth=1.5, linestyle='--', alpha=0.7)
            
            # Calculate 95% confidence band
            expected_values = mean + std * theoretical_quantiles
            se_multiplier = 1.0 / stats.norm.pdf(theoretical_quantiles)
            se = std * np.sqrt(plotting_positions * (1 - plotting_positions) / n) * se_multiplier
            se = np.clip(se, 0, 3 * std)
            
            lower_bound = expected_values - 1.96 * se
            upper_bound = expected_values + 1.96 * se
            
            # Fill confidence band (lighter for multiple series)
            ax.fill_betweenx(theoretical_quantiles, lower_bound, upper_bound, 
                            color=color, alpha=0.08, zorder=1)
            
            # Plot data points
            ax.scatter(sorted_data, theoretical_quantiles, color=color, s=35, alpha=0.8,
                      marker=marker, edgecolors='white', linewidth=0.5, zorder=3,
                      label=f'{label} (n={n})')
            
            # Anderson-Darling test
            ad_result = stats.anderson(data, dist='norm')
            ad_stat = ad_result.statistic
            crit_values = ad_result.critical_values
            if ad_stat < crit_values[2]:
                p_text = ">0.05"
            else:
                p_text = "<0.05"
            
            stats_rows.append(f'{label}: Mean={mean:.2f}, StDev={std:.2f}, AD={ad_stat:.3f}, p{p_text}')
        
        # Set probability scale ticks on Y-axis
        prob_ticks = [0.1, 1, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 99.9]
        z_ticks = [stats.norm.ppf(p/100) for p in prob_ticks]
        ax.set_yticks(z_ticks)
        ax.set_yticklabels([f'{p:.1f}' if p < 1 or p > 99 else f'{int(p)}' for p in prob_ticks])
        ax.set_ylim(stats.norm.ppf(0.001), stats.norm.ppf(0.999))
        
        ax.set_title(f'{title}\nNormal - 95% CI', fontsize=14, fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Value', fontsize=11)
        ax.set_ylabel('Percent', fontsize=11)
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Statistics summary in corner
        stats_text = '\n'.join(stats_rows)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=8, 
               ha='left', va='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY, alpha=0.9))
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'multi_probability_plot.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_pareto(self, data, category_column, value_column=None):
        """
        Generate Pareto Chart.
        
        Args:
            data: pandas DataFrame
            category_column: Column containing categories
            value_column: Optional column for values (if None, counts categories)
            
        Returns:
            str: Path to generated chart image
        """
        if value_column:
            grouped = data.groupby(category_column)[value_column].sum().sort_values(ascending=False)
        else:
            grouped = data[category_column].value_counts()
        
        # Limit to top 10 categories + "Other"
        if len(grouped) > 10:
            top_10 = grouped.head(10)
            other = grouped.iloc[10:].sum()
            grouped = pd.concat([top_10, pd.Series({'Other': other})])
        
        # Calculate cumulative percentage
        total = grouped.sum()
        cumulative_pct = (grouped.cumsum() / total * 100).values
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Bar chart
        x = np.arange(len(grouped))
        bars = ax1.bar(x, grouped.values, color=self.BLUE, edgecolor='white')
        
        # Highlight vital few (80%)
        vital_idx = np.where(cumulative_pct <= 80)[0]
        for idx in vital_idx:
            bars[idx].set_color(self.BLUE)
        for idx in range(len(vital_idx), len(bars)):
            bars[idx].set_color(self.GRAY)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(grouped.index, rotation=45, ha='right')
        ax1.set_ylabel('Count / Value', color=self.BRAND_BURGUNDY)
        ax1.tick_params(axis='y', labelcolor=self.BRAND_BURGUNDY)
        
        # Cumulative line (secondary y-axis - teal for contrast)
        ax2 = ax1.twinx()
        ax2.plot(x, cumulative_pct, color=self.TEAL, marker='o', markersize=6,
                linewidth=2, markerfacecolor=self.TEAL, markeredgecolor='white')
        ax2.set_ylabel('Cumulative %', color=self.TEAL)
        ax2.tick_params(axis='y', labelcolor=self.TEAL)
        ax2.set_ylim(0, 105)
        
        # 80% line
        ax2.axhline(80, color=self.TEAL, linestyle='--', linewidth=1.5, alpha=0.7)
        ax2.text(len(x) - 0.5, 82, '80%', fontsize=9, color=self.TEAL)
        
        fig.suptitle(f'Pareto Chart: {category_column}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        
        # Add vital few annotation
        n_vital = len(vital_idx)
        if n_vital > 0:
            vital_pct = cumulative_pct[n_vital - 1] if n_vital > 0 else 0
            ax1.text(0.02, 0.98, f'Vital Few: {n_vital} categories\n({vital_pct:.1f}% of total)',
                    transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', edgecolor=self.GRAY))
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'pareto_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_histogram(self, data, column_name, bins='auto'):
        """
        Generate standalone histogram.
        
        Args:
            data: pandas Series or array-like of numeric data
            column_name: Name of the data column
            bins: Number of bins or 'auto'
            
        Returns:
            str: Path to generated chart image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if bins == 'auto':
            n_bins = min(int(np.sqrt(len(data))), 30)
        else:
            n_bins = bins
        
        ax.hist(data, bins=n_bins, color=self.BLUE, edgecolor='white', alpha=0.8)
        
        mean = np.mean(data)
        ax.axvline(mean, color=self.TEAL, linestyle='--', linewidth=2,
                  label=f'Mean: {mean:.2f}')
        
        ax.set_title(f'Histogram: {column_name}', fontsize=14, fontweight='bold',
                    color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        output_path = self.temp_dir / 'histogram.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_scatter(self, x_data, y_data, x_name, y_name):
        """
        Generate scatter plot.
        
        Args:
            x_data: X-axis data
            y_data: Y-axis data
            x_name: X-axis label
            y_name: Y-axis label
            
        Returns:
            str: Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.scatter(x_data, y_data, color=self.BLUE, s=50, alpha=0.7,
                  edgecolors='white', linewidth=0.5)
        
        # Add regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
        x_fit = np.array([min(x_data), max(x_data)])
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, color=self.BLACK, linewidth=2,
               label=f'R² = {r_value**2:.4f}')
        
        ax.set_title(f'Scatter Plot: {y_name} vs {x_name}', fontsize=14,
                    fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.legend()
        
        output_path = self.temp_dir / 'scatter.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_anova_boxplot(self, data, value_column, group_column, title=None):
        """
        Generate box plots grouped by a categorical factor for ANOVA visualization.
        
        Parameters:
            data: pandas DataFrame
            value_column: Name of the numeric column (Y variable)
            group_column: Name of the categorical column (factor)
            title: Optional chart title
            
        Returns:
            Path to saved image
        """
        # Get unique groups and their data
        groups = data[group_column].dropna().unique()
        group_data = [data[data[group_column] == g][value_column].dropna().values for g in groups]
        
        # Filter out empty groups
        valid_groups = []
        valid_data = []
        for g, d in zip(groups, group_data):
            if len(d) > 0:
                valid_groups.append(str(g))
                valid_data.append(d)
        
        if not valid_data:
            raise ValueError("No valid data for box plot")
        
        # Calculate figure width based on number of groups
        n_groups = len(valid_groups)
        fig_width = max(8, min(14, 3 + n_groups * 1.2))
        
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        
        # Create box plot
        bp = ax.boxplot(valid_data, labels=valid_groups, patch_artist=True,
                       medianprops={'color': self.BLUE, 'linewidth': 2},
                       whiskerprops={'color': self.BLUE, 'linewidth': 1.5},
                       capprops={'color': self.BLUE, 'linewidth': 1.5},
                       flierprops={'marker': 'o', 'markerfacecolor': self.PINK, 
                                  'markeredgecolor': self.BLUE, 'markersize': 6})
        
        # Color the boxes (colorblind-accessible palette)
        colors = [self.BLUE, self.TEAL, self.SKY_BLUE, self.PINK, 
                  self.INDIGO, self.CYAN, self.OLIVE, '#44AA99']
        for i, patch in enumerate(bp['boxes']):
            color = colors[i % len(colors)]
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            patch.set_edgecolor(self.BLACK)
            patch.set_linewidth(1.5)
        
        # Add individual data points (jittered)
        for i, (group_vals, group_name) in enumerate(zip(valid_data, valid_groups)):
            # Add jitter to x position
            x = np.random.normal(i + 1, 0.04, size=len(group_vals))
            ax.scatter(x, group_vals, alpha=0.4, color='black', s=20, zorder=3)
        
        # Add mean markers
        means = [np.mean(d) for d in valid_data]
        ax.scatter(range(1, n_groups + 1), means, marker='D', color=self.BRAND_BURGUNDY, 
                  s=50, zorder=4, label='Mean')
        
        # Calculate and display group statistics
        stats_text = "Group Statistics:\n"
        for g, d in zip(valid_groups, valid_data):
            stats_text += f"  {g}: n={len(d)}, mean={np.mean(d):.2f}, std={np.std(d, ddof=1):.2f}\n"
        
        # Add statistics as text box
        props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=self.GRAY)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=8,
               verticalalignment='top', fontfamily='monospace', bbox=props)
        
        # Styling
        chart_title = title or f'Box Plot: {value_column} by {group_column}'
        ax.set_title(chart_title, fontsize=14, fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel(group_column, fontsize=11, fontweight='bold')
        ax.set_ylabel(value_column, fontsize=11, fontweight='bold')
        
        # Rotate x labels if many groups
        if n_groups > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Add grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        
        # Add legend
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'anova_boxplot.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_correlation_scatter(self, x_data, y_data, x_name, y_name, 
                                     correlation_results=None, show_regression=True):
        """
        Generate a scatter plot with correlation analysis.
        
        Parameters:
            x_data: X variable data
            y_data: Y variable data
            x_name: Name of X variable
            y_name: Name of Y variable
            correlation_results: Dict from correlation_analysis (optional)
            show_regression: Whether to show regression line
            
        Returns:
            Path to saved image
        """
        x = np.array(x_data)
        y = np.array(y_data)
        
        # Remove pairs with NaN
        valid_mask = ~(np.isnan(x) | np.isnan(y))
        x = x[valid_mask]
        y = y[valid_mask]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        ax.scatter(x, y, color=self.BLUE, alpha=0.6, s=50, edgecolors='white', linewidth=0.5)
        
        # Add regression line if requested
        if show_regression and len(x) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            x_line = np.array([np.min(x), np.max(x)])
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, color=self.BLACK, linewidth=2.5, 
                   label=f'Regression: y = {slope:.4f}x + {intercept:.4f}')
            
            # Add confidence band (approximate)
            y_pred = slope * x + intercept
            residuals = y - y_pred
            std_resid = np.std(residuals)
            ax.fill_between(x_line, y_line - 2*std_resid, y_line + 2*std_resid, 
                           color=self.SKY_BLUE, alpha=0.15, label='95% Prediction Band')
        
        # Add statistics box
        if correlation_results:
            r = correlation_results.get('r', 0)
            r_sq = correlation_results.get('r_squared', 0)
            p = correlation_results.get('p_value', 1)
            n = correlation_results.get('n', len(x))
            strength = correlation_results.get('strength', '')
            direction = correlation_results.get('direction', '')
            
            stats_text = f"Correlation Analysis\n"
            stats_text += f"─────────────────\n"
            stats_text += f"n = {n}\n"
            stats_text += f"r = {r:.4f}\n"
            stats_text += f"R² = {r_sq:.4f}\n"
            stats_text += f"p-value = {p:.4f}\n"
            stats_text += f"─────────────────\n"
            stats_text += f"{strength} {direction}"
            
            # Significance indicator
            if p <= 0.05:
                stats_text += "\n★ Significant"
            
            props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=self.BRAND_BURGUNDY)
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', fontfamily='monospace', bbox=props)
        
        # Styling
        ax.set_title(f'Correlation: {y_name} vs {x_name}', fontsize=14, 
                    fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel(x_name, fontsize=11, fontweight='bold')
        ax.set_ylabel(y_name, fontsize=11, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'correlation_scatter.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_run_chart(self, data, column_name, run_results=None):
        """
        Generate a run chart (sequential plot with median line, no control limits).
        
        Parameters:
            data: Numeric data array
            column_name: Name of the measure
            run_results: Dict from run_chart_analysis (optional)
            
        Returns:
            Path to saved image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot data points connected by lines
        x = np.arange(1, n + 1)
        ax.plot(x, data, color=self.BLUE, linewidth=1.5, marker='o', 
               markersize=6, markerfacecolor=self.BLUE, markeredgecolor='white',
               markeredgewidth=1, label='Data')
        
        # Median line
        median = np.median(data) if n > 0 else 0
        ax.axhline(y=median, color=self.BLACK, linewidth=2, linestyle='-', 
                  label=f'Median = {median:.2f}')
        
        # Mean line (dashed)
        mean = np.mean(data) if n > 0 else 0
        ax.axhline(y=mean, color=self.GRAY, linewidth=1.5, linestyle='--',
                  label=f'Mean = {mean:.2f}')
        
        # Color points above/below median differently
        above = data > median
        below = data < median
        ax.scatter(x[above], data[above], color='#4a7c59', s=60, zorder=5, 
                  edgecolors='white', linewidth=1)
        ax.scatter(x[below], data[below], color='#c44536', s=60, zorder=5,
                  edgecolors='white', linewidth=1)
        
        # Add run analysis box if provided
        if run_results:
            n_runs = run_results.get('n_runs', 0)
            expected = run_results.get('expected_runs', 0)
            p_value = run_results.get('p_value', 1)
            is_random = run_results.get('is_random', True)
            
            stats_text = f"Run Chart Analysis\n"
            stats_text += f"─────────────────\n"
            stats_text += f"n = {n}\n"
            stats_text += f"Runs = {n_runs}\n"
            stats_text += f"Expected = {expected:.1f}\n"
            stats_text += f"p-value = {p_value:.4f}\n"
            stats_text += f"─────────────────\n"
            if is_random:
                stats_text += "✓ Random pattern"
            else:
                stats_text += "⚠ Non-random pattern"
            
            props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=self.BRAND_BURGUNDY)
            ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', horizontalalignment='right',
                   fontfamily='monospace', bbox=props)
        
        # Styling
        ax.set_title(f'Run Chart: {column_name}', fontsize=14, fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel('Observation', fontsize=11, fontweight='bold')
        ax.set_ylabel(column_name, fontsize=11, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Note explaining difference from control chart
        ax.text(0.5, -0.12, 'Note: Run chart shows sequential data with median line. '
               'No control limits - use I-Chart for Statistical Process Control.',
               transform=ax.transAxes, fontsize=8, ha='center', style='italic', color=self.GRAY)
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'run_chart.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_standalone_histogram(self, data, column_name, bins='auto', show_normal=True):
        """
        Generate a standalone histogram with distribution statistics.
        
        Parameters:
            data: Numeric data array
            column_name: Name of the measure
            bins: Number of bins or 'auto'
            show_normal: Whether to overlay normal distribution curve
            
        Returns:
            Path to saved image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n == 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
            output_path = self.temp_dir / 'histogram.png'
            fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            return str(output_path)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Calculate statistics
        mean = np.mean(data)
        median = np.median(data)
        std = np.std(data, ddof=1)
        min_val = np.min(data)
        max_val = np.max(data)
        
        # Create histogram
        counts, bin_edges, patches = ax.hist(data, bins=bins, color=self.BLUE, 
                                             edgecolor='white', alpha=0.7, density=True)
        
        # Overlay normal distribution curve if requested
        if show_normal and std > 0:
            x_norm = np.linspace(min_val - std, max_val + std, 100)
            y_norm = stats.norm.pdf(x_norm, mean, std)
            ax.plot(x_norm, y_norm, color=self.BLACK, linewidth=2.5, 
                   label='Normal Distribution')
        
        # Add vertical lines for mean and median
        ax.axvline(x=mean, color=self.TEAL, linewidth=2, linestyle='-', label=f'Mean = {mean:.2f}')
        ax.axvline(x=median, color=self.PINK, linewidth=2, linestyle='--', label=f'Median = {median:.2f}')
        
        # Statistics box
        # Skewness and kurtosis
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        stats_text = f"Distribution Statistics\n"
        stats_text += f"───────────────────\n"
        stats_text += f"n = {n}\n"
        stats_text += f"Mean = {mean:.4f}\n"
        stats_text += f"Median = {median:.4f}\n"
        stats_text += f"Std Dev = {std:.4f}\n"
        stats_text += f"Min = {min_val:.4f}\n"
        stats_text += f"Max = {max_val:.4f}\n"
        stats_text += f"Range = {max_val - min_val:.4f}\n"
        stats_text += f"───────────────────\n"
        stats_text += f"Skewness = {skewness:.4f}\n"
        stats_text += f"Kurtosis = {kurtosis:.4f}"
        
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=self.BRAND_BURGUNDY)
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right',
               fontfamily='monospace', bbox=props)
        
        # Styling
        ax.set_title(f'Histogram: {column_name}', fontsize=14, fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_xlabel(column_name, fontsize=11, fontweight='bold')
        ax.set_ylabel('Density', fontsize=11, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'histogram.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
    
    def generate_standalone_boxplot(self, data, column_name, show_points=True):
        """
        Generate a standalone box plot with statistics.
        
        Parameters:
            data: Numeric data array
            column_name: Name of the measure
            show_points: Whether to show individual data points
            
        Returns:
            Path to saved image
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n == 0:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
            output_path = self.temp_dir / 'boxplot.png'
            fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            return str(output_path)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Calculate statistics
        mean = np.mean(data)
        median = np.median(data)
        std = np.std(data, ddof=1)
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        min_val = np.min(data)
        max_val = np.max(data)
        
        # Identify outliers
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = data[(data < lower_fence) | (data > upper_fence)]
        n_outliers = len(outliers)
        
        # Create box plot
        bp = ax.boxplot([data], patch_artist=True, widths=0.5,
                       medianprops={'color': 'red', 'linewidth': 2},
                       whiskerprops={'color': self.BLUE, 'linewidth': 1.5},
                       capprops={'color': self.BLUE, 'linewidth': 1.5},
                       flierprops={'marker': 'o', 'markerfacecolor': self.PINK, 
                                  'markeredgecolor': self.BLUE, 'markersize': 8})
        
        # Color the box
        bp['boxes'][0].set_facecolor(self.BLUE)
        bp['boxes'][0].set_alpha(0.7)
        bp['boxes'][0].set_edgecolor(self.BLUE)
        bp['boxes'][0].set_linewidth(2)
        
        # Add mean marker
        ax.scatter([1], [mean], marker='D', color=self.TEAL, s=100, zorder=5, 
                  label=f'Mean = {mean:.2f}')
        
        # Add jittered data points if requested
        if show_points:
            jitter = np.random.normal(0, 0.04, size=n)
            ax.scatter(1 + jitter, data, alpha=0.4, color='black', s=20, zorder=3)
        
        # Statistics box
        stats_text = f"Box Plot Statistics\n"
        stats_text += f"─────────────────\n"
        stats_text += f"n = {n}\n"
        stats_text += f"Mean = {mean:.4f}\n"
        stats_text += f"Median = {median:.4f}\n"
        stats_text += f"Std Dev = {std:.4f}\n"
        stats_text += f"─────────────────\n"
        stats_text += f"Q1 (25%) = {q1:.4f}\n"
        stats_text += f"Q3 (75%) = {q3:.4f}\n"
        stats_text += f"IQR = {iqr:.4f}\n"
        stats_text += f"─────────────────\n"
        stats_text += f"Min = {min_val:.4f}\n"
        stats_text += f"Max = {max_val:.4f}\n"
        stats_text += f"Outliers = {n_outliers}"
        
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=self.BRAND_BURGUNDY)
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', horizontalalignment='right',
               fontfamily='monospace', bbox=props)
        
        # Add annotations for quartiles
        ax.annotate(f'Q3: {q3:.2f}', xy=(1.3, q3), fontsize=9, color=self.GRAY)
        ax.annotate(f'Median: {median:.2f}', xy=(1.3, median), fontsize=9, color=self.BRAND_BURGUNDY)
        ax.annotate(f'Q1: {q1:.2f}', xy=(1.3, q1), fontsize=9, color=self.GRAY)
        
        # Styling
        ax.set_title(f'Box Plot: {column_name}', fontsize=14, fontweight='bold', color=self.BRAND_BURGUNDY)
        ax.set_ylabel(column_name, fontsize=11, fontweight='bold')
        ax.set_xticks([])
        ax.legend(loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = self.temp_dir / 'boxplot.png'
        fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        return str(output_path)
