"""
ethics_framework/analysis/statistical_analysis.py
=================================================
Advanced statistical analysis for experimental results
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import mannwhitneyu, wilcoxon, kruskal, friedmanchisquare
from scipy.stats import shapiro, normaltest, anderson
from scipy.stats import ttest_ind, ttest_rel, f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.power import TTestPower
import pingouin as pg
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis for ethics-by-design experiments
    """
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        self.results = {}
        
    def analyze_performance_comparison(self, 
                                     baseline_latencies: List[float],
                                     ethics_latencies: List[float]) -> Dict[str, Any]:
        """
        Comprehensive statistical comparison of performance
        """
        baseline = np.array(baseline_latencies)
        ethics = np.array(ethics_latencies)
        
        results = {
            'descriptive': self._descriptive_statistics(baseline, ethics),
            'normality': self._test_normality(baseline, ethics),
            'hypothesis_tests': self._hypothesis_testing(baseline, ethics),
            'effect_size': self._calculate_effect_sizes(baseline, ethics),
            'confidence_intervals': self._calculate_confidence_intervals(baseline, ethics),
            'power_analysis': self._power_analysis(baseline, ethics),
            'distribution_comparison': self._compare_distributions(baseline, ethics)
        }
        
        return results
    
    def _descriptive_statistics(self, baseline: np.ndarray, 
                              ethics: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics"""
        
        def calculate_stats(data: np.ndarray, name: str) -> Dict:
            return {
                f'{name}_mean': float(np.mean(data)),
                f'{name}_median': float(np.median(data)),
                f'{name}_std': float(np.std(data, ddof=1)),
                f'{name}_var': float(np.var(data, ddof=1)),
                f'{name}_skew': float(stats.skew(data)),
                f'{name}_kurtosis': float(stats.kurtosis(data)),
                f'{name}_min': float(np.min(data)),
                f'{name}_max': float(np.max(data)),
                f'{name}_range': float(np.max(data) - np.min(data)),
                f'{name}_iqr': float(np.percentile(data, 75) - np.percentile(data, 25)),
                f'{name}_cv': float(np.std(data) / np.mean(data)),  # Coefficient of variation
                f'{name}_percentiles': {
                    'p1': float(np.percentile(data, 1)),
                    'p5': float(np.percentile(data, 5)),
                    'p10': float(np.percentile(data, 10)),
                    'p25': float(np.percentile(data, 25)),
                    'p50': float(np.percentile(data, 50)),
                    'p75': float(np.percentile(data, 75)),
                    'p90': float(np.percentile(data, 90)),
                    'p95': float(np.percentile(data, 95)),
                    'p99': float(np.percentile(data, 99))
                }
            }
        
        stats_dict = {}
        stats_dict.update(calculate_stats(baseline, 'baseline'))
        stats_dict.update(calculate_stats(ethics, 'ethics'))
        
        # Comparative statistics
        overhead = ethics - baseline
        stats_dict.update(calculate_stats(overhead, 'overhead'))
        
        # Percentage overhead
        pct_overhead = ((ethics - baseline) / baseline) * 100
        stats_dict['mean_percentage_overhead'] = float(np.mean(pct_overhead))
        stats_dict['median_percentage_overhead'] = float(np.median(pct_overhead))
        
        return stats_dict
    
    def _test_normality(self, baseline: np.ndarray, 
                       ethics: np.ndarray) -> Dict[str, Any]:
        """Test for normality using multiple methods"""
        
        results = {}
        
        # Shapiro-Wilk test
        baseline_shapiro = shapiro(baseline)
        ethics_shapiro = shapiro(ethics)
        
        results['shapiro_wilk'] = {
            'baseline': {
                'statistic': float(baseline_shapiro.statistic),
                'p_value': float(baseline_shapiro.pvalue),
                'is_normal': baseline_shapiro.pvalue > self.alpha
            },
            'ethics': {
                'statistic': float(ethics_shapiro.statistic),
                'p_value': float(ethics_shapiro.pvalue),
                'is_normal': ethics_shapiro.pvalue > self.alpha
            }
        }
        
        # D'Agostino's K-squared test
        baseline_dagostino = normaltest(baseline)
        ethics_dagostino = normaltest(ethics)
        
        results['dagostino'] = {
            'baseline': {
                'statistic': float(baseline_dagostino.statistic),
                'p_value': float(baseline_dagostino.pvalue),
                'is_normal': baseline_dagostino.pvalue > self.alpha
            },
            'ethics': {
                'statistic': float(ethics_dagostino.statistic),
                'p_value': float(ethics_dagostino.pvalue),
                'is_normal': ethics_dagostino.pvalue > self.alpha
            }
        }
        
        # Anderson-Darling test
        baseline_anderson = anderson(baseline)
        ethics_anderson = anderson(ethics)
        
        results['anderson_darling'] = {
            'baseline': {
                'statistic': float(baseline_anderson.statistic),
                'critical_values': baseline_anderson.critical_values.tolist(),
                'significance_levels': baseline_anderson.significance_level.tolist()
            },
            'ethics': {
                'statistic': float(ethics_anderson.statistic),
                'critical_values': ethics_anderson.critical_values.tolist(),
                'significance_levels': ethics_anderson.significance_level.tolist()
            }
        }
        
        # Overall normality assessment
        baseline_normal = (results['shapiro_wilk']['baseline']['is_normal'] and 
                          results['dagostino']['baseline']['is_normal'])
        ethics_normal = (results['shapiro_wilk']['ethics']['is_normal'] and 
                        results['dagostino']['ethics']['is_normal'])
        
        results['overall_assessment'] = {
            'baseline_is_normal': baseline_normal,
            'ethics_is_normal': ethics_normal,
            'both_normal': baseline_normal and ethics_normal
        }
        
        return results
    
    def _hypothesis_testing(self, baseline: np.ndarray, 
                           ethics: np.ndarray) -> Dict[str, Any]:
        """Perform appropriate hypothesis tests"""
        
        results = {}
        
        # Check if data is paired (same order of processing)
        is_paired = len(baseline) == len(ethics)
        
        # Parametric tests (if normal)
        if is_paired:
            # Paired t-test
            t_stat, p_value = ttest_rel(ethics, baseline)
            results['paired_t_test'] = {
                'statistic': float(t_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Significant difference' if p_value < self.alpha else 'No significant difference'
            }
        else:
            # Independent t-test (with Welch's correction for unequal variances)
            t_stat, p_value = ttest_ind(ethics, baseline, equal_var=False)
            results['welch_t_test'] = {
                'statistic': float(t_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Significant difference' if p_value < self.alpha else 'No significant difference'
            }
        
        # Non-parametric tests (always valid)
        if is_paired:
            # Wilcoxon signed-rank test
            w_stat, p_value = wilcoxon(ethics, baseline)
            results['wilcoxon_signed_rank'] = {
                'statistic': float(w_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Significant difference' if p_value < self.alpha else 'No significant difference'
            }
        else:
            # Mann-Whitney U test
            u_stat, p_value = mannwhitneyu(ethics, baseline, alternative='two-sided')
            results['mann_whitney_u'] = {
                'statistic': float(u_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Significant difference' if p_value < self.alpha else 'No significant difference'
            }
        
        # Permutation test (distribution-free)
        perm_result = self._permutation_test(baseline, ethics)
        results['permutation_test'] = perm_result
        
        # Bootstrap test
        boot_result = self._bootstrap_test(baseline, ethics)
        results['bootstrap_test'] = boot_result
        
        return results
    
    def _calculate_effect_sizes(self, baseline: np.ndarray, 
                               ethics: np.ndarray) -> Dict[str, float]:
        """Calculate various effect size measures"""
        
        # Cohen's d
        pooled_std = np.sqrt((np.var(baseline, ddof=1) + np.var(ethics, ddof=1)) / 2)
        cohens_d = (np.mean(ethics) - np.mean(baseline)) / pooled_std
        
        # Hedges' g (corrected Cohen's d for small samples)
        n1, n2 = len(baseline), len(ethics)
        correction_factor = 1 - (3 / (4 * (n1 + n2) - 9))
        hedges_g = cohens_d * correction_factor
        
        # Glass's delta (when variances are unequal)
        glass_delta = (np.mean(ethics) - np.mean(baseline)) / np.std(baseline, ddof=1)
        
        # Probability of superiority (non-parametric)
        prob_superiority = self._probability_of_superiority(baseline, ethics)
        
        # Cliff's delta (non-parametric effect size)
        cliffs_delta = self._cliffs_delta(baseline, ethics)
        
        # Interpret effect sizes
        def interpret_cohens_d(d):
            d = abs(d)
            if d < 0.2:
                return "negligible"
            elif d < 0.5:
                return "small"
            elif d < 0.8:
                return "medium"
            else:
                return "large"
        
        return {
            'cohens_d': {
                'value': float(cohens_d),
                'interpretation': interpret_cohens_d(cohens_d)
            },
            'hedges_g': {
                'value': float(hedges_g),
                'interpretation': interpret_cohens_d(hedges_g)
            },
            'glass_delta': float(glass_delta),
            'probability_of_superiority': float(prob_superiority),
            'cliffs_delta': {
                'value': float(cliffs_delta),
                'interpretation': self._interpret_cliffs_delta(cliffs_delta)
            }
        }
    
    def _calculate_confidence_intervals(self, baseline: np.ndarray, 
                                      ethics: np.ndarray) -> Dict[str, Any]:
        """Calculate confidence intervals for differences"""
        
        difference = ethics - baseline
        mean_diff = np.mean(difference)
        std_diff = np.std(difference, ddof=1)
        n = len(difference)
        
        # Parametric CI (t-distribution)
        t_critical = stats.t.ppf((1 + self.confidence_level) / 2, n - 1)
        margin_error = t_critical * std_diff / np.sqrt(n)
        
        parametric_ci = {
            'mean_difference': float(mean_diff),
            'lower': float(mean_diff - margin_error),
            'upper': float(mean_diff + margin_error),
            'margin_of_error': float(margin_error)
        }
        
        # Bootstrap CI (non-parametric)
        bootstrap_ci = self._bootstrap_confidence_interval(difference)
        
        # Percentile method CI
        percentile_ci = {
            'lower': float(np.percentile(difference, (1 - self.confidence_level) / 2 * 100)),
            'upper': float(np.percentile(difference, (1 + self.confidence_level) / 2 * 100))
        }
        
        return {
            'parametric': parametric_ci,
            'bootstrap': bootstrap_ci,
            'percentile': percentile_ci
        }
    
    def _power_analysis(self, baseline: np.ndarray, 
                       ethics: np.ndarray) -> Dict[str, float]:
        """Perform statistical power analysis"""
        
        # Calculate effect size
        effect_size = (np.mean(ethics) - np.mean(baseline)) / np.std(baseline, ddof=1)
        
        # Post-hoc power analysis
        power_analyzer = TTestPower()
        
        # Power for current sample size
        current_power = power_analyzer.solve_power(
            effect_size=abs(effect_size),
            nobs=len(baseline),
            alpha=self.alpha,
            power=None
        )
        
        # Required sample size for different power levels
        required_n_80 = power_analyzer.solve_power(
            effect_size=abs(effect_size),
            nobs=None,
            alpha=self.alpha,
            power=0.80
        )
        
        required_n_90 = power_analyzer.solve_power(
            effect_size=abs(effect_size),
            nobs=None,
            alpha=self.alpha,
            power=0.90
        )
        
        required_n_95 = power_analyzer.solve_power(
            effect_size=abs(effect_size),
            nobs=None,
            alpha=self.alpha,
            power=0.95
        )
        
        return {
            'current_power': float(current_power),
            'is_adequately_powered': current_power >= 0.80,
            'required_sample_sizes': {
                'power_80': int(np.ceil(required_n_80)) if required_n_80 else None,
                'power_90': int(np.ceil(required_n_90)) if required_n_90 else None,
                'power_95': int(np.ceil(required_n_95)) if required_n_95 else None
            },
            'effect_size_used': float(effect_size)
        }
    
    def _compare_distributions(self, baseline: np.ndarray, 
                             ethics: np.ndarray) -> Dict[str, Any]:
        """Compare full distributions using various methods"""
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_pvalue = stats.ks_2samp(baseline, ethics)
        
        # Anderson-Darling test
        ad_result = stats.anderson_ksamp([baseline, ethics])
        
        # Epps-Singleton test (for small samples)
        if len(baseline) < 50 and len(ethics) < 50:
            es_stat, es_pvalue = stats.epps_singleton_2samp(baseline, ethics)
            es_result = {
                'statistic': float(es_stat),
                'p_value': float(es_pvalue),
                'reject_null': es_pvalue < self.alpha
            }
        else:
            es_result = None
        
        # Energy distance test
        energy_distance = self._energy_distance(baseline, ethics)
        
        # Wasserstein distance
        wasserstein = stats.wasserstein_distance(baseline, ethics)
        
        return {
            'kolmogorov_smirnov': {
                'statistic': float(ks_stat),
                'p_value': float(ks_pvalue),
                'reject_null': ks_pvalue < self.alpha,
                'conclusion': 'Distributions differ' if ks_pvalue < self.alpha else 'Distributions similar'
            },
            'anderson_darling': {
                'statistic': float(ad_result.statistic),
                'critical_values': ad_result.critical_values.tolist(),
                'p_value': float(ad_result.pvalue) if ad_result.pvalue else None
            },
            'epps_singleton': es_result,
            'energy_distance': float(energy_distance),
            'wasserstein_distance': float(wasserstein)
        }
    
    def _permutation_test(self, baseline: np.ndarray, ethics: np.ndarray, 
                         n_permutations: int = 10000) -> Dict[str, Any]:
        """Perform permutation test for difference in means"""
        
        observed_diff = np.mean(ethics) - np.mean(baseline)
        combined = np.concatenate([baseline, ethics])
        n_baseline = len(baseline)
        
        permuted_diffs = []
        np.random.seed(42)  # For reproducibility
        
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_baseline = combined[:n_baseline]
            perm_ethics = combined[n_baseline:]
            permuted_diffs.append(np.mean(perm_ethics) - np.mean(perm_baseline))
        
        permuted_diffs = np.array(permuted_diffs)
        p_value = np.mean(np.abs(permuted_diffs) >= np.abs(observed_diff))
        
        return {
            'observed_difference': float(observed_diff),
            'p_value': float(p_value),
            'reject_null': p_value < self.alpha,
            'n_permutations': n_permutations,
            'null_distribution_mean': float(np.mean(permuted_diffs)),
            'null_distribution_std': float(np.std(permuted_diffs))
        }
    
    def _bootstrap_test(self, baseline: np.ndarray, ethics: np.ndarray,
                       n_bootstrap: int = 10000) -> Dict[str, Any]:
        """Perform bootstrap hypothesis test"""
        
        # Center the data (null hypothesis: no difference)
        baseline_centered = baseline - np.mean(baseline)
        ethics_centered = ethics - np.mean(ethics)
        combined_centered = np.concatenate([baseline_centered, ethics_centered])
        
        observed_diff = np.mean(ethics) - np.mean(baseline)
        n_baseline = len(baseline)
        
        bootstrap_diffs = []
        np.random.seed(42)
        
        for _ in range(n_bootstrap):
            # Resample from combined centered data
            boot_sample = np.random.choice(combined_centered, 
                                         size=len(combined_centered), 
                                         replace=True)
            boot_baseline = boot_sample[:n_baseline]
            boot_ethics = boot_sample[n_baseline:]
            bootstrap_diffs.append(np.mean(boot_ethics) - np.mean(boot_baseline))
        
        bootstrap_diffs = np.array(bootstrap_diffs)
        p_value = np.mean(np.abs(bootstrap_diffs) >= np.abs(observed_diff))
        
        return {
            'observed_difference': float(observed_diff),
            'p_value': float(p_value),
            'reject_null': p_value < self.alpha,
            'n_bootstrap': n_bootstrap
        }
    
    def _bootstrap_confidence_interval(self, data: np.ndarray,
                                     n_bootstrap: int = 10000) -> Dict[str, float]:
        """Calculate bootstrap confidence interval"""
        
        bootstrap_means = []
        np.random.seed(42)
        
        for _ in range(n_bootstrap):
            boot_sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(boot_sample))
        
        bootstrap_means = np.array(bootstrap_means)
        
        lower_percentile = (1 - self.confidence_level) / 2 * 100
        upper_percentile = (1 + self.confidence_level) / 2 * 100
        
        return {
            'mean': float(np.mean(bootstrap_means)),
            'lower': float(np.percentile(bootstrap_means, lower_percentile)),
            'upper': float(np.percentile(bootstrap_means, upper_percentile)),
            'std_error': float(np.std(bootstrap_means))
        }
    
    def _probability_of_superiority(self, baseline: np.ndarray, 
                                   ethics: np.ndarray) -> float:
        """Calculate probability that a random ethics value exceeds baseline"""
        count = 0
        for e in ethics:
            for b in baseline:
                if e > b:
                    count += 1
        return count / (len(ethics) * len(baseline))
    
    def _cliffs_delta(self, baseline: np.ndarray, ethics: np.ndarray) -> float:
        """Calculate Cliff's delta (non-parametric effect size)"""
        
        # Count dominance
        greater = 0
        less = 0
        
        for e in ethics:
            for b in baseline:
                if e > b:
                    greater += 1
                elif e < b:
                    less += 1
        
        n = len(ethics) * len(baseline)
        return (greater - less) / n
    
    def _interpret_cliffs_delta(self, delta: float) -> str:
        """Interpret Cliff's delta value"""
        abs_delta = abs(delta)
        if abs_delta < 0.147:
            return "negligible"
        elif abs_delta < 0.33:
            return "small"
        elif abs_delta < 0.474:
            return "medium"
        else:
            return "large"
    
    def _energy_distance(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate energy distance between two distributions"""
        
        # Simplified energy distance calculation
        n, m = len(x), len(y)
        
        # E[|X - Y|]
        xy_sum = 0
        for i in range(n):
            for j in range(m):
                xy_sum += abs(x[i] - y[j])
        e_xy = xy_sum / (n * m)
        
        # E[|X - X'|]
        xx_sum = 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    xx_sum += abs(x[i] - x[j])
        e_xx = xx_sum / (n * (n - 1)) if n > 1 else 0
        
        # E[|Y - Y'|]
        yy_sum = 0
        for i in range(m):
            for j in range(m):
                if i != j:
                    yy_sum += abs(y[i] - y[j])
        e_yy = yy_sum / (m * (m - 1)) if m > 1 else 0
        
        return 2 * e_xy - e_xx - e_yy
    
    def analyze_multiple_groups(self, groups: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze differences across multiple groups (e.g., different compositions)"""
        
        group_names = list(groups.keys())
        group_data = [np.array(groups[name]) for name in group_names]
        
        results = {}
        
        # ANOVA (if normal) or Kruskal-Wallis (non-parametric)
        normality_checks = [shapiro(data).pvalue > self.alpha for data in group_data]
        
        if all(normality_checks):
            # One-way ANOVA
            f_stat, p_value = f_oneway(*group_data)
            results['anova'] = {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Groups differ' if p_value < self.alpha else 'No significant difference'
            }
            
            # Post-hoc Tukey HSD
            if p_value < self.alpha:
                all_data = []
                all_groups = []
                for name, data in groups.items():
                    all_data.extend(data)
                    all_groups.extend([name] * len(data))
                
                tukey_result = pairwise_tukeyhsd(all_data, all_groups, alpha=self.alpha)
                results['tukey_hsd'] = {
                    'summary': str(tukey_result),
                    'reject': tukey_result.reject.tolist()
                }
        else:
            # Kruskal-Wallis test
            h_stat, p_value = kruskal(*group_data)
            results['kruskal_wallis'] = {
                'h_statistic': float(h_stat),
                'p_value': float(p_value),
                'reject_null': p_value < self.alpha,
                'conclusion': 'Groups differ' if p_value < self.alpha else 'No significant difference'
            }
            
            # Post-hoc Dunn test
            if p_value < self.alpha:
                results['dunn_test'] = self._dunn_test(groups)
        
        # Effect size (eta-squared for ANOVA)
        if 'anova' in results:
            grand_mean = np.mean(np.concatenate(group_data))
            ss_between = sum(len(data) * (np.mean(data) - grand_mean)**2 
                           for data in group_data)
            ss_total = sum(np.sum((data - grand_mean)**2) for data in group_data)
            eta_squared = ss_between / ss_total
            
            results['effect_size'] = {
                'eta_squared': float(eta_squared),
                'interpretation': self._interpret_eta_squared(eta_squared)
            }
        
        return results
    
    def _interpret_eta_squared(self, eta_squared: float) -> str:
        """Interpret eta-squared effect size"""
        if eta_squared < 0.01:
            return "negligible"
        elif eta_squared < 0.06:
            return "small"
        elif eta_squared < 0.14:
            return "medium"
        else:
            return "large"
    
    def _dunn_test(self, groups: Dict[str, List[float]]) -> Dict[str, Any]:
        """Simplified Dunn test for post-hoc analysis"""
        # This is a simplified version - for production use scikit-posthocs
        group_names = list(groups.keys())
        n_groups = len(group_names)
        
        comparisons = []
        for i in range(n_groups):
            for j in range(i+1, n_groups):
                u_stat, p_value = mannwhitneyu(
                    groups[group_names[i]], 
                    groups[group_names[j]]
                )
                
                # Bonferroni correction
                corrected_p = p_value * (n_groups * (n_groups - 1) / 2)
                
                comparisons.append({
                    'group1': group_names[i],
                    'group2': group_names[j],
                    'u_statistic': float(u_stat),
                    'p_value': float(p_value),
                    'corrected_p_value': float(min(corrected_p, 1.0)),
                    'significant': corrected_p < self.alpha
                })
        
        return {'comparisons': comparisons}
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable statistical report"""
        
        report = []
        report.append("STATISTICAL ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Descriptive statistics
        if 'descriptive' in results:
            desc = results['descriptive']
            report.append("\n1. DESCRIPTIVE STATISTICS")
            report.append("-" * 30)
            report.append(f"Baseline: Mean={desc['baseline_mean']:.2f}, "
                         f"SD={desc['baseline_std']:.2f}, "
                         f"Median={desc['baseline_median']:.2f}")
            report.append(f"Ethics: Mean={desc['ethics_mean']:.2f}, "
                         f"SD={desc['ethics_std']:.2f}, "
                         f"Median={desc['ethics_median']:.2f}")
            report.append(f"Mean Overhead: {desc['mean_percentage_overhead']:.1f}%")
        
        # Normality tests
        if 'normality' in results:
            norm = results['normality']
            report.append("\n2. NORMALITY ASSESSMENT")
            report.append("-" * 30)
            report.append(f"Baseline normality: {norm['overall_assessment']['baseline_is_normal']}")
            report.append(f"Ethics normality: {norm['overall_assessment']['ethics_is_normal']}")
        
        # Hypothesis tests
        if 'hypothesis_tests' in results:
            hyp = results['hypothesis_tests']
            report.append("\n3. HYPOTHESIS TESTING")
            report.append("-" * 30)
            
            # Find the most appropriate test
            if 'paired_t_test' in hyp:
                test = hyp['paired_t_test']
                report.append(f"Paired t-test: p={test['p_value']:.4f}, "
                             f"Conclusion: {test['conclusion']}")
            elif 'welch_t_test' in hyp:
                test = hyp['welch_t_test']
                report.append(f"Welch's t-test: p={test['p_value']:.4f}, "
                             f"Conclusion: {test['conclusion']}")
            
            if 'wilcoxon_signed_rank' in hyp:
                test = hyp['wilcoxon_signed_rank']
                report.append(f"Wilcoxon test: p={test['p_value']:.4f}, "
                             f"Conclusion: {test['conclusion']}")
            elif 'mann_whitney_u' in hyp:
                test = hyp['mann_whitney_u']
                report.append(f"Mann-Whitney U: p={test['p_value']:.4f}, "
                             f"Conclusion: {test['conclusion']}")
        
        # Effect sizes
        if 'effect_size' in results:
            eff = results['effect_size']
            report.append("\n4. EFFECT SIZES")
            report.append("-" * 30)
            report.append(f"Cohen's d: {eff['cohens_d']['value']:.3f} "
                         f"({eff['cohens_d']['interpretation']})")
            report.append(f"Probability of superiority: {eff['probability_of_superiority']:.3f}")
        
        # Confidence intervals
        if 'confidence_intervals' in results:
            ci = results['confidence_intervals']
            report.append("\n5. CONFIDENCE INTERVALS")
            report.append("-" * 30)
            report.append(f"Mean difference: {ci['parametric']['mean_difference']:.2f}")
            report.append(f"95% CI: [{ci['parametric']['lower']:.2f}, "
                         f"{ci['parametric']['upper']:.2f}]")
        
        # Power analysis
        if 'power_analysis' in results:
            pwr = results['power_analysis']
            report.append("\n6. POWER ANALYSIS")
            report.append("-" * 30)
            report.append(f"Statistical power: {pwr['current_power']:.3f}")
            report.append(f"Adequately powered: {pwr['is_adequately_powered']}")
        
        return "\n".join(report)


def analyze_experiment_results(results_path: str) -> None:
    """Analyze experiment results and generate statistical report"""
    
    import json
    
    # Load results
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Initialize analyzer
    analyzer = StatisticalAnalyzer()
    
    # Analyze baseline comparison
    if 'baseline_comparison' in results:
        baseline_latencies = results['baseline_comparison']['baseline_latencies']
        ethics_latencies = results['baseline_comparison']['ethics_latencies']
        
        analysis = analyzer.analyze_performance_comparison(
            baseline_latencies, ethics_latencies
        )
        
        # Generate report
        report = analyzer.generate_report(analysis)
        print(report)
        
        # Save detailed analysis
        with open('results/data/statistical_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        with open('results/data/statistical_report.txt', 'w') as f:
            f.write(report)
    
    # Analyze multiple groups (constraint compositions)
    if 'constraint_composition' in results:
        groups = {}
        for comp_name, comp_data in results['constraint_composition'].items():
            groups[comp_name] = comp_data['latencies']
        
        multi_analysis = analyzer.analyze_multiple_groups(groups)
        
        # Save analysis
        with open('results/data/composition_analysis.json', 'w') as f:
            json.dump(multi_analysis, f, indent=2)


if __name__ == "__main__":
    # Example usage
    analyze_experiment_results('results/data/experiment_results.json')