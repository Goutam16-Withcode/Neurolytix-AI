import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.weightstats import ztest
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split, KFold
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
try:
    from ui import section_header
except ImportError:
    def section_header(title, subtitle=None):
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
import warnings
warnings.filterwarnings('ignore')

def show_statistical_testing(df):
    section_header("Statistical Testing & Inference", "A/B Testing, Causal Inference, and Bayesian Statistics for data-driven decisions.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Create tabs for different statistical methods
    tab1, tab2, tab3 = st.tabs(["🅰️ A/B Testing Framework", "🔗 Causal Inference", "🎲 Bayesian Statistics"])

    with tab1:
        show_ab_testing(df)

    with tab2:
        show_causal_inference(df)

    with tab3:
        show_bayesian_statistics(df)

def show_ab_testing(df):
    """A/B Testing Framework with statistical significance testing."""
    st.subheader("A/B Testing Framework")

    # Test type selection
    test_type = st.selectbox("Test Type",
                           ["Proportion Test (Conversion Rates)", "Mean Test (Continuous Metrics)", "Power Analysis"],
                           key="ab_test_type")

    if test_type == "Proportion Test (Conversion Rates)":
        show_proportion_test(df)
    elif test_type == "Mean Test (Continuous Metrics)":
        show_mean_test(df)
    else:
        show_power_analysis()

def show_proportion_test(df):
    """Proportion-based A/B testing for conversion rates."""
    st.write("**Proportion Test (e.g., Conversion Rates, Click-through Rates)**")

    # Select columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        group_col = st.selectbox("Group Column (A/B groups)", categorical_cols + numeric_cols, key="group_col")
        if not group_col:
            return

    with col2:
        success_col = st.selectbox("Success Metric (0/1)", numeric_cols, key="success_col")
        if not success_col:
            return

    # Parameters
    confidence_level = st.slider("Confidence Level", 0.8, 0.99, 0.95, key="conf_level")
    alternative = st.selectbox("Alternative Hypothesis", ["two-sided", "larger", "smaller"], key="alternative")

    if st.button("Run A/B Test", key="run_ab_test"):
        try:
            # Prepare data
            test_data = df[[group_col, success_col]].dropna()

            # Get unique groups
            groups = test_data[group_col].unique()
            if len(groups) != 2:
                st.error("A/B testing requires exactly 2 groups.")
                return

            group_a, group_b = groups[0], groups[1]

            # Calculate proportions
            a_data = test_data[test_data[group_col] == group_a][success_col]
            b_data = test_data[test_data[group_col] == group_b][success_col]

            a_successes = a_data.sum()
            b_successes = b_data.sum()
            a_total = len(a_data)
            b_total = len(b_data)

            a_rate = a_successes / a_total
            b_rate = b_successes / b_total

            # Statistical test
            successes = np.array([a_successes, b_successes])
            totals = np.array([a_total, b_total])

            z_stat, p_value = proportions_ztest(successes, totals, alternative=alternative)

            # Effect size (relative difference)
            relative_diff = (b_rate - a_rate) / a_rate if a_rate > 0 else 0

            # Confidence interval
            se = np.sqrt(a_rate*(1-a_rate)/a_total + b_rate*(1-b_rate)/b_total)
            z_critical = stats.norm.ppf(1 - (1 - confidence_level)/2)
            ci_lower = (b_rate - a_rate) - z_critical * se
            ci_upper = (b_rate - a_rate) + z_critical * se

            # Display results
            st.success("A/B Test completed!")

            # Results summary
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(f"Group {group_a} Conversion", f"{a_rate:.3%}", f"n={a_total}")
            with col2:
                st.metric(f"Group {group_b} Conversion", f"{b_rate:.3%}", f"n={b_total}")
            with col3:
                st.metric("Relative Difference", f"{relative_diff:.1%}")

            # Statistical significance
            st.subheader("📊 Statistical Significance")

            sig_level = "Significant" if p_value < (1 - confidence_level) else "Not Significant"
            sig_color = "green" if p_value < (1 - confidence_level) else "red"

            st.write(f"**Result: {sig_color}**")
            st.write(f"**P-Value:** {p_value:.4f}")
            st.write(f"**Z-Statistic:** {z_stat:.4f}")
            st.write(f"**Confidence Interval ({confidence_level:.0%}):** [{ci_lower:.4f}, {ci_upper:.4f}]")

            # Visualization
            st.subheader("📈 Conversion Rate Comparison")

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Bar chart
            groups_names = [f'Group {group_a}', f'Group {group_b}']
            rates = [a_rate, b_rate]
            ax1.bar(groups_names, rates, color=['skyblue', 'lightgreen'])
            ax1.set_ylabel('Conversion Rate')
            ax1.set_title('Conversion Rates by Group')
            for i, v in enumerate(rates):
                ax1.text(i, v + 0.01, '.1%', ha='center')

            # Confidence interval plot
            ax2.errorbar(['Difference'], [b_rate - a_rate], yerr=[[b_rate - a_rate - ci_lower], [ci_upper - (b_rate - a_rate)]],
                        fmt='o', capsize=5, color='purple')
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax2.set_title('Difference with Confidence Interval')
            ax2.set_ylabel('Rate Difference')

            st.pyplot(fig)

            # Sample size recommendations
            if p_value >= (1 - confidence_level):
                st.subheader("💡 Sample Size Recommendations")
                st.info("The test was not statistically significant. Consider increasing sample size for more reliable results.")

                # Calculate required sample size
                effect_size = abs(relative_diff) if relative_diff != 0 else 0.1
                analysis = TTestIndPower()
                sample_size = analysis.solve_power(effect_size=effect_size, power=0.8, alpha=1-confidence_level)
                st.write(f"**Recommended sample size per group:** {int(sample_size)}")

        except Exception as e:
            st.error(f"A/B test failed: {str(e)}")

def show_mean_test(df):
    """Mean comparison testing for continuous metrics."""
    st.write("**Mean Test (e.g., Revenue, Time Spent, Engagement Scores)**")

    # Select columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        group_col = st.selectbox("Group Column", categorical_cols + numeric_cols, key="mean_group_col")
    with col2:
        metric_col = st.selectbox("Metric Column", numeric_cols, key="metric_col")

    if group_col and metric_col:
        # Parameters
        equal_var = st.checkbox("Assume equal variances", value=True, key="equal_var")
        alternative = st.selectbox("Alternative", ["two-sided", "less", "greater"], key="mean_alternative")

        if st.button("Run Mean Test", key="run_mean_test"):
            try:
                test_data = df[[group_col, metric_col]].dropna()
                groups = test_data[group_col].unique()

                if len(groups) != 2:
                    st.error("Mean testing requires exactly 2 groups.")
                    return

                group_a, group_b = groups[0], groups[1]
                a_data = test_data[test_data[group_col] == group_a][metric_col]
                b_data = test_data[test_data[group_col] == group_b][metric_col]

                # Statistical test
                if equal_var:
                    t_stat, p_value = stats.ttest_ind(a_data, b_data, alternative=alternative)
                    test_name = "Student's t-test"
                else:
                    t_stat, p_value = stats.ttest_ind(a_data, b_data, equal_var=False, alternative=alternative)
                    test_name = "Welch's t-test"

                # Effect size (Cohen's d)
                mean_diff = b_data.mean() - a_data.mean()
                pooled_std = np.sqrt((a_data.var() * len(a_data) + b_data.var() * len(b_data)) / (len(a_data) + len(b_data)))
                cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

                # Display results
                st.success("Mean comparison test completed!")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(f"Group {group_a} Mean", f"{a_data.mean():.3f}", f"n={len(a_data)}")
                with col2:
                    st.metric(f"Group {group_b} Mean", f"{b_data.mean():.3f}", f"n={len(b_data)}")
                with col3:
                    st.metric("Mean Difference", f"{mean_diff:.3f}")
                with col4:
                    st.metric("Effect Size (Cohen's d)", f"{cohens_d:.3f}")

                st.write(f"**Test:** {test_name}")
                st.write(f"**T-Statistic:** {t_stat:.4f}")
                st.write(f"**P-Value:** {p_value:.4f}")
                # Visualization
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

                # Box plot
                data_to_plot = [a_data, b_data]
                ax1.boxplot(data_to_plot, labels=[f'Group {group_a}', f'Group {group_b}'])
                ax1.set_ylabel(metric_col)
                ax1.set_title('Distribution Comparison')

                # Effect size interpretation
                effect_sizes = {'Very small': 0.01, 'Small': 0.2, 'Medium': 0.5, 'Large': 0.8, 'Very large': 1.2}
                colors = ['lightgray', 'lightblue', 'lightgreen', 'orange', 'red']

                for i, (label, threshold) in enumerate(effect_sizes.items()):
                    if abs(cohens_d) >= threshold:
                        color = colors[i]
                        break
                else:
                    color = 'lightgray'

                ax2.bar(['Effect Size'], [abs(cohens_d)], color=color, alpha=0.7)
                ax2.axhline(y=0.2, color='blue', linestyle='--', alpha=0.7, label='Small (0.2)')
                ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, label='Medium (0.5)')
                ax2.axhline(y=0.8, color='orange', linestyle='--', alpha=0.7, label='Large (0.8)')
                ax2.set_title('Effect Size Magnitude')
                ax2.legend()

                st.pyplot(fig)

            except Exception as e:
                st.error(f"Mean test failed: {str(e)}")

def show_power_analysis():
    """Statistical power analysis for experiment planning."""
    st.write("**Power Analysis (Plan Your Experiments)**")

    # Parameters
    effect_size = st.slider("Expected Effect Size", 0.1, 1.0, 0.3, key="effect_size")
    alpha = st.slider("Significance Level (α)", 0.01, 0.1, 0.05, key="alpha")
    power = st.slider("Desired Power (1-β)", 0.7, 0.95, 0.8, key="power")

    # Calculate sample size
    analysis = TTestIndPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)

    st.success("Power analysis completed!")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Effect Size", f"{effect_size:.2f}")
    with col2:
        st.metric("Significance (α)", f"{alpha:.3f}")
    with col3:
        st.metric("Power (1-β)", f"{power:.2f}")
    with col4:
        st.metric("Sample Size per Group", f"{int(sample_size)}")

    # Power curve visualization
    st.subheader("📊 Power Analysis Curve")

    fig, ax = plt.subplots(figsize=(10, 6))

    sample_sizes = np.arange(10, 200, 5)
    powers = [analysis.solve_power(effect_size=effect_size, nobs1=ss, alpha=alpha) for ss in sample_sizes]

    ax.plot(sample_sizes, powers, 'b-', linewidth=2, label='Power Curve')
    ax.axhline(y=power, color='red', linestyle='--', alpha=0.7, label=f'Target Power ({power:.2f})')
    ax.axvline(x=sample_size, color='green', linestyle='--', alpha=0.7, label=f'Required Sample Size ({int(sample_size)})')

    ax.set_xlabel('Sample Size per Group')
    ax.set_ylabel('Statistical Power')
    ax.set_title('Power vs Sample Size')
    ax.grid(True, alpha=0.3)
    ax.legend()

    st.pyplot(fig)

def show_causal_inference(df):
    """Causal inference methods and analysis."""
    st.subheader("Causal Inference")

    method = st.selectbox("Causal Inference Method",
                         ["Regression Adjustment", "Propensity Score Matching", "Difference-in-Differences"],
                         key="causal_method")

    if method == "Regression Adjustment":
        show_regression_adjustment(df)
    elif method == "Propensity Score Matching":
        show_propensity_matching(df)
    else:
        show_difference_in_differences(df)

def show_regression_adjustment(df):
    """Regression-based causal inference."""
    st.write("**Regression Adjustment (Control for Confounding Variables)**")

    # Select variables
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2, col3 = st.columns(3)

    with col1:
        treatment_col = st.selectbox("Treatment Variable", categorical_cols + numeric_cols, key="treatment_var")
    with col2:
        outcome_col = st.selectbox("Outcome Variable", numeric_cols, key="outcome_var")
    with col3:
        control_vars = st.multiselect("Control Variables", [col for col in numeric_cols if col not in [outcome_col]], key="control_vars")

    if treatment_col and outcome_col and st.button("Estimate Causal Effect", key="run_regression"):
        try:
            # Prepare data
            analysis_data = df[[treatment_col, outcome_col] + control_vars].dropna()

            # Convert treatment to numeric if categorical
            if analysis_data[treatment_col].dtype == 'object':
                treatment_dummies = pd.get_dummies(analysis_data[treatment_col], prefix='treatment', drop_first=True)
                analysis_data = pd.concat([analysis_data.drop(treatment_col, axis=1), treatment_dummies], axis=1)
                treatment_cols = treatment_dummies.columns.tolist()
            else:
                treatment_cols = [treatment_col]

            # Fit regression model
            X = analysis_data[treatment_cols + control_vars]
            X = sm.add_constant(X)
            y = analysis_data[outcome_col]

            model = sm.OLS(y, X).fit()

            # Display results
            st.success("Causal effect estimation completed!")

            st.subheader("📊 Regression Results")
            st.text(model.summary())

            # Causal effect interpretation
            st.subheader("🎯 Causal Effect Interpretation")

            for i, treatment in enumerate(treatment_cols):
                coef = model.params[treatment]
                p_val = model.pvalues[treatment]
                conf_int = model.conf_int().loc[treatment]

                st.write(f"**Treatment Effect ({treatment}):**")
                st.write(f"**Coefficient:** {coef:.4f}")
                st.write(f"**P-Value:** {p_val:.4f}")
                st.write(f"**95% CI:** [{conf_int[0]:.4f}, {conf_int[1]:.4f}]")

                if p_val < 0.05:
                    st.success("✅ Statistically significant effect!")
                else:
                    st.warning("⚠️ Effect not statistically significant.")

        except Exception as e:
            st.error(f"Causal inference failed: {str(e)}")

def show_propensity_matching(df):
    """Propensity score matching for causal inference."""
    st.write("**Propensity Score Matching (Balance Treatment Groups)**")

    st.info("This method matches treated and control units based on their probability of receiving treatment.")

    # This is a simplified implementation - in practice, you'd use libraries like causalinference or pscore
    st.warning("Propensity score matching requires specialized libraries. This is a conceptual demonstration.")

    # Show conceptual approach
    st.subheader("📚 Conceptual Approach")

    st.markdown("""
    **Steps for Propensity Score Matching:**

    1. **Estimate Propensity Scores**: Use logistic regression to predict treatment probability
    2. **Match Units**: Pair treated and control units with similar propensity scores
    3. **Check Balance**: Ensure covariates are balanced between matched groups
    4. **Estimate Effect**: Compare outcomes between matched treated and control groups

    **Advantages:**
    - Reduces confounding bias
    - Creates comparable treatment and control groups
    - Works with observational data

    **Limitations:**
    - Requires good overlap in propensity scores
    - Cannot control for unmeasured confounding
    - Matching quality depends on model specification
    """)

def show_difference_in_differences(df):
    """Difference-in-differences analysis."""
    st.write("**Difference-in-Differences (DiD) Analysis**")

    st.info("DiD compares the before-after difference in treatment vs control groups to estimate causal effects.")

    # This would require time-series panel data structure
    st.warning("DiD analysis requires panel data with time periods. This is a conceptual demonstration.")

    st.subheader("📚 DiD Methodology")

    st.markdown("""
    **DiD Formula:**
    ```
    Causal Effect = (Treated_Post - Treated_Pre) - (Control_Post - Control_Pre)
    ```

    **Assumptions:**
    - Parallel trends: Treatment and control groups would have followed parallel paths without intervention
    - No spillover effects between groups
    - Treatment timing is consistent

    **Applications:**
    - Policy evaluation
    - Marketing campaign analysis
    - Natural experiment analysis
    """)

def show_bayesian_statistics(df):
    """Bayesian statistical analysis."""
    st.subheader("Bayesian Statistics")

    method = st.selectbox("Bayesian Method",
                         ["Bayesian A/B Testing", "Bayesian Regression", "MCMC Sampling Demo"],
                         key="bayesian_method")

    if method == "Bayesian A/B Testing":
        show_bayesian_ab_testing(df)
    elif method == "Bayesian Regression":
        show_bayesian_regression(df)
    else:
        show_mcmc_demo()

def show_bayesian_ab_testing(df):
    """Bayesian A/B testing with beta-binomial model."""
    st.write("**Bayesian A/B Testing (Beta-Binomial Model)**")

    # Select data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        group_col = st.selectbox("Group Column", categorical_cols, key="bayes_group")
    with col2:
        success_col = st.selectbox("Success Metric", numeric_cols, key="bayes_success")

    if group_col and success_col and st.button("Run Bayesian A/B Test", key="run_bayes_ab"):
        try:
            test_data = df[[group_col, success_col]].dropna()
            groups = test_data[group_col].unique()

            if len(groups) != 2:
                st.error("Bayesian A/B testing requires exactly 2 groups.")
                return

            group_a, group_b = groups[0], groups[1]

            # Calculate beta parameters (successes + 1, failures + 1)
            a_data = test_data[test_data[group_col] == group_a][success_col]
            b_data = test_data[test_data[group_col] == group_b][success_col]

            a_successes = a_data.sum()
            b_successes = b_data.sum()
            a_total = len(a_data)
            b_total = len(b_data)

            # Beta distribution parameters
            a_alpha, a_beta = a_successes + 1, (a_total - a_successes) + 1
            b_alpha, b_beta = b_successes + 1, (b_total - b_successes) + 1

            # Posterior means and credible intervals
            a_mean = a_alpha / (a_alpha + a_beta)
            b_mean = b_alpha / (b_alpha + b_beta)

            # 95% credible intervals using beta distribution
            a_lower = stats.beta.ppf(0.025, a_alpha, a_beta)
            a_upper = stats.beta.ppf(0.975, a_alpha, a_beta)
            b_lower = stats.beta.ppf(0.025, b_alpha, b_beta)
            b_upper = stats.beta.ppf(0.975, b_alpha, b_beta)

            # Probability that B is better than A
            # This requires numerical integration - simplified approximation
            prob_b_better = 1 - stats.beta.cdf(a_mean, b_alpha, b_beta)

            # Display results
            st.success("Bayesian A/B test completed!")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(f"Group {group_a} Rate", f"{a_mean:.3f}", f"95% CI: [{a_lower:.3f}, {a_upper:.3f}]")
            with col2:
                st.metric(f"Group {group_b} Rate", f"{b_mean:.3f}", f"95% CI: [{b_lower:.3f}, {b_upper:.3f}]")
            with col3:
                st.metric("P(B > A)", f"{prob_b_better:.3f}")

            # Visualization
            st.subheader("📊 Posterior Distributions")

            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot beta distributions
            x = np.linspace(0, 1, 1000)
            a_pdf = stats.beta.pdf(x, a_alpha, a_beta)
            b_pdf = stats.beta.pdf(x, b_alpha, b_beta)

            ax.plot(x, a_pdf, 'b-', label=f'Group {group_a} (α={a_alpha:.1f}, β={a_beta:.1f})', linewidth=2)
            ax.plot(x, b_pdf, 'r-', label=f'Group {group_b} (α={b_alpha:.1f}, β={b_beta:.1f})', linewidth=2)

            ax.set_xlabel('Conversion Rate')
            ax.set_ylabel('Density')
            ax.set_title('Posterior Distributions')
            ax.legend()
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)

            # Interpretation
            st.subheader("🎯 Bayesian Interpretation")

            if prob_b_better > 0.95:
                st.success("🎉 Strong evidence that Group B performs better!")
            elif prob_b_better > 0.8:
                st.info("👍 Moderate evidence that Group B performs better.")
            elif prob_b_better < 0.05:
                st.success("🎉 Strong evidence that Group A performs better!")
            elif prob_b_better < 0.2:
                st.info("👍 Moderate evidence that Group A performs better.")
            else:
                st.warning("🤔 No clear winner - more data needed.")

        except Exception as e:
            st.error(f"Bayesian A/B test failed: {str(e)}")

def show_bayesian_regression(df):
    """Bayesian linear regression."""
    st.write("**Bayesian Linear Regression**")

    st.info("Bayesian regression provides uncertainty estimates for coefficients and predictions.")

    # This would require pymc3 or similar - showing conceptual approach
    st.warning("Full Bayesian regression requires specialized libraries. This is a conceptual demonstration.")

    st.subheader("📚 Bayesian Regression Concepts")

    st.markdown("""
    **Bayesian Linear Regression:**

    **Model:**
    ```
    y = Xβ + ε, ε ~ N(0, σ²)
    β ~ N(μ₀, Σ₀)  [prior]
    σ² ~ InvGamma(α, β)  [prior]
    ```

    **Advantages:**
    - Provides uncertainty estimates for coefficients
    - Incorporates prior knowledge
    - Handles small datasets better
    - Provides credible intervals instead of confidence intervals

    **Posterior Inference:**
    - MCMC sampling (e.g., Metropolis-Hastings, Gibbs)
    - Variational inference
    - Laplace approximation
    """)

def show_mcmc_demo():
    """Simple MCMC sampling demonstration."""
    st.write("**MCMC Sampling Demonstration**")

    st.info("Markov Chain Monte Carlo (MCMC) is used to sample from complex probability distributions.")

    # Simple Metropolis-Hastings for normal distribution
    if st.button("Run MCMC Demo", key="run_mcmc"):
        try:
            # Target distribution: Normal(5, 2)
            def target_density(x):
                return stats.norm.pdf(x, loc=5, scale=2)

            # Metropolis-Hastings algorithm
            n_samples = 5000
            samples = []
            current = 0  # Starting point

            for i in range(n_samples):
                # Propose new value
                proposal = current + np.random.normal(0, 1)

                # Acceptance ratio
                acceptance_ratio = target_density(proposal) / target_density(current)

                # Accept or reject
                if np.random.random() < acceptance_ratio:
                    current = proposal

                samples.append(current)

            # Burn-in period
            burn_in = 1000
            samples = samples[burn_in:]

            # Display results
            st.success("MCMC sampling completed!")

            # Visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Trace plot
            ax1.plot(samples[:500], alpha=0.7)
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Sample Value')
            ax1.set_title('MCMC Trace Plot (First 500 samples)')
            ax1.grid(True, alpha=0.3)

            # Histogram vs target
            x_range = np.linspace(-5, 15, 1000)
            target_pdf = stats.norm.pdf(x_range, loc=5, scale=2)

            ax2.hist(samples, bins=50, density=True, alpha=0.7, label='MCMC Samples')
            ax2.plot(x_range, target_pdf, 'r-', linewidth=2, label='Target Distribution')
            ax2.set_xlabel('Value')
            ax2.set_ylabel('Density')
            ax2.set_title('Sample Distribution vs Target')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            st.pyplot(fig)

            # Statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Sample Mean", f"{np.mean(samples):.3f}")
            with col2:
                st.metric("Sample Std", f"{np.std(samples):.3f}")
            with col3:
                st.metric("Effective Sample Size", f"{len(samples)}")

            st.info("The MCMC samples should approximate the target Normal(5, 2) distribution!")

        except Exception as e:
            st.error(f"MCMC demo failed: {str(e)}")

def show_baseline_significance_checks(df):
    """Standalone Baseline & Significance Checks for model evaluation."""
    section_header("Baseline & Significance Checks", "Evaluate model performance against baselines and assess statistical significance.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Allow user to select target column
    target_col = st.selectbox("Select Target Variable", df.columns, key="baseline_target")

    # Allow user to select features (exclude target)
    feature_cols = [col for col in df.columns if col != target_col]
    selected_features = st.multiselect("Select Feature Columns", feature_cols,
                                     default=feature_cols[:min(5, len(feature_cols))],
                                     key="baseline_features")

    if not selected_features:
        st.warning("Please select at least one feature column.")
        return

    # Prepare data
    try:
        X = df[selected_features].copy()
        y = df[target_col].copy()

        # Handle missing values
        X = X.fillna(X.mean(numeric_only=True))
        y = y.fillna(y.mode().iloc[0] if y.dtype == 'object' else y.mean())

        # Encode categorical target if needed
        if y.dtype == 'object':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            is_classification = True
        else:
            y_encoded = y
            is_classification = y.nunique() < 20  # Heuristic for classification

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded if is_classification else None)

        # Train a simple model (Random Forest)
        if is_classification:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            scoring = 'accuracy'
        else:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            scoring = 'r2'

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Calculate model performance
        if is_classification:
            model_score = accuracy_score(y_test, y_pred)
        else:
            model_score = r2_score(y_test, y_pred)

        st.markdown('### 🔬 Baseline & Significance Checks')

        # Majority-class baseline (for classification)
        if is_classification:
            majority_acc = pd.Series(y_test).value_counts(normalize=True).max()
            unique_labels = pd.Series(y_test).unique().tolist()
            n_classes = len(unique_labels)
            random_acc = 1.0 / n_classes if n_classes > 0 else 0.0
        else:
            majority_acc = None
            random_acc = None

        # Cross-validated accuracy
        try:
            from sklearn.model_selection import StratifiedKFold, cross_val_score
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42) if is_classification else KFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, X, y_encoded, cv=cv, scoring=scoring)
            cv_mean = float(cv_scores.mean())
            cv_std = float(cv_scores.std())
        except Exception:
            cv_mean = None
            cv_std = None

        # Permutation test
        perm_pvalue = None
        perm_score = None
        try:
            from sklearn.model_selection import permutation_test_score
            n_perms = 100 if len(X_test) > 50 else 500
            score, perm_scores, pvalue = permutation_test_score(model, X_test, y_test, scoring=scoring, n_permutations=min(n_perms, 500), random_state=42)
            perm_score = float(score)
            perm_pvalue = float(pvalue)
        except Exception:
            perm_pvalue = None
            perm_score = None

        # Display results
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Model Score", f"{model_score:.3f}")
            if cv_mean is not None:
                st.metric("CV Mean Score", f"{cv_mean:.3f} ± {cv_std:.3f}")

        with col2:
            if is_classification:
                st.metric("Majority Class Baseline", f"{majority_acc:.3f}")
                st.metric("Random Baseline", f"{random_acc:.3f}")
            else:
                st.metric("Null Model (Mean)", "N/A for regression")

        with col3:
            if perm_pvalue is not None:
                st.metric("Permutation p-value", f"{perm_pvalue:.4f}")
                significance = "Significant" if perm_pvalue < 0.05 else "Not Significant"
                st.metric("Statistical Significance", significance)
            else:
                st.metric("Permutation Test", "Failed")

        # Interpretation
        st.markdown("### 📊 Interpretation")
        if is_classification:
            st.write(f"- **Model Performance**: {model_score:.3f}")
            st.write(f"- **Majority Class Baseline**: {majority_acc:.3f} (predicting the most common class)")
            st.write(f"- **Random Baseline**: {random_acc:.3f} (random guessing)")
            if model_score > majority_acc:
                st.success("✅ Model performs better than majority class baseline!")
            else:
                st.warning("⚠️ Model does not outperform majority class baseline.")
        else:
            st.write(f"- **Model Performance (R²)**: {model_score:.3f}")
            st.write("- For regression, compare against domain-specific baselines.")

        if perm_pvalue is not None:
            if perm_pvalue < 0.05:
                st.success("✅ Model performance is statistically significant (p < 0.05)")
            else:
                st.warning("⚠️ Model performance is not statistically significant (p ≥ 0.05)")

        if cv_mean is not None:
            st.info(f"Cross-validation provides robust estimate: {cv_mean:.3f} ± {cv_std:.3f}")

    except Exception as e:
        st.error(f"Error in baseline checks: {str(e)}")
        import traceback
        st.code(traceback.format_exc())