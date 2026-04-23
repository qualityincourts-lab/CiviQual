"""
CiviQual Stats Sample Size & Power Analysis

Provides sample size calculators and power analysis for:
- One-sample mean
- Two-sample means
- One proportion
- Two proportions
- Power curves

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
import math


@dataclass
class SampleSizeResult:
    """Result of sample size calculation."""
    sample_size: int
    test_type: str
    alpha: float
    power: float
    effect_size: float
    parameters: Dict
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'sample_size': self.sample_size,
            'test_type': self.test_type,
            'alpha': self.alpha,
            'power': self.power,
            'effect_size': self.effect_size,
            'parameters': self.parameters,
            'interpretation': self.interpretation
        }


@dataclass
class PowerResult:
    """Result of power calculation."""
    power: float
    sample_size: int
    test_type: str
    alpha: float
    effect_size: float
    parameters: Dict
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'power': self.power,
            'sample_size': self.sample_size,
            'test_type': self.test_type,
            'alpha': self.alpha,
            'effect_size': self.effect_size,
            'parameters': self.parameters,
            'interpretation': self.interpretation
        }


@dataclass
class PowerCurveData:
    """Data for plotting power curves."""
    sample_sizes: List[int]
    powers: List[float]
    effect_size: float
    alpha: float
    test_type: str


class SampleSizeCalculator:
    """
    Provides sample size and power calculations for common statistical tests.
    """
    
    @staticmethod
    def cohen_d_to_description(d: float) -> str:
        """Convert Cohen's d to effect size description."""
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"
    
    @staticmethod
    def one_sample_mean(
        effect_size: Optional[float] = None,
        mean_diff: Optional[float] = None,
        std_dev: Optional[float] = None,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = 'two-sided'
    ) -> SampleSizeResult:
        """
        Calculate sample size for one-sample t-test.
        
        Provide either:
        - effect_size (Cohen's d), OR
        - mean_diff and std_dev
        
        Args:
            effect_size: Cohen's d (standardized effect size)
            mean_diff: Expected difference from null hypothesis mean
            std_dev: Population standard deviation
            alpha: Significance level
            power: Desired power (1 - beta)
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            SampleSizeResult with calculated sample size
        """
        # Calculate effect size if not provided
        if effect_size is None:
            if mean_diff is None or std_dev is None:
                raise ValueError("Provide either effect_size OR both mean_diff and std_dev")
            effect_size = abs(mean_diff) / std_dev
        
        if effect_size <= 0:
            raise ValueError("Effect size must be positive")
        
        # Get z-values
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        z_beta = stats.norm.ppf(power)
        
        # Calculate sample size
        n = ((z_alpha + z_beta) / effect_size) ** 2
        n = int(math.ceil(n))
        
        # Ensure minimum sample size
        n = max(n, 2)
        
        effect_desc = SampleSizeCalculator.cohen_d_to_description(effect_size)
        
        interpretation = (
            f"A sample size of {n} is required to detect a {effect_desc} effect "
            f"(d = {effect_size:.3f}) with {power*100:.0f}% power at α = {alpha}."
        )
        
        return SampleSizeResult(
            sample_size=n,
            test_type='one_sample_mean',
            alpha=alpha,
            power=power,
            effect_size=effect_size,
            parameters={
                'mean_diff': mean_diff,
                'std_dev': std_dev,
                'alternative': alternative
            },
            interpretation=interpretation
        )
    
    @staticmethod
    def two_sample_means(
        effect_size: Optional[float] = None,
        mean_diff: Optional[float] = None,
        std_dev: Optional[float] = None,
        alpha: float = 0.05,
        power: float = 0.80,
        ratio: float = 1.0,
        alternative: str = 'two-sided'
    ) -> SampleSizeResult:
        """
        Calculate sample size for two-sample t-test.
        
        Args:
            effect_size: Cohen's d
            mean_diff: Expected difference between means
            std_dev: Pooled standard deviation
            alpha: Significance level
            power: Desired power
            ratio: Ratio of n2/n1 (default 1.0 for equal groups)
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            SampleSizeResult with calculated sample sizes
        """
        # Calculate effect size if not provided
        if effect_size is None:
            if mean_diff is None or std_dev is None:
                raise ValueError("Provide either effect_size OR both mean_diff and std_dev")
            effect_size = abs(mean_diff) / std_dev
        
        if effect_size <= 0:
            raise ValueError("Effect size must be positive")
        
        # Get z-values
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        z_beta = stats.norm.ppf(power)
        
        # Calculate sample size for group 1
        n1 = (1 + 1/ratio) * ((z_alpha + z_beta) / effect_size) ** 2
        n1 = int(math.ceil(n1))
        n2 = int(math.ceil(n1 * ratio))
        
        # Ensure minimum
        n1 = max(n1, 2)
        n2 = max(n2, 2)
        
        total_n = n1 + n2
        effect_desc = SampleSizeCalculator.cohen_d_to_description(effect_size)
        
        if ratio == 1.0:
            interpretation = (
                f"Sample sizes of {n1} per group (total N = {total_n}) are required to detect "
                f"a {effect_desc} effect (d = {effect_size:.3f}) with {power*100:.0f}% power at α = {alpha}."
            )
        else:
            interpretation = (
                f"Sample sizes of {n1} (group 1) and {n2} (group 2), total N = {total_n}, are required "
                f"to detect a {effect_desc} effect (d = {effect_size:.3f}) with {power*100:.0f}% power at α = {alpha}."
            )
        
        return SampleSizeResult(
            sample_size=total_n,
            test_type='two_sample_means',
            alpha=alpha,
            power=power,
            effect_size=effect_size,
            parameters={
                'n1': n1,
                'n2': n2,
                'mean_diff': mean_diff,
                'std_dev': std_dev,
                'ratio': ratio,
                'alternative': alternative
            },
            interpretation=interpretation
        )
    
    @staticmethod
    def one_proportion(
        p0: float,
        p1: float,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = 'two-sided'
    ) -> SampleSizeResult:
        """
        Calculate sample size for one-proportion z-test.
        
        Args:
            p0: Null hypothesis proportion
            p1: Alternative hypothesis proportion (expected)
            alpha: Significance level
            power: Desired power
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            SampleSizeResult with calculated sample size
        """
        if not (0 < p0 < 1) or not (0 < p1 < 1):
            raise ValueError("Proportions must be between 0 and 1")
        
        if p0 == p1:
            raise ValueError("p0 and p1 must be different")
        
        # Get z-values
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        z_beta = stats.norm.ppf(power)
        
        # Calculate sample size using normal approximation
        q0 = 1 - p0
        q1 = 1 - p1
        
        numerator = z_alpha * math.sqrt(p0 * q0) + z_beta * math.sqrt(p1 * q1)
        denominator = abs(p1 - p0)
        
        n = (numerator / denominator) ** 2
        n = int(math.ceil(n))
        
        # Ensure minimum
        n = max(n, 10)  # Larger minimum for proportions
        
        effect_h = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p0)))
        
        interpretation = (
            f"A sample size of {n} is required to detect a change in proportion "
            f"from {p0:.1%} to {p1:.1%} (h = {abs(effect_h):.3f}) "
            f"with {power*100:.0f}% power at α = {alpha}."
        )
        
        return SampleSizeResult(
            sample_size=n,
            test_type='one_proportion',
            alpha=alpha,
            power=power,
            effect_size=abs(effect_h),
            parameters={
                'p0': p0,
                'p1': p1,
                'alternative': alternative
            },
            interpretation=interpretation
        )
    
    @staticmethod
    def two_proportions(
        p1: float,
        p2: float,
        alpha: float = 0.05,
        power: float = 0.80,
        ratio: float = 1.0,
        alternative: str = 'two-sided'
    ) -> SampleSizeResult:
        """
        Calculate sample size for two-proportion z-test.
        
        Args:
            p1: Proportion for group 1
            p2: Proportion for group 2
            alpha: Significance level
            power: Desired power
            ratio: Ratio of n2/n1
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            SampleSizeResult with calculated sample sizes
        """
        if not (0 < p1 < 1) or not (0 < p2 < 1):
            raise ValueError("Proportions must be between 0 and 1")
        
        if p1 == p2:
            raise ValueError("p1 and p2 must be different")
        
        # Get z-values
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        z_beta = stats.norm.ppf(power)
        
        # Pooled proportion under null
        p_bar = (p1 + ratio * p2) / (1 + ratio)
        q_bar = 1 - p_bar
        
        q1 = 1 - p1
        q2 = 1 - p2
        
        # Calculate sample size
        numerator = (z_alpha * math.sqrt((1 + 1/ratio) * p_bar * q_bar) + 
                     z_beta * math.sqrt(p1 * q1 + p2 * q2 / ratio))
        denominator = abs(p1 - p2)
        
        n1 = (numerator / denominator) ** 2
        n1 = int(math.ceil(n1))
        n2 = int(math.ceil(n1 * ratio))
        
        # Ensure minimum
        n1 = max(n1, 10)
        n2 = max(n2, 10)
        
        total_n = n1 + n2
        
        effect_h = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))
        
        interpretation = (
            f"Sample sizes of {n1} and {n2} (total N = {total_n}) are required to detect "
            f"a difference between proportions {p1:.1%} and {p2:.1%} (h = {abs(effect_h):.3f}) "
            f"with {power*100:.0f}% power at α = {alpha}."
        )
        
        return SampleSizeResult(
            sample_size=total_n,
            test_type='two_proportions',
            alpha=alpha,
            power=power,
            effect_size=abs(effect_h),
            parameters={
                'p1': p1,
                'p2': p2,
                'n1': n1,
                'n2': n2,
                'ratio': ratio,
                'alternative': alternative
            },
            interpretation=interpretation
        )
    
    @staticmethod
    def calculate_power_one_sample(
        n: int,
        effect_size: float,
        alpha: float = 0.05,
        alternative: str = 'two-sided'
    ) -> PowerResult:
        """
        Calculate power for one-sample t-test.
        
        Args:
            n: Sample size
            effect_size: Cohen's d
            alpha: Significance level
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            PowerResult with calculated power
        """
        if n < 2:
            raise ValueError("Sample size must be at least 2")
        
        # Get critical value
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        # Non-centrality parameter
        ncp = effect_size * math.sqrt(n)
        
        # Calculate power
        if alternative == 'two-sided':
            power = 1 - stats.norm.cdf(z_alpha - ncp) + stats.norm.cdf(-z_alpha - ncp)
        elif alternative == 'greater':
            power = 1 - stats.norm.cdf(z_alpha - ncp)
        else:
            power = stats.norm.cdf(-z_alpha - ncp)
        
        effect_desc = SampleSizeCalculator.cohen_d_to_description(effect_size)
        
        interpretation = (
            f"With n = {n}, the power to detect a {effect_desc} effect "
            f"(d = {effect_size:.3f}) is {power*100:.1f}% at α = {alpha}."
        )
        
        return PowerResult(
            power=power,
            sample_size=n,
            test_type='one_sample_mean',
            alpha=alpha,
            effect_size=effect_size,
            parameters={'alternative': alternative},
            interpretation=interpretation
        )
    
    @staticmethod
    def calculate_power_two_sample(
        n1: int,
        n2: int,
        effect_size: float,
        alpha: float = 0.05,
        alternative: str = 'two-sided'
    ) -> PowerResult:
        """
        Calculate power for two-sample t-test.
        
        Args:
            n1: Sample size group 1
            n2: Sample size group 2
            effect_size: Cohen's d
            alpha: Significance level
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            PowerResult with calculated power
        """
        if n1 < 2 or n2 < 2:
            raise ValueError("Sample sizes must be at least 2")
        
        # Get critical value
        if alternative == 'two-sided':
            z_alpha = stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = stats.norm.ppf(1 - alpha)
        
        # Effective sample size
        n_eff = (n1 * n2) / (n1 + n2)
        
        # Non-centrality parameter
        ncp = effect_size * math.sqrt(n_eff)
        
        # Calculate power
        if alternative == 'two-sided':
            power = 1 - stats.norm.cdf(z_alpha - ncp) + stats.norm.cdf(-z_alpha - ncp)
        elif alternative == 'greater':
            power = 1 - stats.norm.cdf(z_alpha - ncp)
        else:
            power = stats.norm.cdf(-z_alpha - ncp)
        
        effect_desc = SampleSizeCalculator.cohen_d_to_description(effect_size)
        
        interpretation = (
            f"With n1 = {n1} and n2 = {n2}, the power to detect a {effect_desc} effect "
            f"(d = {effect_size:.3f}) is {power*100:.1f}% at α = {alpha}."
        )
        
        return PowerResult(
            power=power,
            sample_size=n1 + n2,
            test_type='two_sample_means',
            alpha=alpha,
            effect_size=effect_size,
            parameters={
                'n1': n1,
                'n2': n2,
                'alternative': alternative
            },
            interpretation=interpretation
        )
    
    @staticmethod
    def power_curve(
        test_type: str,
        effect_size: float,
        alpha: float = 0.05,
        max_n: int = 200,
        **kwargs
    ) -> PowerCurveData:
        """
        Generate power curve data for plotting.
        
        Args:
            test_type: 'one_sample' or 'two_sample'
            effect_size: Cohen's d
            alpha: Significance level
            max_n: Maximum sample size to evaluate
            **kwargs: Additional parameters for specific tests
            
        Returns:
            PowerCurveData for plotting
        """
        sample_sizes = list(range(5, max_n + 1, 5))
        powers = []
        
        for n in sample_sizes:
            if test_type == 'one_sample':
                result = SampleSizeCalculator.calculate_power_one_sample(
                    n=n,
                    effect_size=effect_size,
                    alpha=alpha
                )
            else:
                # Equal groups for two-sample
                n1 = n // 2
                n2 = n - n1
                result = SampleSizeCalculator.calculate_power_two_sample(
                    n1=n1,
                    n2=n2,
                    effect_size=effect_size,
                    alpha=alpha
                )
            
            powers.append(result.power)
        
        return PowerCurveData(
            sample_sizes=sample_sizes,
            powers=powers,
            effect_size=effect_size,
            alpha=alpha,
            test_type=test_type
        )
    
    @staticmethod
    def minimum_detectable_effect(
        n: int,
        alpha: float = 0.05,
        power: float = 0.80,
        test_type: str = 'one_sample',
        ratio: float = 1.0
    ) -> float:
        """
        Calculate the minimum detectable effect size for a given sample size.
        
        Args:
            n: Total sample size
            alpha: Significance level
            power: Desired power
            test_type: 'one_sample' or 'two_sample'
            ratio: For two-sample, ratio of n2/n1
            
        Returns:
            Minimum detectable Cohen's d
        """
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        if test_type == 'one_sample':
            mde = (z_alpha + z_beta) / math.sqrt(n)
        else:
            # Two-sample
            n1 = n / (1 + ratio)
            n_eff = (n1 * n1 * ratio) / (n1 + n1 * ratio)
            mde = (z_alpha + z_beta) / math.sqrt(n_eff)
        
        return mde
    
    @staticmethod
    def quick_reference() -> Dict:
        """
        Return quick reference table of sample sizes for common scenarios.
        
        Returns:
            Dictionary with sample size recommendations
        """
        return {
            'small_effect': {
                'd': 0.2,
                'description': 'Small effect (d = 0.2)',
                'one_sample_80': 196,
                'one_sample_90': 265,
                'two_sample_80_per_group': 393,
                'two_sample_90_per_group': 526
            },
            'medium_effect': {
                'd': 0.5,
                'description': 'Medium effect (d = 0.5)',
                'one_sample_80': 32,
                'one_sample_90': 43,
                'two_sample_80_per_group': 64,
                'two_sample_90_per_group': 85
            },
            'large_effect': {
                'd': 0.8,
                'description': 'Large effect (d = 0.8)',
                'one_sample_80': 13,
                'one_sample_90': 17,
                'two_sample_80_per_group': 26,
                'two_sample_90_per_group': 34
            }
        }
