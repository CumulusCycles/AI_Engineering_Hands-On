"""
Streamlit UI for the LLM Pipeline Demo.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from umap import UMAP

from embeddings import tokenize, encode, get_embedding_stats
from search import get_product_count, search_products, get_all_embeddings, seed_products
import json
import os

st.set_page_config(page_title="LLM Pipeline Demo", layout="wide")

st.title("🔍 LLM Pipeline Demo")
st.markdown("Explore how semantic search works: tokenization → embeddings → similarity search")

# Sidebar for seeding
with st.sidebar:
    st.header("Vector Store")
    count = get_product_count()
    st.metric("Products in Store", count)
    
    if count == 0:
        if st.button("🌱 Seed Database"):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, "data", "seed_products.json")
            with open(data_file, 'r') as f:
                products = json.load(f)
            result = seed_products(products)
            st.success(f"Seeded {result['created']} products!")
            st.rerun()

    # Vector store visualization
    if count > 0:
        st.header("Vector Store Visualization")
        if st.button("📊 Show Embedding Space"):
            st.session_state.show_embeddings = True

# Main content
query = st.text_input("Enter your search query:", value="lightweight waterproof backpack for day hiking")

if st.button("🚀 Run Pipeline", type="primary") and query:
    
    col1, col2 = st.columns(2)

    with col1:
        # Step 1: Tokenization
        st.subheader("Step 1: Tokenization")
        with st.spinner("Tokenizing..."):
            token_result = tokenize(query)
        
        st.write(f"**Token count:** {token_result['token_count']}")

        # Token chips visualization
        token_html = " ".join([
            f'<span style="background-color: steelblue; color: white; padding: 4px 8px; margin: 2px; '
            f'border-radius: 4px; font-family: monospace; display: inline-block;">'
            f'{t["token"]} <sub style="color: #ccc;">({t["token_id"]})</sub></span>'
            for t in token_result['token_mapping']
        ])
        st.markdown(token_html, unsafe_allow_html=True)

    with col2:
        # Step 2: Embedding
        st.subheader("Step 2: Embedding")
        with st.spinner("Generating embedding..."):
            embedding = encode(query)
            stats = get_embedding_stats(embedding)
        
        # Key insight message
        st.info(f"Your query has been converted into a **{stats['dimension']}-dimensional vector**.")

        # Stats in columns
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Dimensions", stats['dimension'])
        with stat_col2:
            st.metric("Mean", f"{stats['mean']:.4f}")
        with stat_col3:
            st.metric("Std Dev", f"{stats['std']:.4f}")

        # Histogram showing distribution of embedding values
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=embedding,
            nbinsx=30,
            marker_color='steelblue',
            opacity=0.75,
            name='Value Distribution'
        ))
        fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Zero")
        fig.update_layout(
            title="Embedding Value Distribution",
            xaxis_title="Value",
            yaxis_title="Count",
            height=200,
            margin=dict(l=40, r=20, t=40, b=40),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Most values cluster near zero. Positive/negative values indicate semantic features.")

    # Step 3: Search Results
    st.subheader("Step 3: Similarity Search")
    with st.spinner("Searching..."):
        results = search_products(query, top_k=3)
    
    if not results:
        st.warning("No products found. Please seed the database first.")
    else:
        # Get top match embedding for comparison
        top_match = results[0]
        top_match_embedding = encode(top_match['description'])
        
        # Calculate cosine similarity for display
        query_arr = np.array(embedding)
        match_arr = np.array(top_match_embedding)
        cosine_sim = np.dot(query_arr, match_arr) / (np.linalg.norm(query_arr) * np.linalg.norm(match_arr))

        # Embedding comparison - overlay line chart
        st.write("**Embedding Comparison** - Query vs Top Match:")
        
        comp_col1, comp_col2 = st.columns([3, 1])

        with comp_col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=embedding,
                mode='lines',
                name='Query',
                line=dict(color='steelblue', width=1),
                opacity=0.8
            ))
            fig.add_trace(go.Scatter(
                y=top_match_embedding,
                mode='lines',
                name=top_match["name"][:20],
                line=dict(color='coral', width=1),
                opacity=0.8
            ))
            fig.update_layout(
                height=250,
                margin=dict(l=40, r=20, t=10, b=40),
                xaxis_title="Dimension",
                yaxis_title="Value",
                yaxis=dict(range=[-0.3, 0.3]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with comp_col2:
            st.metric("Cosine Similarity", f"{cosine_sim:.2%}")
            st.caption("Higher = more similar meaning")

            # Results bar chart
            df = pd.DataFrame(results)
            fig = px.bar(
                df,
                x='score',
                y='name',
                orientation='h',
                color='score',
                color_continuous_scale='Blues',
                title="Similarity Scores"
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Results details
            for r in results:
                with st.expander(f"**{r['name']}** - Score: {r['score']:.4f}"):
                    st.write(f"**Category:** {r['category']}")
                    st.write(f"**Price:** ${r['price']:.2f}" if r['price'] else "Price: N/A")
                    st.write(f"**Description:** {r['description']}")
                    if r['features']:
                        st.write(f"**Features:** {', '.join(r['features'])}")

# Vector store visualization
if st.session_state.get('show_embeddings', False):
    st.subheader("📊 Vector Store Embedding Space (2D UMAP)")
    
    with st.spinner("Computing 2D projection..."):
        data = get_all_embeddings()

        if len(data['embeddings']) > 0:
            embeddings = np.array(data['embeddings'])
            
            # UMAP reduction
            reducer = UMAP(n_components=2, random_state=42)
            coords = reducer.fit_transform(embeddings)
            
            # Create dataframe for plotting
            viz_df = pd.DataFrame({
                'x': coords[:, 0],
                'y': coords[:, 1],
                'name': data['names'],
                'category': data['categories']
            })
            
            # Scatter plot
            fig = px.scatter(
                viz_df,
                x='x',
                y='y',
                color='category',
                hover_name='name',
                title="Products in Embedding Space (similar items cluster together)",
                labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No products in vector store yet.")
