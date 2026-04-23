"""
CiviQual Stats Advanced Capability Analysis

Provides advanced process capability metrics:
- Pp/Ppk (Long-term capability)
- Cpm (Taguchi capability index)
- Box-Cox transformation
- Non-normal capability analysis

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.optimize import brentq
import warnings


@dataclass
class LongTermCapabilityResult:
    """Result of long-term capability analysis (Pp/Ppk)."""
    pp: float
    ppk: float
    ppu: float
    ppl: float
    lsl: float
    usl: float
    target: Optional[float]
    mean: float
    std_dev: float  # Overall (long-term) std dev
    within_std_dev: Optional[float]  # Within-subgroup (short-term) for comparison
    n: int
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'pp': self.pp,
            'ppk': self.ppk,
            'ppu': self.ppu,
            'ppl': self.ppl,
            'lsl': self.lsl,
            'usl': self.usl,
            'target': self.target,
            'mean': self.mean,
            'std_dev': self.std_dev,
            'within_std_dev': self.within_std_dev,
            'n': self.n,
            'interpretation': self.interpretation
        }


@dataclass
class CpmResult:
    """Result of Cpm (Taguchi) capability analysis."""
    cpm: float
    cp: float
    cpk: float
    target: float
    mean: float
    std_dev: float
    target_deviation: float  # Mean deviation from target
    n: int
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'cpm': self.cpm,
            'cp': self.cp,
            'cpk': self.cpk,
            'target': self.target,
            'mean': self.mean,
            'std_dev': self.std_dev,
            'target_deviation': self.target_deviation,
            'n': self.n,
            'interpretation': self.interpretation
        }


@dataclass
class BoxCoxResult:
    """Result of Box-Cox transformation."""
    lambda_value: float
    transformed_data: np.ndarray
    original_mean: float
    original_std: float
    transformed_mean: float
    transformed_std: float
    normality_before: Tuple[float, float]  # (statistic, p-value)
    normality_after: Tuple[float, float]
    transformation_formula: str
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'lambda_value': self.lambda_value,
            'original_mean': self.original_mean,
            'original_std': self.original_std,
            'transformed_mean': self.transformed_mean,
            'transformed_std': self.transformed_std,
            'normality_before_stat': self.normality_before[0],
            'normality_before_p': self.normality_before[1],
            'normality_after_stat': self.normality_after[0],
            'normality_after_p': self.normality_after[1],
            'transformation_formula': self.transformation_formula,
            'interpretation': self.interpretation
        }


@dataclass
class NonNormalCapabilityResult:
    """Result of non-normal capability analysis."""
    method: str  # 'percentile', 'box_cox', 'johnson', 'weibull'
    ppm_below_lsl: float
    ppm_above_usl: float
    ppm_total: float
    equivalent_ppk: float
    lsl: float
    usl: float
    distribution_fit: Dict
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'method': self.method,
            'ppm_below_lsl': self.ppm_below_lsl,
            'ppm_above_usl': self.ppm_above_usl,
            'ppm_total': self.ppm_total,
            'equivalent_ppk': self.equivalent_ppk,
            'lsl': self.lsl,
            'usl': self.usl,
            'distribution_fit': self.distribution_fit,
            'interpretation': self.interpretation
        }


class AdvancedCapability:
    """
    Provides advanced process capability analysis.
    """
    
    @staticmethod
    def long_term_capability(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float,
        target: Optional[float] = None,
        subgroup_size: Optional[int] = None
    ) -> LongTermCapabilityResult:
        """
        Calculate long-term (overall) process capability indices Pp and Ppk.
        
        Pp/Ppk use overall standard deviation, while Cp/Cpk use within-subgroup.
        
        Args:
            data: Process data
            lsl: Lower specification limit
            usl: Upper specification limit
            target: Target value (defaults to midpoint of specs)
            subgroup_size: Optional subgroup size for within std dev comparison
            
        Returns:
            LongTermCapabilityResult with Pp/Ppk metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 2:
            raise ValueError("At least 2 data points required")
        
        if lsl >= usl:
            raise ValueError("LSL must be less than USL")
        
        if target is None:
            target = (lsl + usl) / 2
        
        mean = np.mean(data)
        std_dev = np.std(data, ddof=1)  # Overall (long-term) std dev
        n = len(data)
        
        if std_dev == 0:
            raise ValueError("Standard deviation is zero")
        
        # Calculate Pp (potential capability)
        pp = (usl - lsl) / (6 * std_dev)
        
        # Calculate Ppu and Ppl
        ppu = (usl - mean) / (3 * std_dev)
        ppl = (mean - lsl) / (3 * std_dev)
        
        # Ppk is the minimum
        ppk = min(ppu, ppl)
        
        # Calculate within-subgroup std dev for comparison if subgroups provided
        within_std_dev = None
        if subgroup_size and subgroup_size > 1:
            n_subgroups = len(data) // subgroup_size
            if n_subgroups >= 2:
                ranges = []
                for i in range(n_subgroups):
                    subgroup = data[i*subgroup_size:(i+1)*subgroup_size]
                    ranges.append(np.max(subgroup) - np.min(subgroup))
                r_bar = np.mean(ranges)
                # d2 factors for subgroup sizes
                d2_table = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534}
                d2 = d2_table.get(subgroup_size, 2.326)
                within_std_dev = r_bar / d2
        
        # Interpretation
        if ppk >= 1.33:
            quality_level = "excellent (capable)"
        elif ppk >= 1.0:
            quality_level = "acceptable (marginally capable)"
        elif ppk >= 0.67:
            quality_level = "poor (needs improvement)"
        else:
            quality_level = "inadequate (significant improvement needed)"
        
        interpretation = (
            f"Long-term capability: Pp = {pp:.3f}, Ppk = {ppk:.3f}. "
            f"Process performance is {quality_level}. "
        )
        
        if ppk < pp:
            interpretation += f"Process is off-center (Ppu = {ppu:.3f}, Ppl = {ppl:.3f})."
        
        return LongTermCapabilityResult(
            pp=pp,
            ppk=ppk,
            ppu=ppu,
            ppl=ppl,
            lsl=lsl,
            usl=usl,
            target=target,
            mean=mean,
            std_dev=std_dev,
            within_std_dev=within_std_dev,
            n=n,
            interpretation=interpretation
        )
    
    @staticmethod
    def cpm_taguchi(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float,
        target: float
    ) -> CpmResult:
        """
        Calculate Cpm (Taguchi capability index).
        
        Cpm accounts for deviation from target, not just specification limits.
        It penalizes processes that are off-target even if within specifications.
        
        Args:
            data: Process data
            lsl: Lower specification limit
            usl: Upper specification limit
            target: Target value
            
        Returns:
            CpmResult with Cpm metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 2:
            raise ValueError("At least 2 data points required")
        
        if lsl >= usl:
            raise ValueError("LSL must be less than USL")
        
        if not (lsl <= target <= usl):
            warnings.warn("Target is outside specification limits")
        
        mean = np.mean(data)
        std_dev = np.std(data, ddof=1)
        n = len(data)
        
        # Calculate Cp and Cpk for comparison
        cp = (usl - lsl) / (6 * std_dev)
        cpu = (usl - mean) / (3 * std_dev)
        cpl = (mean - lsl) / (3 * std_dev)
        cpk = min(cpu, cpl)
        
        # Calculate tau (deviation from target)
        target_deviation = mean - target
        
        # Calculate sigma_tau (std dev around target)
        tau_squared = std_dev**2 + target_deviation**2
        sigma_tau = np.sqrt(tau_squared)
        
        # Calculate Cpm
        cpm = (usl - lsl) / (6 * sigma_tau)
        
        # Interpretation
        if cpm >= cpk:
            interpretation = (
                f"Cpm = {cpm:.3f} (Cpk = {cpk:.3f}). "
                f"Process is well-centered on target. "
            )
        else:
            interpretation = (
                f"Cpm = {cpm:.3f} < Cpk = {cpk:.3f}. "
                f"Process is off-target by {abs(target_deviation):.4f}. "
                f"Centering the process on target would improve capability. "
            )
        
        return CpmResult(
            cpm=cpm,
            cp=cp,
            cpk=cpk,
            target=target,
            mean=mean,
            std_dev=std_dev,
            target_deviation=target_deviation,
            n=n,
            interpretation=interpretation
        )
    
    @staticmethod
    def box_cox_transform(
        data: Union[List[float], np.ndarray],
        lambda_value: Optional[float] = None
    ) -> BoxCoxResult:
        """
        Apply Box-Cox transformation to normalize data.
        
        Box-Cox transformation: y = (x^λ - 1) / λ if λ ≠ 0, else y = ln(x)
        
        Args:
            data: Data to transform (must be positive)
            lambda_value: Fixed λ value, or None to optimize
            
        Returns:
            BoxCoxResult with transformed data and statistics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 3:
            raise ValueError("At least 3 data points required")
        
        if np.any(data <= 0):
            raise ValueError("Box-Cox requires all positive data. Consider adding a constant.")
        
        original_mean = np.mean(data)
        original_std = np.std(data, ddof=1)
        
        # Test normality before transformation
        if len(data) >= 8:
            normality_before = stats.anderson(data)
            norm_stat_before = normality_before.statistic
            # Use 5% critical value
            norm_p_before = 0.05 if norm_stat_before < normality_before.critical_values[2] else 0.01
        else:
            stat, p = stats.shapiro(data)
            norm_stat_before = stat
            norm_p_before = p
        
        # Perform transformation
        if lambda_value is None:
            transformed, optimal_lambda = stats.boxcox(data)
        else:
            optimal_lambda = lambda_value
            if lambda_value == 0:
                transformed = np.log(data)
            else:
                transformed = (np.power(data, lambda_value) - 1) / lambda_value
        
        transformed_mean = np.mean(transformed)
        transformed_std = np.std(transformed, ddof=1)
        
        # Test normality after transformation
        if len(transformed) >= 8:
            normality_after = stats.anderson(transformed)
            norm_stat_after = normality_after.statistic
            norm_p_after = 0.05 if norm_stat_after < normality_after.critical_values[2] else 0.01
        else:
            stat, p = stats.shapiro(transformed)
            norm_stat_after = stat
            norm_p_after = p
        
        # Generate transformation formula
        if abs(optimal_lambda) < 0.01:
            formula = "y = ln(x)"
        elif abs(optimal_lambda - 0.5) < 0.01:
            formula = "y = √x (square root)"
        elif abs(optimal_lambda - 1) < 0.01:
            formula = "y = x (no transformation needed)"
        elif abs(optimal_lambda - 2) < 0.01:
            formula = "y = x² (square)"
        elif abs(optimal_lambda + 1) < 0.01:
            formula = "y = 1/x (inverse)"
        else:
            formula = f"y = (x^{optimal_lambda:.4f} - 1) / {optimal_lambda:.4f}"
        
        # Interpretation
        improved = norm_p_after > norm_p_before
        interpretation = (
            f"Box-Cox λ = {optimal_lambda:.4f}. "
            f"Transformation: {formula}. "
        )
        if improved:
            interpretation += "Normality improved after transformation."
        else:
            interpretation += "Normality did not significantly improve. Consider other transformations."
        
        return BoxCoxResult(
            lambda_value=optimal_lambda,
            transformed_data=transformed,
            original_mean=original_mean,
            original_std=original_std,
            transformed_mean=transformed_mean,
            transformed_std=transformed_std,
            normality_before=(norm_stat_before, norm_p_before),
            normality_after=(norm_stat_after, norm_p_after),
            transformation_formula=formula,
            interpretation=interpretation
        )
    
    @staticmethod
    def non_normal_capability_percentile(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float
    ) -> NonNormalCapabilityResult:
        """
        Calculate capability using percentile method (distribution-free).
        
        Uses empirical percentiles to estimate PPM outside specifications.
        
        Args:
            data: Process data
            lsl: Lower specification limit
            usl: Upper specification limit
            
        Returns:
            NonNormalCapabilityResult with capability metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if len(data) < 30:
            warnings.warn("Percentile method works best with n >= 30")
        
        n = len(data)
        
        # Count observations outside specs
        below_lsl = np.sum(data < lsl)
        above_usl = np.sum(data > usl)
        
        # Calculate PPM
        ppm_below = (below_lsl / n) * 1_000_000
        ppm_above = (above_usl / n) * 1_000_000
        ppm_total = ppm_below + ppm_above
        
        # Estimate equivalent Ppk from PPM
        # Using relationship: PPM ≈ 2 * (1 - Φ(3*Ppk)) * 1,000,000
        if ppm_total > 0 and ppm_total < 1_000_000:
            # Solve for Ppk
            defect_rate = ppm_total / 1_000_000
            z = stats.norm.ppf(1 - defect_rate / 2)
            equivalent_ppk = z / 3
        elif ppm_total == 0:
            equivalent_ppk = 2.0  # Cap at high value
        else:
            equivalent_ppk = 0.0
        
        # Calculate empirical percentiles for distribution info
        p_0135 = np.percentile(data, 0.135)
        p_50 = np.percentile(data, 50)
        p_99865 = np.percentile(data, 99.865)
        
        distribution_fit = {
            'method': 'empirical',
            'p_0135': p_0135,
            'p_50_median': p_50,
            'p_99865': p_99865,
            'n': n
        }
        
        interpretation = (
            f"Percentile method: {ppm_total:.0f} PPM total defective "
            f"({ppm_below:.0f} below LSL, {ppm_above:.0f} above USL). "
            f"Equivalent Ppk ≈ {equivalent_ppk:.3f}."
        )
        
        return NonNormalCapabilityResult(
            method='percentile',
            ppm_below_lsl=ppm_below,
            ppm_above_usl=ppm_above,
            ppm_total=ppm_total,
            equivalent_ppk=equivalent_ppk,
            lsl=lsl,
            usl=usl,
            distribution_fit=distribution_fit,
            interpretation=interpretation
        )
    
    @staticmethod
    def non_normal_capability_weibull(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float
    ) -> NonNormalCapabilityResult:
        """
        Calculate capability using Weibull distribution fit.
        
        Useful for reliability data, life data, and right-skewed distributions.
        
        Args:
            data: Process data (must be positive)
            lsl: Lower specification limit
            usl: Upper specification limit
            
        Returns:
            NonNormalCapabilityResult with capability metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if np.any(data <= 0):
            raise ValueError("Weibull requires positive data")
        
        # Fit Weibull distribution
        shape, loc, scale = stats.weibull_min.fit(data, floc=0)
        
        # Calculate probabilities
        p_below_lsl = stats.weibull_min.cdf(lsl, shape, loc, scale)
        p_above_usl = 1 - stats.weibull_min.cdf(usl, shape, loc, scale)
        
        ppm_below = p_below_lsl * 1_000_000
        ppm_above = p_above_usl * 1_000_000
        ppm_total = ppm_below + ppm_above
        
        # Equivalent Ppk
        if ppm_total > 0 and ppm_total < 1_000_000:
            defect_rate = ppm_total / 1_000_000
            z = stats.norm.ppf(1 - defect_rate / 2)
            equivalent_ppk = z / 3
        elif ppm_total == 0:
            equivalent_ppk = 2.0
        else:
            equivalent_ppk = 0.0
        
        distribution_fit = {
            'distribution': 'weibull',
            'shape': shape,
            'scale': scale,
            'location': loc
        }
        
        interpretation = (
            f"Weibull fit (shape={shape:.3f}, scale={scale:.3f}): "
            f"{ppm_total:.0f} PPM total defective. "
            f"Equivalent Ppk ≈ {equivalent_ppk:.3f}."
        )
        
        return NonNormalCapabilityResult(
            method='weibull',
            ppm_below_lsl=ppm_below,
            ppm_above_usl=ppm_above,
            ppm_total=ppm_total,
            equivalent_ppk=equivalent_ppk,
            lsl=lsl,
            usl=usl,
            distribution_fit=distribution_fit,
            interpretation=interpretation
        )
    
    @staticmethod
    def non_normal_capability_lognormal(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float
    ) -> NonNormalCapabilityResult:
        """
        Calculate capability using lognormal distribution fit.
        
        Useful for right-skewed data that cannot be negative.
        
        Args:
            data: Process data (must be positive)
            lsl: Lower specification limit
            usl: Upper specification limit
            
        Returns:
            NonNormalCapabilityResult with capability metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if np.any(data <= 0):
            raise ValueError("Lognormal requires positive data")
        
        # Fit lognormal distribution
        shape, loc, scale = stats.lognorm.fit(data, floc=0)
        
        # Calculate probabilities
        p_below_lsl = stats.lognorm.cdf(lsl, shape, loc, scale)
        p_above_usl = 1 - stats.lognorm.cdf(usl, shape, loc, scale)
        
        ppm_below = p_below_lsl * 1_000_000
        ppm_above = p_above_usl * 1_000_000
        ppm_total = ppm_below + ppm_above
        
        # Equivalent Ppk
        if ppm_total > 0 and ppm_total < 1_000_000:
            defect_rate = ppm_total / 1_000_000
            z = stats.norm.ppf(1 - defect_rate / 2)
            equivalent_ppk = z / 3
        elif ppm_total == 0:
            equivalent_ppk = 2.0
        else:
            equivalent_ppk = 0.0
        
        # Convert to mu/sigma parameterization
        mu = np.log(scale)
        sigma = shape
        
        distribution_fit = {
            'distribution': 'lognormal',
            'mu': mu,
            'sigma': sigma,
            'location': loc,
            'scale': scale
        }
        
        interpretation = (
            f"Lognormal fit (μ={mu:.3f}, σ={sigma:.3f}): "
            f"{ppm_total:.0f} PPM total defective. "
            f"Equivalent Ppk ≈ {equivalent_ppk:.3f}."
        )
        
        return NonNormalCapabilityResult(
            method='lognormal',
            ppm_below_lsl=ppm_below,
            ppm_above_usl=ppm_above,
            ppm_total=ppm_total,
            equivalent_ppk=equivalent_ppk,
            lsl=lsl,
            usl=usl,
            distribution_fit=distribution_fit,
            interpretation=interpretation
        )
    
    @staticmethod
    def capability_comparison(
        data: Union[List[float], np.ndarray],
        lsl: float,
        usl: float,
        target: Optional[float] = None
    ) -> Dict:
        """
        Compare all capability indices for the same data.
        
        Args:
            data: Process data
            lsl: Lower specification limit
            usl: Upper specification limit
            target: Target value
            
        Returns:
            Dictionary with all capability metrics
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        
        if target is None:
            target = (lsl + usl) / 2
        
        results = {}
        
        # Calculate Pp/Ppk
        try:
            pp_result = AdvancedCapability.long_term_capability(data, lsl, usl, target)
            results['pp_ppk'] = pp_result.to_dict()
        except Exception as e:
            results['pp_ppk'] = {'error': str(e)}
        
        # Calculate Cpm
        try:
            cpm_result = AdvancedCapability.cpm_taguchi(data, lsl, usl, target)
            results['cpm'] = cpm_result.to_dict()
        except Exception as e:
            results['cpm'] = {'error': str(e)}
        
        # Calculate percentile-based
        try:
            pct_result = AdvancedCapability.non_normal_capability_percentile(data, lsl, usl)
            results['percentile'] = pct_result.to_dict()
        except Exception as e:
            results['percentile'] = {'error': str(e)}
        
        # Calculate Weibull-based if data is positive
        if np.all(data > 0):
            try:
                weibull_result = AdvancedCapability.non_normal_capability_weibull(data, lsl, usl)
                results['weibull'] = weibull_result.to_dict()
            except Exception as e:
                results['weibull'] = {'error': str(e)}
            
            try:
                lognorm_result = AdvancedCapability.non_normal_capability_lognormal(data, lsl, usl)
                results['lognormal'] = lognorm_result.to_dict()
            except Exception as e:
                results['lognormal'] = {'error': str(e)}
        
        return results
