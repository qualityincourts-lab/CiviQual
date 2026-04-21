"""
CiviQual Stats Hypothesis Tests

Provides non-parametric and categorical hypothesis tests:
- Chi-Square Tests (Goodness of Fit, Independence)
- Mann-Whitney U Test
- Kruskal-Wallis Test
- Wilcoxon Signed-Rank Test
- Mood's Median Test

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd


@dataclass
class ChiSquareResult:
    """Result of Chi-Square test."""
    test_type: str  # 'goodness_of_fit' or 'independence'
    chi_square: float
    p_value: float
    degrees_of_freedom: int
    significant: bool
    alpha: float
    expected_frequencies: np.ndarray
    observed_frequencies: np.ndarray
    cramers_v: Optional[float] = None  # Effect size for independence test
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'test_type': self.test_type,
            'chi_square': self.chi_square,
            'p_value': self.p_value,
            'degrees_of_freedom': self.degrees_of_freedom,
            'significant': self.significant,
            'alpha': self.alpha,
            'cramers_v': self.cramers_v,
            'interpretation': self.interpretation
        }


@dataclass
class MannWhitneyResult:
    """Result of Mann-Whitney U test."""
    u_statistic: float
    p_value: float
    significant: bool
    alpha: float
    effect_size_r: float  # r = Z / sqrt(N)
    median_group1: float
    median_group2: float
    n1: int
    n2: int
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'u_statistic': self.u_statistic,
            'p_value': self.p_value,
            'significant': self.significant,
            'alpha': self.alpha,
            'effect_size_r': self.effect_size_r,
            'median_group1': self.median_group1,
            'median_group2': self.median_group2,
            'n1': self.n1,
            'n2': self.n2,
            'interpretation': self.interpretation
        }


@dataclass
class KruskalWallisResult:
    """Result of Kruskal-Wallis test."""
    h_statistic: float
    p_value: float
    significant: bool
    alpha: float
    effect_size_eta_squared: float
    group_medians: Dict[str, float]
    group_sizes: Dict[str, int]
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'h_statistic': self.h_statistic,
            'p_value': self.p_value,
            'significant': self.significant,
            'alpha': self.alpha,
            'effect_size_eta_squared': self.effect_size_eta_squared,
            'group_medians': self.group_medians,
            'group_sizes': self.group_sizes,
            'interpretation': self.interpretation
        }


@dataclass
class WilcoxonResult:
    """Result of Wilcoxon Signed-Rank test."""
    w_statistic: float
    p_value: float
    significant: bool
    alpha: float
    effect_size_r: float
    median_difference: float
    n_pairs: int
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'w_statistic': self.w_statistic,
            'p_value': self.p_value,
            'significant': self.significant,
            'alpha': self.alpha,
            'effect_size_r': self.effect_size_r,
            'median_difference': self.median_difference,
            'n_pairs': self.n_pairs,
            'interpretation': self.interpretation
        }


@dataclass
class MoodsMedianResult:
    """Result of Mood's Median test."""
    chi_square: float
    p_value: float
    significant: bool
    alpha: float
    grand_median: float
    group_medians: Dict[str, float]
    counts_above: Dict[str, int]
    counts_below: Dict[str, int]
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'chi_square': self.chi_square,
            'p_value': self.p_value,
            'significant': self.significant,
            'alpha': self.alpha,
            'grand_median': self.grand_median,
            'group_medians': self.group_medians,
            'counts_above': self.counts_above,
            'counts_below': self.counts_below,
            'interpretation': self.interpretation
        }


class HypothesisTests:
    """
    Provides non-parametric and categorical hypothesis tests.
    """
    
    @staticmethod
    def chi_square_goodness_of_fit(
        observed: Union[List[int], np.ndarray],
        expected: Optional[Union[List[float], np.ndarray]] = None,
        alpha: float = 0.05
    ) -> ChiSquareResult:
        """
        Perform Chi-Square Goodness of Fit test.
        
        Tests whether observed frequencies differ from expected frequencies.
        
        Args:
            observed: Observed frequencies
            expected: Expected frequencies (if None, assumes equal distribution)
            alpha: Significance level
            
        Returns:
            ChiSquareResult with test results
        """
        observed = np.array(observed)
        n = len(observed)
        total = np.sum(observed)
        
        if expected is None:
            # Assume equal distribution
            expected = np.full(n, total / n)
        else:
            expected = np.array(expected)
            # Scale expected to match observed total
            expected = expected * (total / np.sum(expected))
        
        if len(observed) != len(expected):
            raise ValueError("Observed and expected must have same length")
        
        # Check minimum expected frequency
        if np.any(expected < 5):
            print("Warning: Some expected frequencies are less than 5. Results may be unreliable.")
        
        # Perform test
        chi2, p_value = stats.chisquare(observed, expected)
        df = n - 1
        significant = p_value < alpha
        
        # Interpretation
        if significant:
            interpretation = (
                f"The observed distribution differs significantly from the expected distribution "
                f"(χ² = {chi2:.4f}, df = {df}, p = {p_value:.4f})."
            )
        else:
            interpretation = (
                f"No significant difference between observed and expected distributions "
                f"(χ² = {chi2:.4f}, df = {df}, p = {p_value:.4f})."
            )
        
        return ChiSquareResult(
            test_type='goodness_of_fit',
            chi_square=chi2,
            p_value=p_value,
            degrees_of_freedom=df,
            significant=significant,
            alpha=alpha,
            expected_frequencies=expected,
            observed_frequencies=observed,
            interpretation=interpretation
        )
    
    @staticmethod
    def chi_square_independence(
        contingency_table: Union[np.ndarray, pd.DataFrame],
        alpha: float = 0.05
    ) -> ChiSquareResult:
        """
        Perform Chi-Square Test of Independence.
        
        Tests whether two categorical variables are independent.
        
        Args:
            contingency_table: 2D array or DataFrame of observed frequencies
            alpha: Significance level
            
        Returns:
            ChiSquareResult with test results
        """
        if isinstance(contingency_table, pd.DataFrame):
            contingency_table = contingency_table.values
        
        contingency_table = np.array(contingency_table)
        
        if contingency_table.ndim != 2:
            raise ValueError("Contingency table must be 2-dimensional")
        
        # Check minimum expected frequency
        row_totals = contingency_table.sum(axis=1)
        col_totals = contingency_table.sum(axis=0)
        n = contingency_table.sum()
        expected = np.outer(row_totals, col_totals) / n
        
        if np.any(expected < 5):
            print("Warning: Some expected frequencies are less than 5. Consider using Fisher's exact test.")
        
        # Perform test
        chi2, p_value, df, expected = stats.chi2_contingency(contingency_table)
        significant = p_value < alpha
        
        # Calculate Cramér's V (effect size)
        n_obs = contingency_table.sum()
        min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
        cramers_v = np.sqrt(chi2 / (n_obs * min_dim)) if min_dim > 0 else 0
        
        # Interpret Cramér's V
        if cramers_v < 0.1:
            effect_desc = "negligible"
        elif cramers_v < 0.3:
            effect_desc = "small"
        elif cramers_v < 0.5:
            effect_desc = "medium"
        else:
            effect_desc = "large"
        
        if significant:
            interpretation = (
                f"The variables are significantly associated "
                f"(χ² = {chi2:.4f}, df = {df}, p = {p_value:.4f}). "
                f"Effect size (Cramér's V = {cramers_v:.4f}) indicates a {effect_desc} association."
            )
        else:
            interpretation = (
                f"No significant association between the variables "
                f"(χ² = {chi2:.4f}, df = {df}, p = {p_value:.4f})."
            )
        
        return ChiSquareResult(
            test_type='independence',
            chi_square=chi2,
            p_value=p_value,
            degrees_of_freedom=df,
            significant=significant,
            alpha=alpha,
            expected_frequencies=expected,
            observed_frequencies=contingency_table,
            cramers_v=cramers_v,
            interpretation=interpretation
        )
    
    @staticmethod
    def mann_whitney_u(
        group1: Union[List[float], np.ndarray],
        group2: Union[List[float], np.ndarray],
        alternative: str = 'two-sided',
        alpha: float = 0.05
    ) -> MannWhitneyResult:
        """
        Perform Mann-Whitney U test (Wilcoxon Rank-Sum test).
        
        Non-parametric test for comparing two independent groups.
        Alternative to independent samples t-test when normality is violated.
        
        Args:
            group1: First group data
            group2: Second group data
            alternative: 'two-sided', 'less', or 'greater'
            alpha: Significance level
            
        Returns:
            MannWhitneyResult with test results
        """
        group1 = np.array(group1)
        group2 = np.array(group2)
        
        group1 = group1[~np.isnan(group1)]
        group2 = group2[~np.isnan(group2)]
        
        n1, n2 = len(group1), len(group2)
        
        if n1 < 2 or n2 < 2:
            raise ValueError("Each group must have at least 2 observations")
        
        # Perform test
        u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative=alternative)
        
        significant = p_value < alpha
        
        # Calculate effect size r
        # r = Z / sqrt(N), where Z is from normal approximation
        n_total = n1 + n2
        mean_u = n1 * n2 / 2
        std_u = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        z_score = (u_stat - mean_u) / std_u if std_u > 0 else 0
        effect_size_r = abs(z_score) / np.sqrt(n_total)
        
        # Interpret effect size
        if effect_size_r < 0.1:
            effect_desc = "negligible"
        elif effect_size_r < 0.3:
            effect_desc = "small"
        elif effect_size_r < 0.5:
            effect_desc = "medium"
        else:
            effect_desc = "large"
        
        median1 = np.median(group1)
        median2 = np.median(group2)
        
        if significant:
            interpretation = (
                f"There is a significant difference between the groups "
                f"(U = {u_stat:.2f}, p = {p_value:.4f}). "
                f"Group 1 median: {median1:.4f}, Group 2 median: {median2:.4f}. "
                f"Effect size (r = {effect_size_r:.4f}) indicates a {effect_desc} effect."
            )
        else:
            interpretation = (
                f"No significant difference between the groups "
                f"(U = {u_stat:.2f}, p = {p_value:.4f}). "
                f"Group 1 median: {median1:.4f}, Group 2 median: {median2:.4f}."
            )
        
        return MannWhitneyResult(
            u_statistic=u_stat,
            p_value=p_value,
            significant=significant,
            alpha=alpha,
            effect_size_r=effect_size_r,
            median_group1=median1,
            median_group2=median2,
            n1=n1,
            n2=n2,
            interpretation=interpretation
        )
    
    @staticmethod
    def kruskal_wallis(
        *groups,
        group_names: Optional[List[str]] = None,
        alpha: float = 0.05
    ) -> KruskalWallisResult:
        """
        Perform Kruskal-Wallis H test.
        
        Non-parametric test for comparing three or more independent groups.
        Alternative to one-way ANOVA when normality is violated.
        
        Args:
            *groups: Variable number of group data arrays
            group_names: Optional names for groups
            alpha: Significance level
            
        Returns:
            KruskalWallisResult with test results
        """
        if len(groups) < 2:
            raise ValueError("At least 2 groups required")
        
        # Clean data
        cleaned_groups = []
        for g in groups:
            g = np.array(g)
            g = g[~np.isnan(g)]
            if len(g) < 2:
                raise ValueError("Each group must have at least 2 observations")
            cleaned_groups.append(g)
        
        if group_names is None:
            group_names = [f"Group {i+1}" for i in range(len(cleaned_groups))]
        
        # Perform test
        h_stat, p_value = stats.kruskal(*cleaned_groups)
        significant = p_value < alpha
        
        # Calculate eta-squared effect size
        n_total = sum(len(g) for g in cleaned_groups)
        eta_squared = (h_stat - len(cleaned_groups) + 1) / (n_total - len(cleaned_groups))
        eta_squared = max(0, eta_squared)  # Ensure non-negative
        
        # Interpret effect size
        if eta_squared < 0.01:
            effect_desc = "negligible"
        elif eta_squared < 0.06:
            effect_desc = "small"
        elif eta_squared < 0.14:
            effect_desc = "medium"
        else:
            effect_desc = "large"
        
        # Calculate group medians and sizes
        group_medians = {name: float(np.median(g)) for name, g in zip(group_names, cleaned_groups)}
        group_sizes = {name: len(g) for name, g in zip(group_names, cleaned_groups)}
        
        if significant:
            interpretation = (
                f"There is a significant difference among the groups "
                f"(H = {h_stat:.4f}, p = {p_value:.4f}). "
                f"Effect size (η² = {eta_squared:.4f}) indicates a {effect_desc} effect. "
                f"Post-hoc pairwise comparisons recommended."
            )
        else:
            interpretation = (
                f"No significant difference among the groups "
                f"(H = {h_stat:.4f}, p = {p_value:.4f})."
            )
        
        return KruskalWallisResult(
            h_statistic=h_stat,
            p_value=p_value,
            significant=significant,
            alpha=alpha,
            effect_size_eta_squared=eta_squared,
            group_medians=group_medians,
            group_sizes=group_sizes,
            interpretation=interpretation
        )
    
    @staticmethod
    def wilcoxon_signed_rank(
        x: Union[List[float], np.ndarray],
        y: Optional[Union[List[float], np.ndarray]] = None,
        alternative: str = 'two-sided',
        alpha: float = 0.05
    ) -> WilcoxonResult:
        """
        Perform Wilcoxon Signed-Rank test.
        
        Non-parametric test for comparing two related samples or one sample against a hypothesized median.
        Alternative to paired t-test when normality is violated.
        
        Args:
            x: First sample or differences
            y: Second sample (if None, tests x against zero)
            alternative: 'two-sided', 'less', or 'greater'
            alpha: Significance level
            
        Returns:
            WilcoxonResult with test results
        """
        x = np.array(x)
        
        if y is not None:
            y = np.array(y)
            if len(x) != len(y):
                raise ValueError("x and y must have same length")
            # Remove pairs with NaN
            mask = ~(np.isnan(x) | np.isnan(y))
            x = x[mask]
            y = y[mask]
            differences = x - y
        else:
            x = x[~np.isnan(x)]
            differences = x
        
        n_pairs = len(differences)
        
        if n_pairs < 10:
            print("Warning: Small sample size. Results may be unreliable.")
        
        # Remove zero differences
        differences = differences[differences != 0]
        
        if len(differences) < 2:
            raise ValueError("Not enough non-zero differences for test")
        
        # Perform test
        w_stat, p_value = stats.wilcoxon(differences, alternative=alternative)
        significant = p_value < alpha
        
        # Calculate effect size r
        n = len(differences)
        z_score = stats.norm.ppf(1 - p_value / 2) if p_value < 1 else 0
        effect_size_r = abs(z_score) / np.sqrt(n)
        
        # Interpret effect size
        if effect_size_r < 0.1:
            effect_desc = "negligible"
        elif effect_size_r < 0.3:
            effect_desc = "small"
        elif effect_size_r < 0.5:
            effect_desc = "medium"
        else:
            effect_desc = "large"
        
        median_diff = np.median(differences)
        
        if significant:
            interpretation = (
                f"There is a significant difference "
                f"(W = {w_stat:.2f}, p = {p_value:.4f}). "
                f"Median difference: {median_diff:.4f}. "
                f"Effect size (r = {effect_size_r:.4f}) indicates a {effect_desc} effect."
            )
        else:
            interpretation = (
                f"No significant difference "
                f"(W = {w_stat:.2f}, p = {p_value:.4f}). "
                f"Median difference: {median_diff:.4f}."
            )
        
        return WilcoxonResult(
            w_statistic=w_stat,
            p_value=p_value,
            significant=significant,
            alpha=alpha,
            effect_size_r=effect_size_r,
            median_difference=median_diff,
            n_pairs=n_pairs,
            interpretation=interpretation
        )
    
    @staticmethod
    def moods_median(
        *groups,
        group_names: Optional[List[str]] = None,
        alpha: float = 0.05
    ) -> MoodsMedianResult:
        """
        Perform Mood's Median test.
        
        Non-parametric test comparing medians of two or more independent groups.
        Tests whether samples come from populations with the same median.
        
        Args:
            *groups: Variable number of group data arrays
            group_names: Optional names for groups
            alpha: Significance level
            
        Returns:
            MoodsMedianResult with test results
        """
        if len(groups) < 2:
            raise ValueError("At least 2 groups required")
        
        # Clean data
        cleaned_groups = []
        for g in groups:
            g = np.array(g)
            g = g[~np.isnan(g)]
            if len(g) < 2:
                raise ValueError("Each group must have at least 2 observations")
            cleaned_groups.append(g)
        
        if group_names is None:
            group_names = [f"Group {i+1}" for i in range(len(cleaned_groups))]
        
        # Perform test
        stat, p_value, med, contingency = stats.median_test(*cleaned_groups)
        significant = p_value < alpha
        
        # Calculate group medians
        group_medians = {name: float(np.median(g)) for name, g in zip(group_names, cleaned_groups)}
        
        # Count above/below grand median
        counts_above = {name: int(contingency[0, i]) for i, name in enumerate(group_names)}
        counts_below = {name: int(contingency[1, i]) for i, name in enumerate(group_names)}
        
        if significant:
            interpretation = (
                f"The group medians differ significantly "
                f"(χ² = {stat:.4f}, p = {p_value:.4f}). "
                f"Grand median: {med:.4f}."
            )
        else:
            interpretation = (
                f"No significant difference in group medians "
                f"(χ² = {stat:.4f}, p = {p_value:.4f}). "
                f"Grand median: {med:.4f}."
            )
        
        return MoodsMedianResult(
            chi_square=stat,
            p_value=p_value,
            significant=significant,
            alpha=alpha,
            grand_median=med,
            group_medians=group_medians,
            counts_above=counts_above,
            counts_below=counts_below,
            interpretation=interpretation
        )
    
    @staticmethod
    def select_test(
        data_type: str,
        num_groups: int,
        paired: bool = False,
        normal: bool = True
    ) -> str:
        """
        Recommend appropriate hypothesis test based on data characteristics.
        
        Args:
            data_type: 'continuous' or 'categorical'
            num_groups: Number of groups to compare
            paired: Whether samples are paired/related
            normal: Whether data is normally distributed
            
        Returns:
            Name of recommended test
        """
        if data_type == 'categorical':
            if num_groups == 1:
                return "Chi-Square Goodness of Fit"
            else:
                return "Chi-Square Test of Independence"
        
        # Continuous data
        if num_groups == 1:
            if normal:
                return "One-Sample t-test (in Descriptive Stats)"
            else:
                return "Wilcoxon Signed-Rank Test (against hypothesized median)"
        
        elif num_groups == 2:
            if paired:
                if normal:
                    return "Paired t-test (in Before/After)"
                else:
                    return "Wilcoxon Signed-Rank Test"
            else:
                if normal:
                    return "Two-Sample t-test (in Before/After)"
                else:
                    return "Mann-Whitney U Test"
        
        else:  # 3+ groups
            if normal:
                return "ANOVA (in ANOVA tab)"
            else:
                return "Kruskal-Wallis Test or Mood's Median Test"
