"""Enhanced Streamlit application for Domain Adapted AI Assistant."""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Domain Adapted AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "metrics_data" not in st.session_state:
    st.session_state.metrics_data = []


def test_api_connection() -> bool:
    """Test if API is running."""
    try:
        response = requests.get(f"{st.session_state.api_url}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_api_metrics() -> Optional[Dict[str, Any]]:
    """Fetch metrics from API."""
    try:
        response = requests.get(f"{st.session_state.api_url}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch metrics: {str(e)}")
    return None


def ask_question(question: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Send question to API and get response."""
    try:
        payload = {
            "question": question,
            "use_cache": use_cache,
        }

        with st.spinner("Generating response..."):
            response = requests.post(
                f"{st.session_state.api_url}/ask",
                json=payload,
                timeout=30,
            )

        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            st.error(f"API Error: {error_data.get('detail', 'Unknown error')}")
            return None

    except requests.exceptions.Timeout:
        st.error("Request timed out. The API might be busy or offline.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Failed to connect to API at {st.session_state.api_url}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def format_response_text(text: str) -> str:
    """Format response text for better display."""
    # Add basic markdown formatting
    lines = text.split("\n")
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            formatted_lines.append(line)
    return "\n\n".join(formatted_lines)


def add_to_history(
    question: str, response: str, inference_time: float, from_cache: bool = False
):
    """Add query to history."""
    st.session_state.query_history.append(
        {
            "timestamp": datetime.now(),
            "question": question,
            "response": response,
            "inference_time": inference_time,
            "from_cache": from_cache,
        }
    )


# Main UI Layout
st.title("🤖 Domain Adapted AI Assistant")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Configuration
    st.subheader("API Settings")
    api_url = st.text_input(
        "API URL", value=st.session_state.api_url, help="URL of the FastAPI backend"
    )
    if api_url != st.session_state.api_url:
        st.session_state.api_url = api_url

    # Test API connection
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Test Connection"):
            with st.spinner("Testing..."):
                if test_api_connection():
                    st.success("✅ API is running!")
                else:
                    st.error("❌ Cannot connect to API")

    with col2:
        st.markdown("")  # Spacer for alignment

    st.markdown("---")

    # Settings
    st.subheader("Query Settings")
    use_cache = st.checkbox(
        "Use Cache", value=True, help="Cache responses for identical questions"
    )

    st.markdown("---")

    # History management
    st.subheader("Query History")
    if st.button(f"📋 {'Hide' if st.session_state.show_history else 'Show'} History"):
        st.session_state.show_history = not st.session_state.show_history

    if len(st.session_state.query_history) > 0:
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.success("History cleared!")

    st.markdown("---")

    # System Info
    st.subheader("System Info")
    if st.button("🔄 Refresh Metrics"):
        st.rerun()

    metrics = get_api_metrics()
    if metrics:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Requests", metrics.get("total_requests", 0))
        with col2:
            st.metric("Errors", metrics.get("total_errors", 0))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Time", f"{metrics.get('average_inference_time', 0):.3f}s")
        with col2:
            st.metric("Error Rate", metrics.get("error_rate", "0%"))


# Main content area - Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Metrics", "📜 History", "ℹ️ About"])

# Tab 1: Chat Interface
with tab1:
    st.header("Ask a Question")

    # Input section
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="e.g., What is a semaphore? Explain deadlock in operating systems.",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("")  # Spacer
        submit_button = st.button(
            "🚀 Ask", key="submit_button", use_container_width=True
        )

    st.markdown("---")

    # Response section
    if submit_button and user_question:
        if len(user_question.strip()) < 3:
            st.error("❌ Question must be at least 3 characters long")
        else:
            # Show loading state
            response_data = ask_question(user_question, use_cache=use_cache)

            if response_data:
                # Display response
                st.markdown("### Response")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(
                        f"**Time taken:** {response_data.get('inference_time', 0):.3f}s"
                    )
                with col2:
                    if response_data.get("from_cache", False):
                        st.info("📦 From Cache", icon="ℹ️")

                # Display response text with formatting
                response_text = format_response_text(response_data["response"])
                st.markdown(
                    f'<div class="info-box">{response_text}</div>',
                    unsafe_allow_html=True,
                )

                # Additional metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Tokens Generated", response_data.get("tokens_generated", 0)
                    )
                with col2:
                    st.metric(
                        "Inference Time",
                        f"{response_data.get('inference_time', 0):.3f}s",
                    )
                with col3:
                    cache_status = (
                        "Yes" if response_data.get("from_cache", False) else "No"
                    )
                    st.metric("From Cache", cache_status)

                # Add to history
                add_to_history(
                    user_question,
                    response_data["response"],
                    response_data.get("inference_time", 0),
                    response_data.get("from_cache", False),
                )

                # Show timestamp
                st.caption(f"Generated at: {response_data.get('timestamp', 'Unknown')}")

    # Example questions
    st.markdown("---")
    st.markdown("### 💡 Example Questions")

    example_questions = [
        "What is deadlock?",
        "Explain semaphores in operating systems",
        "What is a mutex?",
        "Describe the process scheduling algorithm",
        "What is virtual memory?",
    ]

    cols = st.columns(2)
    for idx, question in enumerate(example_questions):
        with cols[idx % 2]:
            if st.button(question, key=f"example_{idx}", use_container_width=True):
                st.session_state.user_question = question
                st.rerun()


# Tab 2: Metrics Dashboard
with tab2:
    st.header("📊 System Metrics")

    metrics = get_api_metrics()

    if metrics:
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Requests", metrics.get("total_requests", 0), delta="requests"
            )

        with col2:
            st.metric("Total Errors", metrics.get("total_errors", 0), delta=None)

        with col3:
            avg_time = metrics.get("average_inference_time", 0)
            st.metric("Avg Inference Time", f"{avg_time:.3f}s", delta=None)

        with col4:
            st.metric("Error Rate", metrics.get("error_rate", "0%"), delta=None)

        st.markdown("---")

        # Uptime
        st.markdown("### System Health")
        uptime_seconds = metrics.get("uptime_seconds", 0)
        uptime_hours = uptime_seconds / 3600
        uptime_minutes = (uptime_seconds % 3600) / 60

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Uptime", f"{int(uptime_hours)}h {int(uptime_minutes)}m")

        with col2:
            model_status = (
                "✅ Loaded" if metrics.get("model_loaded", False) else "❌ Not Loaded"
            )
            st.metric("Model Status", model_status)

        st.markdown("---")

        # Cache statistics
        if "cache_stats" in metrics:
            st.markdown("### Cache Statistics")
            cache_stats = metrics["cache_stats"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cache Hits", cache_stats.get("hits", 0))
            with col2:
                st.metric("Cache Misses", cache_stats.get("misses", 0))
            with col3:
                hit_rate = cache_stats.get("hit_rate", "0%")
                st.metric("Hit Rate", hit_rate)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cached Items", cache_stats.get("cached_items", 0))
            with col2:
                st.metric("Max Cache Size", cache_stats.get("max_size", 0))

    else:
        st.warning("Unable to fetch metrics. Make sure the API is running.")


# Tab 3: Query History
with tab3:
    st.header("📜 Query History")

    if len(st.session_state.query_history) > 0:
        # Display as table
        st.markdown(f"**Total Queries:** {len(st.session_state.query_history)}")

        # Convert history to dataframe for display
        history_data = []
        for item in reversed(st.session_state.query_history):
            history_data.append(
                {
                    "Time": item["timestamp"].strftime("%H:%M:%S"),
                    "Question": item["question"][:50] + "..."
                    if len(item["question"]) > 50
                    else item["question"],
                    "Inference Time (s)": f"{item['inference_time']:.3f}",
                    "Cached": "✅" if item["from_cache"] else "❌",
                }
            )

        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Detailed view
        st.markdown("### Detailed View")
        selected_idx = st.selectbox(
            "Select a query to view details:",
            range(len(st.session_state.query_history)),
            format_func=lambda i: (
                f"{i + 1}. {st.session_state.query_history[-(i + 1)]['question'][:40]}..."
            ),
        )

        if selected_idx is not None:
            selected_item = st.session_state.query_history[-(selected_idx + 1)]

            st.markdown(f"**Question:** {selected_item['question']}")
            st.markdown(
                f"**Time:** {selected_item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            )
            st.markdown(f"**Inference Time:** {selected_item['inference_time']:.3f}s")
            st.markdown(
                f"**From Cache:** {'Yes ✅' if selected_item['from_cache'] else 'No'}"
            )

            st.markdown("#### Response:")
            st.markdown(format_response_text(selected_item["response"]))

    else:
        st.info("No query history yet. Ask a question to get started!")


# Tab 4: About
with tab4:
    st.header("ℹ️ About This Application")

    st.markdown("""
    ### Domain Adapted AI Assistant

    This application demonstrates **domain adaptation** using LoRA fine-tuning to improve
    responses for domain-specific questions, particularly in operating systems and computer science.

    ---

    ### 🎯 Key Features

    - **Fine-tuned Model:** Microsoft Phi-2 adapted with LoRA for domain-specific knowledge
    - **Fast Inference:** Efficient text generation with GPU acceleration
    - **Response Caching:** Improved performance with intelligent caching
    - **Performance Metrics:** Real-time monitoring of system performance
    - **Query History:** Track and review previous questions and responses

    ---

    ### 📚 Technology Stack

    - **Model:** Microsoft Phi-2 with LoRA fine-tuning (PEFT)
    - **Backend:** FastAPI with comprehensive logging
    - **Frontend:** Streamlit for interactive interface
    - **Framework:** Hugging Face Transformers

    ---

    ### 👥 Team

    **Ibrahim Alborno (50%)**
    - Instruction dataset creation and expansion
    - LoRA fine-tuning implementation
    - Backend integration with FastAPI
    - Model evaluation

    **Immanuel Olaoye (50%)**
    - Streamlit UI development
    - Logging and monitoring system
    - System testing and deployment
    - Project organization

    ---

    ### 🔧 Configuration

    The application can be customized through environment variables:

    - `MODEL_PATH` - Path to fine-tuned model
    - `API_TIMEOUT` - Request timeout in seconds
    - `MAX_RESPONSE_LENGTH` - Maximum response length
    - `LOG_LEVEL` - Logging verbosity
    - `ENABLE_CACHING` - Enable/disable response caching

    ---

    ### 📖 Documentation

    For more information, visit the project repository or check the API documentation:
    - **API Docs:** http://localhost:8000/docs
    - **ReDoc:** http://localhost:8000/redoc

    ---

    ### 📝 Lab 9 Enhancements

    This Lab 9 submission includes:

    ✅ **Enhanced Application Workflow**
    - Improved Streamlit UI with better navigation
    - Response history tracking
    - Real-time metrics display
    - Example questions for easy testing

    ✅ **System Evaluation & Monitoring**
    - Comprehensive metrics dashboard
    - Performance tracking
    - Cache statistics
    - System health status

    ✅ **Logging & Debugging**
    - Structured logging throughout the application
    - Performance timing measurements
    - Error tracking and reporting
    - Debug mode support

    ✅ **Deployment Ready**
    - Docker containerization
    - Environment configuration
    - Error handling and recovery
    - Production-ready code

    ---

    **Version:** 2.0.0 (Lab 9 Enhanced)
    **Last Updated:** Spring 2026
    """)
