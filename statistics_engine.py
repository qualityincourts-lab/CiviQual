#!/usr/bin/env python3
"""
CiviQual Stats Statistics Engine

Provides statistical analysis capabilities for Lean Six Sigma practitioners.

Copyright (c) 2026 A Step in the Right Direction LLC
All Rights Reserved.
"""

import numpy as np
import pandas as pd
from scipy import stats


class StatisticsEngine:
    """Statistical analysis engine for CiviQual Stats."""
    
    def __init__(self):
        """Initialize the statistics engine."""
        pass
    
    def descriptive_stats(self, data):
        """
        Calculate comprehensive descriptive statistics.
        
        Args:
            data: pandas Series or array-like of numeric data
            
        Returns:
            dict: Dictionary containing all descriptive statistics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        n = len(data)
        
        if n == 0:
            return self._empty_stats()
        
        # Central tendency
        mean = np.mean(data)
        median = np.median(data)
        
        # Mode calculation
        try:
            mode_result = stats.mode(data, keepdims=True)
            mode = mode_result.mode[0]
        except Exception:
            mode = mean  # Fallback
        
        # Dispersion
        std = np.std(data, ddof=1) if n > 1 else 0
        variance = np.var(data, ddof=1) if n > 1 else 0
        data_min = np.min(data)
        data_max = np.max(data)
        data_range = data_max - data_min
        
        # Quartiles
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # Shape
        skewness = stats.skew(data) if n > 2 else 0
        kurtosis = stats.kurtosis(data) if n > 3 else 0
        
        # Normality test (Anderson-Darling)
        try:
            ad_result = stats.anderson(data, dist='norm')
            ad_stat = ad_result.statistic
            ad_critical = ad_result.critical_values[2]  # 5% significance
            is_normal = ad_stat < ad_critical
        except Exception:
            ad_stat = None
            ad_critical = None
            is_normal = None
        
        # Standard error
        se_mean = std / np.sqrt(n) if n > 0 else 0
        
        # Confidence interval for mean (95%)
        if n > 1:
            t_crit = stats.t.ppf(0.975, n - 1)
            ci_lower = mean - t_crit * se_mean
            ci_upper = mean + t_crit * se_mean
        else:
            ci_lower = ci_upper = mean
        
        return {
            'n': n,
            'mean': mean,
            'median': median,
            'mode': mode,
            'std': std,
            'variance': variance,
            'min': data_min,
            'max': data_max,
            'range': data_range,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'se_mean': se_mean,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'ad_stat': ad_stat,
            'ad_critical': ad_critical,
            'is_normal': is_normal
        }
    
    def _empty_stats(self):
        """Return empty statistics dictionary."""
        return {
            'n': 0,
            'mean': 0,
            'median': 0,
            'mode': 0,
            'std': 0,
            'variance': 0,
            'min': 0,
            'max': 0,
            'range': 0,
            'q1': 0,
            'q3': 0,
            'iqr': 0,
            'skewness': 0,
            'kurtosis': 0,
            'se_mean': 0,
            'ci_lower': 0,
            'ci_upper': 0,
            'ad_stat': None,
            'ad_critical': None,
            'is_normal': None
        }
    
    def anderson_darling_test(self, data):
        """
        Perform Anderson-Darling test for normality.
        
        Args:
            data: pandas Series or array-like of numeric data
            
        Returns:
            tuple: (statistic, critical_values, significance_levels)
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 3:
            return 0, [0, 0, 0, 0, 0], [15, 10, 5, 2.5, 1]
        
        try:
            ad_result = stats.anderson(data, dist='norm')
            return ad_result.statistic, ad_result.critical_values, ad_result.significance_level
        except Exception:
            return 0, [0, 0, 0, 0, 0], [15, 10, 5, 2.5, 1]
    
    def control_chart_limits(self, data):
        """
        Calculate control chart limits for I-Chart.
        
        Uses moving range method for calculating limits.
        
        Args:
            data: pandas Series or array-like of numeric data
            
        Returns:
            dict: Control limits and related values
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        n = len(data)
        
        if n < 2:
            return None
        
        # Calculate center line (mean)
        center = np.mean(data)
        
        # Calculate moving ranges
        mr = np.abs(np.diff(data))
        mr_bar = np.mean(mr)
        
        # d2 constant for n=2 (moving range of 2 consecutive points)
        d2 = 1.128
        
        # Estimate sigma using moving range method
        sigma = mr_bar / d2
        
        # Control limits
        ucl = center + 3 * sigma
        lcl = center - 3 * sigma
        
        # Zone boundaries
        zone_a_upper = center + 2 * sigma
        zone_a_lower = center - 2 * sigma
        zone_b_upper = center + 1 * sigma
        zone_b_lower = center - 1 * sigma
        
        return {
            'center': center,
            'ucl': ucl,
            'lcl': lcl,
            'sigma': sigma,
            'mr_bar': mr_bar,
            'zone_a_upper': zone_a_upper,
            'zone_a_lower': zone_a_lower,
            'zone_b_upper': zone_b_upper,
            'zone_b_lower': zone_b_lower,
            'n': n
        }
    
    def detect_special_causes(self, data, rules=None):
        """
        Detect special cause variation using Western Electric rules.
        
        Args:
            data: pandas Series or array-like of numeric data
            rules: dict specifying which rules to apply
            
        Returns:
            dict: Lists of indices flagged by each rule
        """
        if rules is None:
            rules = {'rule1': True, 'rule2': True, 'rule3': True, 'rule4': True, 'rule5': True, 'rule6': True}
        
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        limits = self.control_chart_limits(data)
        if limits is None:
            return {'rule1': [], 'rule2': [], 'rule3': [], 'rule4': [], 'rule5': [], 'rule6': [], 'all': []}
        
        center = limits['center']
        sigma = limits['sigma']
        ucl = limits['ucl']
        lcl = limits['lcl']
        
        flagged = {
            'rule1': [],
            'rule2': [],
            'rule3': [],
            'rule4': [],
            'rule5': [],
            'rule6': [],
            'all': set()
        }
        
        n = len(data)
        
        # Rule 1: Point beyond 3 sigma
        if rules.get('rule1', True):
            for i in range(n):
                if data[i] > ucl or data[i] < lcl:
                    flagged['rule1'].append(i)
                    flagged['all'].add(i)
        
        # Rule 2: 2 of 3 consecutive points beyond 2 sigma (same side)
        if rules.get('rule2', True):
            two_sigma_upper = center + 2 * sigma
            two_sigma_lower = center - 2 * sigma
            
            for i in range(2, n):
                window = data[i-2:i+1]
                above = sum(w > two_sigma_upper for w in window)
                below = sum(w < two_sigma_lower for w in window)
                
                if above >= 2 or below >= 2:
                    flagged['rule2'].append(i)
                    flagged['all'].add(i)
        
        # Rule 3: 4 of 5 consecutive points beyond 1 sigma (same side)
        if rules.get('rule3', True):
            one_sigma_upper = center + sigma
            one_sigma_lower = center - sigma
            
            for i in range(4, n):
                window = data[i-4:i+1]
                above = sum(w > one_sigma_upper for w in window)
                below = sum(w < one_sigma_lower for w in window)
                
                if above >= 4 or below >= 4:
                    flagged['rule3'].append(i)
                    flagged['all'].add(i)
        
        # Rule 4: 8 consecutive points on one side of center
        if rules.get('rule4', True):
            for i in range(7, n):
                window = data[i-7:i+1]
                above = sum(w > center for w in window)
                below = sum(w < center for w in window)
                
                if above == 8 or below == 8:
                    flagged['rule4'].append(i)
                    flagged['all'].add(i)
        
        # Rule 5: 6 consecutive points steadily increasing or decreasing (trend)
        if rules.get('rule5', True):
            for i in range(5, n):
                window = data[i-5:i+1]
                increasing = all(window[j] < window[j+1] for j in range(5))
                decreasing = all(window[j] > window[j+1] for j in range(5))
                
                if increasing or decreasing:
                    flagged['rule5'].append(i)
                    flagged['all'].add(i)
        
        # Rule 6: 14 consecutive points alternating up and down
        if rules.get('rule6', True):
            for i in range(13, n):
                window = data[i-13:i+1]
                alternating = True
                for j in range(13):
                    if j % 2 == 0:
                        if window[j] >= window[j+1]:
                            alternating = False
                            break
                    else:
                        if window[j] <= window[j+1]:
                            alternating = False
                            break
                
                if not alternating:
                    # Try the opposite pattern
                    alternating = True
                    for j in range(13):
                        if j % 2 == 0:
                            if window[j] <= window[j+1]:
                                alternating = False
                                break
                        else:
                            if window[j] >= window[j+1]:
                                alternating = False
                                break
                
                if alternating:
                    flagged['rule6'].append(i)
                    flagged['all'].add(i)
        
        flagged['all'] = list(flagged['all'])
        return flagged
    
    def capability_analysis(self, data, lsl=None, usl=None):
        """
        Perform process capability analysis.
        
        Args:
            data: pandas Series or array-like of numeric data
            lsl: Lower specification limit
            usl: Upper specification limit
            
        Returns:
            dict: Capability indices and related values
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        n = len(data)
        
        if n < 2:
            return None
        
        mean = np.mean(data)
        
        # Calculate StDev(Within) using moving range method
        mr = np.abs(np.diff(data))
        mr_bar = np.mean(mr)
        d2 = 1.128
        std_within = mr_bar / d2
        
        # Calculate StDev(Overall)
        std_overall = np.std(data, ddof=1)
        
        results = {
            'n': n,
            'mean': mean,
            'std_within': std_within,
            'std_overall': std_overall,
            'lsl': lsl,
            'usl': usl,
            'cp': None,
            'cpk': None,
            'cpu': None,
            'cpl': None,
            'pp': None,
            'ppk': None
        }
        
        if usl is not None and lsl is not None:
            # Both limits specified
            results['cp'] = (usl - lsl) / (6 * std_within)
            results['pp'] = (usl - lsl) / (6 * std_overall)
            
            cpu = (usl - mean) / (3 * std_within)
            cpl = (mean - lsl) / (3 * std_within)
            results['cpu'] = cpu
            results['cpl'] = cpl
            results['cpk'] = min(cpu, cpl)
            
            ppu = (usl - mean) / (3 * std_overall)
            ppl = (mean - lsl) / (3 * std_overall)
            results['ppk'] = min(ppu, ppl)
            
        elif usl is not None:
            # Only upper limit
            results['cpu'] = (usl - mean) / (3 * std_within)
            results['cpk'] = results['cpu']
            
        elif lsl is not None:
            # Only lower limit
            results['cpl'] = (mean - lsl) / (3 * std_within)
            results['cpk'] = results['cpl']
        
        # Calculate USL at Cp=1.00 (minimum capable performance)
        results['usl_at_cp1'] = mean + 3 * std_within
        results['lsl_at_cp1'] = mean - 3 * std_within
        
        return results
    
    def run_anova(self, data, response_col, factor_col):
        """
        Perform one-way ANOVA.
        
        Args:
            data: pandas DataFrame
            response_col: Name of response (Y) column
            factor_col: Name of factor (X) column
            
        Returns:
            dict: ANOVA results
        """
        groups = []
        valid_group_names = []  # Track only groups that have data
        
        for name in data[factor_col].unique():
            group_data = data[data[factor_col] == name][response_col].dropna()
            if len(group_data) > 0:
                groups.append(group_data.values)
                valid_group_names.append(name)  # Only add if group has data
        
        if len(groups) < 2:
            return {
                'f_stat': 0,
                'p_value': 1.0,
                'df_between': 0,
                'df_within': 0,
                'ss_between': 0,
                'ss_within': 0,
                'ms_between': 0,
                'ms_within': 0,
                'group_means': {},
                'group_stds': {},
                'group_ns': {}
            }
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        
        # Calculate additional statistics
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)
        
        n_groups = len(groups)
        n_total = len(all_data)
        
        # Sum of squares
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_within = sum(sum((x - np.mean(g))**2 for x in g) for g in groups)
        ss_total = sum((x - grand_mean)**2 for x in all_data)
        
        df_between = n_groups - 1
        df_within = n_total - n_groups
        
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 0
        
        # Group statistics - use valid_group_names which matches groups list
        group_means = {str(name): np.mean(groups[i]) for i, name in enumerate(valid_group_names)}
        group_stds = {str(name): np.std(groups[i], ddof=1) for i, name in enumerate(valid_group_names)}
        group_ns = {str(name): len(groups[i]) for i, name in enumerate(valid_group_names)}
        
        return {
            'f_stat': f_stat if not np.isnan(f_stat) else 0,
            'p_value': p_value if not np.isnan(p_value) else 1.0,
            'df_between': df_between,
            'df_within': df_within,
            'ss_between': ss_between,
            'ss_within': ss_within,
            'ss_total': ss_total,
            'ms_between': ms_between,
            'ms_within': ms_within,
            'eta_squared': ss_between / ss_total if ss_total > 0 else 0,
            'group_means': group_means,
            'group_stds': group_stds,
            'group_ns': group_ns
        }
    
    def tukey_hsd(self, data, response_col, factor_col):
        """
        Perform Tukey's Honest Significant Difference post-hoc test.
        
        Args:
            data: pandas DataFrame
            response_col: Name of response (Y) column
            factor_col: Name of factor (X) column
            
        Returns:
            list: List of dicts with pairwise comparisons
        """
        from scipy.stats import studentized_range
        
        groups = []
        valid_group_names = []
        
        for name in data[factor_col].unique():
            group_data = data[data[factor_col] == name][response_col].dropna()
            if len(group_data) > 0:
                groups.append(group_data.values)
                valid_group_names.append(str(name))
        
        if len(groups) < 2:
            return []
        
        # Calculate pooled variance (MSE)
        all_data = np.concatenate(groups)
        n_total = len(all_data)
        n_groups = len(groups)
        
        # Calculate MSE (within-group variance)
        ss_within = sum(sum((x - np.mean(g))**2 for x in g) for g in groups)
        df_within = n_total - n_groups
        mse = ss_within / df_within if df_within > 0 else 1
        
        comparisons = []
        
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                name_i = valid_group_names[i]
                name_j = valid_group_names[j]
                mean_i = np.mean(groups[i])
                mean_j = np.mean(groups[j])
                n_i = len(groups[i])
                n_j = len(groups[j])
                
                # Mean difference
                mean_diff = abs(mean_i - mean_j)
                
                # Standard error for unequal sample sizes
                se = np.sqrt(mse * 0.5 * (1/n_i + 1/n_j))
                
                # q statistic
                q_stat = mean_diff / se if se > 0 else 0
                
                # Calculate p-value using studentized range distribution
                try:
                    p_value = 1 - studentized_range.cdf(q_stat, n_groups, df_within)
                except:
                    # Fallback: use conservative estimate
                    p_value = 1.0 if q_stat < 2 else 0.05 if q_stat < 4 else 0.01
                
                comparisons.append({
                    'group1': name_i,
                    'group2': name_j,
                    'mean1': mean_i,
                    'mean2': mean_j,
                    'mean_diff': mean_diff,
                    'q_stat': q_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                })
        
        # Sort by mean difference (largest first)
        comparisons.sort(key=lambda x: x['mean_diff'], reverse=True)
        
        return comparisons
    
    def two_sample_t_test(self, data1, data2, alternative='two-sided'):
        """
        Perform two-sample t-test.
        
        Args:
            data1: First sample
            data2: Second sample
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            dict: Test results
        """
        data1 = np.array(data1)
        data2 = np.array(data2)
        data1 = data1[~np.isnan(data1)]
        data2 = data2[~np.isnan(data2)]
        
        n1, n2 = len(data1), len(data2)
        
        if n1 < 2 or n2 < 2:
            return None
        
        mean1, mean2 = np.mean(data1), np.mean(data2)
        std1, std2 = np.std(data1, ddof=1), np.std(data2, ddof=1)
        
        # Welch's t-test
        t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False, alternative=alternative)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
        cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
        
        # Percent change
        if mean2 != 0:
            pct_change = ((mean1 - mean2) / abs(mean2)) * 100
        else:
            pct_change = 0
        
        return {
            't_stat': t_stat,
            'p_value': p_value,
            'mean1': mean1,
            'mean2': mean2,
            'std1': std1,
            'std2': std2,
            'n1': n1,
            'n2': n2,
            'cohens_d': cohens_d,
            'pct_change': pct_change,
            'significant': p_value < 0.05
        }
    
    def percentile_value(self, data, percentile):
        """
        Calculate value at given percentile.
        
        Args:
            data: pandas Series or array-like of numeric data
            percentile: Percentile to calculate (0-100)
            
        Returns:
            float: Value at the specified percentile
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) == 0:
            return 0
        
        return np.percentile(data, percentile)
    
    def percentile_of_value(self, data, value):
        """
        Calculate percentile of a given value.
        
        Args:
            data: pandas Series or array-like of numeric data
            value: Value to find percentile for
            
        Returns:
            float: Percentile of the value (0-100)
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) == 0:
            return 0
        
        return stats.percentileofscore(data, value, kind='rank')
    
    def correlation_analysis(self, x_data, y_data):
        """
        Perform correlation analysis between two variables.
        
        Args:
            x_data: First variable (X)
            y_data: Second variable (Y)
            
        Returns:
            dict: Correlation results including r, r-squared, p-value, interpretation
        """
        x = np.array(x_data)
        y = np.array(y_data)
        
        # Remove pairs with NaN in either variable
        valid_mask = ~(np.isnan(x) | np.isnan(y))
        x = x[valid_mask]
        y = y[valid_mask]
        
        n = len(x)
        
        if n < 3:
            return {
                'r': 0,
                'r_squared': 0,
                'p_value': 1.0,
                'n': n,
                'interpretation': 'Insufficient data',
                'strength': 'None',
                'direction': 'None',
                'slope': 0,
                'intercept': 0,
                'std_err': 0
            }
        
        # Pearson correlation
        r, p_value = stats.pearsonr(x, y)
        r_squared = r ** 2
        
        # Linear regression for slope/intercept
        slope, intercept, r_val, p_val, std_err = stats.linregress(x, y)
        
        # Interpret correlation strength
        abs_r = abs(r)
        if abs_r < 0.1:
            strength = 'Negligible'
        elif abs_r < 0.3:
            strength = 'Weak'
        elif abs_r < 0.5:
            strength = 'Moderate'
        elif abs_r < 0.7:
            strength = 'Strong'
        else:
            strength = 'Very Strong'
        
        # Direction
        if r > 0.05:
            direction = 'Positive'
        elif r < -0.05:
            direction = 'Negative'
        else:
            direction = 'None'
        
        # Full interpretation
        if p_value <= 0.05:
            significance = 'statistically significant'
        else:
            significance = 'not statistically significant'
        
        interpretation = f"{strength} {direction.lower()} correlation (r = {r:.4f}), {significance} (p = {p_value:.4f})"
        
        return {
            'r': r if not np.isnan(r) else 0,
            'r_squared': r_squared if not np.isnan(r_squared) else 0,
            'p_value': p_value if not np.isnan(p_value) else 1.0,
            'n': n,
            'interpretation': interpretation,
            'strength': strength,
            'direction': direction,
            'slope': slope if not np.isnan(slope) else 0,
            'intercept': intercept if not np.isnan(intercept) else 0,
            'std_err': std_err if not np.isnan(std_err) else 0
        }
    
    def run_chart_analysis(self, data):
        """
        Perform run chart analysis (without control limits).
        
        Tests for non-random patterns using runs above/below median.
        
        Args:
            data: pandas Series or array-like of numeric data
            
        Returns:
            dict: Run chart analysis results
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n < 10:
            return {
                'n': n,
                'median': np.median(data) if n > 0 else 0,
                'mean': np.mean(data) if n > 0 else 0,
                'n_runs': 0,
                'expected_runs': 0,
                'p_value': 1.0,
                'is_random': True,
                'interpretation': 'Insufficient data for run test'
            }
        
        median = np.median(data)
        mean = np.mean(data)
        
        # Count runs above/below median
        above_median = data > median
        runs = 1
        for i in range(1, n):
            if above_median[i] != above_median[i-1]:
                runs += 1
        
        # Expected runs and standard deviation under randomness
        n_above = np.sum(above_median)
        n_below = n - n_above
        
        if n_above == 0 or n_below == 0:
            return {
                'n': n,
                'median': median,
                'mean': mean,
                'n_runs': runs,
                'expected_runs': 0,
                'p_value': 1.0,
                'is_random': True,
                'interpretation': 'All values on one side of median'
            }
        
        expected_runs = (2 * n_above * n_below) / n + 1
        std_runs = np.sqrt((2 * n_above * n_below * (2 * n_above * n_below - n)) / 
                          (n**2 * (n - 1)))
        
        if std_runs > 0:
            z_score = (runs - expected_runs) / std_runs
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed
        else:
            z_score = 0
            p_value = 1.0
        
        is_random = p_value > 0.05
        
        if is_random:
            interpretation = f"Process appears random (p = {p_value:.4f}). No significant patterns detected."
        else:
            if runs < expected_runs:
                interpretation = f"Too few runs detected (p = {p_value:.4f}). Possible trend or shift in process."
            else:
                interpretation = f"Too many runs detected (p = {p_value:.4f}). Possible oscillation or over-correction."
        
        return {
            'n': n,
            'median': median,
            'mean': mean,
            'n_runs': runs,
            'expected_runs': expected_runs,
            'p_value': p_value if not np.isnan(p_value) else 1.0,
            'z_score': z_score if not np.isnan(z_score) else 0,
            'is_random': is_random,
            'interpretation': interpretation
        }


# =============================================================================
# Module-level analysis functions used by free_tools.py panels.
# Simple dataclass-returning wrappers; do NOT depend on StatisticsEngine above.
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, List
from itertools import combinations as _combinations


@dataclass
class DescriptiveResult:
    n: int
    mean: float
    std: float
    sem: float
    min: float
    q1: float
    median: float
    q3: float
    max: float
    skewness: float
    kurtosis: float
    ci95_lower: float
    ci95_upper: float


def descriptive(arr) -> DescriptiveResult:
    a = np.asarray(arr, dtype=float)
    n = a.size
    if n == 0:
        return DescriptiveResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    mean = float(a.mean())
    std = float(a.std(ddof=1)) if n > 1 else 0.0
    sem = std / np.sqrt(n) if n > 0 else 0.0
    return DescriptiveResult(
        n=n, mean=mean, std=std, sem=sem,
        min=float(a.min()),
        q1=float(np.percentile(a, 25)),
        median=float(np.median(a)),
        q3=float(np.percentile(a, 75)),
        max=float(a.max()),
        skewness=float(stats.skew(a)) if n > 2 else 0.0,
        kurtosis=float(stats.kurtosis(a)) if n > 3 else 0.0,
        ci95_lower=mean - 1.96 * sem,
        ci95_upper=mean + 1.96 * sem,
    )


@dataclass
class AndersonDarlingResult:
    statistic: float
    p_value: float
    normal_at_95: bool


def anderson_darling(arr) -> AndersonDarlingResult:
    a = np.asarray(arr, dtype=float)
    a = a[~np.isnan(a)]
    if a.size < 8:
        return AndersonDarlingResult(0.0, 1.0, True)
    res = stats.anderson(a, dist="norm")
    crit_5 = float(res.critical_values[2])
    n = a.size
    a2_adj = res.statistic * (1 + 0.75 / n + 2.25 / (n * n))
    if a2_adj >= 0.6:
        p = float(np.exp(1.2937 - 5.709 * a2_adj + 0.0186 * a2_adj ** 2))
    elif a2_adj >= 0.34:
        p = float(np.exp(0.9177 - 4.279 * a2_adj - 1.38 * a2_adj ** 2))
    elif a2_adj >= 0.2:
        p = float(1 - np.exp(-8.318 + 42.796 * a2_adj - 59.938 * a2_adj ** 2))
    else:
        p = float(1 - np.exp(-13.436 + 101.14 * a2_adj - 223.73 * a2_adj ** 2))
    p = max(min(p, 1.0), 0.0)
    return AndersonDarlingResult(
        statistic=float(res.statistic),
        p_value=p,
        normal_at_95=bool(res.statistic < crit_5),
    )


@dataclass
class XmRResult:
    data: np.ndarray
    mr: np.ndarray
    x_center: float
    x_ucl: float
    x_lcl: float
    mr_center: float
    mr_ucl: float
    sigma_hat: float
    signals: List[Dict] = field(default_factory=list)


def xmr_chart(arr) -> XmRResult:
    a = np.asarray(arr, dtype=float)
    a = a[~np.isnan(a)]
    n = a.size
    mr = np.abs(np.diff(a)) if n > 1 else np.array([])
    x_center = float(a.mean()) if n else 0.0
    mr_center = float(mr.mean()) if mr.size else 0.0
    sigma_hat = mr_center / 1.128 if mr_center else 0.0
    x_ucl = x_center + 3 * sigma_hat
    x_lcl = x_center - 3 * sigma_hat
    mr_ucl = 3.267 * mr_center
    signals: List[Dict] = []
    for i, v in enumerate(a):
        if sigma_hat and v > x_ucl:
            signals.append({"index": int(i), "rule": 1,
                            "description": f"X above UCL ({v:.3f} > {x_ucl:.3f})"})
        elif sigma_hat and v < x_lcl:
            signals.append({"index": int(i), "rule": 1,
                            "description": f"X below LCL ({v:.3f} < {x_lcl:.3f})"})
    return XmRResult(
        data=a, mr=mr,
        x_center=x_center, x_ucl=x_ucl, x_lcl=x_lcl,
        mr_center=mr_center, mr_ucl=mr_ucl,
        sigma_hat=sigma_hat, signals=signals,
    )


@dataclass
class CapabilityResult:
    mean: float
    sigma_within: float
    sigma_overall: float
    cp: str
    cpk: str
    pp: str
    ppk: str
    ppm_below: float
    ppm_above: float
    ppm_total: float


def _fmt_index(v) -> str:
    try:
        v = float(v)
        if np.isnan(v):
            return "—"
        return f"{v:.3f}"
    except Exception:
        return "—"


def capability(arr, lsl=None, usl=None) -> CapabilityResult:
    a = np.asarray(arr, dtype=float)
    a = a[~np.isnan(a)]
    n = a.size
    mean = float(a.mean()) if n else 0.0
    sigma_overall = float(a.std(ddof=1)) if n > 1 else 0.0
    mr = np.abs(np.diff(a)) if n > 1 else np.array([])
    sigma_within = float(mr.mean() / 1.128) if mr.size else sigma_overall

    cp = cpk = pp = ppk = float("nan")
    if lsl is not None and usl is not None:
        if sigma_within:
            cp = (usl - lsl) / (6 * sigma_within)
            cpk = min((usl - mean) / (3 * sigma_within),
                      (mean - lsl) / (3 * sigma_within))
        if sigma_overall:
            pp = (usl - lsl) / (6 * sigma_overall)
            ppk = min((usl - mean) / (3 * sigma_overall),
                      (mean - lsl) / (3 * sigma_overall))
    elif usl is not None:
        if sigma_within:
            cpk = (usl - mean) / (3 * sigma_within)
        if sigma_overall:
            ppk = (usl - mean) / (3 * sigma_overall)
    elif lsl is not None:
        if sigma_within:
            cpk = (mean - lsl) / (3 * sigma_within)
        if sigma_overall:
            ppk = (mean - lsl) / (3 * sigma_overall)

    ppm_below = (float(stats.norm.cdf(lsl, mean, sigma_overall) * 1e6)
                 if lsl is not None and sigma_overall else 0.0)
    ppm_above = (float((1 - stats.norm.cdf(usl, mean, sigma_overall)) * 1e6)
                 if usl is not None and sigma_overall else 0.0)

    return CapabilityResult(
        mean=mean,
        sigma_within=sigma_within,
        sigma_overall=sigma_overall,
        cp=_fmt_index(cp), cpk=_fmt_index(cpk),
        pp=_fmt_index(pp), ppk=_fmt_index(ppk),
        ppm_below=ppm_below, ppm_above=ppm_above,
        ppm_total=ppm_below + ppm_above,
    )


@dataclass
class RunChartResult:
    data: np.ndarray
    median: float
    runs_observed: int
    runs_expected: float
    runs_p: float
    longest_run: int
    trend_p: float


def run_chart(arr) -> RunChartResult:
    a = np.asarray(arr, dtype=float)
    a = a[~np.isnan(a)]
    n = a.size
    if n == 0:
        return RunChartResult(a, 0.0, 0, 0.0, 1.0, 0, 1.0)
    median = float(np.median(a))
    above = a > median
    n_above = int(above.sum())
    n_below = n - n_above
    runs = 1 + int(np.sum(above[1:] != above[:-1])) if n > 1 else 1
    if n_above > 0 and n_below > 0 and n > 1:
        e_runs = 1 + 2 * n_above * n_below / n
        v_runs = (2 * n_above * n_below * (2 * n_above * n_below - n)
                  / (n * n * (n - 1)))
        z = (runs - e_runs) / np.sqrt(v_runs) if v_runs > 0 else 0.0
        p = float(2 * (1 - stats.norm.cdf(abs(z))))
    else:
        e_runs = 1.0
        p = 1.0
    longest = 1
    cur = 1
    for i in range(1, n):
        if above[i] == above[i - 1]:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 1
    if n >= 3:
        s = 0
        for i in range(n - 1):
            s += int(np.sum(np.sign(a[i + 1:] - a[i])))
        var_s = n * (n - 1) * (2 * n + 5) / 18.0
        if s > 0:
            z_mk = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z_mk = (s + 1) / np.sqrt(var_s)
        else:
            z_mk = 0.0
        trend_p = float(2 * (1 - stats.norm.cdf(abs(z_mk))))
    else:
        trend_p = 1.0
    return RunChartResult(a, median, runs, float(e_runs), p, longest, trend_p)


@dataclass
class ANOVAResult:
    f_statistic: float
    p_value: float
    ss_between: float
    df_between: int
    ms_between: float
    ss_within: float
    df_within: int
    ms_within: float
    tukey_pairs: List[Dict] = field(default_factory=list)


def one_way_anova(groups: Dict[str, np.ndarray]) -> ANOVAResult:
    arrays = []
    names = []
    for name, vals in groups.items():
        v = np.asarray(vals, dtype=float)
        v = v[~np.isnan(v)]
        if v.size > 0:
            arrays.append(v)
            names.append(str(name))
    if len(arrays) < 2:
        return ANOVAResult(0.0, 1.0, 0.0, 0, 0.0, 0.0, 0, 0.0)
    f, p = stats.f_oneway(*arrays)
    grand = np.concatenate(arrays)
    grand_mean = float(grand.mean())
    ss_between = float(sum(len(a) * (a.mean() - grand_mean) ** 2 for a in arrays))
    ss_within = float(sum(((a - a.mean()) ** 2).sum() for a in arrays))
    df_between = len(arrays) - 1
    df_within = int(len(grand) - len(arrays))
    ms_between = ss_between / df_between if df_between > 0 else 0.0
    ms_within = ss_within / df_within if df_within > 0 else 0.0
    tukey_pairs: List[Dict] = []
    if df_within > 0 and ms_within > 0:
        try:
            q_crit = float(stats.studentized_range.ppf(0.95, len(arrays), df_within))
        except Exception:
            q_crit = None
        if q_crit is not None:
            for i, j in _combinations(range(len(arrays)), 2):
                a, b = arrays[i], arrays[j]
                diff = float(a.mean() - b.mean())
                se = float(np.sqrt(ms_within * (1 / len(a) + 1 / len(b)) / 2))
                hsd = q_crit * se
                tukey_pairs.append({
                    "Pair": f"{names[i]} vs {names[j]}",
                    "Diff": round(diff, 4),
                    "HSD": round(hsd, 4),
                    "Significant": "Yes" if abs(diff) > hsd else "No",
                })
    return ANOVAResult(
        f_statistic=float(f), p_value=float(p),
        ss_between=ss_between, df_between=df_between, ms_between=ms_between,
        ss_within=ss_within, df_within=df_within, ms_within=ms_within,
        tukey_pairs=tukey_pairs,
    )


@dataclass
class CorrelationResult:
    n: int
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float


def correlation(x, y) -> CorrelationResult:
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = ~(np.isnan(xa) | np.isnan(ya))
    xa = xa[mask]
    ya = ya[mask]
    n = int(xa.size)
    if n < 3:
        return CorrelationResult(n, 0.0, 1.0, 0.0, 1.0)
    pr, pp = stats.pearsonr(xa, ya)
    sr, sp = stats.spearmanr(xa, ya)
    return CorrelationResult(n, float(pr), float(pp), float(sr), float(sp))


def pareto_table(cat, cnt) -> pd.DataFrame:
    cat = pd.Series(cat).astype(str).reset_index(drop=True)
    cnt = pd.Series(cnt).astype(float).reset_index(drop=True)
    df = pd.DataFrame({"Category": cat, "Count": cnt})
    df = df.groupby("Category", as_index=False)["Count"].sum()
    df = df.sort_values("Count", ascending=False).reset_index(drop=True)
    total = float(df["Count"].sum()) if not df.empty else 0.0
    df["Percent"] = df["Count"] / total * 100 if total else 0.0
    df["Cumulative %"] = df["Percent"].cumsum()
    return df
