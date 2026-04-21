"""
CiviQual Stats Advanced Control Charts

Provides advanced control chart methods:
- CUSUM (Cumulative Sum) Control Charts
- EWMA (Exponentially Weighted Moving Average) Control Charts

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats


@dataclass
class CUSUMResult:
    """Result of CUSUM analysis."""
    data: np.ndarray
    target: float
    cusum_upper: np.ndarray  # C+
    cusum_lower: np.ndarray  # C-
    ucl: float
    lcl: float
    k: float  # Slack value
    h: float  # Decision interval
    signals_upper: List[int]  # Indices where upper CUSUM signals
    signals_lower: List[int]  # Indices where lower CUSUM signals
    arl_in_control: float
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'target': self.target,
            'ucl': self.ucl,
            'lcl': self.lcl,
            'k': self.k,
            'h': self.h,
            'signals_upper': self.signals_upper,
            'signals_lower': self.signals_lower,
            'n_signals': len(self.signals_upper) + len(self.signals_lower),
            'arl_in_control': self.arl_in_control,
            'interpretation': self.interpretation
        }


@dataclass
class EWMAResult:
    """Result of EWMA analysis."""
    data: np.ndarray
    target: float
    ewma: np.ndarray
    ucl: np.ndarray  # May vary with time
    lcl: np.ndarray
    center_line: float
    lambda_weight: float
    L: float  # Control limit multiplier
    signals: List[int]  # Indices where EWMA signals
    arl_in_control: float
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'target': self.target,
            'center_line': self.center_line,
            'lambda_weight': self.lambda_weight,
            'L': self.L,
            'signals': self.signals,
            'n_signals': len(self.signals),
            'arl_in_control': self.arl_in_control,
            'interpretation': self.interpretation
        }


class AdvancedControlCharts:
    """
    Provides CUSUM and EWMA control chart methods.
    
    These charts are more sensitive to small shifts than Shewhart charts.
    """
    
    @staticmethod
    def cusum(
        data: Union[List[float], np.ndarray],
        target: Optional[float] = None,
        std_dev: Optional[float] = None,
        k: float = 0.5,
        h: float = 5.0
    ) -> CUSUMResult:
        """
        Create CUSUM (Cumulative Sum) control chart.
        
        CUSUM is designed to detect small sustained shifts in the process mean.
        It accumulates deviations from target and signals when the cumulative
        sum exceeds a threshold.
        
        Args:
            data: Process data
            target: Target value (defaults to data mean)
            std_dev: Standard deviation (defaults to estimated from data)
            k: Slack value (allowance), typically 0.5σ
            h: Decision interval, typically 4-5σ
            
        Returns:
            CUSUMResult with CUSUM statistics and signals
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n < 10:
            raise ValueError("At least 10 data points required for CUSUM")
        
        # Set target (μ₀)
        if target is None:
            target = np.mean(data)
        
        # Set standard deviation
        if std_dev is None:
            # Use moving range method
            mr = np.abs(np.diff(data))
            std_dev = np.mean(mr) / 1.128
        
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
        
        # Standardize slack value and decision interval
        K = k * std_dev  # Slack in original units
        H = h * std_dev  # Decision interval in original units
        
        # Calculate CUSUM statistics
        cusum_upper = np.zeros(n)  # C+ (upper CUSUM)
        cusum_lower = np.zeros(n)  # C- (lower CUSUM)
        
        for i in range(n):
            xi = data[i]
            if i == 0:
                cusum_upper[i] = max(0, xi - target - K)
                cusum_lower[i] = max(0, target - xi - K)
            else:
                cusum_upper[i] = max(0, cusum_upper[i-1] + (xi - target - K))
                cusum_lower[i] = max(0, cusum_lower[i-1] + (target - xi - K))
        
        # Detect signals
        signals_upper = list(np.where(cusum_upper > H)[0])
        signals_lower = list(np.where(cusum_lower > H)[0])
        
        # Control limits (for plotting)
        ucl = H
        lcl = -H  # For lower CUSUM plotted negative
        
        # Approximate ARL when in control
        # For k=0.5 and h=5, ARL ≈ 465
        # Using Siegmund approximation
        b = h + 1.166
        arl = np.exp(2 * k * b) / (2 * k**2) if k > 0 else 1000
        
        # Interpretation
        n_signals = len(signals_upper) + len(signals_lower)
        if n_signals == 0:
            interpretation = (
                f"CUSUM chart shows no out-of-control signals. "
                f"Process appears stable around target = {target:.4f}."
            )
        else:
            interpretation = (
                f"CUSUM chart detected {n_signals} signal(s). "
                f"{len(signals_upper)} upward shift(s), {len(signals_lower)} downward shift(s). "
                f"Process may have shifted from target = {target:.4f}."
            )
        
        return CUSUMResult(
            data=data,
            target=target,
            cusum_upper=cusum_upper,
            cusum_lower=cusum_lower,
            ucl=ucl,
            lcl=lcl,
            k=k,
            h=h,
            signals_upper=signals_upper,
            signals_lower=signals_lower,
            arl_in_control=arl,
            interpretation=interpretation
        )
    
    @staticmethod
    def ewma(
        data: Union[List[float], np.ndarray],
        target: Optional[float] = None,
        std_dev: Optional[float] = None,
        lambda_weight: float = 0.2,
        L: float = 3.0,
        exact_limits: bool = True
    ) -> EWMAResult:
        """
        Create EWMA (Exponentially Weighted Moving Average) control chart.
        
        EWMA is designed to detect small shifts by giving more weight to 
        recent observations while not ignoring historical data.
        
        Args:
            data: Process data
            target: Target value (defaults to data mean)
            std_dev: Standard deviation (defaults to estimated from data)
            lambda_weight: Smoothing parameter (0 < λ ≤ 1), typically 0.05-0.25
            L: Control limit width multiplier (typically 2.7-3.0)
            exact_limits: If True, use time-varying limits; if False, use steady-state
            
        Returns:
            EWMAResult with EWMA statistics and signals
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n < 10:
            raise ValueError("At least 10 data points required for EWMA")
        
        if not 0 < lambda_weight <= 1:
            raise ValueError("lambda_weight must be between 0 and 1")
        
        # Set target (μ₀)
        if target is None:
            target = np.mean(data)
        
        # Set standard deviation
        if std_dev is None:
            mr = np.abs(np.diff(data))
            std_dev = np.mean(mr) / 1.128
        
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
        
        lam = lambda_weight
        
        # Calculate EWMA
        ewma = np.zeros(n)
        ewma[0] = lam * data[0] + (1 - lam) * target
        for i in range(1, n):
            ewma[i] = lam * data[i] + (1 - lam) * ewma[i-1]
        
        # Calculate control limits
        if exact_limits:
            # Time-varying limits (exact)
            ucl = np.zeros(n)
            lcl = np.zeros(n)
            for i in range(n):
                factor = np.sqrt(lam / (2 - lam) * (1 - (1 - lam)**(2*(i+1))))
                ucl[i] = target + L * std_dev * factor
                lcl[i] = target - L * std_dev * factor
        else:
            # Steady-state limits (approximate)
            factor = np.sqrt(lam / (2 - lam))
            ucl = np.full(n, target + L * std_dev * factor)
            lcl = np.full(n, target - L * std_dev * factor)
        
        # Detect signals
        signals = list(np.where((ewma > ucl) | (ewma < lcl))[0])
        
        # Approximate ARL when in control
        # Using Lucas & Saccucci approximation for λ=0.2, L=3
        if lam <= 0.1:
            arl = 500  # Approximate
        elif lam <= 0.25:
            arl = 380  # Approximate
        else:
            arl = 250  # Approximate
        
        # Interpretation
        if len(signals) == 0:
            interpretation = (
                f"EWMA chart (λ={lam}, L={L}) shows no out-of-control signals. "
                f"Process appears stable around target = {target:.4f}."
            )
        else:
            interpretation = (
                f"EWMA chart detected {len(signals)} signal(s). "
                f"First signal at observation {signals[0] + 1}. "
                f"Process may have shifted from target = {target:.4f}."
            )
        
        return EWMAResult(
            data=data,
            target=target,
            ewma=ewma,
            ucl=ucl,
            lcl=lcl,
            center_line=target,
            lambda_weight=lam,
            L=L,
            signals=signals,
            arl_in_control=arl,
            interpretation=interpretation
        )
    
    @staticmethod
    def cusum_design(
        shift: float,
        arl_in_control: float = 370,
        arl_out_of_control: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Design CUSUM parameters k and h for desired ARL.
        
        Args:
            shift: Shift to detect (in σ units)
            arl_in_control: Desired in-control ARL (default 370)
            arl_out_of_control: Desired out-of-control ARL
            
        Returns:
            Tuple of (k, h) parameters
        """
        # Common recommendations based on shift size
        if shift <= 0.5:
            k = shift / 2
            h = 5.0  # Conservative
        elif shift <= 1.0:
            k = 0.5
            h = 4.77
        elif shift <= 1.5:
            k = 0.75
            h = 4.0
        else:
            k = 1.0
            h = 3.5
        
        return k, h
    
    @staticmethod
    def ewma_design(
        shift: float,
        arl_in_control: float = 370
    ) -> Tuple[float, float]:
        """
        Design EWMA parameters λ and L for desired ARL.
        
        Args:
            shift: Shift to detect (in σ units)
            arl_in_control: Desired in-control ARL
            
        Returns:
            Tuple of (lambda, L) parameters
        """
        # Recommendations from Lucas & Saccucci
        if shift <= 0.5:
            lam = 0.05
            L = 2.615
        elif shift <= 0.75:
            lam = 0.1
            L = 2.7
        elif shift <= 1.0:
            lam = 0.2
            L = 2.9
        elif shift <= 1.5:
            lam = 0.25
            L = 2.95
        else:
            lam = 0.4
            L = 3.0
        
        return lam, L
    
    @staticmethod
    def compare_chart_sensitivity(
        shift_sizes: List[float] = None
    ) -> Dict:
        """
        Compare sensitivity of different control chart types.
        
        Returns approximate ARL values for different shift sizes.
        
        Args:
            shift_sizes: List of shift sizes (in σ) to evaluate
            
        Returns:
            Dictionary with ARL comparisons
        """
        if shift_sizes is None:
            shift_sizes = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]
        
        # Approximate ARLs from literature
        results = {
            'shift_sizes': shift_sizes,
            'shewhart': [],  # Traditional X-bar chart
            'cusum': [],
            'ewma': []
        }
        
        for shift in shift_sizes:
            # Shewhart (3-sigma limits)
            # ARL = 1/P(signal) ≈ 1/(2*Φ(-3+shift))
            p_signal = 2 * stats.norm.cdf(-3 + shift)
            shewhart_arl = 1/p_signal if p_signal > 0 else 1000
            results['shewhart'].append(min(shewhart_arl, 1000))
            
            # CUSUM (k=0.5, h=5)
            # Approximate using Siegmund formula
            if shift <= 0.25:
                cusum_arl = 300
            elif shift <= 0.5:
                cusum_arl = 38
            elif shift <= 1.0:
                cusum_arl = 10
            elif shift <= 1.5:
                cusum_arl = 5
            else:
                cusum_arl = 3
            results['cusum'].append(cusum_arl)
            
            # EWMA (λ=0.2, L=3)
            if shift <= 0.25:
                ewma_arl = 280
            elif shift <= 0.5:
                ewma_arl = 42
            elif shift <= 1.0:
                ewma_arl = 11
            elif shift <= 1.5:
                ewma_arl = 5
            else:
                ewma_arl = 3
            results['ewma'].append(ewma_arl)
        
        return results
    
    @staticmethod
    def get_cusum_plot_data(result: CUSUMResult) -> Dict:
        """
        Get data formatted for CUSUM plot.
        
        Args:
            result: CUSUMResult from cusum()
            
        Returns:
            Dictionary with plot data
        """
        n = len(result.data)
        
        return {
            'x': list(range(1, n + 1)),
            'cusum_upper': result.cusum_upper.tolist(),
            'cusum_lower': (-result.cusum_lower).tolist(),  # Plot negative
            'ucl': result.ucl,
            'lcl': -result.ucl,  # Symmetric
            'center': 0,
            'signals_upper': [i + 1 for i in result.signals_upper],
            'signals_lower': [i + 1 for i in result.signals_lower],
            'title': f'CUSUM Chart (k={result.k}, h={result.h})'
        }
    
    @staticmethod
    def get_ewma_plot_data(result: EWMAResult) -> Dict:
        """
        Get data formatted for EWMA plot.
        
        Args:
            result: EWMAResult from ewma()
            
        Returns:
            Dictionary with plot data
        """
        n = len(result.data)
        
        return {
            'x': list(range(1, n + 1)),
            'ewma': result.ewma.tolist(),
            'raw_data': result.data.tolist(),
            'ucl': result.ucl.tolist(),
            'lcl': result.lcl.tolist(),
            'center': result.center_line,
            'signals': [i + 1 for i in result.signals],
            'title': f'EWMA Chart (λ={result.lambda_weight}, L={result.L})'
        }
