CiviQual Stats v2.0.0 — Sample Datasets
========================================

Every dataset is synthetic. Field names reference public-sector court
administration contexts so practitioners can orient quickly. Use these
datasets to explore tool behavior before applying CiviQual to operational
data.

Free-tier datasets
------------------
 01_case_processing_days.csv        Single-column continuous data for XmR,
                                    Descriptive Stats, Capability, Histogram.
 02_weekly_filing_volume.csv        Time-series count data for Run Chart.
 03_docketing_accuracy_pct.csv      Monthly accuracy series for control
                                    charting and trend tests.
 04_time_to_panel_days.csv          Single-column right-skewed data for
                                    probability plotting.
 05_oral_arg_lead_days.csv          Near-normal single-column data.
 06_filing_deficiencies_pareto.csv  Category/count pairs for Pareto analysis.
 07_subgroup_measurements.csv       Five-column subgroup data (use with
                                    Capability or a custom X-bar/R workflow).
 08_case_type_duration.csv          Grouped data for one-way ANOVA with
                                    Tukey HSD.
 09_workload_vs_closure.csv         Two columns for Correlation / Scatter.
 10_defect_proportion.csv           Sample size and defectives for p-chart
                                    workflows.
 11_complaints_per_week.csv         Count data for c-chart workflows.
 12_budget_variance_pct.csv         Mean-zero series for Run Chart and
                                    Control Chart Review.
 13_regional_case_duration.csv      Grouped data for Box Plot and ANOVA.
 14_quality_measurements.csv        Large-n single column for Histogram.
 15_capability_fill_weight.csv      Tightly-distributed data suitable for
                                    Capability (LSL = 9.9, USL = 10.2).
 16_raci_examples.csv               RACI worksheet seed values.

Pro-tier datasets
-----------------
 pro_01_gage_rr.csv                 Crossed Gage R&R: 10 parts x 3 operators
                                    x 3 replicates.
 pro_02_doe_factorial.csv           2^3 full factorial with two replicates.
 pro_03_regression.csv              Two predictors and a response for
                                    multiple regression.
 pro_04_two_sample_t.csv            Paired columns for two-sample hypothesis
                                    tests.
 pro_05_cusum_example.csv           Artificial process with a small shift at
                                    observation 31.
 pro_06_fmea_seed.csv               Starter FMEA rows for Planning Tools.
 pro_07_nonnormal_capability.csv    Lognormal data for Advanced Capability
                                    (Box-Cox transformation demonstrates
                                    normalization).

Usage notes
-----------
 - Load any file via File > Open Data.
 - For Capability workflows, set LSL and USL based on the dataset's scale
   (see file 15 above for suggested bounds).
 - For the CUSUM example, set target = 50 and sigma = 1.5 to reproduce the
   intended shift detection.
 - All files use standard comma-separated values with a single header row.
