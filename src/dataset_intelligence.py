import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

from ui import section_header

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def detect_dataset_type(df):
    """
    Intelligent dataset type detection using multiple heuristics
    Returns: dict with dataset_type, confidence, and characteristics
    """
    detection_results = {
        'dataset_type': 'Unknown',
        'confidence': 0.0,
        'characteristics': {},
        'recommendations': []
    }

    # Get basic statistics
    n_rows, n_cols = df.shape
    dtypes = df.dtypes.value_counts()

    # TIME SERIES DETECTION
    ts_score = 0
    ts_characteristics = {}

    # Check for datetime columns
    datetime_cols = []
    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'object']:
            try:
                pd.to_datetime(df[col].dropna().head(10), errors='coerce')
                datetime_cols.append(col)
            except:
                pass

    if datetime_cols:
        ts_score += 30
        ts_characteristics['datetime_columns'] = datetime_cols

        # Check if datetime column could be index
        for dt_col in datetime_cols:
            try:
                temp_df = df.copy()
                temp_df[dt_col] = pd.to_datetime(temp_df[dt_col], errors='coerce')
                temp_df = temp_df.dropna(subset=[dt_col])

                # Check for sequential dates
                if len(temp_df) > 10:
                    date_range = pd.date_range(start=temp_df[dt_col].min(),
                                             end=temp_df[dt_col].max(),
                                             freq='D')
                    coverage = len(temp_df) / len(date_range) if len(date_range) > 0 else 0
                    if coverage > 0.5:
                        ts_score += 25
                        ts_characteristics['good_date_coverage'] = True
            except:
                pass

    # Check for temporal patterns in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0 and len(datetime_cols) > 0:
        # Look for autocorrelation patterns
        try:
            sample_col = numeric_cols[0]
            if len(df[sample_col].dropna()) > 20:
                from pandas.plotting import autocorrelation_plot
                # Simple autocorrelation check
                autocorr = df[sample_col].autocorr(lag=1)
                if abs(autocorr) > 0.3:  # Significant autocorrelation
                    ts_score += 20
                    ts_characteristics['autocorrelation_detected'] = True
        except:
            pass

    # NLP DETECTION
    nlp_score = 0
    nlp_characteristics = {}

    # Check for text columns
    text_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            sample_texts = df[col].dropna().head(20).astype(str)

            # Check average text length
            avg_length = sample_texts.str.len().mean()
            if avg_length > 50:  # Likely text content
                text_cols.append(col)
                nlp_score += 25

                # Check for sentence structure
                sentences = sample_texts.str.count(r'[.!?]')
                avg_sentences = sentences.mean()
                if avg_sentences > 1:
                    nlp_score += 15
                    nlp_characteristics['multi_sentence_texts'] = True

                # Check for common NLP patterns
                has_urls = sample_texts.str.contains(r'http[s]?://').any()
                has_emails = sample_texts.str.contains(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b').any()

                if has_urls or has_emails:
                    nlp_score += 10
                    nlp_characteristics['structured_text'] = True

    # Check for common NLP column names
    nlp_column_names = ['text', 'description', 'comment', 'review', 'message', 'content', 'body', 'title']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in nlp_column_names):
            nlp_score += 20
            nlp_characteristics['nlp_column_names'] = True

    # TABULAR/SUPERVISED LEARNING DETECTION
    tabular_score = 0
    tabular_characteristics = {}

    # Check for target-like columns
    potential_targets = []
    for col in df.columns:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio < 0.1:  # Low cardinality, could be target
            potential_targets.append(col)
        elif unique_ratio > 0.9 and df[col].dtype in ['object', 'category']:
            # High cardinality categorical - might need special handling
            tabular_characteristics['high_cardinality_categorical'] = True

    if potential_targets:
        tabular_score += 15
        tabular_characteristics['potential_targets'] = potential_targets

    # Check for feature-target relationships
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        high_correlations = (abs(corr_matrix) > 0.7).sum().sum() - len(corr_matrix)
        if high_correlations > 0:
            tabular_score += 10
            tabular_characteristics['feature_correlations'] = True

    # DETERMINE PRIMARY DATASET TYPE
    scores = {
        'Time Series': ts_score,
        'NLP': nlp_score,
        'Tabular': tabular_score
    }

    max_score = max(scores.values())
    primary_type = max(scores, key=scores.get)

    # Confidence calculation
    total_score = sum(scores.values())
    if total_score > 0:
        confidence = max_score / total_score
    else:
        confidence = 0.0

    # Set results
    detection_results['dataset_type'] = primary_type
    detection_results['confidence'] = confidence

    # Set characteristics based on type
    if primary_type == 'Time Series':
        detection_results['characteristics'] = ts_characteristics
        detection_results['recommendations'] = [
            "Use Time Series Analysis for trend decomposition and forecasting",
            "Consider seasonal patterns and stationarity tests",
            "Apply Prophet or ARIMA for forecasting"
        ]
    elif primary_type == 'NLP':
        detection_results['characteristics'] = nlp_characteristics
        detection_results['recommendations'] = [
            "Apply text preprocessing (tokenization, stopword removal)",
            "Use TF-IDF or word embeddings for feature extraction",
            "Consider sentiment analysis or text classification"
        ]
    else:  # Tabular
        detection_results['characteristics'] = tabular_characteristics
        detection_results['recommendations'] = [
            "Use traditional ML algorithms (Random Forest, XGBoost)",
            "Consider feature engineering and selection",
            "Apply standard preprocessing (scaling, encoding)"
        ]

    return detection_results

def apply_nlp_algorithms(df, text_column):
    """Apply NLP-specific algorithms and preprocessing"""
    results = {
        'preprocessing': {},
        'analysis': {},
        'models': {}
    }

    try:
        # Text Preprocessing
        texts = df[text_column].fillna('').astype(str)

        # Basic cleaning
        cleaned_texts = []
        for text in texts:
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            # Remove emails
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
            # Remove special characters but keep spaces
            text = re.sub(r'[^\w\s]', '', text)
            # Convert to lowercase
            text = text.lower()
            cleaned_texts.append(text)

        results['preprocessing']['cleaned_texts'] = cleaned_texts

        # Tokenization and stopword removal
        stop_words = set(stopwords.words('english'))
        tokenized_texts = []
        for text in cleaned_texts:
            tokens = word_tokenize(text)
            filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
            tokenized_texts.append(filtered_tokens)

        results['preprocessing']['tokenized_texts'] = tokenized_texts

        # TF-IDF Vectorization
        if len(cleaned_texts) > 10:
            vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()

            results['preprocessing']['tfidf_matrix'] = tfidf_matrix
            results['preprocessing']['feature_names'] = feature_names

            # Top words analysis
            word_counts = Counter()
            for tokens in tokenized_texts:
                word_counts.update(tokens)

            top_words = word_counts.most_common(20)
            results['analysis']['top_words'] = top_words

        # Sentiment Analysis
        try:
            sia = SentimentIntensityAnalyzer()
            sentiments = []

            for text in cleaned_texts:
                sentiment = sia.polarity_scores(text)
                sentiments.append(sentiment)

            results['analysis']['sentiment_scores'] = sentiments

            # Summary statistics
            compound_scores = [s['compound'] for s in sentiments]
            results['analysis']['sentiment_summary'] = {
                'positive': sum(1 for s in compound_scores if s > 0.05),
                'negative': sum(1 for s in compound_scores if s < -0.05),
                'neutral': sum(1 for s in compound_scores if -0.05 <= s <= 0.05),
                'avg_compound': np.mean(compound_scores)
            }

        except Exception as e:
            results['analysis']['sentiment_error'] = str(e)

        # Text Length Analysis
        text_lengths = [len(text.split()) for text in cleaned_texts]
        results['analysis']['text_statistics'] = {
            'avg_length': np.mean(text_lengths),
            'max_length': max(text_lengths),
            'min_length': min(text_lengths),
            'total_words': sum(text_lengths)
        }

    except Exception as e:
        results['error'] = str(e)

    return results

def apply_time_series_algorithms(df, date_column, value_column):
    """Apply time series specific algorithms and analysis"""
    results = {
        'preprocessing': {},
        'analysis': {},
        'forecasting': {}
    }

    try:
        # Prepare time series data
        ts_df = df.copy()
        ts_df[date_column] = pd.to_datetime(ts_df[date_column], errors='coerce')
        ts_df = ts_df.dropna(subset=[date_column, value_column])

        # Sort by date
        ts_df = ts_df.sort_values(date_column)
        ts_df = ts_df.set_index(date_column)

        # Handle missing values
        ts_df[value_column] = ts_df[value_column].fillna(method='ffill').fillna(method='bfill')

        results['preprocessing']['cleaned_data'] = ts_df
        results['preprocessing']['data_points'] = len(ts_df)

        # Basic time series statistics
        results['analysis']['basic_stats'] = {
            'mean': ts_df[value_column].mean(),
            'std': ts_df[value_column].std(),
            'min': ts_df[value_column].min(),
            'max': ts_df[value_column].max(),
            'trend': 'increasing' if ts_df[value_column].iloc[-1] > ts_df[value_column].iloc[0] else 'decreasing'
        }

        # Stationarity test
        try:
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(ts_df[value_column].values)
            results['analysis']['stationarity'] = {
                'adf_statistic': adf_result[0],
                'p_value': adf_result[1],
                'is_stationary': adf_result[1] < 0.05,
                'critical_values': adf_result[4]
            }
        except Exception as e:
            results['analysis']['stationarity_error'] = str(e)

        # Seasonal decomposition
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose

            # Auto-detect period
            freq = pd.infer_freq(ts_df.index)
            if freq:
                if 'D' in freq:
                    period = 7  # Weekly seasonality
                elif 'H' in freq:
                    period = 24  # Daily seasonality
                elif 'M' in freq:
                    period = 12  # Yearly seasonality
                else:
                    period = 7
            else:
                period = min(7, len(ts_df) // 3)

            decomposition = seasonal_decompose(ts_df[value_column], model='additive', period=period)
            results['analysis']['seasonal_decomposition'] = {
                'trend': decomposition.trend.dropna().tolist(),
                'seasonal': decomposition.seasonal.dropna().tolist(),
                'residual': decomposition.resid.dropna().tolist(),
                'period': period
            }

        except Exception as e:
            results['analysis']['decomposition_error'] = str(e)

        # Forecasting with simple models
        try:
            from statsmodels.tsa.arima.model import ARIMA

            # Simple ARIMA model
            if len(ts_df) > 20:
                model = ARIMA(ts_df[value_column], order=(1, 1, 1))
                model_fit = model.fit()

                # Forecast next 10 points
                forecast = model_fit.forecast(steps=10)
                forecast_index = pd.date_range(start=ts_df.index[-1],
                                             periods=11, freq='D')[1:]

                results['forecasting']['arima'] = {
                    'forecast_values': forecast.tolist(),
                    'forecast_index': forecast_index.tolist(),
                    'aic': model_fit.aic,
                    'bic': model_fit.bic
                }

        except Exception as e:
            results['forecasting']['arima_error'] = str(e)

        # Autocorrelation analysis
        try:
            from statsmodels.tsa.stattools import acf, pacf

            if len(ts_df) > 10:
                acf_values = acf(ts_df[value_column], nlags=min(20, len(ts_df)//2))
                pacf_values = pacf(ts_df[value_column], nlags=min(20, len(ts_df)//2))

                results['analysis']['autocorrelation'] = {
                    'acf': acf_values.tolist(),
                    'pacf': pacf_values.tolist()
                }

        except Exception as e:
            results['analysis']['autocorrelation_error'] = str(e)

    except Exception as e:
        results['error'] = str(e)

    return results

def show_dataset_intelligence(df):
    """Main interface for dataset intelligence and specialized algorithms"""
    section_header("🧠 Dataset Intelligence", "AI-powered dataset type detection and specialized algorithms")

    # Dataset Type Detection
    with st.expander("🔍 Dataset Type Detection", expanded=True):
        if st.button("Analyze Dataset Type", key="detect_type"):
            with st.spinner("Analyzing dataset characteristics..."):
                detection = detect_dataset_type(df)

                col1, col2 = st.columns([1, 2])

                with col1:
                    st.metric("Detected Type", detection['dataset_type'])
                    st.metric("Confidence", f"{detection['confidence']:.2%}")

                with col2:
                    st.write("**Characteristics:**")
                    for key, value in detection['characteristics'].items():
                        st.write(f"- {key}: {value}")

                    st.write("**Recommendations:**")
                    for rec in detection['recommendations']:
                        st.write(f"💡 {rec}")

                # Store detection results
                st.session_state.dataset_detection = detection

    # Specialized Analysis based on detected type
    if 'dataset_detection' in st.session_state:
        detection = st.session_state.dataset_detection

        if detection['dataset_type'] == 'NLP':
            show_nlp_analysis(df)
        elif detection['dataset_type'] == 'Time Series':
            show_time_series_analysis(df)
        else:
            show_tabular_analysis(df)

def show_nlp_analysis(df):
    """NLP-specific analysis interface"""
    st.markdown("---")
    with st.expander("📝 Natural Language Processing Analysis", expanded=True):

        # Find text columns
        text_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_texts = df[col].dropna().head(10).astype(str)
                avg_length = sample_texts.str.len().mean()
                if avg_length > 20:  # Likely text content
                    text_cols.append(col)

        if not text_cols:
            st.warning("No suitable text columns found for NLP analysis.")
            return

        text_column = st.selectbox("Select Text Column for Analysis", text_cols, key="nlp_text_col")

        if st.button("Run NLP Analysis", key="nlp_analyze"):
            with st.spinner("Performing NLP analysis..."):
                nlp_results = apply_nlp_algorithms(df, text_column)

                if 'error' in nlp_results:
                    st.error(f"NLP Analysis failed: {nlp_results['error']}")
                    return

                # Display results
                tab1, tab2, tab3 = st.tabs(["📊 Text Statistics", "🔤 Word Analysis", "😊 Sentiment Analysis"])

                with tab1:
                    st.subheader("Text Statistics")
                    stats = nlp_results['analysis']['text_statistics']
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Average Length", f"{stats['avg_length']:.1f} words")
                    with col2:
                        st.metric("Max Length", f"{stats['max_length']} words")
                    with col3:
                        st.metric("Min Length", f"{stats['min_length']} words")
                    with col4:
                        st.metric("Total Words", f"{stats['total_words']:,}")

                with tab2:
                    st.subheader("Top Words Analysis")
                    if 'top_words' in nlp_results['analysis']:
                        top_words = nlp_results['analysis']['top_words']

                        # Create dataframe for display
                        words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                        st.dataframe(words_df)

                        # Word cloud visualization (simple bar chart)
                        st.bar_chart(words_df.set_index('Word').head(15))

                with tab3:
                    st.subheader("Sentiment Analysis")
                    if 'sentiment_summary' in nlp_results['analysis']:
                        sentiment = nlp_results['analysis']['sentiment_summary']

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Positive", sentiment['positive'])
                        with col2:
                            st.metric("Negative", sentiment['negative'])
                        with col3:
                            st.metric("Neutral", sentiment['neutral'])
                        with col4:
                            st.metric("Avg Sentiment", f"{sentiment['avg_compound']:.3f}")

                        # Sentiment distribution
                        sentiment_data = pd.DataFrame({
                            'Sentiment': ['Positive', 'Negative', 'Neutral'],
                            'Count': [sentiment['positive'], sentiment['negative'], sentiment['neutral']]
                        })
                        st.bar_chart(sentiment_data.set_index('Sentiment'))

def show_time_series_analysis(df):
    """Time series specific analysis interface"""
    st.markdown("---")
    with st.expander("📈 Time Series Analysis", expanded=True):

        # Find datetime and numeric columns
        datetime_cols = []
        for col in df.columns:
            if df[col].dtype in ['datetime64[ns]', 'object']:
                try:
                    pd.to_datetime(df[col].dropna().head(5), errors='coerce')
                    datetime_cols.append(col)
                except:
                    pass

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not datetime_cols or not numeric_cols:
            st.warning("Need both datetime and numeric columns for time series analysis.")
            return

        col1, col2 = st.columns(2)

        with col1:
            date_column = st.selectbox("Select Date Column", datetime_cols, key="ts_date_col")

        with col2:
            value_column = st.selectbox("Select Value Column", numeric_cols, key="ts_value_col")

        if st.button("Run Time Series Analysis", key="ts_analyze"):
            with st.spinner("Performing time series analysis..."):
                ts_results = apply_time_series_algorithms(df, date_column, value_column)

                if 'error' in ts_results:
                    st.error(f"Time Series Analysis failed: {ts_results['error']}")
                    return

                # Display results
                tab1, tab2, tab3 = st.tabs(["📊 Basic Analysis", "🔄 Decomposition", "🔮 Forecasting"])

                with tab1:
                    st.subheader("Basic Time Series Statistics")

                    stats = ts_results['analysis']['basic_stats']
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Mean", f"{stats['mean']:.2f}")
                    with col2:
                        st.metric("Std Dev", f"{stats['std']:.2f}")
                    with col3:
                        st.metric("Min", f"{stats['min']:.2f}")
                    with col4:
                        st.metric("Max", f"{stats['max']:.2f}")

                    # Stationarity test
                    if 'stationarity' in ts_results['analysis']:
                        st.subheader("Stationarity Test (Augmented Dickey-Fuller)")
                        stationarity = ts_results['analysis']['stationarity']

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("ADF Statistic", f"{stationarity['adf_statistic']:.4f}")
                            st.metric("p-value", f"{stationarity['p_value']:.4f}")

                        with col2:
                            status = "✅ Stationary" if stationarity['is_stationary'] else "❌ Non-stationary"
                            st.metric("Result", status)

                with tab2:
                    st.subheader("Seasonal Decomposition")
                    if 'seasonal_decomposition' in ts_results['analysis']:
                        decomp = ts_results['analysis']['seasonal_decomposition']

                        st.write(f"**Detected Period:** {decomp['period']}")

                        # Simple trend visualization
                        if len(decomp['trend']) > 0:
                            trend_data = pd.DataFrame({
                                'Trend': decomp['trend'][:min(50, len(decomp['trend']))]  # Show first 50 points
                            })
                            st.line_chart(trend_data)

                with tab3:
                    st.subheader("ARIMA Forecasting")
                    if 'arima' in ts_results['forecasting']:
                        forecast = ts_results['forecasting']['arima']

                        st.write(f"**Model Performance:** AIC={forecast['aic']:.2f}, BIC={forecast['bic']:.2f}")

                        # Display forecast values
                        forecast_df = pd.DataFrame({
                            'Date': forecast['forecast_index'][:10],  # Show first 10 forecasts
                            'Forecast': forecast['forecast_values'][:10]
                        })
                        st.dataframe(forecast_df)

                        # Simple forecast plot
                        st.line_chart(forecast_df.set_index('Date'))

def show_tabular_analysis(df):
    """Standard tabular data analysis interface"""
    st.markdown("---")
    with st.expander("📊 Tabular Data Analysis", expanded=True):
        st.info("This appears to be standard tabular data. Use the existing AutoML and Feature Engineering tools for analysis.")

        # Quick dataset summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            st.metric("Numeric Features", numeric_cols)

        # Suggest next steps
        st.markdown("**Recommended Next Steps:**")
        st.markdown("1. 🧹 Use **Smart Cleaning** for data preprocessing")
        st.markdown("2. ⚙️ Use **Auto Feature Engineering** for feature creation")
        st.markdown("3. 🤖 Use **AutoML (Supervised)** for model training")
        st.markdown("4. 📊 Use **Data Quality & Anomalies** for outlier detection")