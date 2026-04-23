"""
CiviQual Stats Data Tools

Provides data quality and analysis tools:
- Outlier Detection (Grubbs Test, IQR Method, Z-Score)
- Missing Data Analysis and Reporting

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd


@dataclass
class OutlierResult:
    """Result of outlier detection."""
    method: str
    outlier_indices: List[int]
    outlier_values: List[float]
    n_outliers: int
    n_total: int
    percent_outliers: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    statistics: Dict
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'method': self.method,
            'outlier_indices': self.outlier_indices,
            'outlier_values': self.outlier_values,
            'n_outliers': self.n_outliers,
            'n_total': self.n_total,
            'percent_outliers': self.percent_outliers,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'statistics': self.statistics,
            'interpretation': self.interpretation
        }


@dataclass
class GrubbsResult:
    """Result of Grubbs test for a single outlier."""
    test_statistic: float
    critical_value: float
    p_value: float
    is_outlier: bool
    outlier_index: Optional[int]
    outlier_value: Optional[float]
    outlier_direction: str  # 'high', 'low', or 'none'
    alpha: float
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'test_statistic': self.test_statistic,
            'critical_value': self.critical_value,
            'p_value': self.p_value,
            'is_outlier': self.is_outlier,
            'outlier_index': self.outlier_index,
            'outlier_value': self.outlier_value,
            'outlier_direction': self.outlier_direction,
            'alpha': self.alpha,
            'interpretation': self.interpretation
        }


@dataclass
class MissingDataReport:
    """Report on missing data in a dataset."""
    total_cells: int
    missing_cells: int
    complete_cells: int
    percent_missing: float
    columns_with_missing: Dict[str, Dict]  # column_name -> {count, percent, pattern}
    rows_with_missing: int
    complete_rows: int
    percent_complete_rows: float
    missing_pattern: str  # 'MCAR', 'MAR', 'MNAR', or 'Unknown'
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'total_cells': self.total_cells,
            'missing_cells': self.missing_cells,
            'complete_cells': self.complete_cells,
            'percent_missing': self.percent_missing,
            'columns_with_missing': self.columns_with_missing,
            'rows_with_missing': self.rows_with_missing,
            'complete_rows': self.complete_rows,
            'percent_complete_rows': self.percent_complete_rows,
            'missing_pattern': self.missing_pattern,
            'recommendations': self.recommendations
        }


class OutlierDetection:
    """
    Provides multiple methods for outlier detection.
    """
    
    @staticmethod
    def grubbs_test(
        data: Union[List[float], np.ndarray],
        alpha: float = 0.05,
        test_type: str = 'two-sided'
    ) -> GrubbsResult:
        """
        Perform Grubbs test for a single outlier.
        
        Tests whether the value furthest from the mean is an outlier.
        
        Args:
            data: Data array (should be approximately normal)
            alpha: Significance level
            test_type: 'two-sided', 'min', or 'max'
            
        Returns:
            GrubbsResult with test results
        """
        data = np.array(data)
        data = data[~np.isnan(data)]
        n = len(data)
        
        if n < 3:
            raise ValueError("At least 3 data points required for Grubbs test")
        
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        if std == 0:
            return GrubbsResult(
                test_statistic=0,
                critical_value=0,
                p_value=1.0,
                is_outlier=False,
                outlier_index=None,
                outlier_value=None,
                outlier_direction='none',
                alpha=alpha,
                interpretation="Cannot perform test: zero variance in data."
            )
        
        # Calculate test statistic
        if test_type == 'max':
            # Test only maximum
            idx = np.argmax(data)
            G = (data[idx] - mean) / std
            direction = 'high'
        elif test_type == 'min':
            # Test only minimum
            idx = np.argmin(data)
            G = (mean - data[idx]) / std
            direction = 'low'
        else:
            # Two-sided: test value furthest from mean
            deviations = np.abs(data - mean)
            idx = np.argmax(deviations)
            G = deviations[idx] / std
            direction = 'high' if data[idx] > mean else 'low'
        
        # Critical value (using t-distribution approximation)
        if test_type == 'two-sided':
            t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
        else:
            t_crit = stats.t.ppf(1 - alpha / n, n - 2)
        
        G_crit = ((n - 1) / np.sqrt(n)) * np.sqrt(t_crit**2 / (n - 2 + t_crit**2))
        
        # p-value (approximate)
        # Using the relationship between G and t
        t_stat = G * np.sqrt(n - 2) / np.sqrt(n - 1 - G**2) if G**2 < n - 1 else np.inf
        if test_type == 'two-sided':
            p_value = 2 * n * (1 - stats.t.cdf(abs(t_stat), n - 2))
        else:
            p_value = n * (1 - stats.t.cdf(abs(t_stat), n - 2))
        p_value = min(1.0, max(0.0, p_value))
        
        is_outlier = G > G_crit
        
        if is_outlier:
            interpretation = (
                f"Grubbs test detects an outlier (G = {G:.4f} > {G_crit:.4f}). "
                f"Value {data[idx]:.4f} at index {idx} is a {direction} outlier (p = {p_value:.4f})."
            )
        else:
            interpretation = (
                f"No outlier detected (G = {G:.4f} ≤ {G_crit:.4f}, p = {p_value:.4f}). "
                f"Most extreme value: {data[idx]:.4f} at index {idx}."
            )
        
        return GrubbsResult(
            test_statistic=G,
            critical_value=G_crit,
            p_value=p_value,
            is_outlier=is_outlier,
            outlier_index=int(idx) if is_outlier else None,
            outlier_value=float(data[idx]) if is_outlier else None,
            outlier_direction=direction if is_outlier else 'none',
            alpha=alpha,
            interpretation=interpretation
        )
    
    @staticmethod
    def grubbs_iterative(
        data: Union[List[float], np.ndarray],
        alpha: float = 0.05,
        max_iterations: int = 10
    ) -> List[GrubbsResult]:
        """
        Perform iterative Grubbs test to detect multiple outliers.
        
        Removes outliers one at a time and retests until no more are found.
        
        Args:
            data: Data array
            alpha: Significance level
            max_iterations: Maximum outliers to detect
            
        Returns:
            List of GrubbsResult for each detected outlier
        """
        data = np.array(data)
        original_indices = np.arange(len(data))
        mask = ~np.isnan(data)
        current_data = data[mask]
        current_indices = original_indices[mask]
        
        results = []
        
        for _ in range(max_iterations):
            if len(current_data) < 3:
                break
            
            result = OutlierDetection.grubbs_test(current_data, alpha)
            
            if not result.is_outlier:
                break
            
            # Map back to original index
            local_idx = result.outlier_index
            original_idx = current_indices[local_idx]
            result.outlier_index = int(original_idx)
            
            results.append(result)
            
            # Remove outlier for next iteration
            current_data = np.delete(current_data, local_idx)
            current_indices = np.delete(current_indices, local_idx)
        
        return results
    
    @staticmethod
    def iqr_method(
        data: Union[List[float], np.ndarray],
        k: float = 1.5
    ) -> OutlierResult:
        """
        Detect outliers using the IQR (Interquartile Range) method.
        
        Outliers are values below Q1 - k*IQR or above Q3 + k*IQR.
        
        Args:
            data: Data array
            k: IQR multiplier (default 1.5 for mild outliers, 3.0 for extreme)
            
        Returns:
            OutlierResult with detected outliers
        """
        data = np.array(data)
        original_indices = np.arange(len(data))
        mask = ~np.isnan(data)
        clean_data = data[mask]
        clean_indices = original_indices[mask]
        
        q1 = np.percentile(clean_data, 25)
        q3 = np.percentile(clean_data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr
        
        # Find outliers
        outlier_mask = (clean_data < lower_bound) | (clean_data > upper_bound)
        outlier_indices = clean_indices[outlier_mask].tolist()
        outlier_values = clean_data[outlier_mask].tolist()
        
        n_outliers = len(outlier_indices)
        n_total = len(clean_data)
        percent_outliers = (n_outliers / n_total * 100) if n_total > 0 else 0
        
        # Statistics
        statistics = {
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'median': np.median(clean_data),
            'k': k
        }
        
        if n_outliers == 0:
            interpretation = f"No outliers detected using IQR method (k={k}). All values within [{lower_bound:.4f}, {upper_bound:.4f}]."
        else:
            interpretation = (
                f"IQR method (k={k}) detected {n_outliers} outlier(s) ({percent_outliers:.1f}% of data). "
                f"Bounds: [{lower_bound:.4f}, {upper_bound:.4f}]."
            )
        
        return OutlierResult(
            method=f'IQR (k={k})',
            outlier_indices=outlier_indices,
            outlier_values=outlier_values,
            n_outliers=n_outliers,
            n_total=n_total,
            percent_outliers=percent_outliers,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            statistics=statistics,
            interpretation=interpretation
        )
    
    @staticmethod
    def zscore_method(
        data: Union[List[float], np.ndarray],
        threshold: float = 3.0,
        modified: bool = False
    ) -> OutlierResult:
        """
        Detect outliers using Z-score method.
        
        Args:
            data: Data array
            threshold: Z-score threshold (typically 2.5-3.0)
            modified: If True, use Modified Z-score (more robust)
            
        Returns:
            OutlierResult with detected outliers
        """
        data = np.array(data)
        original_indices = np.arange(len(data))
        mask = ~np.isnan(data)
        clean_data = data[mask]
        clean_indices = original_indices[mask]
        
        if modified:
            # Modified Z-score using MAD (Median Absolute Deviation)
            median = np.median(clean_data)
            mad = np.median(np.abs(clean_data - median))
            
            # MAD to std dev conversion factor
            mad_std = mad * 1.4826
            
            if mad_std == 0:
                z_scores = np.zeros_like(clean_data)
            else:
                z_scores = 0.6745 * (clean_data - median) / mad_std
            
            method_name = f'Modified Z-score (threshold={threshold})'
            center = median
        else:
            # Standard Z-score
            mean = np.mean(clean_data)
            std = np.std(clean_data, ddof=1)
            
            if std == 0:
                z_scores = np.zeros_like(clean_data)
            else:
                z_scores = (clean_data - mean) / std
            
            method_name = f'Z-score (threshold={threshold})'
            center = mean
        
        # Find outliers
        outlier_mask = np.abs(z_scores) > threshold
        outlier_indices = clean_indices[outlier_mask].tolist()
        outlier_values = clean_data[outlier_mask].tolist()
        
        n_outliers = len(outlier_indices)
        n_total = len(clean_data)
        percent_outliers = (n_outliers / n_total * 100) if n_total > 0 else 0
        
        # Bounds
        if modified:
            mad_std = np.median(np.abs(clean_data - np.median(clean_data))) * 1.4826
            lower_bound = np.median(clean_data) - threshold * mad_std / 0.6745
            upper_bound = np.median(clean_data) + threshold * mad_std / 0.6745
        else:
            std = np.std(clean_data, ddof=1)
            lower_bound = np.mean(clean_data) - threshold * std
            upper_bound = np.mean(clean_data) + threshold * std
        
        statistics = {
            'center': center,
            'threshold': threshold,
            'max_zscore': float(np.max(np.abs(z_scores))),
            'modified': modified
        }
        
        if n_outliers == 0:
            interpretation = f"No outliers detected using {method_name}."
        else:
            interpretation = f"{method_name} detected {n_outliers} outlier(s) ({percent_outliers:.1f}% of data)."
        
        return OutlierResult(
            method=method_name,
            outlier_indices=outlier_indices,
            outlier_values=outlier_values,
            n_outliers=n_outliers,
            n_total=n_total,
            percent_outliers=percent_outliers,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            statistics=statistics,
            interpretation=interpretation
        )
    
    @staticmethod
    def compare_methods(
        data: Union[List[float], np.ndarray]
    ) -> Dict[str, OutlierResult]:
        """
        Compare multiple outlier detection methods on the same data.
        
        Args:
            data: Data array
            
        Returns:
            Dictionary of method name -> OutlierResult
        """
        results = {}
        
        # IQR (mild)
        results['IQR (k=1.5)'] = OutlierDetection.iqr_method(data, k=1.5)
        
        # IQR (extreme)
        results['IQR (k=3.0)'] = OutlierDetection.iqr_method(data, k=3.0)
        
        # Z-score
        results['Z-score'] = OutlierDetection.zscore_method(data, threshold=3.0)
        
        # Modified Z-score
        results['Modified Z-score'] = OutlierDetection.zscore_method(data, threshold=3.5, modified=True)
        
        # Grubbs (if enough data)
        data_clean = np.array(data)
        data_clean = data_clean[~np.isnan(data_clean)]
        if len(data_clean) >= 3:
            grubbs_results = OutlierDetection.grubbs_iterative(data)
            results['Grubbs'] = OutlierResult(
                method='Grubbs (iterative)',
                outlier_indices=[r.outlier_index for r in grubbs_results],
                outlier_values=[r.outlier_value for r in grubbs_results],
                n_outliers=len(grubbs_results),
                n_total=len(data_clean),
                percent_outliers=len(grubbs_results) / len(data_clean) * 100,
                lower_bound=None,
                upper_bound=None,
                statistics={'n_iterations': len(grubbs_results)},
                interpretation=f"Grubbs test detected {len(grubbs_results)} outlier(s)."
            )
        
        return results


class MissingDataAnalysis:
    """
    Provides analysis and reporting for missing data.
    """
    
    @staticmethod
    def analyze(
        data: Union[pd.DataFrame, np.ndarray],
        column_names: Optional[List[str]] = None
    ) -> MissingDataReport:
        """
        Analyze missing data in a dataset.
        
        Args:
            data: DataFrame or 2D array
            column_names: Column names (if array)
            
        Returns:
            MissingDataReport with analysis
        """
        if isinstance(data, np.ndarray):
            if column_names is None:
                column_names = [f'Column_{i}' for i in range(data.shape[1])]
            df = pd.DataFrame(data, columns=column_names)
        else:
            df = data.copy()
        
        n_rows, n_cols = df.shape
        total_cells = n_rows * n_cols
        
        # Count missing by column
        columns_with_missing = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                columns_with_missing[col] = {
                    'count': int(missing_count),
                    'percent': float(missing_count / n_rows * 100),
                    'dtype': str(df[col].dtype)
                }
        
        # Overall statistics
        missing_cells = df.isna().sum().sum()
        complete_cells = total_cells - missing_cells
        percent_missing = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Rows with any missing
        rows_with_missing = df.isna().any(axis=1).sum()
        complete_rows = n_rows - rows_with_missing
        percent_complete_rows = (complete_rows / n_rows * 100) if n_rows > 0 else 0
        
        # Try to determine missing pattern
        pattern = MissingDataAnalysis._assess_missing_pattern(df)
        
        # Generate recommendations
        recommendations = MissingDataAnalysis._generate_recommendations(
            percent_missing, columns_with_missing, pattern
        )
        
        return MissingDataReport(
            total_cells=total_cells,
            missing_cells=missing_cells,
            complete_cells=complete_cells,
            percent_missing=percent_missing,
            columns_with_missing=columns_with_missing,
            rows_with_missing=rows_with_missing,
            complete_rows=complete_rows,
            percent_complete_rows=percent_complete_rows,
            missing_pattern=pattern,
            recommendations=recommendations
        )
    
    @staticmethod
    def _assess_missing_pattern(df: pd.DataFrame) -> str:
        """
        Attempt to assess the missing data mechanism.
        
        - MCAR: Missing Completely at Random
        - MAR: Missing at Random (depends on observed data)
        - MNAR: Missing Not at Random (depends on missing values)
        
        Note: This is a heuristic assessment, not a formal test.
        """
        missing_cols = df.columns[df.isna().any()].tolist()
        
        if not missing_cols:
            return "No missing data"
        
        # Simple heuristic: check if missingness correlates with other variables
        # This is a rough approximation
        
        try:
            # Check if missingness pattern is random
            missing_indicators = df[missing_cols].isna().astype(int)
            
            # Check correlation between missingness and other variables
            complete_cols = [c for c in df.columns if c not in missing_cols and df[c].dtype in ['int64', 'float64']]
            
            if complete_cols:
                correlations = []
                for miss_col in missing_cols:
                    for comp_col in complete_cols:
                        corr = df[comp_col].fillna(0).corr(df[miss_col].isna().astype(int))
                        if not np.isnan(corr):
                            correlations.append(abs(corr))
                
                if correlations:
                    max_corr = max(correlations)
                    if max_corr > 0.3:
                        return "Possibly MAR (Missing at Random)"
                    else:
                        return "Possibly MCAR (Missing Completely at Random)"
        except:
            pass
        
        return "Unknown (further analysis recommended)"
    
    @staticmethod
    def _generate_recommendations(
        percent_missing: float,
        columns_with_missing: Dict,
        pattern: str
    ) -> List[str]:
        """Generate recommendations based on missing data analysis."""
        recommendations = []
        
        # Overall percent missing
        if percent_missing == 0:
            recommendations.append("No missing data - dataset is complete.")
        elif percent_missing < 5:
            recommendations.append("Low percentage of missing data (<5%). Consider listwise deletion or simple imputation.")
        elif percent_missing < 20:
            recommendations.append("Moderate missing data (5-20%). Multiple imputation recommended.")
        else:
            recommendations.append("High percentage of missing data (>20%). Investigate data collection process.")
        
        # Column-specific recommendations
        high_missing_cols = [col for col, info in columns_with_missing.items() if info['percent'] > 50]
        if high_missing_cols:
            recommendations.append(f"Columns with >50% missing: {', '.join(high_missing_cols)}. Consider dropping these columns.")
        
        # Pattern-based recommendations
        if 'MCAR' in pattern:
            recommendations.append("If MCAR is confirmed, any imputation method is appropriate.")
        elif 'MAR' in pattern:
            recommendations.append("For MAR data, use multiple imputation or maximum likelihood methods.")
        
        return recommendations
    
    @staticmethod
    def generate_text_report(report: MissingDataReport) -> str:
        """Generate a text report of missing data analysis."""
        lines = []
        lines.append("=" * 60)
        lines.append("MISSING DATA ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("OVERVIEW")
        lines.append("-" * 40)
        lines.append(f"Total Cells: {report.total_cells:,}")
        lines.append(f"Missing Cells: {report.missing_cells:,} ({report.percent_missing:.2f}%)")
        lines.append(f"Complete Cells: {report.complete_cells:,}")
        lines.append("")
        lines.append(f"Rows with Missing Data: {report.rows_with_missing:,}")
        lines.append(f"Complete Rows: {report.complete_rows:,} ({report.percent_complete_rows:.1f}%)")
        lines.append("")
        lines.append(f"Missing Pattern Assessment: {report.missing_pattern}")
        lines.append("")
        
        if report.columns_with_missing:
            lines.append("COLUMNS WITH MISSING DATA")
            lines.append("-" * 40)
            for col, info in sorted(report.columns_with_missing.items(), key=lambda x: -x[1]['percent']):
                lines.append(f"  {col}: {info['count']:,} missing ({info['percent']:.1f}%)")
            lines.append("")
        
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for rec in report.recommendations:
            lines.append(f"  • {rec}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def visualize_missing_pattern(df: pd.DataFrame) -> Dict:
        """
        Get data for visualizing missing data pattern.
        
        Returns data suitable for a heatmap or matrix visualization.
        """
        missing_matrix = df.isna().astype(int)
        
        return {
            'columns': list(df.columns),
            'n_rows': len(df),
            'missing_by_column': df.isna().sum().to_dict(),
            'missing_by_row': df.isna().sum(axis=1).tolist(),
            'matrix': missing_matrix.values.tolist()  # For heatmap
        }
