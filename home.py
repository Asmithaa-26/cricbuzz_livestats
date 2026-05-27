import streamlit as st

# ---------------- 🎨 Page Configuration & Professional Styling ----------------
st.set_page_config(
    page_title="Cricbuzz SQL Analytics Portal", 
    page_icon="🏏", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise CSS clean slate targeting layout structural aesthetics over loud colors
custom_css = """
<style>
    /* Premium professional app viewport canvas background */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    
    /* Sleek executive header banner design block */
    .banner-container {
        background-color: #0f172a;
        padding: 3.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        border-left: 5px solid #0284c7;
    }
    .banner-container h1 {
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0;
        font-size: 2.5rem;
    }
    .banner-container p {
        color: #94a3b8 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Force custom uniform grid design alignment on action row navigation triggers */
    div.stButton > button {
        width: 100% !important;
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0369a1 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ---------------- 🏁 Executive Header Banner ----------------
st.markdown("""
    <div class="banner-container">
        <h1>🏏 Cricbuzz SQL Analytics Engine</h1>
        <p>Welcome back, Sholingan | Enterprise Business Intelligence Portal Matrix</p>
    </div>
""", unsafe_allow_html=True)


st.markdown("### Operational Control Centers")
st.markdown("<p style='color: #64748b; margin-top:-15px; margin-bottom: 20px;'>Select a production interface node below to access systemic database registries.</p>", unsafe_allow_html=True)

# ---------------- 🗺️ Clean Navigation Grid Matrix ----------------
col1, col2 = st.columns(2)

with col1:
    # Card 1: Live Matches Module
    with st.container(border=True):
        st.markdown("#### 📺 Live Stream Dashboard")
        st.markdown("<p style='color: #475569; min-height: 45px;'>Monitor live running tournament score lines, field performance telemetry, and immediate delivery timelines.</p>", unsafe_allow_html=True)
        if st.button("Initialize Live Monitor Pipeline", key="nav_live"):
            st.switch_page("pages/1_live_matches.py")
            
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Card 2: Relational SQL Engine Query Module
    with st.container(border=True):
        st.markdown("#### 🧠 SQL Command Sandbox")
        st.markdown("<p style='color: #475569; min-height: 45px;'>Dispatch custom or complex analytical queries directly against the local SQLite core engine storage system blocks.</p>", unsafe_allow_html=True)
        if st.button("Launch Query Terminal Console", key="nav_sql"):
            st.switch_page("pages/3_sql_queries.py")

with col2:
    # Card 3: Top Stats Summary Aggregate Module
    with st.container(border=True):
        st.markdown("#### 📊 Performance Analytics Matrix")
        st.markdown("<p style='color: #475569; min-height: 45px;'>Inspect historical records and top league players segmented by competitive match formats.</p>", unsafe_allow_html=True)
        if st.button("Open Analytics Matrix Tables", key="nav_stats"):
            st.switch_page("pages/2_top_stats.py")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Card 4: Database Management CRUD Module
    with st.container(border=True):
        st.markdown("#### 🔄 Storage Registry Operations (CRUD)")
        st.markdown("<p style='color: #475569; min-height: 45px;'>Execute administrative management commands to safely insert, modify, or erase data points from the system.</p>", unsafe_allow_html=True)
        if st.button("Access Database Manager Stack", key="nav_crud"):
            st.switch_page("pages/4_crud_operations.py")


# ---------------- 🤝 Professional Portfolio Footer ----------------
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    f_col1, f_col2 = st.columns([1, 4])
    with f_col1:
        st.markdown("<h2 style='text-align: center; margin: 0; padding-top: 10px;'>💼</h2>", unsafe_allow_html=True)
    with f_col2:
        st.markdown("**System Engineering & Development Notice**")
        st.markdown(
            """
            This platform serves as a production-grade analytics interface demonstrating end-to-end data pipelines, safe thread-pooled SQL interaction layers, and real-time API sync maps.
            
            *Engineered with precision for cricket analysts, data pipelines developers, and database administrators.*
            
            **Connect with the Architect:** If you find tactical value in this system implementation framework, I am actively open to discussing technical roles, consultancy architecture engineering contracts, or full-time data systems development opportunities.
            """
        )