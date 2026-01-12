"""Offline RAG (Retrieval-Augmented Generation) system.
Uses sentence-transformers for embeddings and FAISS for vector search over a knowledge base
derived from the DataFrame and system outputs (EDA, AutoML, etc.).

Provides dataset-aware AI assistance without internet or API keys.
"""
# typing and numpy
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

# Do lazy imports for heavy optional libraries to avoid noisy import-time errors
SENTENCE_TRANSFORMERS_AVAILABLE = False
FAISS_AVAILABLE = False
SKLEARN_AVAILABLE = False
PD_AVAILABLE = False

try:
    import pandas as pd  # lightweight, usually available
    PD_AVAILABLE = True
except Exception:
    PD_AVAILABLE = False

# Detect sklearn availability lazily at import time
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

# Lightweight fallback if nothing is available
if not (SENTENCE_TRANSFORMERS_AVAILABLE and FAISS_AVAILABLE):
    if not SKLEARN_AVAILABLE:
        from collections import Counter
        import math

        class SimpleVectorizer:
            def __init__(self, max_features=2000):
                self.vocab = []
                self.max_features = max_features

            def fit_transform(self, docs):
                token_counts = Counter()
                tokenized = []
                for d in docs:
                    toks = [t.lower() for t in d.split() if t.strip()]
                    tokenized.append(toks)
                    token_counts.update(toks)
                most_common = [t for t, _ in token_counts.most_common(self.max_features)]
                self.vocab = most_common

                mat = []
                for toks in tokenized:
                    vec = [toks.count(term) for term in self.vocab]
                    mat.append(vec)
                return np.array(mat, dtype=float)

                def transform(self, docs):
                    mat = []
                    for d in docs:
                        toks = [t.lower() for t in d.split() if t.strip()]
                        vec = [toks.count(term) for term in self.vocab]
                        mat.append(vec)
                    return np.array(mat, dtype=float)

        def simple_cosine_similarity(a, b):
            # Convert potential sparse inputs to dense arrays
            try:
                if hasattr(a, 'toarray'):
                    a = a.toarray()
            except Exception:
                pass
            try:
                if hasattr(b, 'toarray'):
                    b = b.toarray()
            except Exception:
                pass

            a = np.asarray(a)
            b = np.asarray(b)

            # Ensure 1D query vector
            if a.ndim > 1:
                # Expect shape (1, n_features)
                a = a.reshape(a.shape[0], -1)
                if a.shape[0] == 1:
                    a = a.ravel()
                else:
                    # take first row if multiple
                    a = a[0].ravel()

            # Ensure 2D document matrix
            if b.ndim == 1:
                b = b.reshape(1, -1)

            a_norm = np.linalg.norm(a)
            b_norm = np.linalg.norm(b, axis=1)
            denom = a_norm * b_norm
            denom[denom == 0] = 1.0
            sims = (b @ a) / denom
            return sims.reshape(1, -1)


def _make_document_for_column(df: pd.DataFrame, col: str) -> str:
    """Create a short human-readable document for a single column."""
    s = df[col].dropna()
    n = len(df)
    non_null = s.shape[0]
    unique = s.nunique(dropna=True)
    preview = ', '.join([str(x) for x in s.head(5).tolist()])
    dtype = str(df[col].dtype)

    doc = f"Column: {col}\nType: {dtype}\nNon-null: {non_null}/{n}\nUnique: {unique}\nSample: {preview}"
    return doc


def build_corpus_from_df(df: pd.DataFrame, additional_knowledge: Optional[List[str]] = None) -> Tuple[List[str], List[str]]:
    """Return a list of documents and their source keys for the given DataFrame and additional knowledge."""
    docs = []
    keys = []

    # Column-level docs (enhanced)
    for c in df.columns:
        docs.append(_make_document_for_column(df, c))
        keys.append(f"column_{c}")

        # Add column-specific statistics for numeric columns
        if df[c].dtype in ['int64', 'float64']:
            col_stats = df[c].describe()
            stats_doc = f"Statistics for {c}: mean={col_stats['mean']:.2f}, std={col_stats['std']:.2f}, min={col_stats['min']}, max={col_stats['max']}"
            docs.append(stats_doc)
            keys.append(f"stats_{c}")

    # Row-level samples (up to 5 rows)
    nrows = min(5, len(df))
    for i in range(nrows):
        row = df.iloc[i].to_dict()
        preview = '; '.join([f"{k}: {v}" for k, v in row.items()])
        docs.append(f"Row {i+1}: {preview}")
        keys.append(f"row_{i+1}")

    # Dataset-level summary
    summary = f"Dataset has {len(df)} rows and {len(df.columns)} columns."
    if PD_AVAILABLE:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # Add data types information
        docs.append(f"Data Types: {len(numeric_cols)} numeric columns, {len(categorical_cols)} categorical columns")
        keys.append("data_types_summary")

        if len(numeric_cols) > 0:
            corr_matrix = df[numeric_cols].corr()
            # Top correlations
            corr_pairs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr = corr_matrix.iloc[i, j]
                    if abs(corr) > 0.3:  # Include moderate correlations too
                        corr_pairs.append(f"{numeric_cols[i]} and {numeric_cols[j]}: {corr:.2f}")
            if corr_pairs:
                summary += f" Significant correlations: {'; '.join(corr_pairs)}."
                # Add detailed correlation document
                docs.append(f"Correlations: {'; '.join(corr_pairs)}")
                keys.append("correlations")

        docs.append(f"Dataset Summary: {summary}")
        keys.append("dataset_summary")

        # Add data quality information
        missing_total = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()
        quality_doc = f"Data Quality: {missing_total} missing values, {duplicates} duplicate rows"
        docs.append(quality_doc)
        keys.append("data_quality")

        # Add size information
        size_doc = f"Dataset Size: {len(df)} rows, {len(df.columns)} columns, {len(df) * len(df.columns)} total cells"
        docs.append(size_doc)
        keys.append("dataset_size")

        # Add column list
        col_list = f"Columns: {', '.join(df.columns.tolist())}"
        docs.append(col_list)
        keys.append("column_list")

    # Additional knowledge from system outputs (EDA, AutoML, etc.)
    if additional_knowledge:
        for i, knowledge in enumerate(additional_knowledge):
            docs.append(knowledge)
            keys.append(f"system_knowledge_{i+1}")

    return docs, keys


class EmbeddingIndex:
    """Vector index using sentence-transformers and FAISS for efficient retrieval."""
    def __init__(self, docs: List[str]):
        self.docs = docs
        # Attempt to use sentence-transformers + faiss if available. Import lazily to
        # avoid noisy import-time failures on systems where faiss isn't compatible.
        try:
            # Lazy import with guarded stderr to reduce noisy native library traces
            import importlib, sys, contextlib, io
            try:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    st = importlib.import_module('sentence_transformers')
                    faiss = importlib.import_module('faiss')
                # If both imported, initialize embedding index
                SentenceTransformer = getattr(st, 'SentenceTransformer')
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                embeddings = self.model.encode(docs, convert_to_numpy=True)
                dim = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dim)
                self.index.add(embeddings)
                self._use_embeddings = True
            except Exception:
                # Embeddings not available; fall back to TF-IDF or simple vectorizer
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    from sklearn.metrics.pairwise import cosine_similarity
                    self.vectorizer = TfidfVectorizer(max_features=2000)
                    self.mat = self.vectorizer.fit_transform(docs)
                    self._use_embeddings = False
                except Exception:
                    self.vectorizer = SimpleVectorizer(max_features=2000)
                    self.mat = self.vectorizer.fit_transform(docs)
                    self._use_embeddings = False
        except Exception:
            # As a last resort, use the simple vectorizer
            self.vectorizer = SimpleVectorizer(max_features=2000)
            self.mat = self.vectorizer.fit_transform(docs)
            self._use_embeddings = False

    def query(self, q: str, top_k: int = 3) -> List[Tuple[int, float]]:
        if self._use_embeddings:
            query_embedding = self.model.encode([q], convert_to_numpy=True)
            distances, indices = self.index.search(query_embedding, top_k)
            results = [(int(idx), 1.0 / (1.0 + dist)) for idx, dist in zip(indices[0], distances[0])]  # Convert distance to similarity
        else:
            if hasattr(self, 'vectorizer'):
                qv = self.vectorizer.transform([q])
                if SKLEARN_AVAILABLE:
                    sims = cosine_similarity(qv, self.mat).ravel()
                else:
                    sims = simple_cosine_similarity(qv, self.mat).ravel()
                order = np.argsort(-sims)
                results = [(int(idx), float(sims[idx])) for idx in order[:top_k]]
            else:
                results = []
        return results


# Fallback index (renamed from SimpleIndex)
class FallbackIndex:
    def __init__(self, docs: List[str]):
        self.docs = docs
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=2000)
            self.mat = self.vectorizer.fit_transform(docs)
            self._use_sklearn = True
        else:
            self.vectorizer = SimpleVectorizer(max_features=2000)
            self.mat = self.vectorizer.fit_transform(docs)
            self._use_sklearn = False

    def query(self, q: str, top_k: int = 3) -> List[Tuple[int, float]]:
        if self._use_sklearn:
            qv = self.vectorizer.transform([q])
            sims = cosine_similarity(qv, self.mat).ravel()
        else:
            qv = self.vectorizer.transform([q])
            sims = simple_cosine_similarity(qv, self.mat).ravel()

        order = np.argsort(-sims)
        results = []
        for idx in order[:top_k]:
            results.append((int(idx), float(sims[idx])))
        return results


def _classify_query_type(prompt: str, df: Optional['pd.DataFrame'] = None) -> str:
    """Classify the type of query to provide appropriate responses."""
    prompt_lower = prompt.lower().strip()

    # Greetings - check first as they're common
    greeting_words = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'hii', 'hai']
    if any(word in prompt_lower for word in greeting_words) and len(prompt.split()) <= 3:
        return 'greeting'

    # Specific column questions - check for column names FIRST (most specific)
    if df is not None and hasattr(df, 'columns'):
        column_names = [col.lower() for col in df.columns]
    else:
        column_names = ['unnamed', 'years', 'experience', 'salary']

    for col in column_names:
        if col in prompt_lower:
            return 'specific_column'

    # Quality questions - check before overview since "tell me about data quality" should be quality
    quality_keywords = ['quality', 'missing', 'null', 'nan', 'clean', 'duplicates', 'outliers']
    if any(word in prompt_lower for word in quality_keywords):
        return 'quality'

    # Size/shape questions
    size_keywords = ['how many', 'size', 'shape', 'rows', 'records', 'entries', 'length']
    if any(word in prompt_lower for word in size_keywords):
        return 'size'

    # Data type questions
    if any(word in prompt_lower for word in ['type', 'types', 'datatype', 'data type']):
        return 'data_types'

    # Statistical questions
    stat_keywords = ['statistics', 'stats', 'mean', 'average', 'median', 'mode', 'std', 'deviation',
                    'variance', 'correlation', 'distribution', 'histogram', 'scatter', 'plot']
    if any(word in prompt_lower for word in stat_keywords):
        return 'statistics'

    # Analysis questions
    analysis_keywords = ['analyze', 'analysis', 'insights', 'patterns', 'trends', 'relationship',
                        'correlation', 'predict', 'forecast', 'model']
    if any(word in prompt_lower for word in analysis_keywords):
        return 'analysis'

    # Column-specific questions (general)
    column_keywords = ['column', 'feature', 'variable', 'field', 'attributes', 'fields',
                      'what columns', 'show columns', 'list columns', 'column names']
    if any(word in prompt_lower for word in column_keywords):
        return 'columns'

    # Comparison questions
    if any(word in prompt_lower for word in ['compare', 'comparison', 'vs', 'versus', 'difference']):
        return 'comparison'

    # Help questions
    help_keywords = ['help', 'how to', 'what can you', 'assist', 'commands', 'options']
    if any(word in prompt_lower for word in help_keywords):
        return 'help'

    # Dataset overview questions - check LAST (most general)
    overview_phrases = ['what is this data', 'tell me about', 'describe the data', 'overview', 'summary',
                       'what data', 'data about', 'dataset info', 'data overview']
    if any(phrase in prompt_lower for phrase in overview_phrases):
        return 'overview'

    return 'general'


def _generate_response_for_type(query_type: str, prompt: str, retrieved_docs: List[str], df: 'pd.DataFrame') -> str:
    """Generate appropriate response based on query type."""

    if query_type == 'greeting':
        return f"Hello! I'm your offline AI assistant for data analysis. I can help you understand your dataset, explore patterns, and answer questions about your data. Your dataset has {len(df)} rows and {len(df.columns)} columns. What would you like to know?"

    elif query_type == 'overview':
        summary = f"Your dataset contains {len(df)} rows and {len(df.columns)} columns. "
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if numeric_cols:
            summary += f"It has {len(numeric_cols)} numeric columns: {', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''}. "
        if categorical_cols:
            summary += f"It has {len(categorical_cols)} categorical columns: {', '.join(categorical_cols[:3])}{'...' if len(categorical_cols) > 3 else ''}. "

        return f"Dataset Overview:\n\n{summary}\n\nWould you like me to dive deeper into any specific aspect?"

    elif query_type == 'columns':
        # Extract column information from retrieved docs
        column_info = []
        for doc in retrieved_docs:
            if doc.startswith('Column:'):
                lines = doc.split('\n')
                col_name = lines[0].replace('Column: ', '')
                col_type = lines[1].replace('Type: ', '')
                col_stats = f"{lines[2]} | {lines[3]}"
                column_info.append(f"* {col_name} ({col_type}): {col_stats}")

        if column_info:
            return f"Column Information:\n\n" + "\n".join(column_info[:5]) + "\n\nI can provide more details about any specific column if you'd like!"
        else:
            # Fallback: list all columns directly
            all_cols = df.columns.tolist()
            return f"Your dataset has {len(all_cols)} columns: {', '.join(all_cols)}\n\nWould you like details about any specific column?"

    elif query_type == 'data_types':
        type_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            type_info.append(f"* {col}: {dtype} ({'has nulls' if null_count > 0 else 'no nulls'})")

        return f"Data Types in your dataset:\n\n" + "\n".join(type_info)

    elif query_type == 'statistics':
        stats_info = []
        for doc in retrieved_docs:
            if 'correlation' in doc.lower() or any(word in doc.lower() for word in ['mean', 'average', 'std', 'min', 'max']):
                stats_info.append(doc)

        if stats_info:
            return f"Statistical Insights:\n\n" + "\n\n".join(stats_info[:3]) + "\n\nWould you like me to run specific statistical analyses?"
        else:
            # Provide basic stats
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                basic_stats = df[numeric_cols].describe().round(2)
                return f"Basic Statistics for numeric columns:\n\n{basic_stats.to_string()}\n\nFor correlations and more advanced stats, try the Statistical Analysis section."
            else:
                return "Your dataset doesn't have numeric columns for statistical analysis."

    elif query_type == 'analysis':
        return f"Analysis Insights:\n\nBased on your dataset, here are some key findings:\n\n" + "\n\n".join(retrieved_docs[:3]) + "\n\nWould you like me to explore specific patterns or relationships in your data?"

    elif query_type == 'specific_column':
        # Try to identify which column the user is asking about
        prompt_lower = prompt.lower()
        target_col = None

        for col in df.columns:
            if col.lower() in prompt_lower:
                target_col = col
                break

        if target_col:
            col_data = df[target_col]
            dtype = str(col_data.dtype)
            non_null = col_data.notna().sum()
            total = len(col_data)
            unique = col_data.nunique()
            sample = col_data.dropna().head(3).tolist()

            response = f"Information about column '{target_col}':\n\n"
            response += f"* Data Type: {dtype}\n"
            response += f"* Non-null values: {non_null}/{total}\n"
            response += f"* Unique values: {unique}\n"
            response += f"* Sample values: {sample}\n\n"

            if col_data.dtype in ['int64', 'float64']:
                response += f"Statistics:\n"
                response += f"* Mean: {col_data.mean():.2f}\n"
                response += f"* Min: {col_data.min()}\n"
                response += f"* Max: {col_data.max()}\n"

            return response
        else:
            return "I couldn't identify which specific column you're asking about. Try mentioning the column name directly."

    elif query_type == 'size':
        return f"Dataset Size Information:\n\n* Total rows: {len(df)}\n* Total columns: {len(df.columns)}\n* Total cells: {len(df) * len(df.columns)}\n* Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB"

    elif query_type == 'quality':
        quality_report = []

        # Missing values
        missing = df.isnull().sum()
        total_missing = missing.sum()
        quality_report.append(f"Missing Values: {total_missing} total ({total_missing/(len(df)*len(df.columns))*100:.1f}%)")

        # Duplicates
        duplicates = df.duplicated().sum()
        quality_report.append(f"Duplicate Rows: {duplicates}")

        # Data types summary
        dtypes_count = df.dtypes.value_counts()
        quality_report.append(f"Data Types: {dict(dtypes_count)}")

        return f"Data Quality Report:\n\n" + "\n".join(f"* {item}" for item in quality_report)

    elif query_type == 'comparison':
        return "For data comparisons, I can help analyze relationships between columns. What specific comparison would you like to make?"

    elif query_type == 'help':
        return """How I Can Help:

* Data Overview: Get summaries of your dataset structure and contents
* Column Analysis: Understand individual features and their characteristics
* Statistical Insights: Explore distributions, correlations, and patterns
* Data Quality: Check for missing values, outliers, and data issues
* Data Types: See what types of data each column contains
* Size Information: Get row/column counts and memory usage
* Specific Columns: Ask about particular columns by name

Try asking me questions like:
- "What's in this dataset?"
- "Tell me about the salary column"
- "Are there any correlations?"
- "Show me the data quality"
- "What are the data types?"
- "How many rows are there?"

What would you like to explore?"""

    else:  # general query
        # For general queries, try to provide relevant information from retrieved docs
        if retrieved_docs:
            context = "\n\n".join(retrieved_docs[:2])  # Limit to top 2 results for brevity
            return f"Based on your dataset, here's what I found relevant to your question:\n\n{context}\n\nDoes this help answer your question? I can provide more specific information if you'd like!"
        else:
            return "I'm not sure how to answer that specific question. Try asking about the dataset overview, columns, statistics, or data quality. Or use the 'Help' option to see what I can assist with."


def _prioritize_documents_by_query_type(query_type: str, docs: List[str], keys: List[str], prompt: str) -> List[Tuple[int, float]]:
    """Prioritize documents based on query type and keyword matching."""
    prompt_lower = prompt.lower()
    prioritized_results = []

    # Define document type priorities for each query type
    type_priorities = {
        'columns': ['column_', 'column_list', 'data_types'],
        'data_types': ['data_types', 'data_types_summary', 'column_'],
        'statistics': ['stats_', 'correlations', 'dataset_summary'],
        'size': ['dataset_size', 'dataset_summary'],
        'quality': ['data_quality', 'dataset_summary'],
        'specific_column': ['column_', 'stats_'],
        'overview': ['dataset_summary', 'data_types_summary', 'column_list'],
        'analysis': ['correlations', 'stats_', 'dataset_summary']
    }

    # Get priority document types for this query
    priority_types = type_priorities.get(query_type, [])

    # Score documents based on relevance
    for i, (doc, key) in enumerate(zip(docs, keys)):
        score = 0.0

        # Priority bonus for document type
        for priority_type in priority_types:
            if priority_type in key:
                score += 2.0
                break

        # Keyword matching bonus
        doc_lower = doc.lower()
        prompt_words = set(prompt_lower.split())

        # Exact matches get highest score
        for word in prompt_words:
            if word in doc_lower:
                score += 1.0

        # Column name matches
        for col in ['unnamed', 'years', 'experience', 'salary']:
            if col in prompt_lower and col in doc_lower:
                score += 3.0

        # Specific keyword matches for better retrieval
        if 'correlation' in prompt_lower and 'correlations' in key:
            score += 4.0
        if 'quality' in prompt_lower and 'data_quality' in key:
            score += 4.0
        if 'size' in prompt_lower and 'dataset_size' in key:
            score += 4.0

        if score > 0:
            prioritized_results.append((i, score))

    # Sort by score (highest first) and return top results
    prioritized_results.sort(key=lambda x: x[1], reverse=True)
    return prioritized_results[:5]  # Return top 5 prioritized results


def offline_reply(prompt: str, df: Optional['pd.DataFrame'] = None, additional_knowledge: Optional[List[str]] = None, top_k: int = 3) -> str:
    """Return a helpful offline RAG-style reply given a prompt, DataFrame, and optional additional knowledge.

    Uses embeddings for retrieval when available, falls back to TF-IDF or simple methods.
    Generates intelligent, conversational answers based on retrieved context.
    """
    if (df is None) or (not PD_AVAILABLE) or (hasattr(df, 'empty') and df.empty):
        return (
            "Offline AI Assistant:\n\nI couldn't access your dataset to provide analysis. "
            "Please make sure you have data loaded in the application. "
            "For full AI responses with internet connectivity, ensure your API key is configured."
        )

    docs, keys = build_corpus_from_df(df, additional_knowledge)
    if not docs:
        return "Offline AI Assistant:\n\nI couldn't build a knowledge base from your dataset. Please check that your data is properly loaded."

    # Classify query first to help with retrieval
    query_type = _classify_query_type(prompt)

    # Try semantic search first
    try:
        idx = EmbeddingIndex(docs)
        semantic_results = idx.query(prompt, top_k=top_k*2)  # Get more results for reranking
    except Exception:
        try:
            idx = FallbackIndex(docs)
            semantic_results = idx.query(prompt, top_k=top_k*2)
        except Exception:
            semantic_results = []

    # Get prioritized results based on query type
    prioritized_results = _prioritize_documents_by_query_type(query_type, docs, keys, prompt)

    # Combine semantic and keyword-based results
    combined_results = []
    seen_indices = set()

    # Add prioritized results first (with higher weight)
    for idx, score in prioritized_results[:3]:
        if idx not in seen_indices:
            combined_results.append((idx, score * 1.5))  # Boost priority results
            seen_indices.add(idx)

    # Add semantic results (if not already included)
    for idx, score in semantic_results[:top_k]:
        if idx not in seen_indices:
            combined_results.append((idx, score))
            seen_indices.add(idx)

    # Sort by combined score
    combined_results.sort(key=lambda x: x[1], reverse=True)
    final_results = combined_results[:top_k]

    if not final_results:
        if query_type == 'greeting':
            return f"Hello! I'm your offline AI assistant for data analysis. Your dataset has {len(df)} rows and {len(df.columns)} columns. What would you like to know?"
        else:
            return f"Offline AI Assistant:\n\nI couldn't find specific information in your dataset to answer '{prompt}'. Try asking about:\n\n* Dataset overview or summary\n* Specific columns or features\n* Statistical patterns\n* Data quality issues\n\nOr use the other analysis tools in the application for visualizations and deeper insights."

    # Retrieve top passages
    retrieved = [docs[doc_idx] for doc_idx, _ in final_results]

    # Generate appropriate response
    response = _generate_response_for_type(query_type, prompt, retrieved, df)

    return f"Offline AI Assistant:\n\n{response}\n\nTip: For more advanced AI analysis, ensure your API key is set and try the online AI features."
