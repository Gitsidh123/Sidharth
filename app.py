import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import hashlib
import os
import re
from datetime import datetime

# ─── Supabase ────────────────────────────────────────────────────────────────
supabase = None
try:
    from supabase import create_client, Client
    
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    
    if SUPABASE_URL and SUPABASE_KEY:
        @st.cache_resource
        def get_supabase() -> Client:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase = get_supabase()
        st.session_state.db_connected = True
    else:
        st.session_state.db_connected = False
except ImportError:
    st.session_state.db_connected = False
except Exception as e:
    st.session_state.db_connected = False

# Initialize DB connection state
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Building Carbon Footprint Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SYSTEM  (Supabase-backed)
# ═══════════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password_strength(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, "Strong password ✓"

def register_user(user_id: str, password: str, full_name: str, email: str):
    if not st.session_state.db_connected:
        return False, "Database not connected. Please configure Supabase credentials."
    
    if not user_id or len(user_id) < 3:
        return False, "User ID must be at least 3 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", user_id):
        return False, "User ID can only contain letters, numbers, and underscores."
    valid, msg = validate_password_strength(password)
    if not valid:
        return False, msg
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    
    try:
        # Check duplicate
        res = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
        if res.data:
            return False, "User ID already exists. Please choose another."
        supabase.table("users").insert({
            "user_id": user_id,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "email": email,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }).execute()
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(user_id: str, password: str):
    if not st.session_state.db_connected:
        return False, None, "Database not connected. Please configure Supabase credentials."
    
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not res.data:
            return False, None, "User ID not found."
        user = res.data[0]
        if user["password_hash"] != hash_password(password):
            return False, None, "Incorrect password."
        return True, user, "Login successful!"
    except Exception as e:
        return False, None, f"Login error: {str(e)}"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #060a0e;
    --bg2:       #0b1118;
    --bg3:       #111820;
    --bg4:       #172030;
    --border:    #1e2e42;
    --border2:   #2a3f5a;
    --green:     #00e5a0;
    --green-dim: #00b37a;
    --amber:     #ffc04d;
    --red:       #ff5f5f;
    --blue:      #5ab4f5;
    --purple:    #b09fff;
    --cyan:      #00d4d4;
    --teal:      #00c8a8;
    --orange:    #ff9f43;
    --text:      #ddeeff;
    --text-dim:  #6a8aaa;
    --text-mid:  #99b8d0;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ── AUTH ── */
.auth-card {
    background: var(--bg2); border: 1px solid var(--border2);
    border-radius: 20px; padding: 2.4rem 2.8rem;
    position: relative; overflow: hidden;
}
.auth-logo { font-size: 2.4rem; text-align: center; margin-bottom: .5rem; }
.auth-title {
    font-family:'Outfit',sans-serif; font-size: 1.55rem; font-weight: 700;
    color: #e8f4ff; text-align: center; margin-bottom: .25rem;
}
.auth-sub {
    font-family:'JetBrains Mono',monospace; font-size: .68rem;
    color: var(--text-mid); text-transform: uppercase; letter-spacing: 2px;
    text-align: center; margin-bottom: 1.8rem;
}

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #050f0a 0%, #080e18 60%, #060a0e 100%);
    border: 1px solid var(--border2); border-radius: 22px;
    padding: 2.6rem 3.2rem; margin-bottom: 2.2rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content:''; position:absolute; top:-80px; right:-80px;
    width:320px; height:320px;
    background:radial-gradient(circle,rgba(0,229,160,.09) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
}
.hero-eyebrow {
    font-family:'JetBrains Mono',monospace; font-size:.68rem; font-weight:500;
    color:var(--green); text-transform:uppercase; letter-spacing:3px; margin-bottom:.8rem;
    display:flex; align-items:center; gap:10px;
}
.hero-eyebrow::before { content:''; width:28px; height:1px; background:var(--green); }
.hero-title {
    font-family:'Outfit',sans-serif; font-size:2.2rem; font-weight:700;
    color:#eef6ff; margin:0; letter-spacing:-.5px; line-height:1.15;
}
.hero-sub {
    color:var(--text-mid); margin:.8rem 0 0 0; font-weight:300;
    font-size:.95rem; line-height:1.7;
}
.hero-badges { display:flex; flex-wrap:wrap; gap:10px; margin-top:1.3rem; }
.badge {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,.05); border:1px solid var(--border2);
    border-radius:30px; padding:5px 14px;
    font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--text-mid);
}
.badge.green { border-color:rgba(0,229,160,.35); color:var(--green); background:rgba(0,229,160,.06); }
.badge.blue  { border-color:rgba(90,180,245,.35); color:var(--blue);  background:rgba(90,180,245,.06); }
.badge.amber { border-color:rgba(255,192,77,.35);  color:var(--amber); background:rgba(255,192,77,.06); }
.badge.orange{ border-color:rgba(255,159,67,.35);  color:var(--orange);background:rgba(255,159,67,.06); }

/* ── SECTION LABEL ── */
.sec-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; font-weight:600;
    color:var(--text-mid); text-transform:uppercase; letter-spacing:3px;
    margin:2.2rem 0 1.2rem 0; display:flex; align-items:center; gap:14px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border); }

/* ── CARD ── */
.card {
    background:var(--bg2); border:1px solid var(--border); border-radius:14px;
    padding:1.3rem 1.6rem; margin-bottom:.8rem;
    transition:border-color .25s, box-shadow .25s;
}
.card:hover { border-color:var(--border2); box-shadow:0 0 28px rgba(0,229,160,.06); }
.card-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.63rem; color:var(--text-dim);
    text-transform:uppercase; letter-spacing:2px; margin-bottom:.5rem;
}
.card-val {
    font-family:'JetBrains Mono',monospace; font-size:1.8rem;
    font-weight:700; color:var(--text); line-height:1.1;
}
.card-unit {
    font-family:'JetBrains Mono',monospace; font-size:.7rem;
    color:var(--green); margin-top:.3rem;
}

/* ── SEASONAL PANEL ── */
.seasonal-panel {
    background: linear-gradient(135deg, #080a0f 0%, #0a0d16 100%);
    border: 1px solid rgba(176,159,255,.3);
    border-radius: 14px; padding: 1.3rem 1.6rem; margin: .8rem 0;
}
.seasonal-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--purple);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px; font-weight:600;
}
.seasonal-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.5rem 0; border-bottom:1px solid rgba(176,159,255,.09);
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
}
.seasonal-row:last-child { border-bottom:none; }
.seasonal-lbl { color:var(--text-mid); }
.seasonal-val { color:var(--purple); font-weight:700; }
.seasonal-note { color:var(--text-dim); font-size:.65rem; }

/* ── T&D PANEL ── */
.td-panel {
    background: linear-gradient(135deg, #0f080a 0%, #160a0c 100%);
    border: 1px solid rgba(255,95,95,.28);
    border-radius: 14px; padding: 1.3rem 1.6rem; margin: .8rem 0;
}
.td-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--red);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px; font-weight:600;
}
.td-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.5rem 0; border-bottom:1px solid rgba(255,95,95,.09);
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
}
.td-row:last-child { border-bottom:none; }
.td-lbl { color:var(--text-mid); }
.td-val { color:var(--red); font-weight:700; }
.td-note { color:var(--text-dim); font-size:.65rem; }

/* ── RENEW PANEL ── */
.renew-panel {
    background: linear-gradient(135deg, #050f0a 0%, #071210 100%);
    border: 1px solid rgba(0,229,160,.28);
    border-radius: 14px; padding: 1.3rem 1.6rem; margin: .8rem 0;
}
.renew-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--green);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px; font-weight:600;
}
.renew-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.48rem 0; border-bottom:1px solid rgba(0,229,160,.08);
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
}
.renew-row:last-child { border-bottom:none; }
.renew-lbl { color:var(--text-mid); }
.renew-val { color:var(--green); font-weight:700; }
.renew-note { color:var(--text-dim); font-size:.65rem; }

/* ── FUEL PANEL ── */
.fuel-panel {
    background: linear-gradient(135deg, #0f0a05 0%, #160e06 100%);
    border: 1px solid rgba(255,179,71,.28);
    border-radius: 14px; padding: 1.3rem 1.6rem; margin: .8rem 0;
}
.fuel-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--amber);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px; font-weight:600;
}
.fuel-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.5rem 0; border-bottom:1px solid rgba(255,179,71,.09);
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
}
.fuel-row:last-child { border-bottom:none; }
.fuel-lbl  { color:var(--text-mid); }
.fuel-val  { color:var(--amber); font-weight:700; }
.fuel-ef   { color:var(--text-dim); font-size:.65rem; }
.fuel-em   { color:#ff9f43; font-weight:700; font-size:.84rem; }

/* ── WATER / WASTE PANEL ── */
.water-panel {
    background: linear-gradient(135deg, #060f1a 0%, #080e1e 100%);
    border: 1px solid rgba(90,180,245,.28);
    border-radius: 16px; padding: 1.4rem 1.8rem; margin: .8rem 0;
}
.water-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--blue);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1.1rem;
    display:flex; align-items:center; gap:8px; font-weight:600;
}
.water-breakdown-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.45rem 0; border-bottom:1px solid rgba(90,180,245,.09);
    font-family:'JetBrains Mono',monospace; font-size:.76rem;
}
.water-breakdown-row:last-child { border-bottom:none; }
.wb-label { color:var(--text-mid); }
.wb-value { color:var(--blue); font-weight:700; }
.wb-emission { color:var(--cyan); }

/* ── TOTAL HERO ── */
.total-hero {
    background:linear-gradient(135deg,#050f0a,#060a0e);
    border:1.5px solid var(--green); border-radius:20px; padding:2.2rem 2.8rem;
    text-align:center; box-shadow:0 0 70px rgba(0,229,160,.09); margin:1.4rem 0;
    position:relative; overflow:hidden;
}
.total-num {
    font-family:'JetBrains Mono',monospace; font-size:3.4rem;
    font-weight:700; color:var(--green); line-height:1;
}
.total-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.7rem;
    color:var(--text-mid); text-transform:uppercase; letter-spacing:3px; margin-top:.7rem;
}

/* ── EF PILLS ── */
.ef-pills { display:flex; flex-wrap:wrap; gap:7px; margin:.7rem 0; }
.ef-pill {
    display:inline-flex; align-items:center; gap:4px;
    background:var(--bg3); border:1px solid var(--border2); border-radius:6px;
    padding:4px 11px; font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--amber);
}
.ef-pill.blue   { color:var(--blue);   border-color:rgba(90,180,245,.3);  background:rgba(90,180,245,.06); }
.ef-pill.green  { color:var(--green);  border-color:rgba(0,229,160,.3);   background:rgba(0,229,160,.06); }
.ef-pill.purple { color:var(--purple); border-color:rgba(176,159,255,.3); background:rgba(176,159,255,.06); }
.ef-pill.cyan   { color:var(--cyan);   border-color:rgba(0,212,212,.3);   background:rgba(0,212,212,.06); }
.ef-pill.red    { color:var(--red);    border-color:rgba(255,95,95,.3);   background:rgba(255,95,95,.06); }
.ef-pill.orange { color:var(--orange); border-color:rgba(255,159,67,.3);  background:rgba(255,159,67,.06); }

/* ── TIPS ── */
.tip {
    background:var(--bg2); border-left:3px solid var(--amber);
    border-radius:0 12px 12px 0; padding:1rem 1.3rem; margin:.6rem 0;
    font-size:.9rem; color:var(--text); line-height:1.65;
}
.tip b { color:#eef6ff; }
.tip.danger   { border-left-color:var(--red); }
.tip.good     { border-left-color:var(--green); }
.tip.info     { border-left-color:var(--blue); }
.tip.water    { border-left-color:var(--cyan); }
.tip.waste    { border-left-color:var(--purple); }
.tip.renew    { border-left-color:var(--green); background:rgba(0,229,160,.04); }
.tip.fuel     { border-left-color:var(--amber); background:rgba(255,192,77,.04); }
.tip.seasonal { border-left-color:var(--purple); background:rgba(176,159,255,.04); }
.tip.td       { border-left-color:var(--red); background:rgba(255,95,95,.04); }

/* ── ELEC SUMMARY ── */
.elec-summary {
    background:var(--bg3); border:1px solid var(--border); border-radius:10px;
    padding:1rem 1.4rem; margin:.6rem 0 1.1rem 0;
}
.elec-summary-title {
    font-family:'JetBrains Mono',monospace; font-size:.63rem; color:var(--text-mid);
    text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.6rem;
}

.water-detail-summary {
    background:var(--bg3); border:1px solid rgba(90,180,245,.22); border-radius:10px;
    padding:1rem 1.4rem; margin:.6rem 0 1.1rem 0;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background:var(--bg) !important;
    border-right:1px solid var(--border) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab"] {
    font-family:'JetBrains Mono',monospace; font-size:.76rem;
    color:var(--text-mid); letter-spacing:.5px;
}
.stTabs [aria-selected="true"] {
    color:var(--green) !important;
    border-bottom-color:var(--green) !important;
}

/* ── METRICS ── */
[data-testid="stMetricValue"] {
    font-family:'JetBrains Mono',monospace !important;
    color:var(--green) !important; font-size:1.35rem !important;
}
[data-testid="stMetricLabel"] {
    color:var(--text-mid) !important; font-size:.67rem !important;
    text-transform:uppercase; letter-spacing:1.2px;
}

/* ── INPUTS ── */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
.stSlider label {
    font-family:'JetBrains Mono',monospace !important;
    font-size:.69rem !important; color:var(--text-mid) !important;
    text-transform:uppercase; letter-spacing:1.2px;
}
div[data-testid="stNumberInput"] input {
    background:var(--bg3) !important; border-color:var(--border2) !important;
    color:var(--text) !important; font-family:'JetBrains Mono',monospace !important;
}

hr { border-color:var(--border) !important; margin:1.8rem 0 !important; }

div[data-testid="stButton"] > button {
    font-family:'JetBrains Mono',monospace !important;
    font-size:.74rem !important; letter-spacing:1px;
    border-radius:10px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

# Show database connection status
if not st.session_state.db_connected:
    st.warning("""
    ⚠️ **Database Not Connected**  
    To use the full app with user accounts and data persistence, configure Supabase:
    
    **Local Development:**
    1. Create `.streamlit/secrets.toml` in your project root
    2. Add:
       ```
       SUPABASE_URL = "https://your-project.supabase.co"
       SUPABASE_KEY = "your-anon-key"
       ```
    3. Restart the app: `streamlit run app.py`
    
    **Streamlit Cloud:**
    - Go to your app settings → Secrets
    - Paste the same credentials above
    
    For now, you can use the app in **demo mode** without authentication.
    """)
    
    # Demo mode: skip auth
    st.info("📱 **Running in Demo Mode** — No authentication required. Data is stored locally and not persisted.")
    st.session_state.authenticated = True
    st.session_state.current_user = "demo_user"
    st.session_state.user_info = {
        "full_name": "Demo User",
        "email": "demo@example.com"
    }

elif not st.session_state.authenticated:
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("""
        <div class="auth-card">
          <div class="auth-logo">🏢</div>
          <div class="auth-title">Carbon Footprint Tracker</div>
          <div class="auth-sub">Secure Access Portal</div>
        </div>
        """, unsafe_allow_html=True)

        auth_tab = st.radio(
            "Auth Mode", ["🔐 Sign In", "🆕 Create Account"],
            horizontal=True, label_visibility="collapsed",
        )
        st.markdown("---")

        if auth_tab == "🔐 Sign In":
            st.markdown("##### Sign in to your account")
            login_id = st.text_input("User ID", placeholder="Enter your user ID", key="login_id")
            login_pw = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pw")
            col_a, col_b = st.columns([2, 1])
            with col_a:
                if st.button("🔓 Sign In", use_container_width=True, type="primary"):
                    if not login_id or not login_pw:
                        st.error("Please enter both User ID and password.")
                    else:
                        ok, info, msg = login_user(login_id.strip(), login_pw)
                        if ok:
                            st.session_state.authenticated = True
                            st.session_state.current_user = login_id.strip()
                            st.session_state.user_info = info
                            st.success(f"Welcome back, {info['full_name']}! 🎉")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
            with col_b:
                if st.button("Clear", use_container_width=True):
                    st.rerun()
        else:
            st.markdown("##### Create a new account")
            r_name  = st.text_input("Full Name", placeholder="Your full name", key="r_name")
            r_email = st.text_input("Email Address", placeholder="name@company.com", key="r_email")
            r_id    = st.text_input("Choose a User ID", placeholder="letters, numbers, underscores (min 3 chars)", key="r_id")
            r_pw1   = st.text_input("Password", type="password",
                                    placeholder="Min 8 chars · 1 uppercase · 1 number", key="r_pw1")
            r_pw2   = st.text_input("Confirm Password", type="password",
                                    placeholder="Re-enter your password", key="r_pw2")
            if r_pw1:
                valid_pw, pw_msg = validate_password_strength(r_pw1)
                colour = "#00e5a0" if valid_pw else "#ff5f5f"
                sym    = "✓" if valid_pw else "✗"
                st.markdown(
                    f"<span style='font-family:JetBrains Mono;font-size:.68rem;color:{colour}'>{sym} {pw_msg}</span>",
                    unsafe_allow_html=True)
            if st.button("🆕 Create Account", use_container_width=True, type="primary"):
                if not all([r_name, r_email, r_id, r_pw1, r_pw2]):
                    st.error("All fields are required.")
                elif r_pw1 != r_pw2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, msg = register_user(r_id.strip(), r_pw1, r_name.strip(), r_email.strip())
                    if ok:
                        st.success(f"✅ {msg} You can now sign in.")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# EMISSION FACTOR DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

INDIA_STATE_EF = {
    "Andhra Pradesh": 0.863, "Arunachal Pradesh": 0.180, "Assam": 0.612,
    "Bihar": 1.021, "Chhattisgarh": 1.102, "Goa": 0.789,
    "Gujarat": 0.841, "Haryana": 0.956, "Himachal Pradesh": 0.136,
    "Jharkhand": 1.089, "Karnataka": 0.641, "Kerala": 0.412,
    "Madhya Pradesh": 0.978, "Maharashtra": 0.861, "Manipur": 0.210,
    "Meghalaya": 0.401, "Mizoram": 0.195, "Nagaland": 0.222,
    "Odisha": 1.045, "Punjab": 0.713, "Rajasthan": 0.897,
    "Sikkim": 0.155, "Tamil Nadu": 0.715, "Telangana": 0.921,
    "Tripura": 0.598, "Uttar Pradesh": 0.982, "Uttarakhand": 0.256,
    "West Bengal": 1.031, "Delhi": 0.801, "Chandigarh": 0.713,
    "Jammu & Kashmir": 0.421, "Ladakh": 0.310, "Puducherry": 0.715,
    "India (National Avg)": 0.820,
}

INTL_COUNTRY_EF = {
    "United States": 0.386, "United Kingdom": 0.233, "Germany": 0.385,
    "France": 0.056, "Australia": 0.610, "China": 0.581,
    "Japan": 0.432, "Canada": 0.130, "Brazil": 0.074,
    "South Africa": 0.899, "UAE": 0.409, "Saudi Arabia": 0.726,
    "Singapore": 0.408, "Malaysia": 0.585, "Indonesia": 0.762,
    "Bangladesh": 0.673, "Pakistan": 0.444, "Sri Lanka": 0.635,
    "Nepal": 0.031, "Global Average": 0.475,
}

INDIA_TD_LOSS = {
    "Andhra Pradesh": 0.142, "Arunachal Pradesh": 0.198, "Assam": 0.213,
    "Bihar": 0.231, "Chhattisgarh": 0.162, "Goa": 0.118,
    "Gujarat": 0.131, "Haryana": 0.168, "Himachal Pradesh": 0.143,
    "Jharkhand": 0.207, "Karnataka": 0.138, "Kerala": 0.125,
    "Madhya Pradesh": 0.174, "Maharashtra": 0.156, "Manipur": 0.245,
    "Meghalaya": 0.218, "Mizoram": 0.231, "Nagaland": 0.252,
    "Odisha": 0.179, "Punjab": 0.148, "Rajasthan": 0.163,
    "Sikkim": 0.171, "Tamil Nadu": 0.135, "Telangana": 0.147,
    "Tripura": 0.196, "Uttar Pradesh": 0.196, "Uttarakhand": 0.158,
    "West Bengal": 0.187, "Delhi": 0.079, "Chandigarh": 0.082,
    "Jammu & Kashmir": 0.198, "Ladakh": 0.175, "Puducherry": 0.095,
    "India (National Avg)": 0.163,
}

INTL_TD_LOSS = {
    "United States": 0.050, "United Kingdom": 0.077, "Germany": 0.045,
    "France": 0.061, "Australia": 0.055, "China": 0.062,
    "Japan": 0.045, "Canada": 0.068, "Brazil": 0.153,
    "South Africa": 0.088, "UAE": 0.072, "Saudi Arabia": 0.065,
    "Singapore": 0.025, "Malaysia": 0.092, "Indonesia": 0.102,
    "Bangladesh": 0.101, "Pakistan": 0.173, "Sri Lanka": 0.118,
    "Nepal": 0.197, "Global Average": 0.082,
}

SEASONAL_HVAC_PROFILE = {
    "hot_humid": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.70, 0.78, 0.92, 1.15, 1.30, 1.20, 1.10, 1.12, 1.08, 1.00, 0.82, 0.72],
        "desc": "Peak cooling in Apr–Jun; monsoon relief Jul–Sep",
    },
    "hot_dry": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.65, 0.72, 0.90, 1.18, 1.40, 1.35, 1.05, 1.00, 0.95, 0.80, 0.68, 0.60],
        "desc": "Extreme cooling May–Jun; mild winters",
    },
    "composite": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.75, 0.80, 0.95, 1.10, 1.25, 1.18, 1.02, 1.00, 0.98, 0.88, 0.78, 0.72],
        "desc": "Bimodal peaks in summer and mild winter heating",
    },
    "cold": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.40, 1.30, 1.10, 0.90, 0.75, 0.70, 0.72, 0.74, 0.78, 0.95, 1.25, 1.45],
        "desc": "Dominant winter heating; low summer cooling",
    },
    "temperate": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.35, 1.25, 1.05, 0.88, 0.75, 0.72, 0.78, 0.80, 0.85, 1.00, 1.20, 1.38],
        "desc": "Winter-dominant heating; mild summer cooling",
    },
    "tropical": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.05, 1.08, 1.12, 1.15, 1.10, 1.05, 1.00, 1.00, 1.02, 1.05, 1.08, 1.06],
        "desc": "Near-uniform high cooling load year-round",
    },
    "arid": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.70, 0.78, 0.95, 1.15, 1.35, 1.45, 1.40, 1.38, 1.20, 1.00, 0.78, 0.68],
        "desc": "Extreme summer cooling; mild winters",
    },
}

STATE_TO_CLIMATE = {
    "Tamil Nadu": "hot_humid", "Kerala": "hot_humid", "Andhra Pradesh": "hot_humid",
    "Telangana": "hot_humid", "Goa": "hot_humid", "Puducherry": "hot_humid",
    "Rajasthan": "hot_dry", "Gujarat": "hot_dry", "Madhya Pradesh": "hot_dry",
    "Haryana": "hot_dry",
    "Delhi": "composite", "Maharashtra": "composite", "Karnataka": "composite",
    "Uttar Pradesh": "composite", "Bihar": "composite", "Jharkhand": "composite",
    "Chhattisgarh": "composite", "West Bengal": "composite", "Odisha": "composite",
    "Punjab": "composite", "Chandigarh": "composite",
    "Himachal Pradesh": "cold", "Jammu & Kashmir": "cold", "Ladakh": "cold",
    "Uttarakhand": "cold", "Sikkim": "cold", "Arunachal Pradesh": "cold",
    "Assam": "hot_humid", "Manipur": "cold", "Meghalaya": "cold",
    "Mizoram": "hot_humid", "Nagaland": "cold", "Tripura": "hot_humid",
    "India (National Avg)": "composite",
    "United Kingdom": "temperate", "Germany": "temperate", "France": "temperate",
    "Canada": "temperate", "Japan": "temperate", "United States": "temperate",
    "Australia": "arid", "South Africa": "hot_dry",
    "Singapore": "tropical", "Malaysia": "tropical", "Indonesia": "tropical",
    "Bangladesh": "hot_humid", "Pakistan": "hot_dry", "Sri Lanka": "hot_humid",
    "Nepal": "cold",
    "UAE": "arid", "Saudi Arabia": "arid",
    "China": "composite", "Brazil": "tropical",
    "Global Average": "composite",
}

OCCUPANCY_PROFILES = {
    "Commercial Office": {
        "profile": [0.92, 0.94, 0.96, 0.95, 0.95, 0.88, 0.75, 0.78, 0.95, 0.96, 0.95, 0.70],
        "desc": "Dips in summer (Jun–Aug) and Dec holidays; high Sep–Nov",
    },
    "Retail / Mall": {
        "profile": [0.85, 0.82, 0.88, 0.90, 0.92, 0.95, 1.00, 1.00, 0.92, 0.90, 0.95, 1.00],
        "desc": "Peak in Jul–Aug and Dec; lower Jan–Feb post-holiday",
    },
    "Hospital / Healthcare": {
        "profile": [0.98, 0.97, 0.97, 0.96, 0.96, 0.95, 0.96, 0.96, 0.97, 0.97, 0.97, 0.95],
        "desc": "Near-uniform; slight dip in monsoon months",
    },
    "Educational Institution": {
        "profile": [0.90, 0.92, 0.92, 0.80, 0.40, 0.20, 0.15, 0.20, 0.88, 0.93, 0.93, 0.50],
        "desc": "Summer break May–Aug; exam season dips; two full terms",
    },
    "Hotel / Hospitality": {
        "profile": [0.75, 0.78, 0.85, 0.88, 0.85, 0.70, 0.80, 0.85, 0.82, 0.88, 0.80, 0.95],
        "desc": "Peak Dec–Jan; dip in lean monsoon months",
    },
    "Industrial / Factory": {
        "profile": [0.95, 0.95, 0.96, 0.96, 0.95, 0.93, 0.90, 0.90, 0.95, 0.96, 0.96, 0.88],
        "desc": "Near-flat; small holiday shutdowns Dec and Aug",
    },
    "Custom / Manual": {
        "profile": [1.0]*12,
        "desc": "All months at full occupancy — override manually per month",
    },
}

FUEL_EF = {
    "India": {
        "diesel":      {"ef": 2.68, "unit": "litres", "use": "Generator / DG Set", "scope": "Scope 1"},
        "lpg":         {"ef": 2.98, "unit": "kg",     "use": "Cooking / Canteen",  "scope": "Scope 1"},
        "natural_gas": {"ef": 2.03, "unit": "m³",     "use": "Heating / Boiler",   "scope": "Scope 1"},
    },
    "default": {
        "diesel":      {"ef": 2.64, "unit": "litres", "use": "Generator / DG Set", "scope": "Scope 1"},
        "lpg":         {"ef": 2.94, "unit": "kg",     "use": "Cooking / Canteen",  "scope": "Scope 1"},
        "natural_gas": {"ef": 2.02, "unit": "m³",     "use": "Heating / Boiler",   "scope": "Scope 1"},
    },
}

WATER_ENERGY_INTENSITY = {
    "India": {
        "supply_kwh_per_m3": 0.40, "treatment_kwh_per_m3": 0.35,
        "distribution_kwh_per_m3": 0.25, "wastewater_return_rate": 0.80,
        "ch4_ef_kg_per_m3": 0.023, "n2o_ef_kg_co2e_per_m3": 0.007,
    },
    "United Kingdom": {
        "supply_kwh_per_m3": 0.59, "treatment_kwh_per_m3": 0.54,
        "distribution_kwh_per_m3": 0.30, "wastewater_return_rate": 0.90,
        "ch4_ef_kg_per_m3": 0.018, "n2o_ef_kg_co2e_per_m3": 0.010,
    },
    "United States": {
        "supply_kwh_per_m3": 0.52, "treatment_kwh_per_m3": 0.50,
        "distribution_kwh_per_m3": 0.38, "wastewater_return_rate": 0.85,
        "ch4_ef_kg_per_m3": 0.020, "n2o_ef_kg_co2e_per_m3": 0.009,
    },
    "Australia": {
        "supply_kwh_per_m3": 0.80, "treatment_kwh_per_m3": 0.65,
        "distribution_kwh_per_m3": 0.55, "wastewater_return_rate": 0.80,
        "ch4_ef_kg_per_m3": 0.016, "n2o_ef_kg_co2e_per_m3": 0.008,
    },
    "default": {
        "supply_kwh_per_m3": 0.45, "treatment_kwh_per_m3": 0.40,
        "distribution_kwh_per_m3": 0.30, "wastewater_return_rate": 0.80,
        "ch4_ef_kg_per_m3": 0.020, "n2o_ef_kg_co2e_per_m3": 0.008,
    },
}

WASTE_EF_MATRIX = {
    "organic":   {"landfill": 0.587, "composting": 0.055, "anaerobic_digestion": 0.020, "incineration": 0.020},
    "paper":     {"landfill": 0.879, "recycling": 0.021, "incineration": 1.062},
    "plastic":   {"landfill": 0.024, "recycling": 0.043, "incineration": 2.948},
    "glass":     {"landfill": 0.009, "recycling": 0.005, "incineration": 0.009},
    "metal":     {"landfill": 0.013, "recycling": 0.008, "incineration": 0.013},
    "general":   {"landfill": 0.460, "incineration": 0.580, "recycling": 0.200},
    "hazardous": {"landfill": 0.600, "incineration": 0.900, "specialist_treatment": 0.250},
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def get_grid_ef(rtype, loc):
    return INDIA_STATE_EF.get(loc, 0.820) if rtype == "India – State" else INTL_COUNTRY_EF.get(loc, 0.475)

def get_td_loss(rtype, loc):
    return INDIA_TD_LOSS.get(loc, 0.163) if rtype == "India – State" else INTL_TD_LOSS.get(loc, 0.082)

def get_effective_ef(grid_ef, td_loss_rate):
    return grid_ef / (1.0 - td_loss_rate)

def get_fuel_ef(rtype):
    return FUEL_EF["India"] if rtype == "India – State" else FUEL_EF["default"]

def get_water_profile(rtype, loc):
    if rtype == "India – State":
        return WATER_ENERGY_INTENSITY["India"]
    return WATER_ENERGY_INTENSITY.get(loc, WATER_ENERGY_INTENSITY["default"])

def get_climate_profile(loc):
    return STATE_TO_CLIMATE.get(loc, "composite")

def get_hvac_seasonal_mult(climate_profile, month_name):
    profile = SEASONAL_HVAC_PROFILE.get(climate_profile, SEASONAL_HVAC_PROFILE["composite"])
    idx = MONTHS.index(month_name) if month_name in MONTHS else 0
    return profile["hvac_mult"][idx]

def get_occupancy_mult(occ_profile_name, month_name):
    profile = OCCUPANCY_PROFILES.get(occ_profile_name, OCCUPANCY_PROFILES["Commercial Office"])
    idx = MONTHS.index(month_name) if month_name in MONTHS else 0
    return profile["profile"][idx]

def calc_water_emissions(water_m3, water_profile, effective_ef):
    wp = water_profile
    ww_vol          = water_m3 * wp["wastewater_return_rate"]
    em_supply       = water_m3 * wp["supply_kwh_per_m3"]       * effective_ef
    em_distribution = water_m3 * wp["distribution_kwh_per_m3"] * effective_ef
    em_ww_treatment = ww_vol   * wp["treatment_kwh_per_m3"]    * effective_ef
    em_ch4          = ww_vol   * wp["ch4_ef_kg_per_m3"]
    em_n2o          = ww_vol   * wp["n2o_ef_kg_co2e_per_m3"]
    em_total        = em_supply + em_distribution + em_ww_treatment + em_ch4 + em_n2o
    return {
        "total": em_total, "supply": em_supply, "distribution": em_distribution,
        "ww_treatment": em_ww_treatment, "ch4_fugitive": em_ch4, "n2o_direct": em_n2o,
        "ww_volume_m3": ww_vol,
        "supply_kwh":   water_m3 * wp["supply_kwh_per_m3"],
        "dist_kwh":     water_m3 * wp["distribution_kwh_per_m3"],
        "ww_kwh":       ww_vol   * wp["treatment_kwh_per_m3"],
        "total_kwh":    water_m3 * (wp["supply_kwh_per_m3"] + wp["distribution_kwh_per_m3"])
                        + ww_vol * wp["treatment_kwh_per_m3"],
    }

def calc_waste_emissions(waste_inputs):
    breakdown = {}
    total = 0.0
    for wtype, info in waste_inputs.items():
        qty    = info["qty"]
        method = info["method"]
        ef     = WASTE_EF_MATRIX.get(wtype, {}).get(method, WASTE_EF_MATRIX["general"]["landfill"])
        em     = qty * ef
        breakdown[wtype] = {"qty": qty, "method": method, "ef": ef, "emission": em}
        total += em
    return total, breakdown

def calc_renewable_breakdown(total_grid_kwh, renew_kwh, self_consumption_rate,
                              time_mismatch_factor, effective_ef):
    effective_renew       = renew_kwh * time_mismatch_factor
    self_consumed         = effective_renew * self_consumption_rate
    grid_export           = effective_renew * (1.0 - self_consumption_rate)
    net_elec_kwh          = max(0.0, total_grid_kwh - self_consumed)
    export_credit_kwh     = grid_export * 0.5
    em_avoided            = self_consumed * effective_ef
    em_export_credit      = export_credit_kwh * effective_ef
    net_elec_em           = net_elec_kwh * effective_ef
    total_renew_benefit   = self_consumed + export_credit_kwh
    renew_pct             = (total_renew_benefit / total_grid_kwh * 100) if total_grid_kwh > 0 else 0.0
    return {
        "renew_generated": renew_kwh, "effective_renew": effective_renew,
        "self_consumed": self_consumed, "grid_export": grid_export,
        "export_credit_kwh": export_credit_kwh, "net_elec_kwh": net_elec_kwh,
        "em_avoided": em_avoided, "em_export_credit": em_export_credit,
        "net_elec_em": net_elec_em, "renew_pct": renew_pct,
        "time_mismatch_factor": time_mismatch_factor,
        "self_consumption_rate": self_consumption_rate,
    }

# ── plo() — safe for dual-axis (no xaxis/yaxis keys) ─────────────────────────
def plo(title):
    return dict(
        title=title,
        paper_bgcolor="#0b1118",
        plot_bgcolor="#0b1118",
        font=dict(color="#99b8d0", family="JetBrains Mono, monospace", size=10),
        title_font=dict(color="#ddeeff", family="Outfit, sans-serif", size=13, weight=600),
        legend=dict(bgcolor="#0b1118", bordercolor="#1e2e42", borderwidth=1,
                    font=dict(color="#99b8d0", size=9)),
        margin=dict(l=10, r=10, t=48, b=10),
    )

# ── Shared axis style ─────────────────────────────────────────────────────────
AX = dict(gridcolor="#111820", linecolor="#1e2e42", tickfont=dict(color="#99b8d0"))

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    user_info = st.session_state.user_info
    st.markdown(f"""
    <div style="background:rgba(0,229,160,.07);border:1px solid rgba(0,229,160,.25);
                border-radius:12px;padding:1rem 1.1rem;margin-bottom:1.1rem">
      <div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;
                  color:#6a8aaa;text-transform:uppercase;letter-spacing:2px;margin-bottom:.4rem">
        Signed In As
      </div>
      <div style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:600;color:#eef6ff">
        👤 {user_info['full_name']}
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#6a8aaa;margin-top:.3rem">
        @{st.session_state.current_user} · {user_info['email']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user  = None
        st.session_state.user_info     = None
        st.rerun()

    st.markdown("---")
    st.markdown("## ⚙️ Configuration")
    building_name = st.text_input("Building Name", value="Tower A – Corporate HQ")
    num_months    = st.slider("Months to Track", 1, 12, 3)
    start_month   = st.selectbox("Starting Month", MONTHS, index=0)
    st.markdown("---")

    st.markdown("### 📍 Location")
    region_type = st.selectbox("Region Type", ["India – State", "International – Country"])
    if region_type == "India – State":
        state_country = st.selectbox(
            "State / UT", sorted(INDIA_STATE_EF.keys()),
            index=sorted(INDIA_STATE_EF.keys()).index("Tamil Nadu")
        )
    else:
        state_country = st.selectbox(
            "Country", sorted(INTL_COUNTRY_EF.keys()),
            index=sorted(INTL_COUNTRY_EF.keys()).index("United States")
        )

    grid_ef       = get_grid_ef(region_type, state_country)
    td_loss_rate  = get_td_loss(region_type, state_country)
    effective_ef  = get_effective_ef(grid_ef, td_loss_rate)
    fuel_ef       = get_fuel_ef(region_type)
    water_profile = get_water_profile(region_type, state_country)
    climate_key   = get_climate_profile(state_country)
    climate_info  = SEASONAL_HVAC_PROFILE.get(climate_key, SEASONAL_HVAC_PROFILE["composite"])

    st.markdown("---")
    st.markdown("### 🏗️ Building Profile")
    building_type = st.selectbox(
        "Building Use Type", list(OCCUPANCY_PROFILES.keys()), index=0,
        help="Determines monthly occupancy variation pattern",
    )

    st.markdown("---")
    st.markdown("### ⚡ T&D Loss Override")
    use_custom_td = st.checkbox("Override T&D Loss Rate", value=False)
    if use_custom_td:
        td_loss_rate = st.slider(
            "T&D Loss Rate (%)", min_value=3, max_value=30,
            value=int(td_loss_rate * 100), step=1,
        ) / 100.0
        effective_ef = get_effective_ef(grid_ef, td_loss_rate)

    st.markdown("---")
    st.markdown("### 📡 Active Emission Factors")
    st.markdown(f"""
<div class="ef-pills">
  <div class="ef-pill green">⚡ Grid {grid_ef:.3f} kg/kWh</div>
</div>
<div class="ef-pills">
  <div class="ef-pill red">⚡ Eff EF (w/ T&D) {effective_ef:.3f} kg/kWh</div>
  <div class="ef-pill orange">📡 T&D Loss {td_loss_rate*100:.1f}%</div>
</div>
<div class="ef-pills">
  <div class="ef-pill purple">🌡 Climate: {climate_key.replace('_',' ').title()}</div>
</div>
<div class="ef-pills">
  <div class="ef-pill">🛢 Diesel {fuel_ef['diesel']['ef']} kg/L</div>
  <div class="ef-pill">🔥 LPG {fuel_ef['lpg']['ef']} kg/kg</div>
</div>
<div class="ef-pills">
  <div class="ef-pill blue">💧 Supply {water_profile['supply_kwh_per_m3']} kWh/m³</div>
  <div class="ef-pill cyan">♻️ WW {water_profile['wastewater_return_rate']*100:.0f}%</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · EPRI · IWA · GHG Protocol · PPAC · World Bank")

# [REST OF THE CODE IS IDENTICAL - the main changes are in the Supabase handling and save function below]
# ═══════════════════════════════════════════════════════════════════════════════
# SAVE TO SUPABASE (with error handling) 
# ═══════════════════════════════════════════════════════════════════════════════

def save_to_supabase(monthly_data_list):
    """Save data to Supabase with error handling"""
    if not st.session_state.db_connected or supabase is None:
        st.warning("💾 Database not connected. Data not persisted to Supabase. (Running in demo mode)")
        return False
    
    try:
        for row in monthly_data_list:
            supabase.table("carbon_reports").upsert({
                "user_id":       st.session_state.current_user,
                "building_name": building_name,
                "region":        state_country,
                "month":         row["Month"],
                "data":          json.dumps({k: (v if not isinstance(v, float) or not pd.isna(v) else 0) for k, v in row.items()}),
                "saved_at":      datetime.now().isoformat(),
            }).execute()
        st.success("✅ Report saved to Supabase successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Save failed: {str(e)}\n\nYour data is still available in the session, but not persisted.")
        return False

# Continue with rest of the app code...
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">Carbon Intelligence Platform · Temporal & Seasonal Edition</div>
  <div class="hero-title">🏢 Building Carbon Footprint Tracker</div>
  <div class="hero-sub">
    Seasonal HVAC load multipliers (climate-calibrated) &nbsp;·&nbsp; Monthly occupancy variation ({building_type})<br>
    T&D loss-adjusted effective emission factors &nbsp;·&nbsp; Weather-driven energy intensity &nbsp;·&nbsp; Renewable accounting
  </div>
  <div class="hero-badges">
    <span class="badge green">📍 {state_country}</span>
    <span class="badge green">⚡ Grid EF: {grid_ef} kg/kWh</span>
    <span class="badge amber">📡 +T&D: {effective_ef:.3f} kg/kWh ({td_loss_rate*100:.1f}% loss)</span>
    <span class="badge blue">🌡 {climate_key.replace('_',' ').title()} climate</span>
    <span class="badge orange">🏗 {building_type}</span>
    <span class="badge">🌱 IPCC AR6 · CEA 2022 · IEA 2023</span>
    <span class="badge green">👤 {user_info['full_name']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.info("✅ **Demo mode active** — All calculations work; data saves to session (not persisted without Supabase).")
