"""Core statistics engine for CiviQual Stats.

Implements the statistical routines used by both Free and Pro tools. All
routines accept numpy arrays or pandas Series and return plain dataclasses
so the calling UI code remains simple.

References:
  - Montgomery, D.C. (2020). Introduction to Statistical Quality Control, 8e.
  - AIAG (2010). Measurement Systems Analysis (MSA) Reference Manual, 4e.
  - NIST/SEMATECH e-Handbook of Statistical Methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Control-chart constants (Montgomery Table VI)
# ---------------------------------------------------------------------------
# d2 converts the average moving range / average subgroup range to sigma-hat.
D2 = {
    2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
    6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
}
# D3 and D4 are the lower and upper range chart control-limit factors.
D3 = {2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000,
      7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004,
      7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
# A2 is the X-bar chart factor used with R-bar.
A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
      7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------
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


def descriptive(values: Iterable[float]) -> DescriptiveResult:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[~np.isnan(arr)]
    n = arr.size
    if n == 0:
        return DescriptiveResult(0, *[float("nan")] * 11)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    sem = std / np.sqrt(n) if n > 1 else 0.0
    q1, med, q3 = np.percentile(arr, [25, 50, 75])
    skew = float(stats.skew(arr, bias=False)) if n > 2 else 0.0
    kurt = float(stats.kurtosis(arr, bias=False)) if n > 3 else 0.0
    if n > 1:
        tcrit = stats.t.ppf(0.975, df=n - 1)
        ci_low = mean - tcrit * sem
        ci_high = mean + tcrit * sem
    else:
        ci_low = ci_high = mean
    return DescriptiveResult(
        n=n, mean=mean, std=std, sem=sem,
        min=float(np.min(arr)), q1=float(q1), median=float(med),
        q3=float(q3), max=float(np.max(arr)),
        skewness=skew, kurtosis=kurt,
        ci95_lower=float(ci_low), ci95_upper=float(ci_high),
    )


# ---------------------------------------------------------------------------
# Individuals / Moving-Range (XmR) chart
# ---------------------------------------------------------------------------
@dataclass
class XmRResult:
    values: np.ndarray
    moving_range: np.ndarray
    x_center: float
    x_ucl: float
    x_lcl: float
    mr_center: float
    mr_ucl: float
    mr_lcl: float
    sigma_hat: float
    signals: list[dict] = field(default_factory=list)


def xmr_chart(values: Iterable[float]) -> XmRResult:
    arr = np.asarray(list(values), dtype=float)
    if arr.size < 2:
        raise ValueError("XmR requires at least two observations.")
    mr = np.abs(np.diff(arr))
    mr_bar = float(np.mean(mr))
    x_bar = float(np.mean(arr))
    sigma = mr_bar / D2[2]
    x_ucl = x_bar + 3 * sigma
    x_lcl = x_bar - 3 * sigma
    mr_ucl = D4[2] * mr_bar
    mr_lcl = D3[2] * mr_bar
    result = XmRResult(
        values=arr,
        moving_range=np.concatenate(([np.nan], mr)),
        x_center=x_bar, x_ucl=x_ucl, x_lcl=x_lcl,
        mr_center=mr_bar, mr_ucl=mr_ucl, mr_lcl=mr_lcl,
        sigma_hat=sigma,
    )
    result.signals = western_electric_rules(arr, x_bar, sigma)
    return result


# ---------------------------------------------------------------------------
# Western Electric rules (Tests 1-8, Nelson/WE combined set)
# ---------------------------------------------------------------------------
def western_electric_rules(
    values: np.ndarray, center: float, sigma: float
) -> list[dict]:
    """Return a list of {'index', 'rule', 'description'} signal dicts."""
    signals: list[dict] = []
    n = len(values)
    z = (values - center) / sigma if sigma > 0 else np.zeros_like(values)

    # Rule 1: one point beyond 3 sigma
    for i, zi in enumerate(z):
        if abs(zi) > 3:
            signals.append({"index": i, "rule": 1,
                            "description": "Point beyond 3 sigma"})

    # Rule 2: 9 points in a row on the same side of the centerline
    for i in range(n - 8):
        seg = values[i:i + 9] - center
        if np.all(seg > 0) or np.all(seg < 0):
            signals.append({"index": i + 8, "rule": 2,
                            "description": "9 points on one side of center"})

    # Rule 3: 6 points in a row increasing or decreasing
    for i in range(n - 5):
        seg = values[i:i + 6]
        diffs = np.diff(seg)
        if np.all(diffs > 0) or np.all(diffs < 0):
            signals.append({"index": i + 5, "rule": 3,
                            "description": "6 points trending"})

    # Rule 4: 14 points alternating up and down
    for i in range(n - 13):
        seg = np.diff(values[i:i + 14])
        if np.all(np.sign(seg[:-1]) != np.sign(seg[1:])):
            signals.append({"index": i + 13, "rule": 4,
                            "description": "14 points alternating"})

    # Rule 5: 2 out of 3 points beyond 2 sigma (same side)
    for i in range(n - 2):
        seg = z[i:i + 3]
        for side in (1, -1):
            count = np.sum(side * seg > 2)
            if count >= 2:
                signals.append({"index": i + 2, "rule": 5,
                                "description": "2 of 3 beyond 2 sigma"})
                break

    # Rule 6: 4 out of 5 points beyond 1 sigma (same side)
    for i in range(n - 4):
        seg = z[i:i + 5]
        for side in (1, -1):
            count = np.sum(side * seg > 1)
            if count >= 4:
                signals.append({"index": i + 4, "rule": 6,
                                "description": "4 of 5 beyond 1 sigma"})
                break

    # Rule 7: 15 points in a row within 1 sigma (stratification)
    for i in range(n - 14):
        seg = z[i:i + 15]
        if np.all(np.abs(seg) < 1):
            signals.append({"index": i + 14, "rule": 7,
                            "description": "15 points within 1 sigma (stratification)"})

    # Rule 8: 8 points in a row with none within 1 sigma (mixture)
    for i in range(n - 7):
        seg = z[i:i + 8]
        if np.all(np.abs(seg) > 1):
            signals.append({"index": i + 7, "rule": 8,
                            "description": "8 points beyond 1 sigma (mixture)"})

    return signals


# ---------------------------------------------------------------------------
# Subgroup X-bar / R chart
# ---------------------------------------------------------------------------
@dataclass
class XbarRResult:
    subgroup_means: np.ndarray
    subgroup_ranges: np.ndarray
    xbar_center: float
    xbar_ucl: float
    xbar_lcl: float
    r_center: float
    r_ucl: float
    r_lcl: float
    sigma_hat: float
    subgroup_size: int


def xbar_r_chart(data: np.ndarray) -> XbarRResult:
    if data.ndim != 2:
        raise ValueError("Subgroup data must be 2-D: rows = subgroups.")
    n = data.shape[1]
    if n < 2 or n > 10:
        raise ValueError("Subgroup size must be between 2 and 10.")
    means = np.mean(data, axis=1)
    ranges = np.ptp(data, axis=1)
    r_bar = float(np.mean(ranges))
    x_bar = float(np.mean(means))
    sigma = r_bar / D2[n]
    return XbarRResult(
        subgroup_means=means,
        subgroup_ranges=ranges,
        xbar_center=x_bar,
        xbar_ucl=x_bar + A2[n] * r_bar,
        xbar_lcl=x_bar - A2[n] * r_bar,
        r_center=r_bar,
        r_ucl=D4[n] * r_bar,
        r_lcl=D3[n] * r_bar,
        sigma_hat=sigma,
        subgroup_size=n,
    )


# ---------------------------------------------------------------------------
# Normality tests
# ---------------------------------------------------------------------------
@dataclass
class NormalityResult:
    test: str
    statistic: float
    p_value: float
    normal_at_95: bool


def anderson_darling(values: Iterable[float]) -> NormalityResult:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[~np.isnan(arr)]
    # Compute the Anderson-Darling statistic directly so behavior is stable
    # across scipy versions (stats.anderson signature changes in 1.17+).
    n = arr.size
    sorted_arr = np.sort(arr)
    mu = float(np.mean(sorted_arr))
    sigma = float(np.std(sorted_arr, ddof=1))
    if sigma == 0:
        return NormalityResult("Anderson-Darling", float("nan"), 1.0, True)
    z = (sorted_arr - mu) / sigma
    cdf = stats.norm.cdf(z)
    # Guard against log(0)
    eps = 1e-12
    cdf = np.clip(cdf, eps, 1 - eps)
    i = np.arange(1, n + 1)
    s = np.sum((2 * i - 1) * (np.log(cdf) + np.log(1 - cdf[::-1])))
    ad = -n - s / n
    # Approximate p-value using the Stephens (1986) transform.
    ad_star = ad * (1 + 0.75 / n + 2.25 / (n * n))
    if ad_star >= 0.600:
        p = np.exp(1.2937 - 5.709 * ad_star + 0.0186 * ad_star**2)
    elif ad_star >= 0.340:
        p = np.exp(0.9177 - 4.279 * ad_star - 1.38 * ad_star**2)
    elif ad_star >= 0.200:
        p = 1 - np.exp(-8.318 + 42.796 * ad_star - 59.938 * ad_star**2)
    else:
        p = 1 - np.exp(-13.436 + 101.14 * ad_star - 223.73 * ad_star**2)
    p = float(np.clip(p, 0.0, 1.0))
    return NormalityResult("Anderson-Darling", float(ad), p, p > 0.05)


def shapiro_wilk(values: Iterable[float]) -> NormalityResult:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[~np.isnan(arr)]
    stat, p = stats.shapiro(arr)
    return NormalityResult("Shapiro-Wilk", float(stat), float(p), p > 0.05)


# ---------------------------------------------------------------------------
# Process capability
# ---------------------------------------------------------------------------
@dataclass
class CapabilityResult:
    mean: float
    sigma_within: float
    sigma_overall: float
    lsl: Optional[float]
    usl: Optional[float]
    cp: Optional[float]
    cpk: Optional[float]
    pp: Optional[float]
    ppk: Optional[float]
    ppm_below: float
    ppm_above: float
    ppm_total: float


def capability(
    values: Iterable[float],
    lsl: Optional[float] = None,
    usl: Optional[float] = None,
    subgroup_size: int = 1,
) -> CapabilityResult:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[~np.isnan(arr)]
    mean = float(np.mean(arr))
    sigma_overall = float(np.std(arr, ddof=1))

    if subgroup_size <= 1:
        mr = np.abs(np.diff(arr))
        sigma_within = float(np.mean(mr)) / D2[2] if mr.size else sigma_overall
    else:
        # Assume arr is already row-major flattened subgroups
        arr2d = arr.reshape(-1, subgroup_size)
        ranges = np.ptp(arr2d, axis=1)
        sigma_within = float(np.mean(ranges)) / D2[subgroup_size]

    def _cpk(mu, s, low, high):
        vals = []
        if low is not None:
            vals.append((mu - low) / (3 * s))
        if high is not None:
            vals.append((high - mu) / (3 * s))
        return min(vals) if vals else None

    cp = (usl - lsl) / (6 * sigma_within) if (usl is not None and lsl is not None and sigma_within > 0) else None
    pp = (usl - lsl) / (6 * sigma_overall) if (usl is not None and lsl is not None and sigma_overall > 0) else None
    cpk = _cpk(mean, sigma_within, lsl, usl) if sigma_within > 0 else None
    ppk = _cpk(mean, sigma_overall, lsl, usl) if sigma_overall > 0 else None

    ppm_below = ppm_above = 0.0
    if lsl is not None and sigma_overall > 0:
        ppm_below = float(stats.norm.cdf((lsl - mean) / sigma_overall)) * 1_000_000
    if usl is not None and sigma_overall > 0:
        ppm_above = float(1 - stats.norm.cdf((usl - mean) / sigma_overall)) * 1_000_000

    return CapabilityResult(
        mean=mean, sigma_within=sigma_within, sigma_overall=sigma_overall,
        lsl=lsl, usl=usl,
        cp=cp, cpk=cpk, pp=pp, ppk=ppk,
        ppm_below=ppm_below, ppm_above=ppm_above,
        ppm_total=ppm_below + ppm_above,
    )


# ---------------------------------------------------------------------------
# One-way ANOVA with Tukey HSD post-hoc
# ---------------------------------------------------------------------------
@dataclass
class AnovaResult:
    f_statistic: float
    p_value: float
    df_between: int
    df_within: int
    ss_between: float
    ss_within: float
    ms_between: float
    ms_within: float
    group_means: dict
    group_n: dict
    tukey_pairs: list[dict] = field(default_factory=list)


def one_way_anova(groups: dict[str, Iterable[float]]) -> AnovaResult:
    names = list(groups.keys())
    arrays = [np.asarray(list(groups[k]), dtype=float) for k in names]
    arrays = [a[~np.isnan(a)] for a in arrays]
    k = len(arrays)
    ns = [len(a) for a in arrays]
    n_total = sum(ns)
    grand_mean = float(np.mean(np.concatenate(arrays)))
    means = [float(np.mean(a)) for a in arrays]
    ss_between = float(sum(ns[i] * (means[i] - grand_mean) ** 2 for i in range(k)))
    ss_within = float(sum(np.sum((arrays[i] - means[i]) ** 2) for i in range(k)))
    df_b = k - 1
    df_w = n_total - k
    ms_b = ss_between / df_b if df_b > 0 else 0.0
    ms_w = ss_within / df_w if df_w > 0 else 0.0
    f_stat = ms_b / ms_w if ms_w > 0 else float("inf")
    p = float(1 - stats.f.cdf(f_stat, df_b, df_w)) if ms_w > 0 else 0.0

    tukey: list[dict] = []
    if ms_w > 0 and df_w > 0:
        mse = ms_w
        q_crit = studentized_range_critical(k, df_w, alpha=0.05)
        for i in range(k):
            for j in range(i + 1, k):
                diff = means[i] - means[j]
                se = np.sqrt(mse * (1 / ns[i] + 1 / ns[j]) / 2)
                q = abs(diff) / se if se > 0 else 0.0
                sig = q > q_crit
                tukey.append({
                    "group_a": names[i], "group_b": names[j],
                    "mean_diff": diff, "q_stat": float(q),
                    "q_critical_05": float(q_crit),
                    "significant": bool(sig),
                })

    return AnovaResult(
        f_statistic=float(f_stat), p_value=p,
        df_between=df_b, df_within=df_w,
        ss_between=ss_between, ss_within=ss_within,
        ms_between=ms_b, ms_within=ms_w,
        group_means=dict(zip(names, means)),
        group_n=dict(zip(names, ns)),
        tukey_pairs=tukey,
    )


def studentized_range_critical(k: int, df: int, alpha: float = 0.05) -> float:
    """Approximate critical value for the studentized range distribution."""
    # scipy provides the distribution; use it when available.
    try:
        return float(stats.studentized_range.ppf(1 - alpha, k, df))
    except Exception:
        # Fallback rough approximation
        return float(np.sqrt(2) * stats.norm.ppf(1 - alpha / (2 * k)))


# ---------------------------------------------------------------------------
# Correlation
# ---------------------------------------------------------------------------
@dataclass
class CorrelationResult:
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    n: int


def correlation(x: Iterable[float], y: Iterable[float]) -> CorrelationResult:
    xa = np.asarray(list(x), dtype=float)
    ya = np.asarray(list(y), dtype=float)
    mask = ~(np.isnan(xa) | np.isnan(ya))
    xa, ya = xa[mask], ya[mask]
    pr, pp = stats.pearsonr(xa, ya)
    sr, sp = stats.spearmanr(xa, ya)
    return CorrelationResult(float(pr), float(pp), float(sr), float(sp), int(xa.size))


# ---------------------------------------------------------------------------
# Pareto analysis
# ---------------------------------------------------------------------------
def pareto_table(categories: Iterable[str], counts: Iterable[float]) -> pd.DataFrame:
    df = pd.DataFrame({"category": list(categories), "count": list(counts)})
    df = df.groupby("category", as_index=False)["count"].sum()
    df = df.sort_values("count", ascending=False).reset_index(drop=True)
    total = df["count"].sum()
    df["percent"] = 100 * df["count"] / total if total else 0.0
    df["cumulative_percent"] = df["percent"].cumsum()
    return df


# ---------------------------------------------------------------------------
# Attribute charts (p, np, c, u)
# ---------------------------------------------------------------------------
@dataclass
class AttributeChartResult:
    chart_type: str
    values: np.ndarray
    center: float
    ucl: np.ndarray
    lcl: np.ndarray


def p_chart(defectives: Iterable[int], sample_sizes: Iterable[int]) -> AttributeChartResult:
    d = np.asarray(list(defectives), dtype=float)
    n = np.asarray(list(sample_sizes), dtype=float)
    p = d / n
    p_bar = float(np.sum(d) / np.sum(n))
    se = np.sqrt(p_bar * (1 - p_bar) / n)
    ucl = np.clip(p_bar + 3 * se, 0, 1)
    lcl = np.clip(p_bar - 3 * se, 0, 1)
    return AttributeChartResult("p", p, p_bar, ucl, lcl)


def np_chart(defectives: Iterable[int], n: int) -> AttributeChartResult:
    d = np.asarray(list(defectives), dtype=float)
    np_bar = float(np.mean(d))
    p_bar = np_bar / n
    se = np.sqrt(np_bar * (1 - p_bar))
    ucl = np.full_like(d, np_bar + 3 * se)
    lcl = np.clip(np.full_like(d, np_bar - 3 * se), 0, None)
    return AttributeChartResult("np", d, np_bar, ucl, lcl)


def c_chart(counts: Iterable[int]) -> AttributeChartResult:
    c = np.asarray(list(counts), dtype=float)
    c_bar = float(np.mean(c))
    ucl = np.full_like(c, c_bar + 3 * np.sqrt(c_bar))
    lcl = np.clip(np.full_like(c, c_bar - 3 * np.sqrt(c_bar)), 0, None)
    return AttributeChartResult("c", c, c_bar, ucl, lcl)


def u_chart(counts: Iterable[int], sample_sizes: Iterable[float]) -> AttributeChartResult:
    c = np.asarray(list(counts), dtype=float)
    n = np.asarray(list(sample_sizes), dtype=float)
    u = c / n
    u_bar = float(np.sum(c) / np.sum(n))
    se = np.sqrt(u_bar / n)
    ucl = u_bar + 3 * se
    lcl = np.clip(u_bar - 3 * se, 0, None)
    return AttributeChartResult("u", u, u_bar, ucl, lcl)


# ---------------------------------------------------------------------------
# Run chart runs tests
# ---------------------------------------------------------------------------
@dataclass
class RunChartResult:
    values: np.ndarray
    median: float
    runs_observed: int
    runs_expected: float
    runs_sd: float
    runs_z: float
    runs_p: float
    longest_run: int
    trend_p: float


def run_chart(values: Iterable[float]) -> RunChartResult:
    arr = np.asarray(list(values), dtype=float)
    med = float(np.median(arr))
    above = arr > med
    runs = 1 + int(np.sum(above[1:] != above[:-1]))
    n1 = int(np.sum(above))
    n2 = int(np.sum(~above))
    if n1 == 0 or n2 == 0:
        return RunChartResult(arr, med, runs, runs, 0.0, 0.0, 1.0, 0, 1.0)
    n = n1 + n2
    mu = 1 + 2 * n1 * n2 / n
    sigma2 = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n * n * (n - 1))
    sigma = float(np.sqrt(max(sigma2, 0)))
    z = (runs - mu) / sigma if sigma > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))

    # Longest run
    longest = cur = 1
    for i in range(1, len(above)):
        if above[i] == above[i - 1]:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 1

    # Trend test (Mann-Kendall)
    n_all = arr.size
    s = 0
    for i in range(n_all - 1):
        for j in range(i + 1, n_all):
            s += int(np.sign(arr[j] - arr[i]))
    var_s = n_all * (n_all - 1) * (2 * n_all + 5) / 18
    if s > 0:
        z_mk = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z_mk = (s + 1) / np.sqrt(var_s)
    else:
        z_mk = 0.0
    trend_p = float(2 * (1 - stats.norm.cdf(abs(z_mk))))

    return RunChartResult(
        values=arr, median=med,
        runs_observed=runs, runs_expected=float(mu), runs_sd=sigma,
        runs_z=float(z), runs_p=float(p),
        longest_run=int(longest),
        trend_p=trend_p,
    )
