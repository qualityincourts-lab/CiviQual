"""
CiviQual Stats Design of Experiments (DOE)

Provides factorial design and analysis:
- 2-3 factor full factorial design generation
- Main effects calculation and plotting
- Interaction effects calculation and plotting
- Pareto of effects
- ANOVA table for factorial designs

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, field
import numpy as np
from scipy import stats
import itertools
import pandas as pd


@dataclass
class Factor:
    """Represents a factor in a DOE."""
    name: str
    low: float
    high: float
    low_label: str = '-1'
    high_label: str = '+1'
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'low': self.low,
            'high': self.high,
            'low_label': self.low_label,
            'high_label': self.high_label
        }


@dataclass
class DesignMatrix:
    """Full factorial design matrix."""
    factors: List[Factor]
    coded_matrix: np.ndarray  # -1/+1 coded
    natural_matrix: np.ndarray  # Natural units
    run_order: List[int]
    n_runs: int
    n_factors: int
    n_replicates: int
    
    def to_dataframe(self, coded: bool = True) -> pd.DataFrame:
        """Convert to DataFrame."""
        matrix = self.coded_matrix if coded else self.natural_matrix
        columns = [f.name for f in self.factors]
        df = pd.DataFrame(matrix, columns=columns)
        df.insert(0, 'Run', self.run_order)
        return df


@dataclass
class EffectResult:
    """Result of effect calculation."""
    factor: str
    effect: float
    coefficient: float
    t_value: float
    p_value: float
    significant: bool
    percent_contribution: float
    
    def to_dict(self) -> Dict:
        return {
            'factor': self.factor,
            'effect': self.effect,
            'coefficient': self.coefficient,
            't_value': self.t_value,
            'p_value': self.p_value,
            'significant': self.significant,
            'percent_contribution': self.percent_contribution
        }


@dataclass
class DOEAnalysisResult:
    """Complete DOE analysis result."""
    factors: List[str]
    response_name: str
    main_effects: List[EffectResult]
    interactions: List[EffectResult]
    model_r_squared: float
    model_adj_r_squared: float
    residual_std_error: float
    anova_table: pd.DataFrame
    predicted_values: np.ndarray
    residuals: np.ndarray
    interpretation: str = ''
    
    def get_significant_effects(self, alpha: float = 0.05) -> List[str]:
        """Get list of significant effect names."""
        significant = []
        for effect in self.main_effects + self.interactions:
            if effect.p_value < alpha:
                significant.append(effect.factor)
        return significant


class DOE:
    """
    Provides Design of Experiments functionality.
    """
    
    @staticmethod
    def create_full_factorial(
        factors: List[Factor],
        n_replicates: int = 1,
        randomize: bool = True,
        seed: Optional[int] = None
    ) -> DesignMatrix:
        """
        Create a full factorial design matrix.
        
        Args:
            factors: List of Factor objects (2-4 factors supported)
            n_replicates: Number of replicates per run
            randomize: Whether to randomize run order
            seed: Random seed for reproducibility
            
        Returns:
            DesignMatrix with design information
        """
        n_factors = len(factors)
        
        if n_factors < 2 or n_factors > 4:
            raise ValueError("Full factorial supports 2-4 factors")
        
        if n_replicates < 1:
            raise ValueError("At least 1 replicate required")
        
        # Generate coded design matrix (-1, +1)
        levels = [-1, 1]
        combinations = list(itertools.product(levels, repeat=n_factors))
        coded_matrix = np.array(combinations)
        
        # Replicate
        if n_replicates > 1:
            coded_matrix = np.tile(coded_matrix, (n_replicates, 1))
        
        n_runs = len(coded_matrix)
        
        # Create natural values matrix
        natural_matrix = np.zeros_like(coded_matrix, dtype=float)
        for i, factor in enumerate(factors):
            natural_matrix[:, i] = np.where(
                coded_matrix[:, i] == -1,
                factor.low,
                factor.high
            )
        
        # Create run order
        run_order = list(range(1, n_runs + 1))
        
        if randomize:
            if seed is not None:
                np.random.seed(seed)
            np.random.shuffle(run_order)
        
        return DesignMatrix(
            factors=factors,
            coded_matrix=coded_matrix,
            natural_matrix=natural_matrix,
            run_order=run_order,
            n_runs=n_runs,
            n_factors=n_factors,
            n_replicates=n_replicates
        )
    
    @staticmethod
    def calculate_effects(
        design: DesignMatrix,
        response: Union[List[float], np.ndarray],
        alpha: float = 0.05
    ) -> Tuple[List[EffectResult], List[EffectResult]]:
        """
        Calculate main effects and interactions.
        
        Args:
            design: Design matrix
            response: Response values for each run
            alpha: Significance level
            
        Returns:
            Tuple of (main_effects, interactions)
        """
        response = np.array(response)
        
        if len(response) != design.n_runs:
            raise ValueError(f"Response length ({len(response)}) must match runs ({design.n_runs})")
        
        X = design.coded_matrix
        y = response
        n = len(y)
        
        factor_names = [f.name for f in design.factors]
        
        # Calculate main effects
        main_effects = []
        for i, name in enumerate(factor_names):
            # Effect = mean(high) - mean(low)
            high_idx = X[:, i] == 1
            low_idx = X[:, i] == -1
            effect = np.mean(y[high_idx]) - np.mean(y[low_idx])
            coefficient = effect / 2
            
            main_effects.append({
                'name': name,
                'effect': effect,
                'coefficient': coefficient
            })
        
        # Calculate two-way interactions
        interactions = []
        for i in range(len(factor_names)):
            for j in range(i + 1, len(factor_names)):
                name = f"{factor_names[i]}*{factor_names[j]}"
                interaction_col = X[:, i] * X[:, j]
                
                high_idx = interaction_col == 1
                low_idx = interaction_col == -1
                effect = np.mean(y[high_idx]) - np.mean(y[low_idx])
                coefficient = effect / 2
                
                interactions.append({
                    'name': name,
                    'effect': effect,
                    'coefficient': coefficient
                })
        
        # Calculate three-way interaction if 3+ factors
        if len(factor_names) >= 3:
            for combo in itertools.combinations(range(len(factor_names)), 3):
                i, j, k = combo
                name = f"{factor_names[i]}*{factor_names[j]}*{factor_names[k]}"
                interaction_col = X[:, i] * X[:, j] * X[:, k]
                
                high_idx = interaction_col == 1
                low_idx = interaction_col == -1
                effect = np.mean(y[high_idx]) - np.mean(y[low_idx])
                coefficient = effect / 2
                
                interactions.append({
                    'name': name,
                    'effect': effect,
                    'coefficient': coefficient
                })
        
        # Build regression model for significance testing
        # Include intercept, main effects, and interactions
        all_effects = main_effects + interactions
        n_effects = len(all_effects)
        
        # Create design matrix with intercept and all effects
        X_full = np.ones((n, 1))  # Intercept
        for i in range(len(factor_names)):
            X_full = np.column_stack([X_full, X[:, i]])
        
        # Add interaction columns
        for i in range(len(factor_names)):
            for j in range(i + 1, len(factor_names)):
                X_full = np.column_stack([X_full, X[:, i] * X[:, j]])
        
        if len(factor_names) >= 3:
            for combo in itertools.combinations(range(len(factor_names)), 3):
                i, j, k = combo
                X_full = np.column_stack([X_full, X[:, i] * X[:, j] * X[:, k]])
        
        # Fit regression
        try:
            beta = np.linalg.lstsq(X_full, y, rcond=None)[0]
            y_pred = X_full @ beta
            residuals = y - y_pred
            
            # Calculate statistics
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            
            df_res = n - len(beta)
            mse = ss_res / df_res if df_res > 0 else 0
            se = np.sqrt(mse)
            
            # Calculate standard errors for coefficients
            if df_res > 0:
                var_beta = mse * np.linalg.inv(X_full.T @ X_full).diagonal()
                se_beta = np.sqrt(var_beta)
            else:
                se_beta = np.ones(len(beta))
        except:
            # Fallback if matrix is singular
            se = np.std(y)
            se_beta = np.ones(n_effects + 1) * se
            df_res = max(1, n - n_effects - 1)
        
        # Calculate t-values and p-values
        total_ss_effects = 0
        effect_results_main = []
        effect_results_int = []
        
        for idx, eff in enumerate(all_effects):
            coef_idx = idx + 1  # Skip intercept
            
            t_value = eff['coefficient'] / se_beta[coef_idx] if se_beta[coef_idx] > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_value), df_res)) if df_res > 0 else 1.0
            significant = p_value < alpha
            
            # SS for this effect (for % contribution)
            ss_effect = (eff['effect']**2 * n) / 4
            total_ss_effects += ss_effect
            
            result = EffectResult(
                factor=eff['name'],
                effect=eff['effect'],
                coefficient=eff['coefficient'],
                t_value=t_value,
                p_value=p_value,
                significant=significant,
                percent_contribution=0  # Calculate after
            )
            
            if '*' in eff['name']:
                effect_results_int.append((result, ss_effect))
            else:
                effect_results_main.append((result, ss_effect))
        
        # Calculate percent contributions
        main_effects_final = []
        for result, ss in effect_results_main:
            result.percent_contribution = (ss / total_ss_effects * 100) if total_ss_effects > 0 else 0
            main_effects_final.append(result)
        
        interactions_final = []
        for result, ss in effect_results_int:
            result.percent_contribution = (ss / total_ss_effects * 100) if total_ss_effects > 0 else 0
            interactions_final.append(result)
        
        return main_effects_final, interactions_final
    
    @staticmethod
    def analyze_factorial(
        design: DesignMatrix,
        response: Union[List[float], np.ndarray],
        response_name: str = 'Response',
        alpha: float = 0.05
    ) -> DOEAnalysisResult:
        """
        Perform complete factorial analysis.
        
        Args:
            design: Design matrix
            response: Response values
            response_name: Name for response variable
            alpha: Significance level
            
        Returns:
            DOEAnalysisResult with complete analysis
        """
        response = np.array(response)
        X = design.coded_matrix
        y = response
        n = len(y)
        
        factor_names = [f.name for f in design.factors]
        
        # Calculate effects
        main_effects, interactions = DOE.calculate_effects(design, response, alpha)
        
        # Build full model
        X_full = np.ones((n, 1))  # Intercept
        for i in range(len(factor_names)):
            X_full = np.column_stack([X_full, X[:, i]])
        
        for i in range(len(factor_names)):
            for j in range(i + 1, len(factor_names)):
                X_full = np.column_stack([X_full, X[:, i] * X[:, j]])
        
        if len(factor_names) >= 3:
            for combo in itertools.combinations(range(len(factor_names)), 3):
                i, j, k = combo
                X_full = np.column_stack([X_full, X[:, i] * X[:, j] * X[:, k]])
        
        # Fit model
        beta = np.linalg.lstsq(X_full, y, rcond=None)[0]
        y_pred = X_full @ beta
        residuals = y - y_pred
        
        # R-squared
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Adjusted R-squared
        p = X_full.shape[1] - 1  # Number of predictors
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1) if n > p + 1 else 0
        
        # Residual standard error
        df_res = n - p - 1
        res_std_error = np.sqrt(ss_res / df_res) if df_res > 0 else 0
        
        # Create ANOVA table
        anova_data = []
        
        # Add main effects
        for effect in main_effects:
            ss = (effect.effect**2 * n) / 4
            ms = ss  # df = 1
            f_value = ms / (res_std_error**2) if res_std_error > 0 else 0
            p_value = 1 - stats.f.cdf(f_value, 1, df_res) if df_res > 0 else 1.0
            
            anova_data.append({
                'Source': effect.factor,
                'DF': 1,
                'SS': ss,
                'MS': ms,
                'F': f_value,
                'P': p_value
            })
        
        # Add interactions
        for effect in interactions:
            ss = (effect.effect**2 * n) / 4
            ms = ss  # df = 1
            f_value = ms / (res_std_error**2) if res_std_error > 0 else 0
            p_value = 1 - stats.f.cdf(f_value, 1, df_res) if df_res > 0 else 1.0
            
            anova_data.append({
                'Source': effect.factor,
                'DF': 1,
                'SS': ss,
                'MS': ms,
                'F': f_value,
                'P': p_value
            })
        
        # Add residual
        anova_data.append({
            'Source': 'Residual',
            'DF': df_res,
            'SS': ss_res,
            'MS': ss_res / df_res if df_res > 0 else 0,
            'F': np.nan,
            'P': np.nan
        })
        
        # Add total
        anova_data.append({
            'Source': 'Total',
            'DF': n - 1,
            'SS': ss_tot,
            'MS': np.nan,
            'F': np.nan,
            'P': np.nan
        })
        
        anova_table = pd.DataFrame(anova_data)
        
        # Generate interpretation
        sig_effects = [e.factor for e in main_effects + interactions if e.significant]
        
        if sig_effects:
            interpretation = (
                f"Model explains {r_squared*100:.1f}% of variance (Adj R² = {adj_r_squared*100:.1f}%). "
                f"Significant effects (α = {alpha}): {', '.join(sig_effects)}. "
            )
        else:
            interpretation = (
                f"Model explains {r_squared*100:.1f}% of variance. "
                f"No effects are significant at α = {alpha}. "
            )
        
        # Add largest effect
        all_effects = main_effects + interactions
        if all_effects:
            largest = max(all_effects, key=lambda x: abs(x.effect))
            interpretation += f"Largest effect: {largest.factor} ({largest.effect:+.4f})."
        
        return DOEAnalysisResult(
            factors=factor_names,
            response_name=response_name,
            main_effects=main_effects,
            interactions=interactions,
            model_r_squared=r_squared,
            model_adj_r_squared=adj_r_squared,
            residual_std_error=res_std_error,
            anova_table=anova_table,
            predicted_values=y_pred,
            residuals=residuals,
            interpretation=interpretation
        )
    
    @staticmethod
    def get_main_effects_plot_data(
        design: DesignMatrix,
        response: Union[List[float], np.ndarray]
    ) -> Dict[str, Dict]:
        """
        Get data for main effects plot.
        
        Args:
            design: Design matrix
            response: Response values
            
        Returns:
            Dictionary with plot data for each factor
        """
        response = np.array(response)
        X = design.coded_matrix
        
        plot_data = {}
        
        for i, factor in enumerate(design.factors):
            low_mask = X[:, i] == -1
            high_mask = X[:, i] == 1
            
            low_mean = np.mean(response[low_mask])
            high_mean = np.mean(response[high_mask])
            overall_mean = np.mean(response)
            
            plot_data[factor.name] = {
                'levels': [factor.low_label, factor.high_label],
                'natural_levels': [factor.low, factor.high],
                'means': [low_mean, high_mean],
                'overall_mean': overall_mean,
                'effect': high_mean - low_mean
            }
        
        return plot_data
    
    @staticmethod
    def get_interaction_plot_data(
        design: DesignMatrix,
        response: Union[List[float], np.ndarray],
        factor1_idx: int,
        factor2_idx: int
    ) -> Dict:
        """
        Get data for interaction plot.
        
        Args:
            design: Design matrix
            response: Response values
            factor1_idx: Index of first factor (x-axis)
            factor2_idx: Index of second factor (separate lines)
            
        Returns:
            Dictionary with plot data
        """
        response = np.array(response)
        X = design.coded_matrix
        
        f1 = design.factors[factor1_idx]
        f2 = design.factors[factor2_idx]
        
        # Get means for each combination
        means = {}
        for f1_level in [-1, 1]:
            for f2_level in [-1, 1]:
                mask = (X[:, factor1_idx] == f1_level) & (X[:, factor2_idx] == f2_level)
                if np.any(mask):
                    key = (f1_level, f2_level)
                    means[key] = np.mean(response[mask])
        
        return {
            'factor1_name': f1.name,
            'factor2_name': f2.name,
            'factor1_levels': [f1.low_label, f1.high_label],
            'factor2_levels': [f2.low_label, f2.high_label],
            'means': means,
            'line_f2_low': [means.get((-1, -1), 0), means.get((1, -1), 0)],
            'line_f2_high': [means.get((-1, 1), 0), means.get((1, 1), 0)]
        }
    
    @staticmethod
    def get_pareto_data(
        main_effects: List[EffectResult],
        interactions: List[EffectResult],
        alpha: float = 0.05
    ) -> Dict:
        """
        Get data for Pareto chart of effects.
        
        Args:
            main_effects: List of main effect results
            interactions: List of interaction results
            alpha: Significance level for reference line
            
        Returns:
            Dictionary with sorted effects data
        """
        all_effects = main_effects + interactions
        
        # Sort by absolute effect size
        sorted_effects = sorted(all_effects, key=lambda x: abs(x.effect), reverse=True)
        
        names = [e.factor for e in sorted_effects]
        effects = [abs(e.effect) for e in sorted_effects]
        significant = [e.significant for e in sorted_effects]
        
        # Calculate critical t-value line (approximate)
        # This is an approximation - actual value depends on df
        critical_t = stats.t.ppf(1 - alpha/2, df=10)
        
        return {
            'names': names,
            'effects': effects,
            'significant': significant,
            'critical_value': None  # Would need residual SE to calculate
        }
    
    @staticmethod
    def predict_response(
        result: DOEAnalysisResult,
        design: DesignMatrix,
        settings: Dict[str, float]
    ) -> float:
        """
        Predict response for given factor settings.
        
        Args:
            result: DOE analysis result
            design: Original design matrix
            settings: Dictionary of factor_name: coded_value (-1 to +1)
            
        Returns:
            Predicted response value
        """
        # Start with grand mean
        all_responses = result.predicted_values + result.residuals
        prediction = np.mean(all_responses)
        
        # Add main effects contributions
        for effect in result.main_effects:
            factor_value = settings.get(effect.factor, 0)
            prediction += effect.coefficient * factor_value
        
        # Add interaction contributions
        for effect in result.interactions:
            factors = effect.factor.split('*')
            interaction_value = 1.0
            for f in factors:
                interaction_value *= settings.get(f, 0)
            prediction += effect.coefficient * interaction_value
        
        return prediction
