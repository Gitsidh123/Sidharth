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

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Building Carbon Footprint Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

USERS_FILE = "users_db.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, "Strong password ✓"

def register_user(user_id, password, full_name, email):
    users = load_users()
    if user_id in users:
        return False, "User ID already exists. Please choose another."
    if not user_id or len(user_id) < 3:
        return False, "User ID must be at least 3 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", user_id):
        return False, "User ID can only contain letters, numbers, and underscores."
    valid, msg = validate_password_strength(password)
    if not valid:
        return False, msg
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    users[user_id] = {
        "password": hash_password(password),
        "full_name": full_name,
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(user_id, password):
    users = load_users()
    if user_id not in users:
        return False, None, "User ID not found."
    if users[user_id]["password"] != hash_password(password):
        return False, None, "Incorrect password."
    return True, users[user_id], "Login successful!"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #060a0e;
    --bg2:       #0b1118;
    --bg3:       #111820;
    --bg4:       #172030;
    --border:    #1a2535;
    --border2:   #243548;
    --green:     #00e5a0;
    --green-dim: #00b37a;
    --amber:     #ffc04d;
    --red:       #ff5f5f;
    --blue:      #5ab4f5;
    --purple:    #b09fff;
    --cyan:      #00d4d4;
    --teal:      #00c8a8;
    --orange:    #ff9f43;
    --text:      #c8daea;
    --text-dim:  #4a6a88;
    --text-mid:  #7a9ab8;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

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
    font-family:'JetBrains Mono',monospace; font-size: .65rem;
    color: var(--text-dim); text-transform: uppercase; letter-spacing: 2px;
    text-align: center; margin-bottom: 1.8rem;
}

.hero {
    background: linear-gradient(135deg, #050f0a 0%, #080e18 60%, #060a0e 100%);
    border: 1px solid var(--border2); border-radius: 22px;
    padding: 2.4rem 3rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content:''; position:absolute; top:-80px; right:-80px;
    width:320px; height:320px;
    background:radial-gradient(circle,rgba(0,229,160,.09) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
}
.hero-eyebrow {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; font-weight:500;
    color:var(--green); text-transform:uppercase; letter-spacing:3px; margin-bottom:.6rem;
    display:flex; align-items:center; gap:8px;
}
.hero-eyebrow::before { content:''; width:24px; height:1px; background:var(--green); }
.hero-title {
    font-family:'Outfit',sans-serif; font-size:2.1rem; font-weight:700;
    color:#e8f4ff; margin:0; letter-spacing:-.5px; line-height:1.15;
}
.hero-sub { color:var(--text-mid); margin:.6rem 0 0 0; font-weight:300; font-size:.9rem; line-height:1.6; }
.hero-badges { display:flex; flex-wrap:wrap; gap:8px; margin-top:1.1rem; }
.badge {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,.04); border:1px solid var(--border2);
    border-radius:30px; padding:4px 13px;
    font-family:'JetBrains Mono',monospace; font-size:.67rem; color:var(--text-mid);
}
.badge.green { border-color:rgba(0,229,160,.3); color:var(--green); background:rgba(0,229,160,.05); }
.badge.blue  { border-color:rgba(90,180,245,.3); color:var(--blue);  background:rgba(90,180,245,.05); }
.badge.amber { border-color:rgba(255,192,77,.3); color:var(--amber); background:rgba(255,192,77,.05); }
.badge.orange { border-color:rgba(255,159,67,.3); color:var(--orange); background:rgba(255,159,67,.05); }

.sec-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.62rem; font-weight:500;
    color:var(--text-dim); text-transform:uppercase; letter-spacing:3px;
    margin:2rem 0 1rem 0; display:flex; align-items:center; gap:12px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border); }

.card {
    background:var(--bg2); border:1px solid var(--border); border-radius:14px;
    padding:1.15rem 1.5rem; margin-bottom:.7rem;
    transition:border-color .25s, box-shadow .25s;
}
.card:hover { border-color:var(--border2); box-shadow:0 0 24px rgba(0,229,160,.05); }
.card-lbl { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:2px; margin-bottom:.3rem; }
.card-val { font-family:'JetBrains Mono',monospace; font-size:1.75rem; font-weight:700; color:var(--text); line-height:1.1; }
.card-unit { font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--green); margin-top:.2rem; }

/* ── SEASONAL PANEL ── */
.seasonal-panel {
    background: linear-gradient(135deg, #080a0f 0%, #0a0d16 100%);
    border: 1px solid rgba(176,159,255,.25);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin: .6rem 0;
}
.seasonal-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--purple);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:.85rem;
    display:flex; align-items:center; gap:8px;
}
.seasonal-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.38rem 0; border-bottom:1px solid rgba(176,159,255,.07);
    font-family:'JetBrains Mono',monospace; font-size:.73rem;
}
.seasonal-row:last-child { border-bottom:none; }
.seasonal-lbl { color:var(--text-mid); }
.seasonal-val { color:var(--purple); font-weight:600; }
.seasonal-note { color:var(--text-dim); font-size:.62rem; }

/* ── T&D LOSS PANEL ── */
.td-panel {
    background: linear-gradient(135deg, #0f080a 0%, #160a0c 100%);
    border: 1px solid rgba(255,95,95,.22);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin: .6rem 0;
}
.td-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--red);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:.85rem;
    display:flex; align-items:center; gap:8px;
}
.td-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.38rem 0; border-bottom:1px solid rgba(255,95,95,.07);
    font-family:'JetBrains Mono',monospace; font-size:.73rem;
}
.td-row:last-child { border-bottom:none; }
.td-lbl { color:var(--text-mid); }
.td-val { color:var(--red); font-weight:600; }
.td-note { color:var(--text-dim); font-size:.62rem; }

/* ── RENEW PANEL ── */
.renew-panel {
    background: linear-gradient(135deg, #050f0a 0%, #071210 100%);
    border: 1px solid rgba(0,229,160,.25);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin: .6rem 0;
}
.renew-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--green);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:.85rem;
    display:flex; align-items:center; gap:8px;
}
.renew-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.35rem 0; border-bottom:1px solid rgba(0,229,160,.07);
    font-family:'JetBrains Mono',monospace; font-size:.73rem;
}
.renew-row:last-child { border-bottom:none; }
.renew-lbl { color:var(--text-mid); }
.renew-val { color:var(--green); font-weight:600; }
.renew-note { color:var(--text-dim); font-size:.62rem; }

/* ── FUEL PANEL ── */
.fuel-panel {
    background: linear-gradient(135deg, #0f0a05 0%, #160e06 100%);
    border: 1px solid rgba(255,179,71,.22);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin: .6rem 0;
}
.fuel-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--amber);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:.85rem;
    display:flex; align-items:center; gap:8px;
}
.fuel-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.38rem 0; border-bottom:1px solid rgba(255,179,71,.07);
    font-family:'JetBrains Mono',monospace; font-size:.73rem;
}
.fuel-row:last-child { border-bottom:none; }
.fuel-lbl  { color:var(--text-mid); }
.fuel-val  { color:var(--amber); font-weight:600; }
.fuel-ef   { color:var(--text-dim); font-size:.62rem; }
.fuel-em   { color:#ff9f43; font-weight:700; font-size:.82rem; }

/* ── WATER PANEL ── */
.water-panel {
    background: linear-gradient(135deg, #060f1a 0%, #080e1e 100%);
    border: 1px solid rgba(90,180,245,.25);
    border-radius: 16px; padding: 1.3rem 1.6rem; margin: .6rem 0;
}
.water-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--blue);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px;
}
.water-breakdown-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.4rem 0; border-bottom:1px solid rgba(90,180,245,.08);
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
}
.water-breakdown-row:last-child { border-bottom:none; }
.wb-label { color:var(--text-mid); }
.wb-value { color:var(--blue); font-weight:600; }
.wb-emission { color:var(--cyan); }

/* ── WASTE PANEL ── */
.waste-panel {
    background: linear-gradient(135deg, #0d0a18 0%, #100c1e 100%);
    border: 1px solid rgba(176,159,255,.25);
    border-radius: 16px; padding: 1.3rem 1.6rem; margin: .6rem 0;
}

/* ── TOTAL HERO ── */
.total-hero {
    background:linear-gradient(135deg,#050f0a,#060a0e);
    border:1.5px solid var(--green); border-radius:20px; padding:2rem 2.4rem;
    text-align:center; box-shadow:0 0 60px rgba(0,229,160,.08); margin:1.2rem 0;
    position:relative; overflow:hidden;
}
.total-num { font-family:'JetBrains Mono',monospace; font-size:3.2rem; font-weight:700; color:var(--green); line-height:1; }
.total-lbl { font-family:'JetBrains Mono',monospace; font-size:.66rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:3px; margin-top:.6rem; }

/* ── EF PILLS ── */
.ef-pills { display:flex; flex-wrap:wrap; gap:6px; margin:.6rem 0; }
.ef-pill {
    display:inline-flex; align-items:center; gap:4px;
    background:var(--bg3); border:1px solid var(--border2); border-radius:6px;
    padding:3px 10px; font-family:'JetBrains Mono',monospace; font-size:.66rem; color:var(--amber);
}
.ef-pill.blue   { color:var(--blue);   border-color:rgba(90,180,245,.25);  background:rgba(90,180,245,.05); }
.ef-pill.green  { color:var(--green);  border-color:rgba(0,229,160,.25);   background:rgba(0,229,160,.05); }
.ef-pill.purple { color:var(--purple); border-color:rgba(176,159,255,.25); background:rgba(176,159,255,.05); }
.ef-pill.cyan   { color:var(--cyan);   border-color:rgba(0,212,212,.25);   background:rgba(0,212,212,.05); }
.ef-pill.red    { color:var(--red);    border-color:rgba(255,95,95,.25);   background:rgba(255,95,95,.05); }
.ef-pill.orange { color:var(--orange); border-color:rgba(255,159,67,.25);  background:rgba(255,159,67,.05); }

/* ── TIPS ── */
.tip { background:var(--bg2); border-left:3px solid var(--amber); border-radius:0 12px 12px 0; padding:.85rem 1.1rem; margin:.5rem 0; font-size:.87rem; color:var(--text); line-height:1.55; }
.tip.danger { border-left-color:var(--red); }
.tip.good   { border-left-color:var(--green); }
.tip.info   { border-left-color:var(--blue); }
.tip.water  { border-left-color:var(--cyan); }
.tip.waste  { border-left-color:var(--purple); }
.tip.renew  { border-left-color:var(--green); background:rgba(0,229,160,.03); }
.tip.fuel   { border-left-color:var(--amber); background:rgba(255,192,77,.03); }
.tip.seasonal { border-left-color:var(--purple); background:rgba(176,159,255,.03); }
.tip.td     { border-left-color:var(--red); background:rgba(255,95,95,.03); }

/* ── ELEC SUMMARY ── */
.elec-summary {
    background:var(--bg3); border:1px solid var(--border); border-radius:10px;
    padding:.9rem 1.3rem; margin:.5rem 0 1rem 0;
}
.elec-summary-title { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.5rem; }

.water-detail-summary {
    background:var(--bg3); border:1px solid rgba(90,180,245,.2); border-radius:10px;
    padding:.9rem 1.3rem; margin:.5rem 0 1rem 0;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] { background:var(--bg) !important; border-right:1px solid var(--border) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab"] { font-family:'JetBrains Mono',monospace; font-size:.75rem; color:var(--text-dim); letter-spacing:.5px; }
.stTabs [aria-selected="true"] { color:var(--green) !important; border-bottom-color:var(--green) !important; }

/* ── METRICS ── */
[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace !important; color:var(--green) !important; font-size:1.3rem !important; }
[data-testid="stMetricLabel"] { color:var(--text-dim) !important; font-size:.65rem !important; text-transform:uppercase; letter-spacing:1.2px; }

/* ── INPUTS ── */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
.stSlider label {
    font-family:'JetBrains Mono',monospace !important;
    font-size:.67rem !important; color:var(--text-dim) !important;
    text-transform:uppercase; letter-spacing:1.2px;
}
div[data-testid="stNumberInput"] input {
    background:var(--bg3) !important; border-color:var(--border2) !important;
    color:var(--text) !important; font-family:'JetBrains Mono',monospace !important;
}

hr { border-color:var(--border) !important; margin:1.5rem 0 !important; }

div[data-testid="stButton"] > button {
    font-family:'JetBrains Mono',monospace !important;
    font-size:.72rem !important; letter-spacing:1px;
    border-radius:10px !important;
}
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
if not st.session_state.authenticated:
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
            r_pw1 = st.text_input("Password", type="password",
                                   placeholder="Min 8 chars · 1 uppercase · 1 number", key="r_pw1")
            r_pw2 = st.text_input("Confirm Password", type="password",
                                   placeholder="Re-enter your password", key="r_pw2")
            if r_pw1:
                valid_pw, pw_msg = validate_password_strength(r_pw1)
                if valid_pw:
                    st.markdown(f"<span style='font-family:JetBrains Mono;font-size:.65rem;color:#00e5a0'>✓ {pw_msg}</span>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='font-family:JetBrains Mono;font-size:.65rem;color:#ff5f5f'>✗ {pw_msg}</span>",
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

# ═══════════════════════════════════════════════════════════════════════════════
# NEW: TRANSMISSION & DISTRIBUTION LOSS RATES BY REGION
# Sources: CEA Annual Report 2022-23, IEA 2023, World Bank Energy data
# T&D losses inflate the actual generation needed — so the effective
# consumption-side EF = grid_ef / (1 - td_loss_rate)
# ═══════════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════════
# NEW: SEASONAL HVAC LOAD MULTIPLIERS
# Derived from ASHRAE 90.1, ECBC India, typical degree-day profiles
# Month index 0 = Jan ... 11 = Dec
# ═══════════════════════════════════════════════════════════════════════════════
SEASONAL_HVAC_PROFILE = {
    # Hot-humid (South India, coastal: Tamil Nadu, Kerala, AP, Telangana, Goa)
    "hot_humid": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.70, 0.78, 0.92, 1.15, 1.30, 1.20, 1.10, 1.12, 1.08, 1.00, 0.82, 0.72],
        "desc": "Peak cooling in Apr–Jun; monsoon relief Jul–Sep",
    },
    # Hot-dry (Rajasthan, Gujarat, MP, UP western, Haryana)
    "hot_dry": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.65, 0.72, 0.90, 1.18, 1.40, 1.35, 1.05, 1.00, 0.95, 0.80, 0.68, 0.60],
        "desc": "Extreme cooling May–Jun; mild winters",
    },
    # Composite (Delhi, Maharashtra, Karnataka inland)
    "composite": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.75, 0.80, 0.95, 1.10, 1.25, 1.18, 1.02, 1.00, 0.98, 0.88, 0.78, 0.72],
        "desc": "Bimodal peaks in summer and mild winter heating",
    },
    # Cold (Himachal, J&K, Uttarakhand, NE hills)
    "cold": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.40, 1.30, 1.10, 0.90, 0.75, 0.70, 0.72, 0.74, 0.78, 0.95, 1.25, 1.45],
        "desc": "Dominant winter heating; low summer cooling",
    },
    # Temperate international (UK, Germany, Canada)
    "temperate": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.35, 1.25, 1.05, 0.88, 0.75, 0.72, 0.78, 0.80, 0.85, 1.00, 1.20, 1.38],
        "desc": "Winter-dominant heating; mild summer cooling",
    },
    # Tropical international (Singapore, Malaysia, Indonesia)
    "tropical": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [1.05, 1.08, 1.12, 1.15, 1.10, 1.05, 1.00, 1.00, 1.02, 1.05, 1.08, 1.06],
        "desc": "Near-uniform high cooling load year-round",
    },
    # Arid international (UAE, Saudi Arabia, Australia outback)
    "arid": {
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "hvac_mult": [0.70, 0.78, 0.95, 1.15, 1.35, 1.45, 1.40, 1.38, 1.20, 1.00, 0.78, 0.68],
        "desc": "Extreme summer cooling; mild winters",
    },
}

# Map states/countries to climate profiles
STATE_TO_CLIMATE = {
    # India
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
    # International
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

# ═══════════════════════════════════════════════════════════════════════════════
# NEW: OCCUPANCY PROFILES
# Fraction of maximum occupancy per month (seasonal/holiday effects)
# ═══════════════════════════════════════════════════════════════════════════════
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
        "diesel":      {"ef": 2.68, "unit": "litres",  "use": "Generator / DG Set",  "scope": "Scope 1"},
        "lpg":         {"ef": 2.98, "unit": "kg",      "use": "Cooking / Canteen",    "scope": "Scope 1"},
        "natural_gas": {"ef": 2.03, "unit": "m³",      "use": "Heating / Boiler",     "scope": "Scope 1"},
    },
    "default": {
        "diesel":      {"ef": 2.64, "unit": "litres",  "use": "Generator / DG Set",  "scope": "Scope 1"},
        "lpg":         {"ef": 2.94, "unit": "kg",      "use": "Cooking / Canteen",    "scope": "Scope 1"},
        "natural_gas": {"ef": 2.02, "unit": "m³",      "use": "Heating / Boiler",     "scope": "Scope 1"},
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
    if rtype == "India – State":
        return INDIA_TD_LOSS.get(loc, 0.163)
    else:
        return INTL_TD_LOSS.get(loc, 0.082)

def get_effective_ef(grid_ef, td_loss_rate):
    """
    Effective consumption-side EF accounting for T&D losses.
    If a building consumes 1 kWh, the grid must generate 1/(1-td_loss) kWh.
    effective_ef = grid_generation_ef / (1 - td_loss_rate)
    This is the market-based + location-based hybrid approach per GHG Protocol.
    """
    return grid_ef / (1.0 - td_loss_rate)

def get_fuel_ef(rtype):
    return FUEL_EF["India"] if rtype == "India – State" else FUEL_EF["default"]

def get_water_profile(rtype, loc):
    if rtype == "India – State":
        return WATER_ENERGY_INTENSITY["India"]
    if loc in WATER_ENERGY_INTENSITY:
        return WATER_ENERGY_INTENSITY[loc]
    return WATER_ENERGY_INTENSITY["default"]

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
    effective_renew  = renew_kwh * time_mismatch_factor
    self_consumed    = effective_renew * self_consumption_rate
    grid_export      = effective_renew * (1.0 - self_consumption_rate)
    net_elec_kwh     = max(0.0, total_grid_kwh - self_consumed)
    export_credit_kwh = grid_export * 0.5
    em_avoided       = self_consumed * effective_ef
    em_export_credit = export_credit_kwh * effective_ef
    net_elec_em      = net_elec_kwh * effective_ef
    total_renew_benefit_kwh = self_consumed + export_credit_kwh
    renew_pct = (total_renew_benefit_kwh / total_grid_kwh * 100) if total_grid_kwh > 0 else 0.0
    return {
        "renew_generated": renew_kwh, "effective_renew": effective_renew,
        "self_consumed": self_consumed, "grid_export": grid_export,
        "export_credit_kwh": export_credit_kwh, "net_elec_kwh": net_elec_kwh,
        "em_avoided": em_avoided, "em_export_credit": em_export_credit,
        "net_elec_em": net_elec_em, "renew_pct": renew_pct,
        "time_mismatch_factor": time_mismatch_factor,
        "self_consumption_rate": self_consumption_rate,
    }

def plo(title):
    return dict(
        title=title, paper_bgcolor="#0b1118", plot_bgcolor="#0b1118",
        font=dict(color="#4a6a88", family="JetBrains Mono, monospace", size=10),
        title_font=dict(color="#c8daea", family="Outfit, sans-serif", size=13, weight=600),
        legend=dict(bgcolor="#0b1118", bordercolor="#1a2535", borderwidth=1,
                    font=dict(color="#7a9ab8", size=9)),
        margin=dict(l=10, r=10, t=44, b=10),
        xaxis=dict(gridcolor="#111820", linecolor="#1a2535"),
        yaxis=dict(gridcolor="#111820", linecolor="#1a2535"),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    user_info = st.session_state.user_info
    st.markdown(f"""
    <div style="background:rgba(0,229,160,.06);border:1px solid rgba(0,229,160,.2);
                border-radius:12px;padding:.85rem 1rem;margin-bottom:1rem">
      <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;
                  color:#4a6a88;text-transform:uppercase;letter-spacing:2px;margin-bottom:.3rem">
        Signed In As
      </div>
      <div style="font-family:'Outfit',sans-serif;font-size:.95rem;
                  font-weight:600;color:#e8f4ff">
        👤 {user_info['full_name']}
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.63rem;color:#4a6a88;margin-top:.2rem">
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
        "Building Use Type",
        list(OCCUPANCY_PROFILES.keys()),
        index=0,
        help="Determines monthly occupancy variation pattern",
    )

    # ── T&D Loss Override ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ T&D Loss Override")
    use_custom_td = st.checkbox("Override T&D Loss Rate", value=False)
    if use_custom_td:
        td_loss_rate = st.slider(
            "T&D Loss Rate (%)", min_value=3, max_value=30,
            value=int(td_loss_rate * 100), step=1,
            help="Transmission & Distribution losses as % of generation"
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

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
start_idx = MONTHS.index(start_month)
active_months = [MONTHS[(start_idx + i) % 12] for i in range(num_months)]

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

# ═══════════════════════════════════════════════════════════════════════════════
# SEASONAL & OCCUPANCY PREVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🌡️ Seasonal HVAC & Occupancy Profile Preview — click to expand", expanded=False):
    prev_c1, prev_c2 = st.columns(2)
    with prev_c1:
        st.markdown(f"**Climate Profile: {climate_key.replace('_',' ').title()}** — {climate_info['desc']}")
        fig_s = go.Figure()
        hvac_mults = climate_info["hvac_mult"]
        colors = ["#ff5f5f" if m > 1.1 else "#ffc04d" if m > 0.9 else "#00e5a0" for m in hvac_mults]
        fig_s.add_trace(go.Bar(
            x=MONTHS, y=hvac_mults, marker_color=colors, marker_line_width=0,
            name="HVAC Load Multiplier",
            text=[f"{m:.2f}×" for m in hvac_mults],
            textposition="outside", textfont=dict(size=8, color="#7a9ab8"),
        ))
        fig_s.add_hline(y=1.0, line_dash="dot", line_color="#4a6a88", line_width=1)
        fig_s.update_layout(**plo(f"Seasonal HVAC Load Multipliers — {climate_key.replace('_',' ').title()}"),
                             yaxis_title="Multiplier (1.0 = baseline)", yaxis_range=[0, 1.7])
        st.plotly_chart(fig_s, use_container_width=True)

    with prev_c2:
        occ_prof = OCCUPANCY_PROFILES.get(building_type, OCCUPANCY_PROFILES["Commercial Office"])
        st.markdown(f"**Occupancy Profile: {building_type}** — {occ_prof['desc']}")
        fig_o = go.Figure()
        occ_mults = occ_prof["profile"]
        occ_colors = ["#00e5a0" if o > 0.85 else "#ffc04d" if o > 0.5 else "#ff5f5f" for o in occ_mults]
        fig_o.add_trace(go.Bar(
            x=MONTHS, y=[o*100 for o in occ_mults], marker_color=occ_colors, marker_line_width=0,
            name="Occupancy %",
            text=[f"{o*100:.0f}%" for o in occ_mults],
            textposition="outside", textfont=dict(size=8, color="#7a9ab8"),
        ))
        fig_o.add_hline(y=100, line_dash="dot", line_color="#4a6a88", line_width=1)
        fig_o.update_layout(**plo(f"Monthly Occupancy Variation — {building_type}"),
                             yaxis_title="Occupancy (%)", yaxis_range=[0, 120])
        st.plotly_chart(fig_o, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MONTHLY INPUT TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-lbl">📥 Monthly Operational Data</div>', unsafe_allow_html=True)

monthly_data = []
tabs = st.tabs([f"📅 {m}" for m in active_months])

WASTE_DISPOSAL_OPTIONS = {
    "organic":   ["composting", "anaerobic_digestion", "landfill", "incineration"],
    "paper":     ["recycling", "landfill", "incineration"],
    "plastic":   ["recycling", "landfill", "incineration"],
    "glass":     ["recycling", "landfill", "incineration"],
    "metal":     ["recycling", "landfill", "incineration"],
    "general":   ["landfill", "recycling", "incineration"],
    "hazardous": ["specialist_treatment", "landfill", "incineration"],
}

WASTE_LABELS = {
    "organic":   ("🥦 Organic / Food",     "High CH4 if landfilled — composting cuts 90%"),
    "paper":     ("📄 Paper / Cardboard",  "Recycling EF is 42× lower than landfill"),
    "plastic":   ("🧴 Plastic",            "Incineration EF: 2.95 kg/kg — avoid!"),
    "glass":     ("🫙 Glass",              "Stable — recycling is always best option"),
    "metal":     ("🔩 Metal / Aluminium",  "High embodied energy — recycling saves 95%"),
    "general":   ("🗑️ General / Mixed",    "Mixed stream; segregate to reduce EF"),
    "hazardous": ("⚠️ Hazardous / E-Waste","Requires specialist treatment"),
}

for tab_i, (tab, m) in enumerate(zip(tabs, active_months)):
    with tab:
        # ── Get seasonal multipliers for this month ────────────────────
        hvac_seasonal_mult  = get_hvac_seasonal_mult(climate_key, m)
        occupancy_mult      = get_occupancy_mult(building_type, m)

        st.markdown(f"#### {m} — *{building_name}*")

        # ── Seasonal context banner ────────────────────────────────────
        hvac_tag  = "🔴 Peak Cooling" if hvac_seasonal_mult > 1.15 else "🟡 Moderate Load" if hvac_seasonal_mult > 0.90 else "🟢 Low Load"
        occ_tag   = "🟢 Full" if occupancy_mult > 0.90 else "🟡 Partial" if occupancy_mult > 0.60 else "🔴 Low"
        st.markdown(f"""<div class="seasonal-panel">
          <div class="seasonal-panel-title">🌡️ {m} Seasonal & Occupancy Context</div>
          <div class="seasonal-row">
            <span class="seasonal-lbl">🌡️ HVAC Seasonal Load Multiplier</span>
            <span class="seasonal-val">{hvac_seasonal_mult:.2f}×</span>
            <span class="seasonal-note">{hvac_tag} · {climate_key.replace('_',' ').title()} climate</span>
          </div>
          <div class="seasonal-row">
            <span class="seasonal-lbl">👥 Occupancy Rate</span>
            <span class="seasonal-val">{occupancy_mult*100:.0f}%</span>
            <span class="seasonal-note">{occ_tag} · {building_type}</span>
          </div>
          <div class="seasonal-row">
            <span class="seasonal-lbl">📡 T&D Loss-Adjusted EF</span>
            <span class="seasonal-val">{effective_ef:.4f} kg CO₂/kWh</span>
            <span class="seasonal-note">Grid {grid_ef:.3f} ÷ (1 − {td_loss_rate*100:.1f}%) · CEA/IEA 2023</span>
          </div>
          <div class="seasonal-row">
            <span class="seasonal-lbl">⚡ Additional Emission from T&D Losses</span>
            <span class="seasonal-val">+{(effective_ef - grid_ef):.4f} kg/kWh</span>
            <span class="seasonal-note">({(effective_ef/grid_ef - 1)*100:.1f}% uplift vs bare grid EF)</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Electricity ────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.4rem">⚡ Electricity Breakdown (kWh)</div>',
                    unsafe_allow_html=True)

        # Suggest seasonal HVAC value
        ec1, ec2, ec3, ec4 = st.columns(4)
        hvac_suggested = round(2000.0 * hvac_seasonal_mult / 1) * 1
        hvac       = ec1.number_input("🌡️ HVAC", min_value=0.0, value=float(hvac_suggested), step=50.0, key=f"hvac_{tab_i}",
                                      help=f"Seasonal multiplier {hvac_seasonal_mult:.2f}× applied to suggest {hvac_suggested:.0f} kWh for {m}")
        lighting   = ec2.number_input("💡 Lighting",   min_value=0.0, value=800.0,  step=50.0,  key=f"light_{tab_i}")
        # Occupancy scales appliances and elevators
        app_sug    = round(1500.0 * occupancy_mult / 25) * 25
        elev_sug   = round(200.0  * occupancy_mult / 25) * 25
        appliances = ec3.number_input("🖥️ Appliances", min_value=0.0, value=float(app_sug), step=50.0, key=f"app_{tab_i}",
                                      help=f"Occupancy {occupancy_mult*100:.0f}% → suggested {app_sug:.0f} kWh")
        elevators  = ec4.number_input("🛗 Elevators",  min_value=0.0, value=float(elev_sug), step=25.0, key=f"elev_{tab_i}",
                                      help=f"Occupancy {occupancy_mult*100:.0f}% → suggested {elev_sug:.0f} kWh")
        total_grid = hvac + lighting + appliances + elevators

        if total_grid > 0:
            pcts = {k: v/total_grid*100 for k, v in
                    {"HVAC": hvac, "Lighting": lighting, "Appliances": appliances, "Elevators": elevators}.items()}
            st.markdown(f"""<div class="elec-summary">
              <div class="elec-summary-title">Total Grid Draw · T&D Loss-Adjusted EF: {effective_ef:.4f} kg/kWh</div>
              <span style="font-family:'JetBrains Mono',monospace;font-size:1.25rem;color:#c8daea;font-weight:700">{total_grid:,.0f} kWh</span>
              &nbsp;&nbsp;
              <span style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#4a6a88">
                HVAC {pcts['HVAC']:.0f}% &nbsp;·&nbsp; Lighting {pcts['Lighting']:.0f}% &nbsp;·&nbsp; Appliances {pcts['Appliances']:.0f}% &nbsp;·&nbsp; Elevators {pcts['Elevators']:.0f}%
              </span>
              &nbsp;&nbsp;
              <span style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#ff5f5f">
                T&D loss implies {total_grid * td_loss_rate/(1-td_loss_rate):.0f} kWh additional generation needed
              </span>
            </div>""", unsafe_allow_html=True)

        # ── T&D Loss Breakdown Panel ───────────────────────────────────
        if total_grid > 0:
            generation_required = total_grid / (1.0 - td_loss_rate)
            td_loss_kwh         = generation_required - total_grid
            td_loss_em_uplift   = total_grid * (effective_ef - grid_ef)
            st.markdown(f"""<div class="td-panel">
              <div class="td-panel-title">📡 Transmission & Distribution Loss Accounting — GHG Protocol Market-Based</div>
              <div class="td-row">
                <span class="td-lbl">🏢 Building Metered Consumption</span>
                <span class="td-val">{total_grid:,.1f} kWh</span>
                <span class="td-note">at the meter</span>
              </div>
              <div class="td-row">
                <span class="td-lbl">🔌 T&D Loss Rate for {state_country}</span>
                <span class="td-val">{td_loss_rate*100:.1f}%</span>
                <span class="td-note">Source: {'CEA Annual Report 2022-23' if region_type == 'India – State' else 'IEA 2023 / World Bank'}</span>
              </div>
              <div class="td-row">
                <span class="td-lbl">⚡ Total Generation Required at Plant</span>
                <span class="td-val">{generation_required:,.1f} kWh</span>
                <span class="td-note">{td_loss_kwh:,.1f} kWh lost in transmission</span>
              </div>
              <div class="td-row">
                <span class="td-lbl">📈 Bare Grid EF</span>
                <span class="td-val">{grid_ef:.4f} kg/kWh</span>
                <span class="td-note">generation-side (location-based)</span>
              </div>
              <div class="td-row">
                <span class="td-lbl" style="color:#ff5f5f">📡 Effective EF (T&D Adjusted)</span>
                <span class="td-val" style="color:#ff5f5f">{effective_ef:.4f} kg/kWh</span>
                <span class="td-note">= {grid_ef:.3f} ÷ (1 − {td_loss_rate:.3f})</span>
              </div>
              <div class="td-row" style="border-top:1px solid rgba(255,95,95,.15);margin-top:.3rem;padding-top:.45rem">
                <span class="td-lbl" style="color:#ff9f43">Additional Emission from T&D Losses</span>
                <span class="td-val" style="color:#ff9f43">+{td_loss_em_uplift:.2f} kg CO₂e</span>
                <span class="td-note" style="color:#ff5f5f">+{(effective_ef/grid_ef-1)*100:.1f}% vs bare EF</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Renewables ─────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.5rem">☀️ On-Site Renewable Energy</div>',
                    unsafe_allow_html=True)
        ren_c1, ren_c2, ren_c3 = st.columns(3)
        renew = ren_c1.number_input("☀️ Renewable Generated (kWh)", min_value=0.0, value=0.0,
                                     step=50.0, key=f"renew_{tab_i}")
        self_consumption_rate = ren_c2.slider("🏠 Self-Consumption Rate (%)", 0, 100, 70, 5,
                                               key=f"sc_rate_{tab_i}") / 100.0
        time_mismatch_factor  = ren_c3.slider("⏱ Generation–Usage Match (%)", 0, 100, 85, 5,
                                               key=f"tmm_{tab_i}") / 100.0

        renew_breakdown = calc_renewable_breakdown(
            total_grid, renew, self_consumption_rate, time_mismatch_factor, effective_ef
        )

        if renew > 0:
            rb = renew_breakdown
            st.markdown(f"""<div class="renew-panel">
              <div class="renew-panel-title">☀️ Renewable Accounting (effective EF {effective_ef:.4f} kg/kWh)</div>
              <div class="renew-row"><span class="renew-lbl">⚡ Generated</span><span class="renew-val">{rb['renew_generated']:,.1f} kWh</span><span class="renew-note">raw output</span></div>
              <div class="renew-row"><span class="renew-lbl">⏱ After Time-Mismatch</span><span class="renew-val">{rb['effective_renew']:,.1f} kWh</span><span class="renew-note">{rb['renew_generated']-rb['effective_renew']:,.1f} kWh mismatch loss</span></div>
              <div class="renew-row"><span class="renew-lbl">🏠 Self-Consumed</span><span class="renew-val">{rb['self_consumed']:,.1f} kWh</span><span class="renew-note">→ avoids {rb['em_avoided']:,.2f} kg CO₂e</span></div>
              <div class="renew-row"><span class="renew-lbl">🔌 Grid Export (50% credit)</span><span class="renew-val">{rb['grid_export']:,.1f} kWh</span><span class="renew-note">→ credit {rb['em_export_credit']:,.2f} kg CO₂e</span></div>
              <div class="renew-row" style="border-top:1px solid rgba(0,229,160,.15);margin-top:.3rem;padding-top:.45rem">
                <span class="renew-lbl" style="color:#00e5a0">Net Grid Draw</span>
                <span class="renew-val">{rb['net_elec_kwh']:,.1f} kWh</span>
                <span class="renew-note" style="color:#00e5a0">{rb['renew_pct']:.1f}% effective offset · {rb['net_elec_em']:,.2f} kg CO₂e</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Fuels ──────────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">⛽ Fuel Usage — Categorised by End-Use</div>',
                    unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:.6rem;color:#ffc04d;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.2rem'>🛢 Diesel · {fuel_ef['diesel']['use']}</div>", unsafe_allow_html=True)
            diesel = st.number_input(f"Diesel (litres) · EF: {fuel_ef['diesel']['ef']} kg CO₂/L",
                                     min_value=0.0, value=0.0, step=10.0, key=f"diesel_{tab_i}")
        with fc2:
            st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:.6rem;color:#ffc04d;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.2rem'>🔥 LPG · {fuel_ef['lpg']['use']}</div>", unsafe_allow_html=True)
            lpg = st.number_input(f"LPG (kg) · EF: {fuel_ef['lpg']['ef']} kg CO₂/kg",
                                  min_value=0.0, value=0.0, step=5.0, key=f"lpg_{tab_i}")
        with fc3:
            st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:.6rem;color:#ffc04d;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.2rem'>💨 Natural Gas · {fuel_ef['natural_gas']['use']}</div>", unsafe_allow_html=True)
            natgas = st.number_input(f"Natural Gas (m³) · EF: {fuel_ef['natural_gas']['ef']} kg CO₂/m³",
                                     min_value=0.0, value=0.0, step=5.0, key=f"natgas_{tab_i}")

        em_diesel = diesel * fuel_ef["diesel"]["ef"]
        em_lpg    = lpg    * fuel_ef["lpg"]["ef"]
        em_natgas = natgas * fuel_ef["natural_gas"]["ef"]
        em_fuel   = em_diesel + em_lpg + em_natgas

        if em_fuel > 0:
            st.markdown(f"""<div class="fuel-panel">
              <div class="fuel-panel-title">⛽ Fuel Emission Breakdown — Scope 1 Direct Combustion</div>
              <div class="fuel-row"><span class="fuel-lbl">🛢 Diesel</span><span class="fuel-val">{diesel:.1f} L × {fuel_ef['diesel']['ef']} kg/L</span><span class="fuel-em">{em_diesel:.2f} kg CO₂e</span></div>
              <div class="fuel-row"><span class="fuel-lbl">🔥 LPG</span><span class="fuel-val">{lpg:.1f} kg × {fuel_ef['lpg']['ef']} kg/kg</span><span class="fuel-em">{em_lpg:.2f} kg CO₂e</span></div>
              <div class="fuel-row"><span class="fuel-lbl">💨 Natural Gas</span><span class="fuel-val">{natgas:.1f} m³ × {fuel_ef['natural_gas']['ef']} kg/m³</span><span class="fuel-em">{em_natgas:.2f} kg CO₂e</span></div>
              <div class="fuel-row" style="border-top:1px solid rgba(255,179,71,.15);margin-top:.3rem;padding-top:.45rem">
                <span class="fuel-lbl" style="color:#ffc04d">Total Fuel</span><span class="fuel-ef">Scope 1</span>
                <span class="fuel-em" style="font-size:.95rem">{em_fuel:.2f} kg CO₂e</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Water ──────────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">💧 Water Consumption</div>',
                    unsafe_allow_html=True)
        # Occupancy scales water too
        water_sug = round(200.0 * occupancy_mult / 10) * 10
        w_col1, w_col2 = st.columns([1, 2])
        with w_col1:
            water_m3 = st.number_input("Total Water (m³)", min_value=0.0, value=float(water_sug),
                                        step=10.0, key=f"water_{tab_i}",
                                        help=f"Occupancy {occupancy_mult*100:.0f}% → suggested {water_sug:.0f} m³")

        water_em = calc_water_emissions(water_m3, water_profile, effective_ef)

        with w_col2:
            st.markdown(f"""<div class="water-detail-summary">
              <div class="elec-summary-title">💧 {water_m3:.0f} m³ · Effective EF: {effective_ef:.4f} kg/kWh</div>
              <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:.4rem">
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">Supply</div>
                  <div style="font-size:.9rem;color:#5ab4f5;font-weight:600">{water_em['supply']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">Pumping</div>
                  <div style="font-size:.9rem;color:#5ab4f5;font-weight:600">{water_em['distribution']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">WW Treat</div>
                  <div style="font-size:.9rem;color:#00d4d4;font-weight:600">{water_em['ww_treatment']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">CH₄</div>
                  <div style="font-size:.9rem;color:#ffc04d;font-weight:600">{water_em['ch4_fugitive']:.3f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">N₂O</div>
                  <div style="font-size:.9rem;color:#ffc04d;font-weight:600">{water_em['n2o_direct']:.3f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
              </div>
              <div style="margin-top:.7rem;padding-top:.5rem;border-top:1px solid #1a2535;font-family:'JetBrains Mono',monospace">
                <span style="font-size:.6rem;color:#4a6a88">TOTAL WATER</span>
                <span style="font-size:1.05rem;color:#5ab4f5;font-weight:700;margin-left:10px">{water_em['total']:.2f} kg CO₂e</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Waste ──────────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">🗑️ Waste — Category & Disposal Method</div>',
                    unsafe_allow_html=True)

        waste_inputs_raw = {}
        waste_cols_1 = st.columns(4)
        waste_cols_2 = st.columns(3)
        waste_type_cols = {
            "organic":   (waste_cols_1[0], 50.0),
            "paper":     (waste_cols_1[1], 30.0),
            "plastic":   (waste_cols_1[2], 20.0),
            "glass":     (waste_cols_1[3], 10.0),
            "metal":     (waste_cols_2[0], 5.0),
            "general":   (waste_cols_2[1], 40.0),
            "hazardous": (waste_cols_2[2], 2.0),
        }
        for wtype, (col_, default_qty) in waste_type_cols.items():
            label, _ = WASTE_LABELS[wtype]
            with col_:
                qty = st.number_input(f"{label} (kg)", min_value=0.0, value=default_qty,
                                      step=2.0, key=f"w_{wtype}_{tab_i}")
                method = st.selectbox("Disposal", WASTE_DISPOSAL_OPTIONS[wtype],
                                      key=f"wd_{wtype}_{tab_i}", label_visibility="collapsed")
                waste_inputs_raw[wtype] = {"qty": qty, "method": method}

        # ── Calculations ───────────────────────────────────────────────
        rb             = renew_breakdown
        em_hvac        = hvac       * effective_ef
        em_lighting    = lighting   * effective_ef
        em_appliances  = appliances * effective_ef
        em_elevators   = elevators  * effective_ef
        em_electricity = rb["net_elec_em"]
        em_water       = water_em["total"]
        em_waste_total, waste_breakdown = calc_waste_emissions(waste_inputs_raw)
        em_total       = em_electricity + em_fuel + em_water + em_waste_total

        td_loss_kwh_month    = total_grid * td_loss_rate / (1 - td_loss_rate)
        td_uplift_em_month   = total_grid * (effective_ef - grid_ef)

        monthly_data.append({
            "Month": m,
            "HVAC (kWh)": hvac, "Lighting (kWh)": lighting,
            "Appliances (kWh)": appliances, "Elevators (kWh)": elevators,
            "Total Grid (kWh)": total_grid,
            "HVAC Seasonal Mult": hvac_seasonal_mult,
            "Occupancy Rate (%)": occupancy_mult * 100,
            "Climate Profile": climate_key,
            "T&D Loss Rate (%)": td_loss_rate * 100,
            "T&D Loss kWh": td_loss_kwh_month,
            "T&D Uplift Emission (kg)": td_uplift_em_month,
            "Grid EF (kg/kWh)": grid_ef,
            "Effective EF (kg/kWh)": effective_ef,
            "Renewables Generated (kWh)": renew,
            "Renewables Self-Consumed (kWh)": rb["self_consumed"],
            "Renewables Grid Export (kWh)": rb["grid_export"],
            "Renewables Export Credit (kWh)": rb["export_credit_kwh"],
            "Time Mismatch Factor": rb["time_mismatch_factor"],
            "Self Consumption Rate": rb["self_consumption_rate"],
            "Net Elec (kWh)": rb["net_elec_kwh"],
            "Renewable %": rb["renew_pct"],
            "Diesel (L)": diesel, "LPG (kg)": lpg, "Nat Gas (m³)": natgas,
            "Em Diesel": em_diesel, "Em LPG": em_lpg, "Em Nat Gas": em_natgas,
            "Water (m³)": water_m3,
            "Water Supply Emission": water_em["supply"],
            "Water Distribution Emission": water_em["distribution"],
            "Water WW Treatment Emission": water_em["ww_treatment"],
            "Water CH4 Emission": water_em["ch4_fugitive"],
            "Water N2O Emission": water_em["n2o_direct"],
            "Water Total kWh": water_em["total_kwh"],
            **{f"Waste {wt} (kg)": waste_inputs_raw[wt]["qty"] for wt in waste_inputs_raw},
            **{f"Waste {wt} Method": waste_inputs_raw[wt]["method"] for wt in waste_inputs_raw},
            **{f"Em Waste {wt}": waste_breakdown[wt]["emission"] for wt in waste_breakdown},
            "Em HVAC": em_hvac, "Em Lighting": em_lighting,
            "Em Appliances": em_appliances, "Em Elevators": em_elevators,
            "Elec Emission": em_electricity,
            "Fuel Emission": em_fuel,
            "Water Emission": em_water,
            "Waste Emission": em_waste_total,
            "Total Emission": em_total,
        })

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(monthly_data)
st.markdown('<div class="sec-lbl">📊 Results & Analysis</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "📋 Summary", "🔬 Month Detail", "⚡ Electricity & ☀️ Renewables",
    "📡 T&D & Seasonal Analysis", "💧 Water Deep Dive", "📈 Charts", "💡 Recommendations"
])

with t1:
    st.markdown(f"#### Monthly CO₂ Summary — *{building_name}* &nbsp;|&nbsp; 📍 {state_country}")
    disp = df[["Month","Elec Emission","Fuel Emission","Water Emission","Waste Emission",
               "Total Emission","Renewable %","Effective EF (kg/kWh)","T&D Loss Rate (%)","Occupancy Rate (%)"]].round(2).copy()
    disp.columns = ["Month","Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)",
                    "Total CO₂ (kg)","Eff. Renew %","Eff. EF","T&D Loss %","Occupancy %"]
    tots = disp[["Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)","Total CO₂ (kg)"]].sum()
    tr = pd.DataFrame([["─ TOTAL ─", tots["Electricity (kg)"], tots["Fuel (kg)"],
                         tots["Water (kg)"], tots["Waste (kg)"], tots["Total CO₂ (kg)"], "─","─","─","─"]],
                      columns=disp.columns)
    disp_full = pd.concat([disp, tr], ignore_index=True)
    st.dataframe(
        disp_full.style
            .format({"Electricity (kg)": "{:.2f}", "Fuel (kg)": "{:.2f}",
                     "Water (kg)": "{:.2f}", "Waste (kg)": "{:.2f}", "Total CO₂ (kg)": "{:.2f}"})
            .background_gradient(subset=["Total CO₂ (kg)"], cmap="YlOrRd"),
        use_container_width=True,
        height=min(420, (num_months + 3) * 38),
    )
    st.markdown("---")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("🌍 Total CO₂", f"{df['Total Emission'].sum():,.1f} kg")
    k2.metric("📅 Monthly Avg", f"{df['Total Emission'].mean():,.1f} kg")
    k3.metric("📌 Peak Month", df.loc[df['Total Emission'].idxmax(), 'Month'])
    k4.metric("☀️ Renew Avg", f"{df['Renewable %'].mean():.1f}%")
    k5.metric("📡 Avg T&D Loss", f"{df['T&D Loss Rate (%)'].mean():.1f}%")
    k6.metric("📡 Eff. EF", f"{effective_ef:.4f} kg/kWh")

    st.markdown("---")
    td_total_uplift = df["T&D Uplift Emission (kg)"].sum()
    st.markdown(f"""<div class="tip td">
        📡 <b>T&D Losses added {td_total_uplift:.1f} kg CO₂e total</b> ({td_uplift_em_month / df['Elec Emission'].mean() * 100 if df['Elec Emission'].mean() > 0 else 0:.1f}% uplift).
        Grid EF {grid_ef:.3f} → Effective EF {effective_ef:.4f} kg/kWh after {td_loss_rate*100:.1f}% T&D loss.
    </div>""", unsafe_allow_html=True)

with t2:
    sel = st.selectbox("Select Month", df["Month"].tolist(), key="sel_month_detail")
    row = df[df["Month"] == sel].iloc[0]
    st.markdown(f"#### {sel} — Full Breakdown")

    # Seasonal context
    st.markdown(f"""<div class="seasonal-panel" style="margin-bottom:1rem">
      <div class="seasonal-panel-title">🌡️ {sel} Temporal Context</div>
      <div class="seasonal-row"><span class="seasonal-lbl">HVAC Seasonal Multiplier</span><span class="seasonal-val">{row['HVAC Seasonal Mult']:.2f}×</span><span class="seasonal-note">{climate_key.replace('_',' ').title()}</span></div>
      <div class="seasonal-row"><span class="seasonal-lbl">Occupancy Rate</span><span class="seasonal-val">{row['Occupancy Rate (%)']:.0f}%</span><span class="seasonal-note">{building_type}</span></div>
      <div class="seasonal-row"><span class="seasonal-lbl">Effective EF (T&D adjusted)</span><span class="seasonal-val">{row['Effective EF (kg/kWh)']:.4f} kg/kWh</span><span class="seasonal-note">+{(row['Effective EF (kg/kWh)']-row['Grid EF (kg/kWh)']):.4f} from T&D losses</span></div>
    </div>""", unsafe_allow_html=True)

    ca, cb, cc, cd = st.columns(4)
    for col_, label, icon, hint in [
        (ca, "Elec Emission",  "⚡ Electricity", f"Net {row['Net Elec (kWh)']:,.0f} kWh · T&D incl."),
        (cb, "Fuel Emission",  "🔥 Fuel",        "Diesel · LPG · Nat Gas"),
        (cc, "Water Emission", "💧 Water",        f"{row['Water (m³)']:,.0f} m³"),
        (cd, "Waste Emission", "🗑️ Waste",        "7 categories"),
    ]:
        col_.markdown(f"""<div class="card">
            <div class="card-lbl">{icon}</div>
            <div class="card-val">{row[label]:,.1f}</div>
            <div class="card-unit">kg CO₂e · {hint}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="total-hero">
        <div class="total-lbl">Total Monthly Carbon Footprint</div>
        <div class="total-num">{row['Total Emission']:,.2f}</div>
        <div class="total-lbl" style="color:var(--green);margin-top:.3rem">kg CO₂e &nbsp;·&nbsp; {row['Total Emission']/1000:.3f} tCO₂e</div>
        <div class="total-lbl" style="margin-top:.2rem">T&D uplift: +{row['T&D Uplift Emission (kg)']:.2f} kg · Occ: {row['Occupancy Rate (%)']:.0f}% · HVAC mult: {row['HVAC Seasonal Mult']:.2f}×</div>
    </div>""", unsafe_allow_html=True)

with t3:
    st.markdown("#### ⚡ Electricity & ☀️ Renewable Analysis")
    ec1, ec2 = st.columns(2)
    with ec1:
        fig_e1 = go.Figure()
        for col_, clr, lbl in [
            ("Em HVAC","#4ea8de","HVAC"), ("Em Lighting","#ffb347","Lighting"),
            ("Em Appliances","#a78bfa","Appliances"), ("Em Elevators","#00e5a0","Elevators")
        ]:
            fig_e1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                    marker_color=clr, marker_line_width=0))
        fig_e1.update_layout(**plo("Electricity Emissions by Sub-Category (kg CO₂e · T&D adjusted)"),
                              barmode="stack", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_e1, use_container_width=True)
    with ec2:
        # Show HVAC seasonal mult trend
        fig_e2 = go.Figure()
        fig_e2.add_trace(go.Scatter(
            x=df["Month"], y=df["HVAC Seasonal Mult"], mode="lines+markers",
            line=dict(color="#ff5f5f", width=2.5), marker=dict(size=7),
            name="HVAC Mult", yaxis="y"
        ))
        fig_e2.add_trace(go.Scatter(
            x=df["Month"], y=df["Occupancy Rate (%)"], mode="lines+markers",
            line=dict(color="#00e5a0", width=2, dash="dot"), marker=dict(size=7),
            name="Occupancy %", yaxis="y2"
        ))
        fig_e2.update_layout(
    title="Seasonal HVAC Multiplier vs Occupancy Rate",
    paper_bgcolor="#0b1118",
    plot_bgcolor="#0b1118",
    font=dict(color="#4a6a88", family="JetBrains Mono, monospace", size=10),
    title_font=dict(color="#c8daea", family="Outfit, sans-serif", size=13, weight=600),
    legend=dict(bgcolor="#0b1118", bordercolor="#1a2535", borderwidth=1,
                font=dict(color="#7a9ab8", size=9)),
    margin=dict(l=10, r=10, t=44, b=10),
    yaxis=dict(title="HVAC Mult", gridcolor="#111820", linecolor="#1a2535"),
    yaxis2=dict(title="Occupancy %", overlaying="y", side="right",
                gridcolor="#111820", linecolor="#1a2535"),
)
        st.plotly_chart(fig_e2, use_container_width=True)

    elec_tbl = df[["Month","HVAC (kWh)","Lighting (kWh)","Appliances (kWh)","Elevators (kWh)",
                    "Total Grid (kWh)","Net Elec (kWh)","Elec Emission",
                    "HVAC Seasonal Mult","Occupancy Rate (%)","Renewable %"]].round(2)
    st.dataframe(elec_tbl, use_container_width=True, hide_index=True)

with t4:
    st.markdown("#### 📡 T&D Loss Analysis & Seasonal Profile")

    td1, td2 = st.columns(2)
    with td1:
        fig_td = go.Figure()
        fig_td.add_trace(go.Bar(
            x=df["Month"], y=df["T&D Loss kWh"],
            name="T&D Loss (kWh)", marker_color="#ff5f5f", marker_line_width=0,
        ))
        fig_td.add_trace(go.Scatter(
            x=df["Month"], y=df["T&D Uplift Emission (kg)"], mode="lines+markers",
            name="T&D Emission Uplift (kg CO₂e)", line=dict(color="#ffc04d", width=2),
            marker=dict(size=7), yaxis="y2"
        ))
        fig_td.update_layout(
    title=f"T&D Loss kWh & Emission Uplift — {td_loss_rate*100:.1f}% loss rate",
    paper_bgcolor="#0b1118",
    plot_bgcolor="#0b1118",
    font=dict(color="#4a6a88", family="JetBrains Mono, monospace", size=10),
    title_font=dict(color="#c8daea", family="Outfit, sans-serif", size=13, weight=600),
    legend=dict(bgcolor="#0b1118", bordercolor="#1a2535", borderwidth=1,
                font=dict(color="#7a9ab8", size=9)),
    margin=dict(l=10, r=10, t=44, b=10),
    yaxis=dict(title="kWh lost in T&D", gridcolor="#111820", linecolor="#1a2535"),
    yaxis2=dict(title="kg CO₂e uplift", overlaying="y", side="right",
                gridcolor="#111820", linecolor="#1a2535"),
)
        st.plotly_chart(fig_td, use_container_width=True)

    with td2:
        # Stacked: grid-only em vs T&D uplift
        fig_td2 = go.Figure()
        bare_elec_em = df["Total Grid (kWh)"] * df["Grid EF (kg/kWh)"]
        fig_td2.add_trace(go.Bar(x=df["Month"], y=bare_elec_em,
                                  name="Grid EF Only (no T&D)", marker_color="#5ab4f5", marker_line_width=0))
        fig_td2.add_trace(go.Bar(x=df["Month"], y=df["T&D Uplift Emission (kg)"],
                                  name="T&D Loss Uplift", marker_color="#ff5f5f", marker_line_width=0))
        fig_td2.update_layout(**plo("Electricity Emission: Grid vs T&D Uplift (kg CO₂e)"),
                               barmode="stack", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_td2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🌡️ Seasonal Load & Occupancy vs Emission Correlation")
    s1, s2 = st.columns(2)
    with s1:
        fig_seas = go.Figure()
        fig_seas.add_trace(go.Scatter(
            x=df["HVAC Seasonal Mult"], y=df["Em HVAC"], mode="markers+text",
            text=df["Month"], textposition="top center",
            marker=dict(size=10, color=df["Em HVAC"], colorscale="RdYlGn_r",
                        showscale=True, colorbar=dict(title="kg CO₂e")),
            name="Months"
        ))
        fig_seas.update_layout(**plo("HVAC Seasonal Multiplier vs HVAC Emission"),
                               xaxis_title="Seasonal Mult", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_seas, use_container_width=True)
    with s2:
        fig_occ = go.Figure()
        fig_occ.add_trace(go.Scatter(
            x=df["Occupancy Rate (%)"], y=df["Total Emission"], mode="markers+text",
            text=df["Month"], textposition="top center",
            marker=dict(size=10, color=df["Total Emission"], colorscale="RdYlGn_r",
                        showscale=True, colorbar=dict(title="kg CO₂e")),
            name="Months"
        ))
        fig_occ.update_layout(**plo("Occupancy Rate vs Total Monthly Emission"),
                               xaxis_title="Occupancy %", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_occ, use_container_width=True)

    # T&D table
    td_tbl = df[["Month","Total Grid (kWh)","Grid EF (kg/kWh)","T&D Loss Rate (%)","T&D Loss kWh",
                 "Effective EF (kg/kWh)","T&D Uplift Emission (kg)","HVAC Seasonal Mult","Occupancy Rate (%)"]].round(4)
    st.dataframe(td_tbl, use_container_width=True, hide_index=True)

    st.markdown(f"""<div class="tip td" style="margin-top:.8rem">
        📡 <b>GHG Protocol location-based method:</b> The effective EF = grid generation EF ÷ (1 − T&D loss rate).
        For {state_country} with {td_loss_rate*100:.1f}% T&D losses, every kWh consumed requires
        {1/(1-td_loss_rate):.3f} kWh generated. This adds {(effective_ef - grid_ef):.4f} kg CO₂/kWh
        (+{(effective_ef/grid_ef-1)*100:.1f}%) to all electricity emissions.
        Sources: {'CEA Annual Report 2022-23' if region_type == 'India – State' else 'IEA 2023 / World Bank Energy Report'}.
    </div>""", unsafe_allow_html=True)

with t5:
    st.markdown("#### 💧 Water Emissions — Full Lifecycle Analysis")
    wc1, wc2 = st.columns(2)
    with wc1:
        fig_w1 = go.Figure()
        for col_, clr, lbl in [
            ("Water Supply Emission","#5ab4f5","Supply"),
            ("Water Distribution Emission","#00d4d4","Pumping"),
            ("Water WW Treatment Emission","#4ea8de","WW Treatment"),
            ("Water CH4 Emission","#ffc04d","CH₄ Fugitive"),
            ("Water N2O Emission","#ff9f43","N₂O Direct"),
        ]:
            fig_w1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                    marker_color=clr, marker_line_width=0))
        fig_w1.update_layout(**plo("Water Emission Components (kg CO₂e · T&D adjusted)"),
                              barmode="stack", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_w1, use_container_width=True)
    with wc2:
        avg_w = [df["Water Supply Emission"].mean(), df["Water Distribution Emission"].mean(),
                 df["Water WW Treatment Emission"].mean(), df["Water CH4 Emission"].mean(),
                 df["Water N2O Emission"].mean()]
        fig_w2 = go.Figure(go.Pie(
            labels=["Supply","Pumping","WW Treatment","CH₄","N₂O"], values=avg_w, hole=0.58,
            marker=dict(colors=["#5ab4f5","#00d4d4","#4ea8de","#ffc04d","#ff9f43"],
                        line=dict(color="#0b1118", width=2)),
            textfont=dict(family="JetBrains Mono", color="#c8daea", size=10),
        ))
        fig_w2.update_layout(**plo("Avg Water Emission Share"))
        st.plotly_chart(fig_w2, use_container_width=True)

    w_tbl = df[["Month","Water (m³)","Occupancy Rate (%)","Water Supply Emission","Water Distribution Emission",
                "Water WW Treatment Emission","Water CH4 Emission","Water N2O Emission","Water Emission"]].round(4)
    st.dataframe(w_tbl, use_container_width=True, hide_index=True)

with t6:
    ch1, ch2 = st.columns(2)
    with ch1:
        fig1 = go.Figure()
        for col_, clr, lbl in [
            ("Elec Emission","#00e5a0","Electricity (T&D adj.)"),
            ("Fuel Emission","#ffb347","Fuel"),
            ("Water Emission","#5ab4f5","Water"),
            ("Waste Emission","#b09fff","Waste"),
        ]:
            fig1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                  marker_color=clr, marker_line_width=0))
        fig1.update_layout(**plo("Monthly CO₂e by Category (kg)"),
                           barmode="stack", yaxis_title="kg CO₂e")
        st.plotly_chart(fig1, use_container_width=True)
    with ch2:
        avg_vals = [df["Elec Emission"].mean(), df["Fuel Emission"].mean(),
                    df["Water Emission"].mean(), df["Waste Emission"].mean()]
        fig2 = go.Figure(go.Pie(
            labels=["Electricity","Fuel","Water","Waste"], values=avg_vals, hole=0.58,
            marker=dict(colors=["#00e5a0","#ffb347","#5ab4f5","#b09fff"],
                        line=dict(color="#0b1118", width=2)),
            textfont=dict(family="JetBrains Mono", color="#c8daea", size=10),
        ))
        fig2.update_layout(**plo("Avg Emission Share"))
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["Month"], y=df["Total Emission"], mode="lines+markers",
        line=dict(color="#00e5a0", width=2.5),
        marker=dict(size=7, color="#00e5a0", line=dict(color="#060a0e", width=2)),
        fill="tozeroy", fillcolor="rgba(0,229,160,.07)", name="Total CO₂e"
    ))
    if len(df) > 0:
        fig3.add_trace(go.Scatter(
            x=df["Month"], y=df["HVAC Seasonal Mult"] * df["Total Emission"].mean(),
            mode="lines", line=dict(color="#b09fff", width=1.5, dash="dot"),
            name="Seasonal Load Index (scaled)"
        ))
    fig3.update_layout(**plo("Total Monthly CO₂e Trend + Seasonal Index"), yaxis_title="kg CO₂e")
    st.plotly_chart(fig3, use_container_width=True)

    # T&D uplift vs grid-only comparison
    fig4 = go.Figure()
    grid_only_em = df["Net Elec (kWh)"] * df["Grid EF (kg/kWh)"]
    fig4.add_trace(go.Scatter(
        x=df["Month"], y=grid_only_em, mode="lines+markers",
        line=dict(color="#5ab4f5", width=2, dash="dot"), name="Bare Grid EF (no T&D)"
    ))
    fig4.add_trace(go.Scatter(
        x=df["Month"], y=df["Elec Emission"], mode="lines+markers",
        line=dict(color="#ff5f5f", width=2.5), name=f"With T&D Loss ({td_loss_rate*100:.1f}%)"
    ))
    fig4.update_layout(**plo("Electricity Emission: With vs Without T&D Losses"), yaxis_title="kg CO₂e")
    st.plotly_chart(fig4, use_container_width=True)

with t7:
    st.markdown(f"#### 💡 Location-Aware Recommendations — {state_country}")
    any_tip = False

    # T&D recommendation
    if td_loss_rate > 0.18:
        any_tip = True
        st.markdown(f"""<div class="tip td">
            📡 <b>High T&D loss rate: {td_loss_rate*100:.1f}%</b> for {state_country} (national avg: {'16.3%' if region_type == 'India – State' else '8.2%'}).
            Your effective EF is {effective_ef:.4f} vs bare grid {grid_ef:.3f} kg/kWh.
            Switching to on-site generation (solar + BESS) bypasses T&D losses entirely — effectively using grid EF, not effective EF.
            Priority: maximise self-consumption to eliminate T&D uplift.
        </div>""", unsafe_allow_html=True)
    elif td_loss_rate > 0.12:
        any_tip = True
        st.markdown(f"""<div class="tip info">
            📡 <b>Moderate T&D losses: {td_loss_rate*100:.1f}%</b>.
            Effective EF uplift = +{(effective_ef-grid_ef):.4f} kg/kWh (+{(effective_ef/grid_ef-1)*100:.1f}%).
            On-site solar with self-consumption avoids this penalty on every kWh generated and used on-site.
        </div>""", unsafe_allow_html=True)

    # Seasonal HVAC
    peak_hvac_month = df.loc[df["HVAC Seasonal Mult"].idxmax(), "Month"]
    max_mult = df["HVAC Seasonal Mult"].max()
    if max_mult > 1.20:
        any_tip = True
        st.markdown(f"""<div class="tip seasonal">
            🌡️ <b>Seasonal HVAC peak in {peak_hvac_month} ({max_mult:.2f}× baseline load)</b> for {climate_key.replace('_',' ').title()} climate.
            Pre-cool building fabric during off-peak tariff hours (typically 22:00–06:00).
            Consider thermal mass storage or phase-change materials to shift 20–30% of peak cooling load.
            BMS pre-cooling setback can reduce peak-hour demand by 15–25%.
        </div>""", unsafe_allow_html=True)

    # Occupancy-driven tip
    min_occ_month = df.loc[df["Occupancy Rate (%)"].idxmin(), "Month"]
    min_occ = df["Occupancy Rate (%)"].min()
    max_em_month  = df.loc[df["Total Emission"].idxmax(), "Month"]
    if min_occ < 60:
        any_tip = True
        st.markdown(f"""<div class="tip seasonal">
            👥 <b>Low occupancy in {min_occ_month} ({min_occ:.0f}%)</b>.
            Implement occupancy-linked BMS zones: reduce HVAC setpoints by 2–3°C and dim lighting to 40% in unoccupied areas.
            Potential saving: up to {(1 - min_occ/100) * df.loc[df['Occupancy Rate (%)']==min_occ,'Elec Emission'].values[0] if len(df.loc[df['Occupancy Rate (%)']==min_occ]) > 0 else 0:.0f} kg CO₂e in low-occ months.
        </div>""", unsafe_allow_html=True)

    if grid_ef > 0.85:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            📡 <b>High grid emission factor ({grid_ef} kg/kWh) + T&D uplift → {effective_ef:.4f} kg/kWh effective</b>.
            Prioritise on-site solar, RECs, or a green PPA. Each 1 MWh of self-consumed renewable
            avoids {effective_ef:.2f} kg CO₂ (vs {grid_ef:.2f} without T&D correction).
        </div>""", unsafe_allow_html=True)

    avg_hvac_pct = (df["Em HVAC"].sum() / df["Elec Emission"].sum() * 100) if df["Elec Emission"].sum() > 0 else 0
    if avg_hvac_pct > 45:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            🌡️ <b>HVAC is {avg_hvac_pct:.0f}% of electricity emissions</b>.
            Upgrade to inverter chillers (COP ≥ 5.0), deploy BMS setback, improve envelope insulation. Target: cut cooling load 20–35%.
        </div>""", unsafe_allow_html=True)

    if df["Em Diesel"].sum() > 0:
        any_tip = True
        st.markdown(f"""<div class="tip fuel">
            🛢 <b>Diesel Generator: {df['Em Diesel'].sum():,.1f} kg CO₂ total.</b>
            Replace DG sets with grid-tied UPS + Li-ion battery backup.
        </div>""", unsafe_allow_html=True)

    if df["Em LPG"].sum() > 0:
        any_tip = True
        st.markdown(f"""<div class="tip fuel">
            🔥 <b>LPG Canteen: {df['Em LPG'].sum():,.1f} kg CO₂.</b>
            Switch to induction cooking — eliminates Scope 1 combustion, reduces kitchen heat load by 30–40%.
        </div>""", unsafe_allow_html=True)

    avg_water_em = df["Water Emission"].mean()
    if avg_water_em > 50:
        any_tip = True
        st.markdown(f"""<div class="tip water">
            💧 <b>Water emissions avg {avg_water_em:.1f} kg CO₂e/month</b> (using effective EF {effective_ef:.4f}).
            Water-efficient fixtures (4-star WELS) reduce consumption 30–40%. Greywater recycling cuts WW treatment 20–50%.
        </div>""", unsafe_allow_html=True)

    if not any_tip:
        st.markdown(f"""<div class="tip good">
            🎉 <b>Building performance looks solid for {state_country}</b>.
            All categories within healthy ranges. Target 5–10% annual reduction via ISO 50001 audits.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 🏆 Emission Intensity Benchmarks")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Your Avg Monthly", f"{df['Total Emission'].mean():,.0f} kg CO₂e")
    b2.metric("IGBC Green Rating", "< 1,800 kg/floor")
    b3.metric("LEED Gold Reference", "< 1,200 kg/floor")
    b4.metric("Net-Zero Target", "< 500 kg/floor")

# ═══════════════════════════════════════════════════════════════════════════════
# NORMALISATION & UNCERTAINTY
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("### 📊 Normalization, T&D Impact & Uncertainty")

col_n1, col_n2 = st.columns(2)
with col_n1:
    floor_area = st.number_input("Building Floor Area (m²)", min_value=1.0, value=1000.0, step=50.0)
with col_n2:
    occupants  = st.number_input("Max Design Occupancy (persons)", min_value=1, value=100, step=5)

uncertainty_level = st.selectbox(
    "Data Quality Level",
    ["High Accuracy (±5%)", "Moderate Accuracy (±10%)", "Low Accuracy (±20%)"]
)
UNCERTAINTY_MAP = {"High Accuracy (±5%)": 0.05, "Moderate Accuracy (±10%)": 0.10, "Low Accuracy (±20%)": 0.20}
uncertainty_factor = UNCERTAINTY_MAP[uncertainty_level]

st.markdown("### 📊 Normalized Metrics")
n1, n2, n3, n4 = st.columns(4)
total_em = df["Total Emission"].sum()
td_total_uplift_all = df["T&D Uplift Emission (kg)"].sum()
n1.metric("🏢 CO₂ per m²",       f"{total_em / floor_area:.2f} kg/m²")
n2.metric("👥 CO₂ per Occupant", f"{total_em / occupants:.2f} kg/person")
n3.metric("📡 T&D Emission Add",  f"{td_total_uplift_all:.1f} kg CO₂e")
n4.metric("📡 T&D % of Total",   f"{td_total_uplift_all/total_em*100:.1f}%" if total_em > 0 else "—")

st.markdown("### 📉 Uncertainty Range")
low  = total_em * (1 - uncertainty_factor)
high = total_em * (1 + uncertainty_factor)
st.markdown(f"""<div class="card">
  <div class="card-lbl">UNCERTAINTY RANGE (±{uncertainty_factor*100:.0f}%)</div>
  <div class="card-val">{low:,.1f} – {high:,.1f}</div>
  <div class="card-unit">kg CO₂e total</div>
</div>""", unsafe_allow_html=True)

st.markdown("### 🧠 Key Assumptions")
st.markdown(f"""<div class="tip info">
• <b>T&D Losses:</b> {state_country} = {td_loss_rate*100:.1f}% · Effective EF = {grid_ef:.3f} ÷ (1 − {td_loss_rate:.3f}) = <b>{effective_ef:.4f} kg CO₂/kWh</b> · Source: {'CEA Annual Report 2022-23' if region_type == 'India – State' else 'IEA 2023 / World Bank'}<br>
• <b>Seasonal HVAC:</b> {climate_key.replace('_',' ').title()} climate profile · Multipliers from ASHRAE 90.1 / ECBC India degree-day analysis<br>
• <b>Occupancy Variation:</b> {building_type} profile · Affects HVAC, appliances, elevators, water suggestions<br>
• Renewable self-consumption and grid export credited at 50% of effective EF (off-peak displacement assumption)<br>
• Diesel EF {fuel_ef['diesel']['ef']} kg/L · LPG {fuel_ef['lpg']['ef']} kg/kg · Nat Gas {fuel_ef['natural_gas']['ef']} kg/m³ (PPAC / IPCC AR6 / DEFRA 2023)<br>
• Water energy intensity: EPRI / IWA · Wastewater CH₄ + N₂O: IPCC 2006 Tier 2<br>
• Waste EFs: IPCC 2006 / DEFRA 2023<br>
• Uniform uncertainty ±{uncertainty_factor*100:.0f}% applied to all categories
</div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"🌱 Building Carbon Tracker · 📍 {state_country} · "
    f"Grid EF: {grid_ef} · T&D: {td_loss_rate*100:.1f}% · Eff EF: {effective_ef:.4f} kg/kWh · "
    f"Climate: {climate_key} · {building_type} · "
    "CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · EPRI · IWA · GHG Protocol · PPAC · World Bank · "
    f"Session: {st.session_state.current_user}"
)
st.markdown("###  Normalization & Assumptions")

floor_area = st.number_input("Building Floor Area (m²)", min_value=1.0, value=1000.0, step=50.0)
occupants  = st.number_input("Number of Occupants", min_value=1, value=100, step=5)

st.markdown("#### ⚠️ Uncertainty Settings")

uncertainty_level = st.selectbox(
    "Data Quality Level",
    ["High Accuracy (±5%)", "Moderate Accuracy (±10%)", "Low Accuracy (±20%)"]
)

UNCERTAINTY_MAP = {
    "High Accuracy (±5%)": 0.05,
    "Moderate Accuracy (±10%)": 0.10,
    "Low Accuracy (±20%)": 0.20
}

uncertainty_factor = UNCERTAINTY_MAP[uncertainty_level]


co2_per_m2 = em_total / floor_area if floor_area > 0 else 0
co2_per_occupant = em_total / occupants if occupants > 0 else 0

lower_bound = em_total * (1 - uncertainty_factor)
upper_bound = em_total * (1 + uncertainty_factor)

monthly_data.append({
    "CO2 per m2": co2_per_m2,
    "CO2 per occupant": co2_per_occupant,
    "Emission Lower Bound": lower_bound,
    "Emission Upper Bound": upper_bound,
    "Uncertainty %": uncertainty_factor * 100,
})


st.markdown("###  Normalized Performance Metrics")

n1, n2 = st.columns(2)

n1.metric(
    "🏢 CO₂ per m²",
    f"{(df['Total Emission'].sum() / floor_area):.2f} kg/m²"
)

n2.metric(
    "👥 CO₂ per Occupant",
    f"{(df['Total Emission'].sum() / occupants):.2f} kg/person"
)


st.markdown("### Uncertainty Analysis")

total_em = df["Total Emission"].sum()
low = total_em * (1 - uncertainty_factor)
high = total_em * (1 + uncertainty_factor)

st.markdown(f"""
<div class="card">
  <div class="card-lbl">UNCERTAINTY RANGE</div>
  <div class="card-val">{low:,.1f} – {high:,.1f}</div>
  <div class="card-unit">kg CO₂e (±{uncertainty_factor*100:.0f}%)</div>
</div>
""", unsafe_allow_html=True)


st.markdown("###  Key Assumptions")

st.markdown(f"""
<div class="tip info">
• Grid emission factor assumed constant at <b>{grid_ef} kg CO₂/kWh</b><br>
• Water energy intensity based on regional averages<br>
• Waste factors from IPCC / DEFRA datasets<br>
• Fuel combustion assumed complete<br>
• Occupancy fixed at <b>{occupants}</b><br>
• Floor area fixed at <b>{floor_area} m²</b><br>
• Uniform uncertainty applied: ±{uncertainty_factor*100:.0f}%
</div>
""", unsafe_allow_html=True)


disp["CO₂ per m²"] = (disp["Total CO₂ (kg)"] / floor_area).round(2)
disp["CO₂ per occupant"] = (disp["Total CO₂ (kg)"] / occupants).round(2)
