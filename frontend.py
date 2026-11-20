import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


def error_detail(res):
    """Return the backend's error message, or the HTTP status if there isn't one."""
    try:
        return res.json().get("detail", res.status_code)
    except ValueError:
        return res.status_code

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus AI", page_icon="🌐", layout="wide")

# --- CUSTOM THEME & CSS ---
def local_css():
    st.markdown("""
    <style>
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Background & Glassmorphism */
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #ffffff;
        }

        /* Floating Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Glassmorphic Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            margin-bottom: 20px;
        }

        /* Modern Chat Interface */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            margin: 10px 0px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Custom Button */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            color: white;
            border: none;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton>button:hover {
            box-shadow: 0px 0px 15px rgba(0, 210, 255, 0.5);
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- SIDEBAR: KNOWLEDGE HUB ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 NEXUS</h2>", unsafe_allow_html=True)
    st.markdown("---")

    with st.container():
        st.markdown("### 📥 Source Ingestion")
        uploaded_file = st.file_uploader("Upload PDF Knowledge", type="pdf", label_visibility="collapsed")

        if st.button("PROPELLANT INDEX"):
            if not uploaded_file:
                st.warning("Choose a PDF first.")
            else:
                with st.status("Analyzing Synapses...", expanded=True) as status:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    try:
                        res = requests.post(f"{API_URL}/upload-knowledge", files=files, timeout=600)
                    except requests.RequestException:
                        status.update(label="Transmission Failed", state="error")
                        st.error(f"Can't reach the backend at {API_URL}. Is uvicorn running?")
                    else:
                        if res.ok:
                            status.update(label="Index Complete!", state="complete", expanded=False)
                            st.success(res.json().get("message", "Knowledge Integrated."))
                        else:
                            status.update(label="Transmission Failed", state="error")
                            st.error(f"Upload failed: {error_detail(res)}")

    st.divider()
    st.markdown("### ⚙️ Engine Specs")
    st.caption("Search: dense + sparse + graph, reranked")
    st.caption("Vector Dim: 3072")

# --- MAIN CONTENT: AERO WORKSPACE ---
col_space, col_main, col_space2 = st.columns([1, 4, 1])

with col_main:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Intelligent Doc <span>AI</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.7;'>Neural-linked document retrieval and synthesis.</p>", unsafe_allow_html=True)

    # Chat Memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    with st.container():
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input Area
    if prompt := st.chat_input("Query the nexus..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Decoding latent space..."):
                try:
                    response = requests.post(f"{API_URL}/ask", json={"question": prompt}, timeout=300)
                except requests.RequestException:
                    response = None
                    st.error(f"Can't reach the backend at {API_URL}. Is uvicorn running?")

                if response is not None and response.ok:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.popover("📍 View Evidence"):
                            for i, s in enumerate(sources):
                                st.markdown(f"**Snippet {i+1}:**\n{s[:250]}...")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                elif response is not None:
                    st.error(f"Request failed: {error_detail(response)}")