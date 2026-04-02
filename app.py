import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Building Carbon Footprint Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #080c10;
    --bg2:       #0e1419;
    --bg3:       #151c24;
    --border:    #1e2a36;
    --border2:   #2a3a4a;
    --green:     #00d68f;
    --amber:     #ffb347;
    --red:       #ff5e5e;
    --blue:      #4ea8de;
    --purple:    #a78bfa;
    --text:      #d4e0ec;
    --text-dim:  #5a7a96;
    --text-mid:  #8ba8c2;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

.hero {
    background: linear-gradient(120deg, #091a12 0%, #0a141e 55%, #080c10 100%);
    border: 1px solid var(--border2);
    border-radius: 20px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content:''; position:absolute; top:-60px; right:-60px;
    width:240px; height:240px;
    background:radial-gradient(circle,rgba(0,214,143,.13) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
}
.hero-title { font-family:'Outfit',sans-serif; font-size:2rem; font-weight:700; color:var(--green); margin:0; letter-spacing:-.5px; }
.hero-sub { color:var(--text-mid); margin:.5rem 0 0 0; font-weight:300; font-size:.92rem; }
.loc-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:var(--bg3); border:1px solid var(--border2); border-radius:20px;
    padding:3px 12px; margin-top:.9rem;
    font-family:'JetBrains Mono',monospace; font-size:.7rem; color:var(--green);
}

.sec-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; font-weight:500;
    color:var(--text-dim); text-transform:uppercase; letter-spacing:3px;
    margin:1.8rem 0 .9rem 0; display:flex; align-items:center; gap:10px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border); }

.card { background:var(--bg2); border:1px solid var(--border); border-radius:13px; padding:1.1rem 1.4rem; margin-bottom:.7rem; transition:border-color .2s,box-shadow .2s; }
.card:hover { border-color:var(--border2); box-shadow:0 0 18px rgba(0,214,143,.05); }
.card-lbl { font-family:'JetBrains Mono',monospace; font-size:.62rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:2px; margin-bottom:.3rem; }
.card-val { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700; color:var(--text); line-height:1.1; }
.card-unit { font-family:'JetBrains Mono',monospace; font-size:.7rem; color:var(--green); margin-top:.15rem; }

.total-hero {
    background:linear-gradient(135deg,#071510,#080c10);
    border:1.5px solid var(--green); border-radius:18px; padding:1.8rem 2rem;
    text-align:center; box-shadow:0 0 40px rgba(0,214,143,.07); margin:1rem 0;
}
.total-num { font-family:'JetBrains Mono',monospace; font-size:3rem; font-weight:700; color:var(--green); line-height:1; }
.total-lbl { font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:2.5px; margin-top:.5rem; }

.ef-pill {
    display:inline-flex; align-items:center; gap:5px;
    background:var(--bg3); border:1px solid var(--border2); border-radius:6px;
    padding:3px 9px; font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--amber); margin:2px;
}

.tip { background:var(--bg2); border-left:3px solid var(--amber); border-radius:0 10px 10px 0; padding:.7rem 1rem; margin:.4rem 0; font-size:.87rem; color:var(--text); line-height:1.5; }
.tip.danger { border-left-color:var(--red); }
.tip.good   { border-left-color:var(--green); }
.tip.info   { border-left-color:var(--blue); }

.elec-summary {
    background:var(--bg3); border:1px solid var(--border); border-radius:10px;
    padding:.85rem 1.2rem; margin:.5rem 0 1rem 0;
}
.elec-summary-title { font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.4rem; }

section[data-testid="stSidebar"] { background:var(--bg) !important; border-right:1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { font-family:'JetBrains Mono',monospace; font-size:.78rem; color:var(--text-dim); }
.stTabs [aria-selected="true"] { color:var(--green) !important; border-bottom-color:var(--green) !important; }
[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace !important; color:var(--green) !important; font-size:1.35rem !important; }
[data-testid="stMetricLabel"] { color:var(--text-dim) !important; font-size:.68rem !important; text-transform:uppercase; letter-spacing:1px; }
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
.stSlider label {
    font-family:'JetBrains Mono',monospace !important;
    font-size:.7rem !important; color:var(--text-dim) !important;
    text-transform:uppercase; letter-spacing:1.2px;
}
div[data-testid="stNumberInput"] input {
    background:var(--bg3) !important; border-color:var(--border2) !important;
    color:var(--text) !important; font-family:'JetBrains Mono',monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# EMISSION FACTOR DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# India State Grid EF (kg CO₂/kWh) — CEA CO2 Baseline 2022-23
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

# International Grid EF (kg CO₂/kWh) — IEA 2023
INTL_COUNTRY_EF = {
    "United States": 0.386, "United Kingdom": 0.233, "Germany": 0.385,
    "France": 0.056, "Australia": 0.610, "China": 0.581,
    "Japan": 0.432, "Canada": 0.130, "Brazil": 0.074,
    "South Africa": 0.899, "UAE": 0.409, "Saudi Arabia": 0.726,
    "Singapore": 0.408, "Malaysia": 0.585, "Indonesia": 0.762,
    "Bangladesh": 0.673, "Pakistan": 0.444, "Sri Lanka": 0.635,
    "Nepal": 0.031, "Global Average": 0.475,
}

# Fuel EF (kg CO₂/unit) — IPCC AR6 / DEFRA 2023 / BEE India
FUEL_EF = {
    "India": {"diesel": 2.68, "lpg": 2.98, "natural_gas": 2.03},
    "default": {"diesel": 2.64, "lpg": 2.94, "natural_gas": 2.02},
}

# Water EF (kg CO₂/m³)
WATER_EF_MAP = {
    "India": 0.344, "United Kingdom": 0.344, "United States": 0.376,
    "Australia": 0.710, "default": 0.344,
}

# Waste EF (kg CO₂/kg) — IPCC 2006 / DEFRA
WASTE_EF = {
    "food_organic": 0.10, "paper": 1.06, "plastic": 6.00,
    "glass": 0.009, "general": 0.46,
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def get_grid_ef(rtype, loc):
    return INDIA_STATE_EF.get(loc, 0.820) if rtype == "India – State" else INTL_COUNTRY_EF.get(loc, 0.475)

def get_fuel_ef(rtype):
    return FUEL_EF["India"] if rtype == "India – State" else FUEL_EF["default"]

def get_water_ef(rtype, loc):
    if rtype == "India – State":
        return WATER_EF_MAP["India"]
    return WATER_EF_MAP.get(loc, WATER_EF_MAP["default"])

def plo(title):
    return dict(
        title=title, paper_bgcolor="#0e1419", plot_bgcolor="#0e1419",
        font=dict(color="#5a7a96", family="JetBrains Mono, monospace", size=10),
        title_font=dict(color="#d4e0ec", family="Outfit, sans-serif", size=13, weight=600),
        legend=dict(bgcolor="#0e1419", bordercolor="#1e2a36", borderwidth=1,
                    font=dict(color="#8ba8c2", size=9)),
        margin=dict(l=10, r=10, t=44, b=10),
        xaxis=dict(gridcolor="#131d27", linecolor="#1e2a36"),
        yaxis=dict(gridcolor="#131d27", linecolor="#1e2a36"),
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    building_name = st.text_input("Building Name", value="Tower A – Corporate HQ")
    num_months    = st.slider("Months to Track", 1, 12, 3)

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

    grid_ef   = get_grid_ef(region_type, state_country)
    fuel_ef   = get_fuel_ef(region_type)
    water_ef_ = get_water_ef(region_type, state_country)

    st.markdown("---")
    st.markdown("### 📡 Active Emission Factors")
    st.markdown(f"""
<div class="ef-pill">⚡ Grid {grid_ef} kg/kWh</div>
<div class="ef-pill">🛢 Diesel {fuel_ef['diesel']} kg/L</div>
<div class="ef-pill">🔥 LPG {fuel_ef['lpg']} kg/kg</div>
<div class="ef-pill">💨 Gas {fuel_ef['natural_gas']} kg/m³</div>
<div class="ef-pill">💧 Water {water_ef_} kg/m³</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("India CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · BEE India")

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div class="hero-title">🏢 Building Carbon Footprint Tracker</div>
  <div class="hero-sub">Location-calibrated emissions · HVAC / Lighting / Appliances / Elevators · Monthly analysis</div>
  <div class="loc-badge">📍 {state_country} &nbsp;·&nbsp; Grid EF: {grid_ef} kg CO₂/kWh</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MONTHLY INPUT TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-lbl">📥 Monthly Operational Data</div>', unsafe_allow_html=True)

monthly_data = []
tabs = st.tabs([f"📅 {MONTHS[i]}" for i in range(num_months)])

for i, tab in enumerate(tabs):
    with tab:
        m = MONTHS[i]
        st.markdown(f"#### {m} — *{building_name}*")

        # ── ELECTRICITY SUB-BREAKDOWN ─────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.4rem">⚡ Electricity Breakdown (kWh)</div>',
                    unsafe_allow_html=True)

        ec1, ec2, ec3, ec4 = st.columns(4)
        hvac       = ec1.number_input("🌡️ HVAC",       min_value=0.0, value=2000.0, step=50.0, key=f"hvac_{i}")
        lighting   = ec2.number_input("💡 Lighting",   min_value=0.0, value=800.0,  step=50.0, key=f"light_{i}")
        appliances = ec3.number_input("🖥️ Appliances", min_value=0.0, value=1500.0, step=50.0, key=f"app_{i}")
        elevators  = ec4.number_input("🛗 Elevators",  min_value=0.0, value=200.0,  step=25.0, key=f"elev_{i}")

        total_grid = hvac + lighting + appliances + elevators

        if total_grid > 0:
            pcts = {k: v/total_grid*100 for k, v in
                    {"HVAC": hvac, "Lighting": lighting, "Appliances": appliances, "Elevators": elevators}.items()}
            st.markdown(f"""<div class="elec-summary">
              <div class="elec-summary-title">Total Grid Draw</div>
              <span style="font-family:'JetBrains Mono',monospace;font-size:1.25rem;color:#d4e0ec;font-weight:700">{total_grid:,.0f} kWh</span>
              &nbsp;&nbsp;
              <span style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#5a7a96">
                HVAC {pcts['HVAC']:.0f}% &nbsp;·&nbsp; Lighting {pcts['Lighting']:.0f}% &nbsp;·&nbsp; Appliances {pcts['Appliances']:.0f}% &nbsp;·&nbsp; Elevators {pcts['Elevators']:.0f}%
              </span>
            </div>""", unsafe_allow_html=True)

        ren_col, _ = st.columns([1, 2])
        renew = ren_col.number_input("☀️ Renewable Generation (kWh)", min_value=0.0, value=0.0,
                                     step=50.0, key=f"renew_{i}")

        # ── FUEL ─────────────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">🔥 Fuel Usage</div>',
                    unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        diesel = fc1.number_input("🛢 Diesel (litres)",  min_value=0.0, value=0.0, step=10.0, key=f"diesel_{i}")
        lpg    = fc2.number_input("🔥 LPG (kg)",         min_value=0.0, value=0.0, step=5.0,  key=f"lpg_{i}")
        natgas = fc3.number_input("💨 Natural Gas (m³)", min_value=0.0, value=0.0, step=5.0,  key=f"natgas_{i}")

        # ── WATER & WASTE ────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">💧 Water & 🗑️ Waste</div>',
                    unsafe_allow_html=True)
        wc1, wc2, wc3, wc4, wc5, wc6 = st.columns(6)
        water_m3  = wc1.number_input("💧 Water (m³)",        min_value=0.0, value=200.0, step=10.0, key=f"water_{i}")
        w_organic = wc2.number_input("🥦 Organic (kg)",      min_value=0.0, value=50.0,  step=5.0,  key=f"worg_{i}")
        w_paper   = wc3.number_input("📄 Paper (kg)",        min_value=0.0, value=30.0,  step=5.0,  key=f"wpap_{i}")
        w_plastic = wc4.number_input("🧴 Plastic (kg)",      min_value=0.0, value=20.0,  step=5.0,  key=f"wpla_{i}")
        w_glass   = wc5.number_input("🫙 Glass (kg)",        min_value=0.0, value=10.0,  step=2.0,  key=f"wglass_{i}")
        w_general = wc6.number_input("🗑️ General (kg)",      min_value=0.0, value=40.0,  step=5.0,  key=f"wgen_{i}")

        # ── COMPUTE ──────────────────────────────────────────────────────
        net_elec       = max(0.0, total_grid - renew)
        em_hvac        = hvac       * grid_ef
        em_lighting    = lighting   * grid_ef
        em_appliances  = appliances * grid_ef
        em_elevators   = elevators  * grid_ef
        em_electricity = net_elec   * grid_ef
        em_diesel      = diesel  * fuel_ef["diesel"]
        em_lpg         = lpg     * fuel_ef["lpg"]
        em_natgas      = natgas  * fuel_ef["natural_gas"]
        em_fuel        = em_diesel + em_lpg + em_natgas
        em_water       = water_m3 * water_ef_
        em_waste       = (w_organic * WASTE_EF["food_organic"] +
                          w_paper   * WASTE_EF["paper"] +
                          w_plastic * WASTE_EF["plastic"] +
                          w_glass   * WASTE_EF["glass"] +
                          w_general * WASTE_EF["general"])
        em_total       = em_electricity + em_fuel + em_water + em_waste
        renewable_pct  = (renew / total_grid * 100) if total_grid > 0 else 0.0

        monthly_data.append({
            "Month": m,
            "HVAC (kWh)": hvac, "Lighting (kWh)": lighting,
            "Appliances (kWh)": appliances, "Elevators (kWh)": elevators,
            "Total Grid (kWh)": total_grid, "Renewables (kWh)": renew, "Net Elec (kWh)": net_elec,
            "Diesel (L)": diesel, "LPG (kg)": lpg, "Nat Gas (m³)": natgas,
            "Water (m³)": water_m3,
            "Organic (kg)": w_organic, "Paper (kg)": w_paper,
            "Plastic (kg)": w_plastic, "Glass (kg)": w_glass, "General (kg)": w_general,
            "Em HVAC": em_hvac, "Em Lighting": em_lighting,
            "Em Appliances": em_appliances, "Em Elevators": em_elevators,
            "Elec Emission": em_electricity,
            "Fuel Emission": em_fuel,
            "Water Emission": em_water,
            "Waste Emission": em_waste,
            "Total Emission": em_total,
            "Renewable %": renewable_pct,
            "Grid EF": grid_ef,
        })

df = pd.DataFrame(monthly_data)

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-lbl">📊 Results & Analysis</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs([
    "📋 Summary", "🔬 Month Detail", "⚡ Electricity", "📈 Charts", "💡 Recommendations"
])

# ── SUMMARY ──────────────────────────────────────────────────────────────────
with t1:
    st.markdown(f"#### Monthly CO₂ Summary — *{building_name}* &nbsp;|&nbsp; 📍 {state_country}")

    disp = df[["Month","Elec Emission","Fuel Emission","Water Emission","Waste Emission",
               "Total Emission","Renewable %","Grid EF"]].round(2).copy()
    disp.columns = ["Month","Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)",
                    "Total CO₂ (kg)","Renewable %","Grid EF (kg/kWh)"]

    tots = disp[["Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)","Total CO₂ (kg)"]].sum()
    tr = pd.DataFrame([["─ TOTAL ─", tots["Electricity (kg)"], tots["Fuel (kg)"],
                         tots["Water (kg)"], tots["Waste (kg)"], tots["Total CO₂ (kg)"], "─", "─"]],
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
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🌍 Total CO₂", f"{df['Total Emission'].sum():,.1f} kg")
    k2.metric("📅 Monthly Avg", f"{df['Total Emission'].mean():,.1f} kg")
    k3.metric("📌 Peak Month", df.loc[df['Total Emission'].idxmax(), 'Month'])
    k4.metric("☀️ Avg Renewable", f"{df['Renewable %'].mean():.1f}%")
    k5.metric("📡 Grid EF", f"{grid_ef} kg/kWh")

# ── MONTH DETAIL ─────────────────────────────────────────────────────────────
with t2:
    sel = st.selectbox("Select Month", df["Month"].tolist(), key="sel_month_detail")
    row = df[df["Month"] == sel].iloc[0]

    st.markdown(f"#### {sel} — Full Breakdown")

    ca, cb, cc, cd = st.columns(4)
    for col_, label, icon, hint in [
        (ca, "Elec Emission",  "⚡ Electricity", f"Net {row['Net Elec (kWh)']:,.0f} kWh"),
        (cb, "Fuel Emission",  "🔥 Fuel",         "Diesel + LPG + Gas"),
        (cc, "Water Emission", "💧 Water",        f"{row['Water (m³)']:,.0f} m³"),
        (cd, "Waste Emission", "🗑️ Waste",        "All categories"),
    ]:
        col_.markdown(f"""<div class="card">
            <div class="card-lbl">{icon}</div>
            <div class="card-val">{row[label]:,.1f}</div>
            <div class="card-unit">kg CO₂ · {hint}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="total-hero">
        <div class="total-lbl">Total Monthly Carbon Footprint</div>
        <div class="total-num">{row['Total Emission']:,.2f}</div>
        <div class="total-lbl" style="color:#00d68f;margin-top:.3rem">kg CO₂ &nbsp;·&nbsp; {row['Total Emission']/1000:.3f} tCO₂</div>
    </div>""", unsafe_allow_html=True)

    if row["Renewables (kWh)"] > 0:
        saved = row["Renewables (kWh)"] * grid_ef
        st.success(f"☀️ Renewables avoided **{saved:,.1f} kg CO₂** this month ({row['Renewable %']:.1f}% offset at {grid_ef} kg/kWh).")

    st.markdown("##### Component Ledger")
    ledger = {
        "Component": [
            "HVAC", "Lighting", "Appliances", "Elevators",
            "Renewable Offset (−)", "NET Electricity",
            "Diesel", "LPG", "Natural Gas",
            "Water Treatment",
            "Organic Waste", "Paper", "Plastic", "Glass", "General Waste"
        ],
        "Quantity": [
            f"{row['HVAC (kWh)']:.0f} kWh", f"{row['Lighting (kWh)']:.0f} kWh",
            f"{row['Appliances (kWh)']:.0f} kWh", f"{row['Elevators (kWh)']:.0f} kWh",
            f"−{row['Renewables (kWh)']:.0f} kWh", f"{row['Net Elec (kWh)']:.0f} kWh",
            f"{row['Diesel (L)']:.1f} L", f"{row['LPG (kg)']:.1f} kg", f"{row['Nat Gas (m³)']:.1f} m³",
            f"{row['Water (m³)']:.1f} m³",
            f"{row['Organic (kg)']:.1f} kg", f"{row['Paper (kg)']:.1f} kg",
            f"{row['Plastic (kg)']:.1f} kg", f"{row['Glass (kg)']:.1f} kg", f"{row['General (kg)']:.1f} kg",
        ],
        "EF Used": [
            grid_ef, grid_ef, grid_ef, grid_ef, f"−{grid_ef}", grid_ef,
            fuel_ef['diesel'], fuel_ef['lpg'], fuel_ef['natural_gas'],
            water_ef_,
            WASTE_EF['food_organic'], WASTE_EF['paper'], WASTE_EF['plastic'],
            WASTE_EF['glass'], WASTE_EF['general'],
        ],
        "Emission (kg CO₂)": [
            row['Em HVAC'], row['Em Lighting'], row['Em Appliances'], row['Em Elevators'],
            -row['Renewables (kWh)'] * grid_ef, row['Elec Emission'],
            row['Diesel (L)'] * fuel_ef['diesel'],
            row['LPG (kg)'] * fuel_ef['lpg'],
            row['Nat Gas (m³)'] * fuel_ef['natural_gas'],
            row['Water Emission'],
            row['Organic (kg)'] * WASTE_EF['food_organic'],
            row['Paper (kg)'] * WASTE_EF['paper'],
            row['Plastic (kg)'] * WASTE_EF['plastic'],
            row['Glass (kg)'] * WASTE_EF['glass'],
            row['General (kg)'] * WASTE_EF['general'],
        ]
    }
    ldf = pd.DataFrame(ledger)
    ldf["Emission (kg CO₂)"] = ldf["Emission (kg CO₂)"].round(3)
    st.dataframe(ldf, use_container_width=True, hide_index=True)

# ── ELECTRICITY BREAKDOWN ─────────────────────────────────────────────────────
with t3:
    st.markdown("#### ⚡ Electricity Sub-Category Analysis")

    ec1, ec2 = st.columns(2)
    with ec1:
        fig_e1 = go.Figure()
        for col_, clr, lbl in [
            ("Em HVAC","#4ea8de","HVAC"), ("Em Lighting","#ffb347","Lighting"),
            ("Em Appliances","#a78bfa","Appliances"), ("Em Elevators","#00d68f","Elevators")
        ]:
            fig_e1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                    marker_color=clr, marker_line_width=0))
        fig_e1.update_layout(**plo("Electricity Emissions by Sub-Category (kg CO₂)"),
                              barmode="stack", yaxis_title="kg CO₂")
        st.plotly_chart(fig_e1, use_container_width=True)

    with ec2:
        avg_kwh = [df["HVAC (kWh)"].mean(), df["Lighting (kWh)"].mean(),
                   df["Appliances (kWh)"].mean(), df["Elevators (kWh)"].mean()]
        fig_e2 = go.Figure(go.Pie(
            labels=["HVAC","Lighting","Appliances","Elevators"], values=avg_kwh, hole=0.58,
            marker=dict(colors=["#4ea8de","#ffb347","#a78bfa","#00d68f"],
                        line=dict(color="#0e1419", width=2)),
            textfont=dict(family="JetBrains Mono", color="#d4e0ec", size=10),
        ))
        fig_e2.update_layout(**plo("Avg kWh Consumption Share"))
        st.plotly_chart(fig_e2, use_container_width=True)

    elec_tbl = df[["Month","HVAC (kWh)","Lighting (kWh)","Appliances (kWh)","Elevators (kWh)",
                    "Total Grid (kWh)","Renewables (kWh)","Net Elec (kWh)","Elec Emission","Renewable %"]].round(2).copy()
    elec_tbl.columns = ["Month","HVAC","Lighting","Appliances","Elevators",
                         "Total Grid","Renewables","Net kWh","Net Emission (kg CO₂)","Renewable %"]
    st.dataframe(elec_tbl, use_container_width=True, hide_index=True)

    avg_hvac_pct = (df["HVAC (kWh)"].mean() / df["Total Grid (kWh)"].mean() * 100) if df["Total Grid (kWh)"].mean() > 0 else 0
    if avg_hvac_pct > 45:
        st.markdown(f"""<div class="tip danger" style="margin-top:.8rem">
            🌡️ <b>HVAC is consuming {avg_hvac_pct:.0f}% of total electricity</b> — above recommended 35-40%.
            Audit chiller performance, implement BMS setback schedules, and review building insulation.
        </div>""", unsafe_allow_html=True)

# ── CHARTS ────────────────────────────────────────────────────────────────────
with t4:
    ch1, ch2 = st.columns(2)

    with ch1:
        fig1 = go.Figure()
        for col_, clr, lbl in [
            ("Elec Emission","#00d68f","Electricity"),
            ("Fuel Emission","#ffb347","Fuel"),
            ("Water Emission","#4ea8de","Water"),
            ("Waste Emission","#a78bfa","Waste"),
        ]:
            fig1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                  marker_color=clr, marker_line_width=0))
        fig1.update_layout(**plo("Monthly CO₂ by Category (kg)"),
                           barmode="stack", yaxis_title="kg CO₂")
        st.plotly_chart(fig1, use_container_width=True)

    with ch2:
        avg_vals = [df["Elec Emission"].mean(), df["Fuel Emission"].mean(),
                    df["Water Emission"].mean(), df["Waste Emission"].mean()]
        fig2 = go.Figure(go.Pie(
            labels=["Electricity","Fuel","Water","Waste"], values=avg_vals, hole=0.58,
            marker=dict(colors=["#00d68f","#ffb347","#4ea8de","#a78bfa"],
                        line=dict(color="#0e1419", width=2)),
            textfont=dict(family="JetBrains Mono", color="#d4e0ec", size=10),
        ))
        fig2.update_layout(**plo("Avg Emission Share Across Months"))
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["Month"], y=df["Total Emission"], mode="lines+markers",
        line=dict(color="#00d68f", width=2.5),
        marker=dict(size=7, color="#00d68f", line=dict(color="#080c10", width=2)),
        fill="tozeroy", fillcolor="rgba(0,214,143,.07)", name="Total CO₂"
    ))
    fig3.update_layout(**plo("Total Monthly CO₂ Trend (kg)"), yaxis_title="kg CO₂")
    st.plotly_chart(fig3, use_container_width=True)

    if df["Renewables (kWh)"].sum() > 0:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Total Grid (kWh)"], name="Grid Draw", marker_color="#ff5e5e"))
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Renewables (kWh)"], name="Renewable Gen", marker_color="#00d68f"))
        fig4.update_layout(**plo("Grid Draw vs Renewable Generation (kWh)"),
                           barmode="group", yaxis_title="kWh")
        st.plotly_chart(fig4, use_container_width=True)

# ── RECOMMENDATIONS ───────────────────────────────────────────────────────────
with t5:
    st.markdown(f"#### 💡 Location-Aware Recommendations — {state_country}")
    any_tip = False

    if grid_ef > 0.85:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            📡 <b>High grid emission factor ({grid_ef} kg/kWh)</b> for {state_country}.
            This is among the most carbon-intensive grids. Prioritise on-site solar, RECs
            (Renewable Energy Certificates) or a green PPA to neutralise grid impact immediately.
        </div>""", unsafe_allow_html=True)

    avg_hvac_pct = (df["Em HVAC"].sum() / df["Elec Emission"].sum() * 100) if df["Elec Emission"].sum() > 0 else 0
    if avg_hvac_pct > 45:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            🌡️ <b>HVAC is {avg_hvac_pct:.0f}% of electricity emissions</b>.
            Upgrade to inverter-class chillers (COP ≥ 5.0), deploy BMS setback schedules,
            and improve building envelope insulation to cut cooling load by 20–35%.
        </div>""", unsafe_allow_html=True)

    avg_light_pct = (df["Em Lighting"].sum() / df["Elec Emission"].sum() * 100) if df["Elec Emission"].sum() > 0 else 0
    if avg_light_pct > 20:
        any_tip = True
        st.markdown(f"""<div class="tip">
            💡 <b>Lighting is {avg_light_pct:.0f}% of electricity emissions</b>.
            Full LED retrofit + daylight sensors + occupancy-based controls can reduce lighting energy by 40–60%.
        </div>""", unsafe_allow_html=True)

    if df["Renewable %"].mean() < 10:
        any_tip = True
        st.markdown(f"""<div class="tip info">
            ☀️ <b>Renewable offset averages only {df['Renewable %'].mean():.1f}%</b>.
            At {state_country}'s {grid_ef} kg/kWh grid EF, each 1,000 kWh of solar avoids
            {grid_ef*1000:.0f} kg CO₂. A 50 kWp rooftop system typically generates 5,500–6,500 kWh/month.
        </div>""", unsafe_allow_html=True)

    if df["Fuel Emission"].mean() > 100:
        any_tip = True
        st.markdown(f"""<div class="tip">
            🔥 <b>Fuel emissions average {df['Fuel Emission'].mean():,.0f} kg CO₂/month</b>.
            Replace diesel gensets with grid-tied UPS + lithium battery backup.
            LPG boilers can often be replaced with heat-pump technology for 60–70% emission reduction.
        </div>""", unsafe_allow_html=True)

    if df["Plastic (kg)"].mean() > 15:
        any_tip = True
        st.markdown(f"""<div class="tip">
            🧴 <b>Plastic waste averages {df['Plastic (kg)'].mean():.0f} kg/month</b>
            (EF: 6.0 kg CO₂/kg — highest of all waste types).
            Implement source segregation, vendor take-back schemes, and reduce single-use plastics.
        </div>""", unsafe_allow_html=True)

    if not any_tip:
        st.markdown(f"""<div class="tip good">
            🎉 <b>Building performance looks solid for {state_country}</b>.
            All emission categories are within healthy ranges. Target 5–10% annual reduction
            through quarterly energy audits and ISO 50001 Energy Management practices.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 🏆 Emission Intensity Benchmarks")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Your Avg Monthly", f"{df['Total Emission'].mean():,.0f} kg")
    b2.metric("IGBC Green Rating", "< 1,800 kg/floor")
    b3.metric("LEED Gold Reference", "< 1,200 kg/floor")
    b4.metric("Net-Zero Target", "< 500 kg/floor")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"🌱 Building Carbon Tracker · 📍 {state_country} · Grid EF: {grid_ef} kg CO₂/kWh · "
    "Sources: India CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · BEE India · PPAC · GHG Protocol"
)
