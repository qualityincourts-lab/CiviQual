"""
CiviQual Stats Multiple Regression

Provides multiple regression analysis:
- Up to 5 predictors
- VIF (Variance Inflation Factor) for multicollinearity
- Residual analysis
- Prediction intervals
- Model equation output

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd


@dataclass
class CoefficientResult:
    """Result for a single regression coefficient."""
    variable: str
    coefficient: float
    std_error: float
    t_value: float
    p_value: float
    ci_lower: float
    ci_upper: float
    vif: float
    significant: bool
    
    def to_dict(self) -> Dict:
        return {
            'variable': self.variable,
            'coefficient': self.coefficient,
            'std_error': self.std_error,
            't_value': self.t_value,
            'p_value': self.p_value,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'vif': self.vif,
            'significant': self.significant
        }


@dataclass
class RegressionResult:
    """Complete multiple regression result."""
    coefficients: List[CoefficientResult]
    intercept: CoefficientResult
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_p_value: float
    residual_std_error: float
    n: int
    p: int  # Number of predictors
    df_regression: int
    df_residual: int
    anova_table: pd.DataFrame
    residuals: np.ndarray
    fitted_values: np.ndarray
    standardized_residuals: np.ndarray
    model_equation: str
    interpretation: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'coefficients': [c.to_dict() for c in self.coefficients],
            'intercept': self.intercept.to_dict(),
            'r_squared': self.r_squared,
            'adj_r_squared': self.adj_r_squared,
            'f_statistic': self.f_statistic,
            'f_p_value': self.f_p_value,
            'residual_std_error': self.residual_std_error,
            'n': self.n,
            'p': self.p,
            'model_equation': self.model_equation,
            'interpretation': self.interpretation
        }


@dataclass
class PredictionResult:
    """Result of prediction with intervals."""
    x_values: Dict[str, float]
    predicted: float
    ci_lower: float
    ci_upper: float
    pi_lower: float
    pi_upper: float
    confidence_level: float


@dataclass
class ResidualDiagnostics:
    """Residual diagnostic statistics."""
    residuals: np.ndarray
    standardized_residuals: np.ndarray
    cooks_distance: np.ndarray
    leverage: np.ndarray
    durbin_watson: float
    shapiro_wilk_stat: float
    shapiro_wilk_p: float
    normality_assessment: str
    independence_assessment: str
    influential_points: List[int]


class MultipleRegression:
    """
    Provides multiple regression analysis.
    """
    
    MAX_PREDICTORS = 5
    
    @staticmethod
    def calculate_vif(X: np.ndarray, predictor_idx: int) -> float:
        """
        Calculate VIF for a single predictor.
        
        Args:
            X: Predictor matrix (without intercept)
            predictor_idx: Index of predictor to calculate VIF for
            
        Returns:
            VIF value
        """
        if X.shape[1] == 1:
            return 1.0
        
        # Get the predictor
        y = X[:, predictor_idx]
        
        # Other predictors as X
        other_idx = [i for i in range(X.shape[1]) if i != predictor_idx]
        X_other = X[:, other_idx]
        
        # Add intercept
        X_with_int = np.column_stack([np.ones(len(y)), X_other])
        
        # Fit regression
        try:
            beta = np.linalg.lstsq(X_with_int, y, rcond=None)[0]
            y_pred = X_with_int @ beta
            
            ss_res = np.sum((y - y_pred)**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            if r_squared >= 1:
                return np.inf
            
            vif = 1 / (1 - r_squared)
            return vif
            
        except:
            return np.inf
    
    @staticmethod
    def fit(
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        predictor_names: Optional[List[str]] = None,
        response_name: str = 'Y',
        alpha: float = 0.05
    ) -> RegressionResult:
        """
        Fit multiple regression model.
        
        Args:
            X: Predictor matrix (n x p)
            y: Response vector (n,)
            predictor_names: Names for predictors
            response_name: Name for response variable
            alpha: Significance level
            
        Returns:
            RegressionResult with complete analysis
        """
        # Convert to numpy
        if isinstance(X, pd.DataFrame):
            if predictor_names is None:
                predictor_names = list(X.columns)
            X = X.values
        
        if isinstance(y, pd.Series):
            y = y.values
        
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)
        
        # Handle 1D X
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        n, p = X.shape
        
        if p > MultipleRegression.MAX_PREDICTORS:
            raise ValueError(f"Maximum {MultipleRegression.MAX_PREDICTORS} predictors allowed")
        
        if n <= p + 1:
            raise ValueError(f"Need at least {p + 2} observations for {p} predictors")
        
        if predictor_names is None:
            predictor_names = [f'X{i+1}' for i in range(p)]
        
        # Remove missing values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X = X[mask]
        y = y[mask]
        n = len(y)
        
        # Add intercept
        X_with_int = np.column_stack([np.ones(n), X])
        
        # Fit model using OLS
        try:
            beta = np.linalg.lstsq(X_with_int, y, rcond=None)[0]
        except:
            raise ValueError("Could not fit model. Check for perfect multicollinearity.")
        
        # Predictions and residuals
        y_pred = X_with_int @ beta
        residuals = y - y_pred
        
        # Sum of squares
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        ss_reg = ss_tot - ss_res
        
        # Degrees of freedom
        df_reg = p
        df_res = n - p - 1
        df_tot = n - 1
        
        # Mean squares
        ms_reg = ss_reg / df_reg if df_reg > 0 else 0
        ms_res = ss_res / df_res if df_res > 0 else 0
        
        # R-squared
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        adj_r_squared = 1 - (1 - r_squared) * df_tot / df_res if df_res > 0 else 0
        
        # F-test
        f_stat = ms_reg / ms_res if ms_res > 0 else 0
        f_p_value = 1 - stats.f.cdf(f_stat, df_reg, df_res)
        
        # Residual standard error
        res_std_error = np.sqrt(ms_res)
        
        # Coefficient standard errors
        try:
            var_cov = ms_res * np.linalg.inv(X_with_int.T @ X_with_int)
            se_beta = np.sqrt(np.diag(var_cov))
        except:
            se_beta = np.ones(p + 1) * res_std_error
        
        # t-values and p-values
        t_values = beta / se_beta
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_values), df_res))
        
        # Confidence intervals
        t_crit = stats.t.ppf(1 - alpha/2, df_res)
        ci_lower = beta - t_crit * se_beta
        ci_upper = beta + t_crit * se_beta
        
        # VIF for each predictor
        vifs = [MultipleRegression.calculate_vif(X, i) for i in range(p)]
        
        # Create coefficient results
        intercept_result = CoefficientResult(
            variable='Intercept',
            coefficient=beta[0],
            std_error=se_beta[0],
            t_value=t_values[0],
            p_value=p_values[0],
            ci_lower=ci_lower[0],
            ci_upper=ci_upper[0],
            vif=0,  # No VIF for intercept
            significant=p_values[0] < alpha
        )
        
        coef_results = []
        for i in range(p):
            coef_results.append(CoefficientResult(
                variable=predictor_names[i],
                coefficient=beta[i + 1],
                std_error=se_beta[i + 1],
                t_value=t_values[i + 1],
                p_value=p_values[i + 1],
                ci_lower=ci_lower[i + 1],
                ci_upper=ci_upper[i + 1],
                vif=vifs[i],
                significant=p_values[i + 1] < alpha
            ))
        
        # ANOVA table
        anova_data = [
            {'Source': 'Regression', 'DF': df_reg, 'SS': ss_reg, 'MS': ms_reg, 'F': f_stat, 'P': f_p_value},
            {'Source': 'Residual', 'DF': df_res, 'SS': ss_res, 'MS': ms_res, 'F': np.nan, 'P': np.nan},
            {'Source': 'Total', 'DF': df_tot, 'SS': ss_tot, 'MS': np.nan, 'F': np.nan, 'P': np.nan}
        ]
        anova_table = pd.DataFrame(anova_data)
        
        # Standardized residuals
        leverage = np.diag(X_with_int @ np.linalg.inv(X_with_int.T @ X_with_int) @ X_with_int.T)
        std_residuals = residuals / (res_std_error * np.sqrt(1 - leverage))
        
        # Model equation
        equation_parts = [f"{beta[0]:.4f}"]
        for i, name in enumerate(predictor_names):
            sign = "+" if beta[i + 1] >= 0 else ""
            equation_parts.append(f"{sign}{beta[i + 1]:.4f}*{name}")
        model_equation = f"{response_name} = " + " ".join(equation_parts)
        
        # Interpretation
        sig_predictors = [c.variable for c in coef_results if c.significant]
        high_vif = [c.variable for c in coef_results if c.vif > 5]
        
        interpretation = (
            f"Model: R² = {r_squared:.4f}, Adj R² = {adj_r_squared:.4f}, "
            f"F({df_reg},{df_res}) = {f_stat:.2f}, p = {f_p_value:.4f}. "
        )
        
        if f_p_value < alpha:
            interpretation += "Model is significant. "
        else:
            interpretation += "Model is not significant. "
        
        if sig_predictors:
            interpretation += f"Significant predictors: {', '.join(sig_predictors)}. "
        
        if high_vif:
            interpretation += f"Multicollinearity concern (VIF > 5): {', '.join(high_vif)}."
        
        return RegressionResult(
            coefficients=coef_results,
            intercept=intercept_result,
            r_squared=r_squared,
            adj_r_squared=adj_r_squared,
            f_statistic=f_stat,
            f_p_value=f_p_value,
            residual_std_error=res_std_error,
            n=n,
            p=p,
            df_regression=df_reg,
            df_residual=df_res,
            anova_table=anova_table,
            residuals=residuals,
            fitted_values=y_pred,
            standardized_residuals=std_residuals,
            model_equation=model_equation,
            interpretation=interpretation
        )
    
    @staticmethod
    def predict(
        result: RegressionResult,
        X_new: Union[Dict[str, float], np.ndarray, pd.DataFrame],
        X_original: np.ndarray,
        y_original: np.ndarray,
        confidence_level: float = 0.95
    ) -> PredictionResult:
        """
        Make predictions with confidence and prediction intervals.
        
        Args:
            result: Fitted regression result
            X_new: New predictor values
            X_original: Original X data (for interval calculation)
            y_original: Original y data
            confidence_level: Confidence level for intervals
            
        Returns:
            PredictionResult with predicted value and intervals
        """
        # Convert X_new to array
        if isinstance(X_new, dict):
            x_values = X_new
            x_array = np.array([X_new[c.variable] for c in result.coefficients])
        elif isinstance(X_new, pd.DataFrame):
            x_values = X_new.iloc[0].to_dict()
            x_array = X_new.values[0]
        else:
            x_array = np.array(X_new).flatten()
            x_values = {c.variable: x_array[i] for i, c in enumerate(result.coefficients)}
        
        # Add intercept
        x_with_int = np.concatenate([[1], x_array])
        
        # Get coefficients
        beta = np.array([result.intercept.coefficient] + [c.coefficient for c in result.coefficients])
        
        # Prediction
        y_pred = np.dot(x_with_int, beta)
        
        # For intervals, need original X with intercept
        X_orig_int = np.column_stack([np.ones(len(y_original)), X_original])
        
        # Calculate intervals
        alpha = 1 - confidence_level
        t_crit = stats.t.ppf(1 - alpha/2, result.df_residual)
        
        try:
            XtX_inv = np.linalg.inv(X_orig_int.T @ X_orig_int)
            
            # Standard error of mean prediction
            se_mean = result.residual_std_error * np.sqrt(x_with_int @ XtX_inv @ x_with_int)
            
            # Standard error of individual prediction
            se_pred = result.residual_std_error * np.sqrt(1 + x_with_int @ XtX_inv @ x_with_int)
            
        except:
            se_mean = result.residual_std_error
            se_pred = result.residual_std_error * np.sqrt(2)
        
        # Confidence interval (for mean response)
        ci_lower = y_pred - t_crit * se_mean
        ci_upper = y_pred + t_crit * se_mean
        
        # Prediction interval (for individual response)
        pi_lower = y_pred - t_crit * se_pred
        pi_upper = y_pred + t_crit * se_pred
        
        return PredictionResult(
            x_values=x_values,
            predicted=y_pred,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            pi_lower=pi_lower,
            pi_upper=pi_upper,
            confidence_level=confidence_level
        )
    
    @staticmethod
    def residual_diagnostics(
        result: RegressionResult,
        X: np.ndarray,
        y: np.ndarray
    ) -> ResidualDiagnostics:
        """
        Perform residual diagnostics.
        
        Args:
            result: Fitted regression result
            X: Original predictor matrix
            y: Original response vector
            
        Returns:
            ResidualDiagnostics with diagnostic statistics
        """
        residuals = result.residuals
        std_residuals = result.standardized_residuals
        n = len(residuals)
        p = result.p
        
        # Add intercept
        X_with_int = np.column_stack([np.ones(n), X])
        
        # Hat matrix (leverage)
        try:
            H = X_with_int @ np.linalg.inv(X_with_int.T @ X_with_int) @ X_with_int.T
            leverage = np.diag(H)
        except:
            leverage = np.ones(n) * (p + 1) / n
        
        # Cook's distance
        mse = result.residual_std_error**2
        cooks_d = (std_residuals**2 / (p + 1)) * (leverage / (1 - leverage))
        
        # Durbin-Watson statistic
        diff_residuals = np.diff(residuals)
        durbin_watson = np.sum(diff_residuals**2) / np.sum(residuals**2)
        
        # Normality test
        if n >= 8:
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
        else:
            shapiro_stat, shapiro_p = np.nan, np.nan
        
        # Assess normality
        if np.isnan(shapiro_p):
            normality_assessment = "Insufficient data for normality test"
        elif shapiro_p > 0.05:
            normality_assessment = "Residuals appear normally distributed (Shapiro-Wilk p > 0.05)"
        else:
            normality_assessment = "Residuals may not be normal (Shapiro-Wilk p < 0.05)"
        
        # Assess independence (Durbin-Watson)
        if durbin_watson < 1.5:
            independence_assessment = "Positive autocorrelation may be present (DW < 1.5)"
        elif durbin_watson > 2.5:
            independence_assessment = "Negative autocorrelation may be present (DW > 2.5)"
        else:
            independence_assessment = "No strong evidence of autocorrelation (1.5 < DW < 2.5)"
        
        # Identify influential points (Cook's D > 4/n)
        threshold = 4 / n
        influential_points = list(np.where(cooks_d > threshold)[0])
        
        return ResidualDiagnostics(
            residuals=residuals,
            standardized_residuals=std_residuals,
            cooks_distance=cooks_d,
            leverage=leverage,
            durbin_watson=durbin_watson,
            shapiro_wilk_stat=shapiro_stat,
            shapiro_wilk_p=shapiro_p,
            normality_assessment=normality_assessment,
            independence_assessment=independence_assessment,
            influential_points=influential_points
        )
    
    @staticmethod
    def stepwise_selection(
        X: np.ndarray,
        y: np.ndarray,
        predictor_names: List[str],
        method: str = 'backward',
        alpha_in: float = 0.05,
        alpha_out: float = 0.10
    ) -> List[str]:
        """
        Perform stepwise variable selection.
        
        Args:
            X: Predictor matrix
            y: Response vector
            predictor_names: Names of predictors
            method: 'forward', 'backward', or 'both'
            alpha_in: p-value threshold for entering
            alpha_out: p-value threshold for removing
            
        Returns:
            List of selected predictor names
        """
        n, p = X.shape
        
        if method == 'backward':
            # Start with all predictors
            selected = list(range(p))
            
            while len(selected) > 0:
                # Fit model with current predictors
                X_current = X[:, selected]
                result = MultipleRegression.fit(
                    X_current, y,
                    [predictor_names[i] for i in selected]
                )
                
                # Find predictor with highest p-value
                max_p = 0
                max_idx = -1
                for i, coef in enumerate(result.coefficients):
                    if coef.p_value > max_p:
                        max_p = coef.p_value
                        max_idx = i
                
                # Remove if p-value > alpha_out
                if max_p > alpha_out:
                    selected.pop(max_idx)
                else:
                    break
            
            return [predictor_names[i] for i in selected]
        
        elif method == 'forward':
            # Start with no predictors
            selected = []
            remaining = list(range(p))
            
            while len(remaining) > 0:
                best_p = 1
                best_idx = -1
                
                for idx in remaining:
                    # Try adding this predictor
                    test_selected = selected + [idx]
                    X_test = X[:, test_selected]
                    
                    try:
                        result = MultipleRegression.fit(
                            X_test, y,
                            [predictor_names[i] for i in test_selected]
                        )
                        # Get p-value for the new predictor
                        new_p = result.coefficients[-1].p_value
                        if new_p < best_p:
                            best_p = new_p
                            best_idx = idx
                    except:
                        continue
                
                # Add if p-value < alpha_in
                if best_p < alpha_in:
                    selected.append(best_idx)
                    remaining.remove(best_idx)
                else:
                    break
            
            return [predictor_names[i] for i in selected]
        
        else:
            raise ValueError("Method must be 'forward', 'backward', or 'both'")
