"""
MLflow observability dashboard for the chatbot.
"""

import os

import mlflow
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from core.observability import ChatbotObserver
from core.utils import setup_logging

setup_logging()

st.set_page_config(page_title="Observability Dashboard", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    #MainMenu, footer, header, .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    body, .stApp, [data-testid="stAppViewContainer"] {
        background: #0a0a1a !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }

    h1, h2, h3, p, label, span, div {
        color: white !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 16px !important;
        background-clip: padding-box !important;
        box-shadow: inset 0 0 0 1px rgba(102, 126, 234, 0.4),
                    0 0 20px rgba(118, 75, 162, 0.15) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #a0a0c0 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    [data-testid="stTable"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stTable"] table {
        color: white !important;
    }

    .chunks-note {
        font-size: 12px;
        color: #a0a0c0 !important;
        margin-top: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Observability Dashboard")

if st.button("🔄 Refresh"):
    st.rerun()

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_runs")
mlflow.set_tracking_uri(tracking_uri)

observer = ChatbotObserver()
stats = observer.get_summary_stats()
runs_df = observer.get_runs_dataframe()


def build_line_chart(x_values, y_values, name, line_color, marker_color, y_title):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name=name,
            line=dict(color=line_color, width=2),
            marker=dict(size=8, color=marker_color),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.05)",
        font_color="white",
        xaxis=dict(title="Query Number", gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title=y_title, gridcolor="rgba(255,255,255,0.1)"),
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


def render_plotly_chart(fig: go.Figure, *, cdn_loaded: list[bool], height: int = 320) -> None:
    """Render Plotly via HTML/CDN — avoids Streamlit PlotlyChart.js load failures."""
    include_js = False if cdn_loaded[0] else "cdn"
    cdn_loaded[0] = True
    chart_html = fig.to_html(
        include_plotlyjs=include_js,
        full_html=False,
        config={"displayModeBar": False, "responsive": True},
    )
    components.html(
        f'<div style="width:100%;">{chart_html}</div>',
        height=height,
        scrolling=False,
    )


if stats.get("total_queries", 0) == 0 or runs_df is None or runs_df.empty:
    st.info("No queries logged yet. Start chatting to see metrics here.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", int(stats["total_queries"]))
    col2.metric("Avg Latency (ms)", f"{stats['avg_latency_ms']:.1f}")
    col3.metric("Avg Chunks Retrieved", f"{stats['avg_chunks_retrieved']:.1f}")
    if stats["avg_chunks_retrieved"] == 0.0:
        col3.markdown(
            '<p class="chunks-note">ℹ️ Chunks are retrieved after 2+ conversation turns</p>',
            unsafe_allow_html=True,
        )
    col4.metric("Avg Relevance Score", f"{stats['avg_relevance_score']:.2f}")

    plotly_cdn_loaded = [False]

    latency_data = runs_df["latency_ms"].tolist()
    latency_x = list(range(1, len(latency_data) + 1))

    st.subheader("Latency Over Time")
    render_plotly_chart(
        build_line_chart(
            latency_x,
            latency_data,
            "Latency (ms)",
            "#667eea",
            "#764ba2",
            "Latency (ms)",
        ),
        cdn_loaded=plotly_cdn_loaded,
    )

    response_length_data = runs_df["response_length"].tolist()
    response_x = list(range(1, len(response_length_data) + 1))

    st.subheader("Response Length Over Time")
    render_plotly_chart(
        build_line_chart(
            response_x,
            response_length_data,
            "Response Length",
            "#f093fb",
            "#f5576c",
            "Response Length",
        ),
        cdn_loaded=plotly_cdn_loaded,
    )

    st.subheader("Raw Runs")
    st.table(
        runs_df[["run_number", "latency_ms", "chunks_retrieved", "response_length", "relevance_score"]]
    )
