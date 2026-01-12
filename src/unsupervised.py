import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import plotly.express as px
from ui import section_header, apply_neuro_theme

def show_unsupervised(df):
    section_header("Unsupervised Learning", "Discover hidden patterns and clusters.")
    
    # Select Numerical Columns only
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numerical columns for unsupervised learning.")
        return

    selected_cols = st.multiselect("Select Features for Analysis", numeric_cols, default=numeric_cols[:5])
    
    if not selected_cols:
        return

    X = df[selected_cols].dropna()
    
    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    tab1, tab2, tab3 = st.tabs(["Clustering", "Dimensionality Reduction", "Anomaly Detection"])
    
    with tab1:
        st.subheader("Clustering")
        algo = st.selectbox("Select Algorithm", ["K-Means", "DBSCAN", "Hierarchical Clustering"])
        
        if algo == "K-Means":
            k = st.slider("Number of Clusters (K)", 2, 10, 3)
            if st.button("Run K-Means"):
                model = KMeans(n_clusters=k, random_state=42)
                clusters = model.fit_predict(X_scaled)
                X['Cluster'] = clusters.astype(str)
                
                # Metrics
                sil = silhouette_score(X_scaled, clusters)
                db = davies_bouldin_score(X_scaled, clusters)
                c1, c2 = st.columns(2)
                c1.metric("Silhouette Score (High is good)", f"{sil:.4f}")
                c2.metric("Davies-Bouldin (Low is good)", f"{db:.4f}")
                
                # Visualize (2D PCA for plot)
                pca = PCA(n_components=2)
                components = pca.fit_transform(X_scaled)
                fig = px.scatter(x=components[:,0], y=components[:,1], color=X['Cluster'], 
                               title=f"K-Means Clusters (PCA Projection)", labels={'x':'PC1', 'y':'PC2'})
                st.plotly_chart(apply_neuro_theme(fig), use_container_width=True, theme=None)
                
        elif algo == "DBSCAN":
            eps = st.slider("Epsilon (eps)", 0.1, 5.0, 0.5)
            min_samples = st.slider("Min Samples", 2, 20, 5)
            if st.button("Run DBSCAN"):
                model = DBSCAN(eps=eps, min_samples=min_samples)
                clusters = model.fit_predict(X_scaled)
                X['Cluster'] = clusters.astype(str)
                
                # Check if valid clusters exist (> 1 cluster + noise)
                if len(set(clusters)) > 1:
                    sil = silhouette_score(X_scaled, clusters)
                    db = davies_bouldin_score(X_scaled, clusters)
                    c1, c2 = st.columns(2)
                    c1.metric("Silhouette Score", f"{sil:.4f}")
                    c2.metric("Davies-Bouldin", f"{db:.4f}")
                else:
                    st.warning("Not enough clusters found to calculate metrics.")
                
                # Visualize
                pca = PCA(n_components=2)
                components = pca.fit_transform(X_scaled)
                fig = px.scatter(x=components[:,0], y=components[:,1], color=X['Cluster'], 
                               title=f"DBSCAN Clusters (PCA Projection)", labels={'x':'PC1', 'y':'PC2'})
                st.plotly_chart(apply_neuro_theme(fig), use_container_width=True, theme=None)

        elif algo == "Hierarchical Clustering":
            k = st.slider("Number of Clusters", 2, 10, 3)
            if st.button("Run Hierarchical"):
                model = AgglomerativeClustering(n_clusters=k)
                clusters = model.fit_predict(X_scaled)
                X['Cluster'] = clusters.astype(str)
                
                pca = PCA(n_components=2)
                components = pca.fit_transform(X_scaled)
                fig = px.scatter(x=components[:,0], y=components[:,1], color=X['Cluster'],
                               title=f"Hierarchical Clusters (PCA Projection)", labels={'x':'PC1', 'y':'PC2'})
                st.plotly_chart(apply_neuro_theme(fig), use_container_width=True, theme=None)
                
    with tab2:
        st.subheader("Dimensionality Reduction")
        method = st.radio("Method", ["PCA", "t-SNE"])
        dims = st.radio("Dimensions", [2, 3])
        
        if st.button("Run Projection"):
            if method == "PCA":
                model = PCA(n_components=dims)
                components = model.fit_transform(X_scaled)
                var_ratio = model.explained_variance_ratio_
                st.info(f"Explained Variance Ratio: {var_ratio}")
            else: # t-SNE
                model = TSNE(n_components=dims, random_state=42)
                components = model.fit_transform(X_scaled)
            
            if dims == 2:
                fig = px.scatter(x=components[:,0], y=components[:,1], title=f"{method} 2D Projection")
            else:
                fig = px.scatter_3d(x=components[:,0], y=components[:,1], z=components[:,2], title=f"{method} 3D Projection")
            
            st.plotly_chart(fig, use_container_width=True)
            
    with tab3:
        st.subheader("Anomaly Detection")
        st.caption("Identify outliers using Isolation Forest.")
        contamination = st.slider("Contamination (Expected % of outliers)", 0.01, 0.5, 0.05)
        
        if st.button("Detect Anomalies"):
            model = IsolationForest(contamination=contamination, random_state=42)
            preds = model.fit_predict(X_scaled)
            # 1 for inliers, -1 for outliers
            X['Anomaly'] = np.where(preds == -1, 'Outlier', 'Normal')
            
            st.warning(f"Detected {len(X[X['Anomaly']=='Outlier'])} outliers out of {len(X)} records.")
            
            pca = PCA(n_components=2)
            components = pca.fit_transform(X_scaled)
            fig = px.scatter(x=components[:,0], y=components[:,1], color=X['Anomaly'],
                           color_discrete_map={'Normal': 'blue', 'Outlier': 'red'},
                           title="Anomaly Detection (PCA Projection)")
            st.plotly_chart(fig, use_container_width=True)
