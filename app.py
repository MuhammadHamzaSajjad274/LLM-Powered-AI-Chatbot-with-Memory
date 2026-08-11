"""
Streamlit UI for the LLM-Powered AI Chatbot with Long-Term Memory.
Stunning animated glassmorphism interface with RAG pipeline backend.
"""

import html
import textwrap
from datetime import datetime

import streamlit as st
import os
from main import ChatbotPipeline



# Bridge Streamlit Cloud secrets to environment variables
if hasattr(st, 'secrets'):
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ[key] = value
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

body, .stApp, [data-testid="stAppViewContainer"] {
    background: #0a0a1a !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d2b 0%, #1a1a3e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] * { color: #e8e8f0 !important; }

[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 30px !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: white !important;
    border: none !important;
}

[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border-radius: 50% !important;
    border: none !important;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    33% { transform: translateY(-20px) rotate(5deg); }
    66% { transform: translateY(-10px) rotate(-3deg); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes orb {
    0% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -30px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
    100% { transform: translate(0, 0) scale(1); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

@keyframes typingDot {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-8px); opacity: 1; }
}

/* Landing page */
.landing-screen {
    position: relative;
    min-height: 92vh;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.landing-bg {
    position: absolute;
    inset: 0;
    background: linear-gradient(-45deg, #0a0a1a, #1a0a2e, #0a1a2e, #2e0a1a);
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
    z-index: 0;
}

.landing-orb {
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
    z-index: 1;
}

.landing-orb-1 {
    width: 300px; height: 300px;
    top: 8%; left: 5%;
    background: radial-gradient(circle, #667eea, transparent);
    filter: blur(60px);
    opacity: 0.4;
    animation: orb 8s ease-in-out infinite;
}

.landing-orb-2 {
    width: 250px; height: 250px;
    top: 35%; right: 8%;
    background: radial-gradient(circle, #f093fb, transparent);
    filter: blur(50px);
    opacity: 0.3;
    animation: orb 10s ease-in-out infinite reverse;
}

.landing-orb-3 {
    width: 200px; height: 200px;
    bottom: 10%; left: 12%;
    background: radial-gradient(circle, #4facfe, transparent);
    filter: blur(40px);
    opacity: 0.35;
    animation: orb 12s ease-in-out infinite 2s;
}

.landing-particles {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 2;
}

.landing-particle {
    position: absolute;
    border-radius: 50%;
    animation: float ease-in-out infinite;
}

.landing-content {
    position: relative;
    z-index: 3;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
}

.landing-title {
    font-size: 72px;
    font-weight: 800;
    margin: 0 0 16px 0;
    background: linear-gradient(135deg, #667eea, #f093fb, #4facfe);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: gradientShift 3s ease infinite, fadeInUp 1s ease;
}

.landing-subtitle {
    color: rgba(255,255,255,0.6);
    font-size: 18px;
    margin-bottom: 48px;
    animation: fadeInUp 1s ease 0.3s both;
}

.feature-row {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    justify-content: center;
    margin-bottom: 48px;
}

.feature-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 30px;
    width: 200px;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-6px);
    border-color: rgba(255,255,255,0.2);
    box-shadow: 0 20px 40px rgba(102,126,234,0.2);
}

.feature-card-1 { animation: fadeInUp 1s ease 0.5s both; }
.feature-card-2 { animation: fadeInUp 1s ease 0.7s both; }
.feature-card-3 { animation: fadeInUp 1s ease 0.9s both; }

.feature-icon { font-size: 36px; margin-bottom: 12px; }
.feature-title { font-weight: 600; font-size: 16px; margin-bottom: 8px; color: #fff; }
.feature-desc { font-size: 13px; color: #a0a0c0; line-height: 1.5; }

.landing-btn-area .stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 16px 48px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    color: white !important;
    box-shadow: 0 0 30px rgba(102,126,234,0.5) !important;
    animation: pulse 2s ease infinite, fadeInUp 1s ease 1.1s both !important;
    cursor: pointer !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}

.landing-btn-area .stButton > button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 0 45px rgba(102,126,234,0.7) !important;
}

/* Chat interface */
.chat-view { padding-bottom: 120px; animation: fadeInUp 0.5s ease; }

.chat-header-bar {
    width: 100%;
    height: 80px;
    background: rgba(10,10,26,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 100;
    margin: -1rem -1rem 1.5rem -1rem;
}

.chat-header-inner {
    display: flex;
    align-items: center;
    gap: 14px;
    width: 100%;
    position: relative;
    padding-bottom: 4px;
}

.chat-header-inner::after {
    content: "";
    position: absolute;
    bottom: -12px;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, #667eea, #f093fb, #4facfe);
    background-size: 200% 100%;
    animation: gradientShift 3s linear infinite;
}

.header-bot-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}

.header-bot-name { font-size: 18px; font-weight: 600; color: #fff; }

.header-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #a0a0c0;
    margin-top: 2px;
}

.status-dot-green {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00f2fe;
    animation: pulse 2s ease infinite;
}

.messages-container { padding: 0 8px; }

.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    margin-bottom: 20px;
    max-width: 100%;
}

.msg-row.user {
    flex-direction: row-reverse;
    animation: slideInRight 0.3s ease;
}

.msg-row.assistant {
    flex-direction: row;
    animation: slideInLeft 0.3s ease;
}

.msg-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    background: rgba(255,255,255,0.08);
}

.msg-bubble-wrap { max-width: 70%; }

.msg-bubble {
    padding: 12px 18px;
    line-height: 1.55;
    font-size: 15px;
    word-wrap: break-word;
    white-space: pre-wrap;
}

.msg-bubble.user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 18px 18px 4px 18px;
    color: #fff;
}

.msg-bubble.assistant {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    color: #fff;
}

.msg-timestamp {
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    margin-top: 6px;
}

.msg-row.user .msg-timestamp { text-align: right; }

.typing-indicator {
    display: inline-flex;
    gap: 6px;
    padding: 14px 18px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #667eea;
    animation: typingDot 1.2s ease infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* Sidebar */
.sidebar-logo-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin: 0 auto 12px auto;
    animation: pulse 3s ease infinite;
}

.sidebar-brand {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #f093fb);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 8px;
}

.gradient-hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, #667eea, #f093fb, #4facfe);
    background-size: 200% 100%;
    animation: gradientShift 4s linear infinite;
    margin: 16px 0;
    border-radius: 2px;
}

.stat-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}

.stat-label { font-size: 12px; color: #a0a0c0; margin-bottom: 4px; }
.stat-value { font-size: 20px; font-weight: 700; color: #fff; }

[data-testid="stSidebar"] .stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
}

.sidebar-clear .stButton > button {
    background: linear-gradient(135deg, #f5576c, #f093fb) !important;
    color: white !important;
}

.sidebar-dash .stButton > button {
    background: linear-gradient(135deg, #4facfe, #00f2fe) !important;
    color: #0a0a1a !important;
}

.error-card {
    background: rgba(245, 87, 108, 0.12);
    border: 1px solid rgba(245, 87, 108, 0.35);
    border-radius: 16px;
    padding: 32px;
    max-width: 600px;
    margin: 80px auto;
    text-align: center;
    animation: fadeInUp 0.6s ease;
}

.error-card h2 { color: #f5576c; margin-bottom: 12px; }
.error-card p { color: #a0a0c0; line-height: 1.6; }

.block-container { max-width: 900px; padding-top: 1rem; }

[data-testid="stBottom"],
section[data-testid="stBottom"] {
    background: linear-gradient(to top, #0a0a1a 80%, transparent) !important;
}

@media (max-width: 768px) {
    .landing-title { font-size: 42px; }
    .feature-row { flex-direction: column; align-items: center; }
    .msg-bubble-wrap { max-width: 85%; }
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "pipeline" not in st.session_state:
    try:
        st.session_state.pipeline = ChatbotPipeline()
        st.session_state.pipeline_error = None
    except Exception as exc:
        st.session_state.pipeline = None
        st.session_state.pipeline_error = str(exc)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PARTICLE_DATA = [
    (6, 8, 15, 7.2, "#667eea", 0.55, 0.3),
    (8, 22, 8, 9.5, "#f093fb", 0.65, 1.1),
    (5, 38, 42, 11.0, "#4facfe", 0.50, 2.4),
    (10, 55, 25, 8.3, "#f5576c", 0.70, 0.8),
    (7, 72, 60, 13.2, "#00f2fe", 0.45, 3.5),
    (9, 88, 18, 6.8, "#667eea", 0.60, 4.2),
    (4, 12, 72, 10.5, "#f093fb", 0.75, 1.8),
    (8, 28, 88, 12.1, "#4facfe", 0.55, 0.0),
    (6, 45, 5, 9.0, "#f5576c", 0.65, 2.9),
    (10, 62, 48, 7.5, "#00f2fe", 0.50, 1.5),
    (5, 78, 35, 14.0, "#667eea", 0.80, 4.8),
    (7, 92, 78, 8.8, "#764ba2", 0.45, 3.1),
    (9, 5, 55, 11.5, "#4facfe", 0.70, 0.6),
    (4, 18, 32, 6.5, "#f5576c", 0.55, 2.0),
    (8, 33, 92, 9.8, "#667eea", 0.60, 4.5),
    (6, 48, 12, 12.8, "#f093fb", 0.75, 1.2),
    (10, 65, 68, 7.0, "#00f2fe", 0.50, 3.8),
    (5, 82, 45, 10.2, "#4facfe", 0.65, 0.4),
    (7, 95, 22, 13.5, "#f5576c", 0.55, 2.6),
    (9, 42, 82, 8.0, "#667eea", 0.70, 5.0),
]


def build_particles_html() -> str:
    parts = []
    for size, left, top, duration, color, opacity, delay in PARTICLE_DATA:
        parts.append(
            f'<div class="landing-particle" style="width:{size}px;height:{size}px;'
            f'left:{left}%;top:{top}%;background:{color};opacity:{opacity};'
            f'animation-duration:{duration}s;animation-delay:{delay}s;"></div>'
        )
    return f'<div class="landing-particles">{"".join(parts)}</div>'


def render_landing_page() -> None:
    st.markdown(
        f"""
        <div class="landing-screen">
            <div class="landing-bg"></div>
            <div class="landing-orb landing-orb-1"></div>
            <div class="landing-orb landing-orb-2"></div>
            <div class="landing-orb landing-orb-3"></div>
            {build_particles_html()}
            <div class="landing-content">
                <h1 class="landing-title">🤖 AI Chatbot</h1>
                <p class="landing-subtitle">
                    Powered by Mistral 7B • Long-Term Memory • RAG Pipeline
                </p>
                <div class="feature-row">
                    <div class="feature-card feature-card-1">
                        <div class="feature-icon">🧠</div>
                        <div class="feature-title">Long-Term Memory</div>
                        <div class="feature-desc">Remembers your conversations</div>
                    </div>
                    <div class="feature-card feature-card-2">
                        <div class="feature-icon">🔍</div>
                        <div class="feature-title">RAG Pipeline</div>
                        <div class="feature-desc">Retrieves relevant context</div>
                    </div>
                    <div class="feature-card feature-card-3">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-title">Streaming AI</div>
                        <div class="feature-desc">Real-time token generation</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col_btn, _ = st.columns([1, 1.4, 1])
    with col_btn:
        st.markdown('<div class="landing-btn-area">', unsafe_allow_html=True)
        if st.button("Start Chatting →", use_container_width=True, key="start_chat"):
            st.session_state.chat_started = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_message_html(role: str, content: str, timestamp: str) -> str:
    safe = html.escape(content)
    avatar = "👤" if role == "user" else "🤖"
    row_cls = "user" if role == "user" else "assistant"
    bubble_cls = "user" if role == "user" else "assistant"

    return textwrap.dedent(f"""
        <div class="msg-row {row_cls}">
            <div class="msg-avatar">{avatar}</div>
            <div class="msg-bubble-wrap">
                <div class="msg-bubble {bubble_cls}">{safe}</div>
                <div class="msg-timestamp">{html.escape(timestamp)}</div>
            </div>
        </div>
    """).strip()


def render_typing_html() -> str:
    return textwrap.dedent("""
        <div class="msg-row assistant">
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble-wrap">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    """).strip()


def render_chat_header() -> None:
    st.markdown(
        """
        <div class="chat-header-bar">
            <div class="chat-header-inner">
                <div class="header-bot-avatar">🤖</div>
                <div>
                    <div class="header-bot-name">AI Assistant</div>
                    <div class="header-status">
                        <span class="status-dot-green"></span>
                        <span>Online</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    pipeline = st.session_state.pipeline
    msg_count = len(st.session_state.messages)

    try:
        chunk_count = pipeline.memory.retriever.collection.count()
    except Exception:
        chunk_count = 0

    last_retrieval = getattr(pipeline, "last_query_retrieval", {"memory": 0, "kb": 0})
    memory_retrieved = last_retrieval.get("memory", 0)
    kb_retrieved = last_retrieval.get("kb", 0)

    try:
        llm_backend = pipeline.llm.llm_type.upper()
    except Exception:
        llm_backend = "UNKNOWN"

    st.markdown(
        """
        <div class="sidebar-logo-circle">🤖</div>
        <div class="sidebar-brand">AI Chatbot</div>
        <hr class="gradient-hr">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">💬 Messages</div>
            <div class="stat-value">{msg_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">🧠 Memory Stored</div>
            <div class="stat-value">{chunk_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">🔍 Memory Retrieved (last query)</div>
            <div class="stat-value">{memory_retrieved}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">📚 KB Retrieved (last query)</div>
            <div class="stat-value">{kb_retrieved}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">⚡ LLM Backend</div>
            <div class="stat-value">{html.escape(llm_backend)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="gradient-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-clear">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
        st.session_state.messages = []
        st.session_state.chat_started = False
        if pipeline is not None:
            pipeline.clear_conversation()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-dash">', unsafe_allow_html=True)
    if st.button("📊 Dashboard", use_container_width=True, key="open_dashboard"):
        st.switch_page("pages/dashboard.py")
    st.markdown("</div>", unsafe_allow_html=True)


def render_pipeline_error() -> None:
    st.markdown(
        f"""
        <div class="error-card">
            <h2>⚠️ Pipeline Initialization Failed</h2>
            <p>{html.escape(st.session_state.pipeline_error or "Unknown error")}</p>
            <p>Check your <code>configs/model_config.yaml</code> and <code>.env</code> settings, then refresh the page.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_interface() -> None:
    pipeline = st.session_state.pipeline

    st.markdown('<div class="chat-view">', unsafe_allow_html=True)
    render_chat_header()

    history_html = '<div class="messages-container">'
    for msg in st.session_state.messages:
        ts = msg.get("timestamp", "")
        history_html += render_message_html(msg["role"], msg["content"], ts)
    history_html += "</div>"
    st.markdown(history_html, unsafe_allow_html=True)

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.chat_started = True
        timestamp = datetime.now().strftime("%H:%M")

        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp,
        })

        st.markdown(render_message_html("user", user_input, timestamp), unsafe_allow_html=True)

        typing_slot = st.empty()
        typing_slot.markdown(render_typing_html(), unsafe_allow_html=True)

        response_slot = st.empty()
        full_response = ""

        try:
            for chunk in pipeline.process_query_stream(user_input):
                full_response += chunk
                response_slot.markdown(
                    render_message_html(
                        "assistant",
                        full_response,
                        datetime.now().strftime("%H:%M"),
                    ),
                    unsafe_allow_html=True,
                )
            typing_slot.empty()
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
        except Exception as exc:
            typing_slot.empty()
            error_msg = f"Error: {exc}"
            response_slot.markdown(
                render_message_html(
                    "assistant",
                    error_msg,
                    datetime.now().strftime("%H:%M"),
                ),
                unsafe_allow_html=True,
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now().strftime("%H:%M"),
            })

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

with st.sidebar:
    if st.session_state.pipeline_error:
        st.markdown(
            """
            <div class="sidebar-logo-circle">🤖</div>
            <div class="sidebar-brand">AI Chatbot</div>
            <hr class="gradient-hr">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="stat-card"><div class="stat-label">Status</div>'
            '<div class="stat-value" style="font-size:14px;color:#f5576c;">Offline</div></div>',
            unsafe_allow_html=True,
        )
    else:
        render_sidebar()

if st.session_state.pipeline_error:
    render_pipeline_error()
elif not st.session_state.chat_started:
    render_landing_page()
else:
    render_chat_interface()
