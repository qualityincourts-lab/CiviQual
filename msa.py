"""
CiviQual Stats Measurement System Analysis (MSA)

Provides Gage R&R analysis:
- Crossed Gage R&R (ANOVA method)
- %Contribution, %Study Variation, %Tolerance
- Number of Distinct Categories
- Components of variation

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd


@dataclass
class VarianceComponent:
    """A variance component from Gage R&R."""
    source: str
    variance: float
    std_dev: float
    study_var: float  # 6 * std_dev
    percent_contribution: float  # % of total variance
    percent_study_var: float  # % of total study variation
    percent_tolerance: Optional[float]  # % of tolerance (if provided)
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'variance': self.variance,
            'std_dev': self.std_dev,
            'study_var': self.study_var,
            'percent_contribution': self.percent_contribution,
            'percent_study_var': self.percent_study_var,
            'percent_tolerance': self.percent_tolerance
        }


@dataclass
class GageRRResult:
    """Complete Gage R&R analysis result."""
    components: List[VarianceComponent]
    anova_table: pd.DataFrame
    n_operators: int
    n_parts: int
    n_replicates: int
    total_observations: int
    gage_rr_variance: float
    gage_rr_std_dev: float
    gage_rr_percent_contribution: float
    gage_rr_percent_study_var: float
    gage_rr_percent_tolerance: Optional[float]
    repeatability_variance: float
    reproducibility_variance: float
    part_to_part_variance: float
    ndc: int  # Number of Distinct Categories
    tolerance: Optional[float]
    assessment: str
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'components': [c.to_dict() for c in self.components],
            'n_operators': self.n_operators,
            'n_parts': self.n_parts,
            'n_replicates': self.n_replicates,
            'gage_rr_variance': self.gage_rr_variance,
            'gage_rr_std_dev': self.gage_rr_std_dev,
            'gage_rr_percent_contribution': self.gage_rr_percent_contribution,
            'gage_rr_percent_study_var': self.gage_rr_percent_study_var,
            'gage_rr_percent_tolerance': self.gage_rr_percent_tolerance,
            'repeatability_variance': self.repeatability_variance,
            'reproducibility_variance': self.reproducibility_variance,
            'part_to_part_variance': self.part_to_part_variance,
            'ndc': self.ndc,
            'assessment': self.assessment,
            'interpretation': self.interpretation
        }


class MSA:
    """
    Provides Measurement System Analysis (Gage R&R).
    """
    
    @staticmethod
    def gage_rr_crossed(
        data: Union[np.ndarray, pd.DataFrame],
        operator_col: Optional[str] = None,
        part_col: Optional[str] = None,
        measurement_col: Optional[str] = None,
        tolerance: Optional[float] = None,
        alpha: float = 0.05
    ) -> GageRRResult:
        """
        Perform crossed Gage R&R analysis using ANOVA method.
        
        In a crossed design, each operator measures each part multiple times.
        
        Args:
            data: Data in one of these formats:
                  - DataFrame with operator, part, and measurement columns
                  - 3D array [operators x parts x replicates]
            operator_col: Column name for operators (if DataFrame)
            part_col: Column name for parts (if DataFrame)
            measurement_col: Column name for measurements (if DataFrame)
            tolerance: Specification tolerance (USL - LSL) for %Tolerance
            alpha: Significance level for ANOVA
            
        Returns:
            GageRRResult with complete analysis
        """
        # Convert data to 3D array [operators, parts, replicates]
        if isinstance(data, pd.DataFrame):
            if operator_col is None or part_col is None or measurement_col is None:
                raise ValueError("Column names required for DataFrame input")
            
            # Pivot to get structured data
            operators = sorted(data[operator_col].unique())
            parts = sorted(data[part_col].unique())
            
            n_operators = len(operators)
            n_parts = len(parts)
            
            # Determine number of replicates
            counts = data.groupby([operator_col, part_col]).size()
            n_replicates = counts.min()
            
            # Create 3D array
            arr = np.zeros((n_operators, n_parts, n_replicates))
            for i, op in enumerate(operators):
                for j, pt in enumerate(parts):
                    mask = (data[operator_col] == op) & (data[part_col] == pt)
                    values = data.loc[mask, measurement_col].values[:n_replicates]
                    arr[i, j, :len(values)] = values
        else:
            arr = np.array(data)
            if arr.ndim != 3:
                raise ValueError("Array must be 3D [operators x parts x replicates]")
            n_operators, n_parts, n_replicates = arr.shape
        
        total_n = n_operators * n_parts * n_replicates
        
        # Grand mean
        grand_mean = np.mean(arr)
        
        # Calculate means
        operator_means = np.mean(arr, axis=(1, 2))
        part_means = np.mean(arr, axis=(0, 2))
        cell_means = np.mean(arr, axis=2)  # Operator x Part
        
        # Sum of Squares
        # SS Total
        ss_total = np.sum((arr - grand_mean)**2)
        
        # SS Operator
        ss_operator = n_parts * n_replicates * np.sum((operator_means - grand_mean)**2)
        
        # SS Part
        ss_part = n_operators * n_replicates * np.sum((part_means - grand_mean)**2)
        
        # SS Operator*Part (Interaction)
        # First calculate expected from additive model
        expected_cell = (operator_means[:, np.newaxis] + part_means[np.newaxis, :] - grand_mean)
        ss_interaction = n_replicates * np.sum((cell_means - expected_cell)**2)
        
        # SS Repeatability (within cells)
        ss_repeat = np.sum((arr - cell_means[:, :, np.newaxis])**2)
        
        # Degrees of freedom
        df_operator = n_operators - 1
        df_part = n_parts - 1
        df_interaction = df_operator * df_part
        df_repeat = n_operators * n_parts * (n_replicates - 1)
        df_total = total_n - 1
        
        # Mean Squares
        ms_operator = ss_operator / df_operator if df_operator > 0 else 0
        ms_part = ss_part / df_part if df_part > 0 else 0
        ms_interaction = ss_interaction / df_interaction if df_interaction > 0 else 0
        ms_repeat = ss_repeat / df_repeat if df_repeat > 0 else 0
        
        # F-statistics and p-values
        f_operator = ms_operator / ms_interaction if ms_interaction > 0 else 0
        p_operator = 1 - stats.f.cdf(f_operator, df_operator, df_interaction)
        
        f_part = ms_part / ms_interaction if ms_interaction > 0 else 0
        p_part = 1 - stats.f.cdf(f_part, df_part, df_interaction)
        
        f_interaction = ms_interaction / ms_repeat if ms_repeat > 0 else 0
        p_interaction = 1 - stats.f.cdf(f_interaction, df_interaction, df_repeat)
        
        # Variance Components (using expected mean squares)
        # σ²_repeat = MS_repeat
        var_repeat = ms_repeat
        
        # σ²_interaction = (MS_interaction - MS_repeat) / n_replicates
        var_interaction = max(0, (ms_interaction - ms_repeat) / n_replicates)
        
        # σ²_operator = (MS_operator - MS_interaction) / (n_parts * n_replicates)
        var_operator = max(0, (ms_operator - ms_interaction) / (n_parts * n_replicates))
        
        # σ²_part = (MS_part - MS_interaction) / (n_operators * n_replicates)
        var_part = max(0, (ms_part - ms_interaction) / (n_operators * n_replicates))
        
        # Combined variance components
        var_reproducibility = var_operator + var_interaction
        var_gage_rr = var_repeat + var_reproducibility
        var_total = var_gage_rr + var_part
        
        # Standard deviations
        std_repeat = np.sqrt(var_repeat)
        std_operator = np.sqrt(var_operator)
        std_interaction = np.sqrt(var_interaction)
        std_reproducibility = np.sqrt(var_reproducibility)
        std_gage_rr = np.sqrt(var_gage_rr)
        std_part = np.sqrt(var_part)
        std_total = np.sqrt(var_total)
        
        # Study Variation (6σ)
        sv_repeat = 6 * std_repeat
        sv_operator = 6 * std_operator
        sv_interaction = 6 * std_interaction
        sv_reproducibility = 6 * std_reproducibility
        sv_gage_rr = 6 * std_gage_rr
        sv_part = 6 * std_part
        sv_total = 6 * std_total
        
        # Percent Contribution (% of total variance)
        pct_contrib_repeat = (var_repeat / var_total * 100) if var_total > 0 else 0
        pct_contrib_operator = (var_operator / var_total * 100) if var_total > 0 else 0
        pct_contrib_interaction = (var_interaction / var_total * 100) if var_total > 0 else 0
        pct_contrib_reproducibility = (var_reproducibility / var_total * 100) if var_total > 0 else 0
        pct_contrib_gage_rr = (var_gage_rr / var_total * 100) if var_total > 0 else 0
        pct_contrib_part = (var_part / var_total * 100) if var_total > 0 else 0
        
        # Percent Study Variation (% of total study variation)
        pct_sv_repeat = (sv_repeat / sv_total * 100) if sv_total > 0 else 0
        pct_sv_operator = (sv_operator / sv_total * 100) if sv_total > 0 else 0
        pct_sv_interaction = (sv_interaction / sv_total * 100) if sv_total > 0 else 0
        pct_sv_reproducibility = (sv_reproducibility / sv_total * 100) if sv_total > 0 else 0
        pct_sv_gage_rr = (sv_gage_rr / sv_total * 100) if sv_total > 0 else 0
        pct_sv_part = (sv_part / sv_total * 100) if sv_total > 0 else 0
        
        # Percent Tolerance (if provided)
        pct_tol_repeat = (sv_repeat / tolerance * 100) if tolerance else None
        pct_tol_reproducibility = (sv_reproducibility / tolerance * 100) if tolerance else None
        pct_tol_gage_rr = (sv_gage_rr / tolerance * 100) if tolerance else None
        pct_tol_part = (sv_part / tolerance * 100) if tolerance else None
        
        # Number of Distinct Categories
        # ndc = sqrt(2) * (σ_part / σ_gage_rr)
        if std_gage_rr > 0:
            ndc = int(np.floor(np.sqrt(2) * (std_part / std_gage_rr)))
        else:
            ndc = 0
        ndc = max(1, ndc)
        
        # Create variance components list
        components = [
            VarianceComponent('Total Gage R&R', var_gage_rr, std_gage_rr, sv_gage_rr,
                            pct_contrib_gage_rr, pct_sv_gage_rr, pct_tol_gage_rr),
            VarianceComponent('  Repeatability', var_repeat, std_repeat, sv_repeat,
                            pct_contrib_repeat, pct_sv_repeat, pct_tol_repeat),
            VarianceComponent('  Reproducibility', var_reproducibility, std_reproducibility, sv_reproducibility,
                            pct_contrib_reproducibility, pct_sv_reproducibility, pct_tol_reproducibility),
            VarianceComponent('    Operator', var_operator, std_operator, sv_operator,
                            pct_contrib_operator, pct_sv_operator, None),
            VarianceComponent('    Operator*Part', var_interaction, std_interaction, sv_interaction,
                            pct_contrib_interaction, pct_sv_interaction, None),
            VarianceComponent('Part-to-Part', var_part, std_part, sv_part,
                            pct_contrib_part, pct_sv_part, pct_tol_part),
            VarianceComponent('Total Variation', var_total, std_total, sv_total,
                            100.0, 100.0, None)
        ]
        
        # Create ANOVA table
        anova_data = [
            {'Source': 'Operator', 'DF': df_operator, 'SS': ss_operator, 'MS': ms_operator, 'F': f_operator, 'P': p_operator},
            {'Source': 'Part', 'DF': df_part, 'SS': ss_part, 'MS': ms_part, 'F': f_part, 'P': p_part},
            {'Source': 'Operator*Part', 'DF': df_interaction, 'SS': ss_interaction, 'MS': ms_interaction, 'F': f_interaction, 'P': p_interaction},
            {'Source': 'Repeatability', 'DF': df_repeat, 'SS': ss_repeat, 'MS': ms_repeat, 'F': np.nan, 'P': np.nan},
            {'Source': 'Total', 'DF': df_total, 'SS': ss_total, 'MS': np.nan, 'F': np.nan, 'P': np.nan}
        ]
        anova_table = pd.DataFrame(anova_data)
        
        # Assessment based on %Study Variation
        if pct_sv_gage_rr < 10:
            assessment = "ACCEPTABLE"
            assess_detail = "Measurement system is acceptable (<10% of study variation)"
        elif pct_sv_gage_rr < 30:
            assessment = "MARGINAL"
            assess_detail = "Measurement system is marginal (10-30% of study variation). May be acceptable based on application."
        else:
            assessment = "UNACCEPTABLE"
            assess_detail = "Measurement system is unacceptable (>30% of study variation). Improvement required."
        
        # Interpretation
        interpretation = (
            f"Gage R&R Study: {n_operators} operators, {n_parts} parts, {n_replicates} replicates.\n\n"
            f"Assessment: {assessment}\n"
            f"%Study Variation (Gage R&R): {pct_sv_gage_rr:.2f}%\n"
            f"  - Repeatability: {pct_sv_repeat:.2f}%\n"
            f"  - Reproducibility: {pct_sv_reproducibility:.2f}%\n"
            f"Part-to-Part: {pct_sv_part:.2f}%\n\n"
            f"Number of Distinct Categories (ndc): {ndc}\n"
        )
        
        if ndc < 5:
            interpretation += "  WARNING: ndc < 5 indicates inadequate discrimination.\n"
        
        interpretation += f"\n{assess_detail}"
        
        if tolerance:
            interpretation += f"\n\n%Tolerance (Gage R&R): {pct_tol_gage_rr:.2f}%"
        
        return GageRRResult(
            components=components,
            anova_table=anova_table,
            n_operators=n_operators,
            n_parts=n_parts,
            n_replicates=n_replicates,
            total_observations=total_n,
            gage_rr_variance=var_gage_rr,
            gage_rr_std_dev=std_gage_rr,
            gage_rr_percent_contribution=pct_contrib_gage_rr,
            gage_rr_percent_study_var=pct_sv_gage_rr,
            gage_rr_percent_tolerance=pct_tol_gage_rr,
            repeatability_variance=var_repeat,
            reproducibility_variance=var_reproducibility,
            part_to_part_variance=var_part,
            ndc=ndc,
            tolerance=tolerance,
            assessment=assessment,
            interpretation=interpretation
        )
    
    @staticmethod
    def get_bar_chart_data(result: GageRRResult) -> Dict:
        """
        Get data for Gage R&R bar chart (components of variation).
        
        Args:
            result: GageRRResult from gage_rr_crossed()
            
        Returns:
            Dictionary with plot data
        """
        sources = ['Gage R&R', 'Repeat', 'Reprod', 'Part-to-Part']
        
        pct_contribution = [
            result.gage_rr_percent_contribution,
            result.components[1].percent_contribution,  # Repeatability
            result.components[2].percent_contribution,  # Reproducibility
            result.components[5].percent_contribution   # Part-to-Part
        ]
        
        pct_study_var = [
            result.gage_rr_percent_study_var,
            result.components[1].percent_study_var,
            result.components[2].percent_study_var,
            result.components[5].percent_study_var
        ]
        
        data = {
            'sources': sources,
            'percent_contribution': pct_contribution,
            'percent_study_var': pct_study_var
        }
        
        if result.tolerance:
            data['percent_tolerance'] = [
                result.gage_rr_percent_tolerance,
                result.components[1].percent_tolerance,
                result.components[2].percent_tolerance,
                result.components[5].percent_tolerance
            ]
        
        return data
    
    @staticmethod
    def generate_gage_rr_report(result: GageRRResult) -> str:
        """
        Generate a formatted Gage R&R report.
        
        Args:
            result: GageRRResult from gage_rr_crossed()
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("GAGE R&R STUDY REPORT")
        report.append("=" * 60)
        report.append("")
        report.append(f"Operators: {result.n_operators}")
        report.append(f"Parts: {result.n_parts}")
        report.append(f"Replicates: {result.n_replicates}")
        report.append(f"Total Observations: {result.total_observations}")
        report.append("")
        
        report.append("-" * 60)
        report.append("ANOVA TABLE")
        report.append("-" * 60)
        report.append(result.anova_table.to_string(index=False))
        report.append("")
        
        report.append("-" * 60)
        report.append("VARIANCE COMPONENTS")
        report.append("-" * 60)
        
        header = f"{'Source':<20} {'VarComp':>10} {'StdDev':>10} {'%Contrib':>10} {'%StudyVar':>10}"
        if result.tolerance:
            header += f" {'%Tolerance':>10}"
        report.append(header)
        report.append("-" * len(header))
        
        for comp in result.components:
            line = f"{comp.source:<20} {comp.variance:>10.4f} {comp.std_dev:>10.4f} {comp.percent_contribution:>10.2f} {comp.percent_study_var:>10.2f}"
            if result.tolerance and comp.percent_tolerance is not None:
                line += f" {comp.percent_tolerance:>10.2f}"
            report.append(line)
        
        report.append("")
        report.append("-" * 60)
        report.append("ASSESSMENT")
        report.append("-" * 60)
        report.append(f"Status: {result.assessment}")
        report.append(f"Number of Distinct Categories: {result.ndc}")
        report.append("")
        report.append(result.interpretation)
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
