"""
CiviQual Stats Lean Calculators

Provides calculators for common Lean Six Sigma metrics:
- Process Sigma Calculator
- DPMO Calculator
- Rolled Throughput Yield (RTY)
- First Pass Yield (FPY)
- Takt Time Calculator
- Cycle Time Analysis
- Little's Law Calculator
- Cost of Poor Quality (COPQ)

Copyright (c) 2026 A Step in the Right Direction LLC
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
import numpy as np


@dataclass
class SigmaResult:
    """Result of process sigma calculation."""
    sigma_level: float
    dpmo: float
    yield_percent: float
    defect_percent: float
    cpk_equivalent: float
    
    def to_dict(self) -> Dict:
        return {
            'sigma_level': self.sigma_level,
            'dpmo': self.dpmo,
            'yield_percent': self.yield_percent,
            'defect_percent': self.defect_percent,
            'cpk_equivalent': self.cpk_equivalent
        }


@dataclass 
class RTYResult:
    """Result of rolled throughput yield calculation."""
    rty: float
    rty_percent: float
    process_sigma: float
    individual_yields: List[float]
    hidden_factory_loss: float
    
    def to_dict(self) -> Dict:
        return {
            'rty': self.rty,
            'rty_percent': self.rty_percent,
            'process_sigma': self.process_sigma,
            'individual_yields': self.individual_yields,
            'hidden_factory_loss': self.hidden_factory_loss
        }


@dataclass
class TaktTimeResult:
    """Result of takt time calculation."""
    takt_time: float
    takt_time_unit: str
    available_time: float
    demand: float
    cycle_time_ratio: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'takt_time': self.takt_time,
            'takt_time_unit': self.takt_time_unit,
            'available_time': self.available_time,
            'demand': self.demand,
            'cycle_time_ratio': self.cycle_time_ratio
        }


@dataclass
class LittlesLawResult:
    """Result of Little's Law calculation."""
    wip: float
    throughput: float
    lead_time: float
    solved_for: str  # Which variable was calculated
    
    def to_dict(self) -> Dict:
        return {
            'wip': self.wip,
            'throughput': self.throughput,
            'lead_time': self.lead_time,
            'solved_for': self.solved_for
        }


@dataclass
class COPQResult:
    """Result of Cost of Poor Quality calculation."""
    total_copq: float
    internal_failure: float
    external_failure: float
    appraisal: float
    prevention: float
    copq_percent_revenue: float
    
    def to_dict(self) -> Dict:
        return {
            'total_copq': self.total_copq,
            'internal_failure': self.internal_failure,
            'external_failure': self.external_failure,
            'appraisal': self.appraisal,
            'prevention': self.prevention,
            'copq_percent_revenue': self.copq_percent_revenue
        }


class LeanCalculators:
    """
    Provides Lean Six Sigma calculators for process metrics.
    """
    
    # Standard sigma shift (1.5σ shift is standard for Six Sigma)
    SIGMA_SHIFT = 1.5
    
    @staticmethod
    def dpmo_to_sigma(dpmo: float, include_shift: bool = True) -> float:
        """
        Convert DPMO to process sigma level.
        
        Args:
            dpmo: Defects per million opportunities
            include_shift: If True, includes 1.5σ shift (standard Six Sigma)
            
        Returns:
            Sigma level
        """
        if dpmo <= 0:
            return 6.0 if include_shift else 4.5
        if dpmo >= 1_000_000:
            return 0.0
        
        # Calculate z-score from yield
        yield_rate = 1 - (dpmo / 1_000_000)
        z_score = stats.norm.ppf(yield_rate)
        
        # Add 1.5σ shift if requested
        sigma = z_score + (LeanCalculators.SIGMA_SHIFT if include_shift else 0)
        
        return max(0, sigma)
    
    @staticmethod
    def sigma_to_dpmo(sigma: float, include_shift: bool = True) -> float:
        """
        Convert sigma level to DPMO.
        
        Args:
            sigma: Process sigma level
            include_shift: If True, sigma includes 1.5σ shift
            
        Returns:
            DPMO value
        """
        # Remove shift to get actual z-score
        z_score = sigma - (LeanCalculators.SIGMA_SHIFT if include_shift else 0)
        
        # Calculate yield from z-score
        yield_rate = stats.norm.cdf(z_score)
        
        # Convert to DPMO
        dpmo = (1 - yield_rate) * 1_000_000
        
        return max(0, min(1_000_000, dpmo))
    
    @staticmethod
    def calculate_process_sigma(
        defects: int,
        units: int,
        opportunities: int,
        include_shift: bool = True
    ) -> SigmaResult:
        """
        Calculate process sigma level from defect data.
        
        Args:
            defects: Number of defects found
            units: Number of units inspected
            opportunities: Number of defect opportunities per unit
            include_shift: Include 1.5σ shift (standard)
            
        Returns:
            SigmaResult with sigma level and related metrics
        """
        total_opportunities = units * opportunities
        
        if total_opportunities <= 0:
            raise ValueError("Total opportunities must be positive")
        
        dpo = defects / total_opportunities
        dpmo = dpo * 1_000_000
        
        sigma_level = LeanCalculators.dpmo_to_sigma(dpmo, include_shift)
        yield_percent = (1 - dpo) * 100
        defect_percent = dpo * 100
        cpk_equivalent = sigma_level / 3
        
        return SigmaResult(
            sigma_level=sigma_level,
            dpmo=dpmo,
            yield_percent=yield_percent,
            defect_percent=defect_percent,
            cpk_equivalent=cpk_equivalent
        )
    
    @staticmethod
    def calculate_dpmo(
        defects: int,
        units: int,
        opportunities: int
    ) -> Tuple[float, float, float]:
        """
        Calculate DPMO, DPO, and DPU.
        
        Args:
            defects: Number of defects
            units: Number of units
            opportunities: Opportunities per unit
            
        Returns:
            Tuple of (DPMO, DPO, DPU)
        """
        if units <= 0 or opportunities <= 0:
            raise ValueError("Units and opportunities must be positive")
        
        dpu = defects / units
        dpo = defects / (units * opportunities)
        dpmo = dpo * 1_000_000
        
        return dpmo, dpo, dpu
    
    @staticmethod
    def calculate_first_pass_yield(
        units_in: int,
        defects: int
    ) -> Tuple[float, float]:
        """
        Calculate First Pass Yield (FPY).
        
        Args:
            units_in: Number of units entering the process
            defects: Number of defective units
            
        Returns:
            Tuple of (FPY as decimal, FPY as percent)
        """
        if units_in <= 0:
            raise ValueError("Units must be positive")
        
        fpy = (units_in - defects) / units_in
        fpy_percent = fpy * 100
        
        return fpy, fpy_percent
    
    @staticmethod
    def calculate_rty(yields: List[float]) -> RTYResult:
        """
        Calculate Rolled Throughput Yield (RTY).
        
        RTY = Product of individual process step yields
        
        Args:
            yields: List of individual step yields (as decimals, 0-1)
            
        Returns:
            RTYResult with RTY and related metrics
        """
        if not yields:
            raise ValueError("At least one yield value required")
        
        for y in yields:
            if not 0 <= y <= 1:
                raise ValueError("Yields must be between 0 and 1")
        
        # Calculate RTY
        rty = 1.0
        for y in yields:
            rty *= y
        
        rty_percent = rty * 100
        
        # Calculate process sigma from RTY
        if rty > 0:
            dpmo_equivalent = (1 - rty) * 1_000_000
            process_sigma = LeanCalculators.dpmo_to_sigma(dpmo_equivalent)
        else:
            process_sigma = 0.0
        
        # Hidden factory loss (1 - RTY)
        hidden_factory_loss = (1 - rty) * 100
        
        return RTYResult(
            rty=rty,
            rty_percent=rty_percent,
            process_sigma=process_sigma,
            individual_yields=yields,
            hidden_factory_loss=hidden_factory_loss
        )
    
    @staticmethod
    def calculate_takt_time(
        available_time: float,
        demand: int,
        time_unit: str = 'minutes',
        actual_cycle_time: Optional[float] = None
    ) -> TaktTimeResult:
        """
        Calculate Takt Time.
        
        Takt Time = Available Time / Customer Demand
        
        Args:
            available_time: Available production time
            demand: Customer demand (units)
            time_unit: Unit of time (seconds, minutes, hours)
            actual_cycle_time: Optional actual cycle time for comparison
            
        Returns:
            TaktTimeResult with takt time and analysis
        """
        if demand <= 0:
            raise ValueError("Demand must be positive")
        if available_time <= 0:
            raise ValueError("Available time must be positive")
        
        takt_time = available_time / demand
        
        # Calculate cycle time ratio if provided
        cycle_time_ratio = None
        if actual_cycle_time is not None and actual_cycle_time > 0:
            cycle_time_ratio = actual_cycle_time / takt_time
        
        return TaktTimeResult(
            takt_time=takt_time,
            takt_time_unit=time_unit,
            available_time=available_time,
            demand=demand,
            cycle_time_ratio=cycle_time_ratio
        )
    
    @staticmethod
    def calculate_cycle_time_stats(cycle_times: List[float]) -> Dict:
        """
        Calculate cycle time statistics.
        
        Args:
            cycle_times: List of individual cycle times
            
        Returns:
            Dictionary with cycle time statistics
        """
        if not cycle_times:
            raise ValueError("Cycle times list cannot be empty")
        
        ct_array = np.array(cycle_times)
        
        return {
            'mean': float(np.mean(ct_array)),
            'median': float(np.median(ct_array)),
            'std_dev': float(np.std(ct_array, ddof=1)),
            'min': float(np.min(ct_array)),
            'max': float(np.max(ct_array)),
            'range': float(np.max(ct_array) - np.min(ct_array)),
            'cv': float(np.std(ct_array, ddof=1) / np.mean(ct_array)) if np.mean(ct_array) > 0 else 0,
            'count': len(cycle_times),
            'total': float(np.sum(ct_array))
        }
    
    @staticmethod
    def calculate_littles_law(
        wip: Optional[float] = None,
        throughput: Optional[float] = None,
        lead_time: Optional[float] = None
    ) -> LittlesLawResult:
        """
        Apply Little's Law: WIP = Throughput × Lead Time
        
        Provide any two values to calculate the third.
        
        Args:
            wip: Work in Process (units)
            throughput: Throughput rate (units per time period)
            lead_time: Lead time (time periods)
            
        Returns:
            LittlesLawResult with all three values
        """
        provided = sum(1 for x in [wip, throughput, lead_time] if x is not None)
        
        if provided != 2:
            raise ValueError("Exactly two values must be provided")
        
        if wip is None:
            if throughput <= 0 or lead_time <= 0:
                raise ValueError("Throughput and lead time must be positive")
            wip = throughput * lead_time
            solved_for = 'WIP'
        elif throughput is None:
            if wip <= 0 or lead_time <= 0:
                raise ValueError("WIP and lead time must be positive")
            throughput = wip / lead_time
            solved_for = 'Throughput'
        else:
            if wip <= 0 or throughput <= 0:
                raise ValueError("WIP and throughput must be positive")
            lead_time = wip / throughput
            solved_for = 'Lead Time'
        
        return LittlesLawResult(
            wip=wip,
            throughput=throughput,
            lead_time=lead_time,
            solved_for=solved_for
        )
    
    @staticmethod
    def calculate_copq(
        internal_failure: float,
        external_failure: float,
        appraisal: float,
        prevention: float,
        revenue: Optional[float] = None
    ) -> COPQResult:
        """
        Calculate Cost of Poor Quality (COPQ).
        
        COPQ Categories:
        - Internal Failure: Scrap, rework, retesting
        - External Failure: Warranty, returns, complaints
        - Appraisal: Inspection, testing, audits
        - Prevention: Training, planning, improvement
        
        Args:
            internal_failure: Internal failure costs
            external_failure: External failure costs
            appraisal: Appraisal costs
            prevention: Prevention costs
            revenue: Optional revenue for percentage calculation
            
        Returns:
            COPQResult with cost breakdown
        """
        total_copq = internal_failure + external_failure + appraisal + prevention
        
        copq_percent = 0.0
        if revenue and revenue > 0:
            copq_percent = (total_copq / revenue) * 100
        
        return COPQResult(
            total_copq=total_copq,
            internal_failure=internal_failure,
            external_failure=external_failure,
            appraisal=appraisal,
            prevention=prevention,
            copq_percent_revenue=copq_percent
        )
    
    @staticmethod
    def sigma_lookup_table() -> List[Dict]:
        """
        Generate sigma level lookup table.
        
        Returns:
            List of dictionaries with sigma levels and metrics
        """
        table = []
        sigma_levels = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
        
        for sigma in sigma_levels:
            dpmo = LeanCalculators.sigma_to_dpmo(sigma)
            yield_pct = 100 - (dpmo / 10000)
            
            table.append({
                'sigma': sigma,
                'dpmo': round(dpmo, 1),
                'yield_percent': round(yield_pct, 4),
                'defect_rate': f"1 in {int(1_000_000 / dpmo) if dpmo > 0 else '∞'}"
            })
        
        return table
    
    @staticmethod
    def process_efficiency(
        value_added_time: float,
        total_lead_time: float
    ) -> Tuple[float, float]:
        """
        Calculate Process Cycle Efficiency (PCE).
        
        PCE = Value-Added Time / Total Lead Time
        
        Args:
            value_added_time: Time spent on value-adding activities
            total_lead_time: Total process lead time
            
        Returns:
            Tuple of (PCE as decimal, PCE as percent)
        """
        if total_lead_time <= 0:
            raise ValueError("Total lead time must be positive")
        
        pce = value_added_time / total_lead_time
        pce_percent = pce * 100
        
        return pce, pce_percent
    
    @staticmethod
    def oee_calculation(
        availability: float,
        performance: float,
        quality: float
    ) -> Tuple[float, float]:
        """
        Calculate Overall Equipment Effectiveness (OEE).
        
        OEE = Availability × Performance × Quality
        
        Args:
            availability: Equipment availability (0-1)
            performance: Performance efficiency (0-1)
            quality: Quality rate (0-1)
            
        Returns:
            Tuple of (OEE as decimal, OEE as percent)
        """
        for val, name in [(availability, 'Availability'), (performance, 'Performance'), (quality, 'Quality')]:
            if not 0 <= val <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        
        oee = availability * performance * quality
        oee_percent = oee * 100
        
        return oee, oee_percent
