import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    --text:      #c8daea;
    --text-dim:  #4a6a88;
    --text-mid:  #7a9ab8;
    --water1:    #5ab4f5;
    --water2:    #00d4d4;
    --waste1:    #b09fff;
    --waste2:    #e07bff;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #050f0a 0%, #080e18 60%, #060a0e 100%);
    border: 1px solid var(--border2);
    border-radius: 22px;
    padding: 2.4rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:''; position:absolute; top:-80px; right:-80px;
    width:320px; height:320px;
    background:radial-gradient(circle,rgba(0,229,160,.09) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
}
.hero::after {
    content:''; position:absolute; bottom:-60px; left:30%;
    width:200px; height:200px;
    background:radial-gradient(circle,rgba(90,180,245,.06) 0%,transparent 65%);
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

/* ── SECTION LABELS ── */
.sec-lbl {
    font-family:'JetBrains Mono',monospace; font-size:.62rem; font-weight:500;
    color:var(--text-dim); text-transform:uppercase; letter-spacing:3px;
    margin:2rem 0 1rem 0; display:flex; align-items:center; gap:12px;
}
.sec-lbl::after { content:''; flex:1; height:1px; background:var(--border); }

/* ── CARDS ── */
.card {
    background:var(--bg2); border:1px solid var(--border); border-radius:14px;
    padding:1.15rem 1.5rem; margin-bottom:.7rem;
    transition:border-color .25s, box-shadow .25s;
}
.card:hover { border-color:var(--border2); box-shadow:0 0 24px rgba(0,229,160,.05); }
.card-icon { font-size:1.1rem; margin-bottom:.35rem; }
.card-lbl { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:2px; margin-bottom:.3rem; }
.card-val { font-family:'JetBrains Mono',monospace; font-size:1.75rem; font-weight:700; color:var(--text); line-height:1.1; }
.card-unit { font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--green); margin-top:.2rem; }

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
.water-component {
    background:rgba(90,180,245,.06); border:1px solid rgba(90,180,245,.12);
    border-radius:10px; padding:.75rem 1rem; margin-bottom:.5rem;
}
.water-component-label { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:1.5px; }
.water-component-value { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:600; color:var(--blue); }
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
.waste-panel-title {
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:var(--purple);
    text-transform:uppercase; letter-spacing:2.5px; margin-bottom:1rem;
    display:flex; align-items:center; gap:8px;
}
.waste-category {
    border-radius:10px; padding:.75rem 1rem; margin-bottom:.5rem;
    display:flex; align-items:center; gap:12px;
}
.waste-organic  { background:rgba(255,160,80,.06);  border:1px solid rgba(255,160,80,.15); }
.waste-recycl   { background:rgba(0,229,160,.05);   border:1px solid rgba(0,229,160,.12); }
.waste-landfill { background:rgba(255,95,95,.06);   border:1px solid rgba(255,95,95,.12); }
.waste-incinerate { background:rgba(255,192,77,.06); border:1px solid rgba(255,192,77,.12); }
.waste-cat-icon { font-size:1.3rem; }
.waste-cat-info { flex:1; }
.waste-cat-name { font-family:'JetBrains Mono',monospace; font-size:.72rem; color:var(--text); font-weight:500; }
.waste-cat-desc { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); margin-top:.1rem; }
.waste-cat-em   { font-family:'JetBrains Mono',monospace; font-size:.85rem; font-weight:600; }

/* ── TOTAL HERO ── */
.total-hero {
    background:linear-gradient(135deg,#050f0a,#060a0e);
    border:1.5px solid var(--green); border-radius:20px; padding:2rem 2.4rem;
    text-align:center; box-shadow:0 0 60px rgba(0,229,160,.08); margin:1.2rem 0;
    position:relative; overflow:hidden;
}
.total-hero::before {
    content:''; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    width:260px; height:260px;
    background:radial-gradient(circle,rgba(0,229,160,.07) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
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
.ef-pill.blue  { color:var(--blue);   border-color:rgba(90,180,245,.25);  background:rgba(90,180,245,.05); }
.ef-pill.green { color:var(--green);  border-color:rgba(0,229,160,.25);   background:rgba(0,229,160,.05); }
.ef-pill.purple{ color:var(--purple); border-color:rgba(176,159,255,.25); background:rgba(176,159,255,.05); }
.ef-pill.cyan  { color:var(--cyan);   border-color:rgba(0,212,212,.25);   background:rgba(0,212,212,.05); }
.ef-pill.red   { color:var(--red);    border-color:rgba(255,95,95,.25);   background:rgba(255,95,95,.05); }

/* ── TIPS ── */
.tip { background:var(--bg2); border-left:3px solid var(--amber); border-radius:0 12px 12px 0; padding:.85rem 1.1rem; margin:.5rem 0; font-size:.87rem; color:var(--text); line-height:1.55; }
.tip.danger { border-left-color:var(--red); }
.tip.good   { border-left-color:var(--green); }
.tip.info   { border-left-color:var(--blue); }
.tip.water  { border-left-color:var(--cyan); }
.tip.waste  { border-left-color:var(--purple); }

/* ── ELEC SUMMARY ── */
.elec-summary {
    background:var(--bg3); border:1px solid var(--border); border-radius:10px;
    padding:.9rem 1.3rem; margin:.5rem 0 1rem 0;
}
.elec-summary-title { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:.5rem; }

/* ── WATER DETAIL SUMMARY ── */
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

/* ── DIVIDER ── */
hr { border-color:var(--border) !important; margin:1.5rem 0 !important; }
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
    "India":   {"diesel": 2.68, "lpg": 2.98, "natural_gas": 2.03},
    "default": {"diesel": 2.64, "lpg": 2.94, "natural_gas": 2.02},
}

# ─── WATER EMISSION FACTORS (ENHANCED) ───────────────────────────────────────
# Energy intensity of water supply (kWh/m³) — EPRI / IWA / Regional
WATER_ENERGY_INTENSITY = {
    # (supply_kwh_per_m3, treatment_kwh_per_m3, distribution_kwh_per_m3)
    # supply = abstraction + primary treatment; treatment = advanced/wastewater; distribution = pumping
    "India": {
        "supply_kwh_per_m3":       0.40,   # Surface water abstraction + primary treatment
        "treatment_kwh_per_m3":    0.35,   # Wastewater treatment (activated sludge)
        "distribution_kwh_per_m3": 0.25,   # Distribution pumping
        "wastewater_return_rate":  0.80,   # Fraction of supply that becomes wastewater
        "ch4_ef_kg_per_m3":        0.023,  # Direct CH4 from anaerobic wastewater (IPCC 2006)
        "n2o_ef_kg_co2e_per_m3":   0.007,  # N₂O from nitrification/denitrification
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

# ─── WASTE EMISSION FACTORS (ENHANCED) ───────────────────────────────────────
# Disposal-method-specific EFs (kg CO₂e/kg) — IPCC 2006, DEFRA 2023, GHG Protocol
WASTE_EF_MATRIX = {
    # Organic / Food Waste
    "organic": {
        "landfill":    0.587,   # High CH4 from anaerobic decomposition (IPCC Tier 2)
        "composting":  0.055,   # Aerobic, low CH4
        "anaerobic_digestion": 0.020,  # Biogas captured — net low
        "incineration":0.020,   # Minimal – mostly CO2 from combustion, partial biogenic
    },
    # Recyclable: Paper / Cardboard
    "paper": {
        "landfill":    0.879,   # Slow anaerobic decay
        "recycling":   0.021,   # Collection + reprocessing energy only
        "incineration":1.062,   # DEFRA combustion EF
    },
    # Recyclable: Plastic
    "plastic": {
        "landfill":    0.024,   # Stable, minimal decay
        "recycling":   0.043,   # Mechanical recycling energy
        "incineration":2.948,   # High fossil CO2 from combustion
    },
    # Glass
    "glass": {
        "landfill":    0.009,
        "recycling":   0.005,
        "incineration":0.009,
    },
    # Metal (incl. cans, aluminium foil)
    "metal": {
        "landfill":    0.013,
        "recycling":   0.008,
        "incineration":0.013,
    },
    # General / Mixed (non-classified)
    "general": {
        "landfill":    0.460,
        "incineration":0.580,
        "recycling":   0.200,
    },
    # Hazardous / E-waste
    "hazardous": {
        "landfill":    0.600,
        "incineration":0.900,
        "specialist_treatment": 0.250,
    },
}

# Waste CH4 GWP-100 = 27.9 (AR6)
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def get_grid_ef(rtype, loc):
    return INDIA_STATE_EF.get(loc, 0.820) if rtype == "India – State" else INTL_COUNTRY_EF.get(loc, 0.475)

def get_fuel_ef(rtype):
    return FUEL_EF["India"] if rtype == "India – State" else FUEL_EF["default"]

def get_water_profile(rtype, loc):
    """Return water energy intensity profile for the region."""
    if rtype == "India – State":
        return WATER_ENERGY_INTENSITY["India"]
    if loc in WATER_ENERGY_INTENSITY:
        return WATER_ENERGY_INTENSITY[loc]
    return WATER_ENERGY_INTENSITY["default"]

def calc_water_emissions(water_m3, water_profile, grid_ef):
    """
    Detailed water emission calculation:
      1. Supply energy (abstraction + primary treatment)
      2. Distribution / pumping energy
      3. Wastewater treatment energy
      4. Direct CH4 fugitive from wastewater
      5. Direct N2O from nitrification/denitrification
    Returns dict with component breakdown.
    """
    wp = water_profile
    ww_vol = water_m3 * wp["wastewater_return_rate"]

    em_supply       = water_m3  * wp["supply_kwh_per_m3"]       * grid_ef
    em_distribution = water_m3  * wp["distribution_kwh_per_m3"] * grid_ef
    em_ww_treatment = ww_vol    * wp["treatment_kwh_per_m3"]    * grid_ef
    em_ch4          = ww_vol    * wp["ch4_ef_kg_per_m3"]
    em_n2o          = ww_vol    * wp["n2o_ef_kg_co2e_per_m3"]
    em_total        = em_supply + em_distribution + em_ww_treatment + em_ch4 + em_n2o

    return {
        "total":          em_total,
        "supply":         em_supply,
        "distribution":   em_distribution,
        "ww_treatment":   em_ww_treatment,
        "ch4_fugitive":   em_ch4,
        "n2o_direct":     em_n2o,
        "ww_volume_m3":   ww_vol,
        # Energy breakdown (kWh)
        "supply_kwh":     water_m3 * wp["supply_kwh_per_m3"],
        "dist_kwh":       water_m3 * wp["distribution_kwh_per_m3"],
        "ww_kwh":         ww_vol   * wp["treatment_kwh_per_m3"],
        "total_kwh":      water_m3 * (wp["supply_kwh_per_m3"] + wp["distribution_kwh_per_m3"])
                          + ww_vol * wp["treatment_kwh_per_m3"],
    }

def calc_waste_emissions(waste_inputs):
    """
    waste_inputs: dict of {waste_type: {quantity_kg, disposal_method}}
    Returns total emission and per-category breakdown.
    """
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
    grid_ef       = get_grid_ef(region_type, state_country)
    fuel_ef       = get_fuel_ef(region_type)
    water_profile = get_water_profile(region_type, state_country)

    st.markdown("---")
    st.markdown("### 📡 Active Emission Factors")
    st.markdown(f"""
<div class="ef-pills">
<div class="ef-pill green">⚡ Grid {grid_ef} kg/kWh</div>
<div class="ef-pill">🛢 Diesel {fuel_ef['diesel']} kg/L</div>
<div class="ef-pill">🔥 LPG {fuel_ef['lpg']} kg/kg</div>
<div class="ef-pill">💨 Gas {fuel_ef['natural_gas']} kg/m³</div>
</div>
<div class="ef-pills">
<div class="ef-pill blue">💧 Supply {water_profile['supply_kwh_per_m3']} kWh/m³</div>
<div class="ef-pill cyan">🚿 Pumping {water_profile['distribution_kwh_per_m3']} kWh/m³</div>
<div class="ef-pill blue">⬇️ WW Treat {water_profile['treatment_kwh_per_m3']} kWh/m³</div>
<div class="ef-pill cyan">♻️ WW Return {water_profile['wastewater_return_rate']*100:.0f}%</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("India CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · EPRI · IWA · GHG Protocol")

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">Carbon Intelligence Platform</div>
  <div class="hero-title">🏢 Building Carbon Footprint Tracker</div>
  <div class="hero-sub">
    Location-calibrated operational emissions &nbsp;·&nbsp; HVAC / Lighting / Appliances / Elevators<br>
    Enhanced water cycle accounting &nbsp;·&nbsp; Waste disposal method classification
  </div>
  <div class="hero-badges">
    <span class="badge green">📍 {state_country}</span>
    <span class="badge green">⚡ Grid EF: {grid_ef} kg CO₂/kWh</span>
    <span class="badge blue">💧 Water EI: {water_profile['supply_kwh_per_m3']+water_profile['distribution_kwh_per_m3']+water_profile['wastewater_return_rate']*water_profile['treatment_kwh_per_m3']:.2f} kWh/m³</span>
    <span class="badge">🌱 IPCC AR6 · IEA 2023 · DEFRA 2023</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MONTHLY INPUT TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-lbl">📥 Monthly Operational Data</div>', unsafe_allow_html=True)

monthly_data = []
tabs = st.tabs([f"📅 {MONTHS[i]}" for i in range(num_months)])

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
    "organic":   ("🥦 Organic / Food", "High CH4 if landfilled — composting cuts 90%"),
    "paper":     ("📄 Paper / Cardboard", "Recycling EF is 42× lower than landfill"),
    "plastic":   ("🧴 Plastic", "Incineration EF: 2.95 kg/kg — avoid!"),
    "glass":     ("🫙 Glass", "Stable — recycling is always best option"),
    "metal":     ("🔩 Metal / Aluminium", "High embodied energy — recycling saves 95%"),
    "general":   ("🗑️ General / Mixed", "Mixed stream; segregate to reduce EF"),
    "hazardous": ("⚠️ Hazardous / E-Waste", "Requires specialist treatment"),
}

for i, tab in enumerate(tabs):
    with tab:
        m = MONTHS[i]
        st.markdown(f"#### {m} — *{building_name}*")

        # ── ELECTRICITY ───────────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.4rem">⚡ Electricity Breakdown (kWh)</div>',
                    unsafe_allow_html=True)
        ec1, ec2, ec3, ec4 = st.columns(4)
        hvac       = ec1.number_input("🌡️ HVAC",       min_value=0.0, value=2000.0, step=50.0,  key=f"hvac_{i}")
        lighting   = ec2.number_input("💡 Lighting",   min_value=0.0, value=800.0,  step=50.0,  key=f"light_{i}")
        appliances = ec3.number_input("🖥️ Appliances", min_value=0.0, value=1500.0, step=50.0,  key=f"app_{i}")
        elevators  = ec4.number_input("🛗 Elevators",  min_value=0.0, value=200.0,  step=25.0,  key=f"elev_{i}")
        total_grid = hvac + lighting + appliances + elevators

        if total_grid > 0:
            pcts = {k: v/total_grid*100 for k, v in
                    {"HVAC": hvac, "Lighting": lighting, "Appliances": appliances, "Elevators": elevators}.items()}
            st.markdown(f"""<div class="elec-summary">
              <div class="elec-summary-title">Total Grid Draw</div>
              <span style="font-family:'JetBrains Mono',monospace;font-size:1.25rem;color:#c8daea;font-weight:700">{total_grid:,.0f} kWh</span>
              &nbsp;&nbsp;
              <span style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#4a6a88">
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

        # ── WATER (ENHANCED) ──────────────────────────────────────────────
        st.markdown('<div class="sec-lbl" style="margin-top:.6rem">💧 Water — Supply, Pumping & Wastewater Treatment</div>',
                    unsafe_allow_html=True)

        w_col1, w_col2 = st.columns([1, 2])
        with w_col1:
            water_m3 = st.number_input("Total Water Consumption (m³)", min_value=0.0,
                                        value=200.0, step=10.0, key=f"water_{i}")

        # Compute water emissions
        water_em = calc_water_emissions(water_m3, water_profile, grid_ef)

        with w_col2:
            st.markdown(f"""<div class="water-detail-summary">
              <div class="elec-summary-title">💧 Water Emission Breakdown — {water_m3:.0f} m³ input</div>
              <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-top:.4rem">
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">Supply</div>
                  <div style="font-size:.9rem;color:#5ab4f5;font-weight:600">{water_em['supply']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂ ({water_em['supply_kwh']:.1f} kWh)</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">Pumping</div>
                  <div style="font-size:.9rem;color:#5ab4f5;font-weight:600">{water_em['distribution']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂ ({water_em['dist_kwh']:.1f} kWh)</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">WW Treat</div>
                  <div style="font-size:.9rem;color:#00d4d4;font-weight:600">{water_em['ww_treatment']:.2f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂ ({water_em['ww_kwh']:.1f} kWh)</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">CH₄ Fugitive</div>
                  <div style="font-size:.9rem;color:#ffc04d;font-weight:600">{water_em['ch4_fugitive']:.3f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e ({water_em['ww_volume_m3']:.0f} m³ WW)</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace">
                  <div style="font-size:.58rem;color:#4a6a88;text-transform:uppercase">N₂O Direct</div>
                  <div style="font-size:.9rem;color:#ffc04d;font-weight:600">{water_em['n2o_direct']:.3f}</div>
                  <div style="font-size:.55rem;color:#4a6a88">kg CO₂e</div>
                </div>
              </div>
              <div style="margin-top:.7rem;padding-top:.5rem;border-top:1px solid #1a2535;font-family:'JetBrains Mono',monospace">
                <span style="font-size:.6rem;color:#4a6a88">TOTAL WATER EMISSION</span>
                <span style="font-size:1.05rem;color:#5ab4f5;font-weight:700;margin-left:10px">{water_em['total']:.2f} kg CO₂e</span>
                <span style="font-size:.6rem;color:#4a6a88;margin-left:8px">({water_em['total_kwh']:.1f} kWh total energy)</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── WASTE (ENHANCED) ──────────────────────────────────────────────
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
                                      step=2.0, key=f"w_{wtype}_{i}")
                method = st.selectbox(f"Disposal", WASTE_DISPOSAL_OPTIONS[wtype],
                                      key=f"wd_{wtype}_{i}",
                                      label_visibility="collapsed")
                waste_inputs_raw[wtype] = {"qty": qty, "method": method}

        # ── COMPUTE ───────────────────────────────────────────────────────
        net_elec       = max(0.0, total_grid - renew)
        em_hvac        = hvac       * grid_ef
        em_lighting    = lighting   * grid_ef
        em_appliances  = appliances * grid_ef
        em_elevators   = elevators  * grid_ef
        em_electricity = net_elec   * grid_ef

        em_diesel  = diesel * fuel_ef["diesel"]
        em_lpg     = lpg    * fuel_ef["lpg"]
        em_natgas  = natgas * fuel_ef["natural_gas"]
        em_fuel    = em_diesel + em_lpg + em_natgas

        em_water = water_em["total"]

        em_waste_total, waste_breakdown = calc_waste_emissions(waste_inputs_raw)

        em_total      = em_electricity + em_fuel + em_water + em_waste_total
        renewable_pct = (renew / total_grid * 100) if total_grid > 0 else 0.0

        monthly_data.append({
            "Month": m,
            "HVAC (kWh)": hvac, "Lighting (kWh)": lighting,
            "Appliances (kWh)": appliances, "Elevators (kWh)": elevators,
            "Total Grid (kWh)": total_grid, "Renewables (kWh)": renew, "Net Elec (kWh)": net_elec,
            "Diesel (L)": diesel, "LPG (kg)": lpg, "Nat Gas (m³)": natgas,
            "Water (m³)": water_m3,
            "Water Supply Emission": water_em["supply"],
            "Water Distribution Emission": water_em["distribution"],
            "Water WW Treatment Emission": water_em["ww_treatment"],
            "Water CH4 Emission": water_em["ch4_fugitive"],
            "Water N2O Emission": water_em["n2o_direct"],
            "Water Total kWh": water_em["total_kwh"],
            # Waste per category
            **{f"Waste {wt} (kg)": waste_inputs_raw[wt]["qty"] for wt in waste_inputs_raw},
            **{f"Waste {wt} Method": waste_inputs_raw[wt]["method"] for wt in waste_inputs_raw},
            **{f"Em Waste {wt}": waste_breakdown[wt]["emission"] for wt in waste_breakdown},
            # Sub-emissions
            "Em HVAC": em_hvac, "Em Lighting": em_lighting,
            "Em Appliances": em_appliances, "Em Elevators": em_elevators,
            "Elec Emission": em_electricity,
            "Fuel Emission": em_fuel,
            "Water Emission": em_water,
            "Waste Emission": em_waste_total,
            "Total Emission": em_total,
            "Renewable %": renewable_pct,
            "Grid EF": grid_ef,
        })

# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(monthly_data)
st.markdown('<div class="sec-lbl">📊 Results & Analysis</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6 = st.tabs([
    "📋 Summary", "🔬 Month Detail", "⚡ Electricity", "💧 Water Deep Dive", "📈 Charts", "💡 Recommendations"
])

# ── SUMMARY ───────────────────────────────────────────────────────────────────
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

# ── MONTH DETAIL ──────────────────────────────────────────────────────────────
with t2:
    sel = st.selectbox("Select Month", df["Month"].tolist(), key="sel_month_detail")
    row = df[df["Month"] == sel].iloc[0]
    st.markdown(f"#### {sel} — Full Breakdown")

    ca, cb, cc, cd = st.columns(4)
    for col_, label, icon, hint in [
        (ca, "Elec Emission",  "⚡ Electricity", f"Net {row['Net Elec (kWh)']:,.0f} kWh"),
        (cb, "Fuel Emission",  "🔥 Fuel",         "Diesel + LPG + Gas"),
        (cc, "Water Emission", "💧 Water",        f"{row['Water (m³)']:,.0f} m³ supply"),
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
    </div>""", unsafe_allow_html=True)

    if row["Renewables (kWh)"] > 0:
        saved = row["Renewables (kWh)"] * grid_ef
        st.success(f"☀️ Renewables avoided **{saved:,.1f} kg CO₂** this month ({row['Renewable %']:.1f}% offset at {grid_ef} kg/kWh).")

    # ── Water sub-breakdown ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("##### 💧 Water Emission Ledger")
    st.markdown(f"""<div class="water-panel">
      <div class="water-panel-title">💧 Water Lifecycle Emissions — {row['Water (m³)']:,.0f} m³ consumed</div>
      <div class="water-breakdown-row"><span class="wb-label">🏗️ Supply & Abstraction Energy</span><span class="wb-value">{row['Water (m³)']*water_profile['supply_kwh_per_m3']:.1f} kWh</span><span class="wb-emission">{row['Water Supply Emission']:.3f} kg CO₂e</span></div>
      <div class="water-breakdown-row"><span class="wb-label">🚰 Distribution & Pumping Energy</span><span class="wb-value">{row['Water (m³)']*water_profile['distribution_kwh_per_m3']:.1f} kWh</span><span class="wb-emission">{row['Water Distribution Emission']:.3f} kg CO₂e</span></div>
      <div class="water-breakdown-row"><span class="wb-label">🔄 Wastewater Volume ({water_profile['wastewater_return_rate']*100:.0f}% return)</span><span class="wb-value">{row['Water (m³)']*water_profile['wastewater_return_rate']:.1f} m³</span><span class="wb-emission">→ treated</span></div>
      <div class="water-breakdown-row"><span class="wb-label">⚙️ Wastewater Treatment Energy</span><span class="wb-value">{row['Water Total kWh'] - row['Water (m³)']*(water_profile['supply_kwh_per_m3']+water_profile['distribution_kwh_per_m3']):.1f} kWh</span><span class="wb-emission">{row['Water WW Treatment Emission']:.3f} kg CO₂e</span></div>
      <div class="water-breakdown-row"><span class="wb-label">💨 Fugitive CH₄ (anaerobic decomposition)</span><span class="wb-value">IPCC Tier 2</span><span class="wb-emission">{row['Water CH4 Emission']:.4f} kg CO₂e</span></div>
      <div class="water-breakdown-row"><span class="wb-label">🌫️ Direct N₂O (nitrification/denitrification)</span><span class="wb-value">IPCC 2006</span><span class="wb-emission">{row['Water N2O Emission']:.4f} kg CO₂e</span></div>
      <div class="water-breakdown-row" style="border-top:1px solid rgba(90,180,245,.2);margin-top:.3rem;padding-top:.5rem">
        <span class="wb-label" style="color:#5ab4f5;font-weight:600">TOTAL WATER EMISSION</span>
        <span class="wb-value" style="color:#00d4d4">{row['Water Total kWh']:.1f} kWh total</span>
        <span class="wb-emission" style="color:#5ab4f5;font-size:.9rem;font-weight:700">{row['Water Emission']:.3f} kg CO₂e</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Waste sub-breakdown ─────────────────────────────────────────────
    st.markdown("##### 🗑️ Waste Emission Ledger")
    waste_rows = []
    for wtype in ["organic","paper","plastic","glass","metal","general","hazardous"]:
        qty_col    = f"Waste {wtype} (kg)"
        method_col = f"Waste {wtype} Method"
        em_col     = f"Em Waste {wtype}"
        if qty_col in row and row[qty_col] > 0:
            waste_rows.append({
                "Category": WASTE_LABELS[wtype][0],
                "Qty (kg)": row[qty_col],
                "Disposal Method": row[method_col].replace("_"," ").title(),
                "EF (kg CO₂e/kg)": WASTE_EF_MATRIX.get(wtype,{}).get(row[method_col], 0),
                "Emission (kg CO₂e)": row[em_col],
                "Note": WASTE_LABELS[wtype][1],
            })
    if waste_rows:
        wdf = pd.DataFrame(waste_rows).round(4)
        st.dataframe(wdf, use_container_width=True, hide_index=True)

# ── ELECTRICITY BREAKDOWN ─────────────────────────────────────────────────────
with t3:
    st.markdown("#### ⚡ Electricity Sub-Category Analysis")
    ec1, ec2 = st.columns(2)
    with ec1:
        fig_e1 = go.Figure()
        for col_, clr, lbl in [
            ("Em HVAC","#4ea8de","HVAC"), ("Em Lighting","#ffb347","Lighting"),
            ("Em Appliances","#a78bfa","Appliances"), ("Em Elevators","#00e5a0","Elevators")
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
            marker=dict(colors=["#4ea8de","#ffb347","#a78bfa","#00e5a0"],
                        line=dict(color="#0b1118", width=2)),
            textfont=dict(family="JetBrains Mono", color="#c8daea", size=10),
        ))
        fig_e2.update_layout(**plo("Avg kWh Consumption Share"))
        st.plotly_chart(fig_e2, use_container_width=True)

    elec_tbl = df[["Month","HVAC (kWh)","Lighting (kWh)","Appliances (kWh)","Elevators (kWh)",
                    "Total Grid (kWh)","Renewables (kWh)","Net Elec (kWh)","Elec Emission","Renewable %"]].round(2).copy()
    elec_tbl.columns = ["Month","HVAC","Lighting","Appliances","Elevators",
                         "Total Grid","Renewables","Net kWh","Net Emission (kg CO₂)","Renewable %"]
    st.dataframe(elec_tbl, use_container_width=True, hide_index=True)

    avg_hvac_pct = (df["Em HVAC"].sum() / df["Elec Emission"].sum() * 100) if df["Elec Emission"].sum() > 0 else 0
    if avg_hvac_pct > 45:
        st.markdown(f"""<div class="tip danger" style="margin-top:.8rem">
            🌡️ <b>HVAC is consuming {avg_hvac_pct:.0f}% of electricity emissions</b> — above recommended 35-40%.
            Audit chiller performance (target COP ≥ 5.0), implement BMS setback schedules, improve building envelope insulation.
        </div>""", unsafe_allow_html=True)

# ── WATER DEEP DIVE ───────────────────────────────────────────────────────────
with t4:
    st.markdown("#### 💧 Water Emissions — Full Lifecycle Analysis")

    # Info panel about methodology
    st.markdown(f"""<div class="water-panel">
      <div class="water-panel-title">📐 Methodology — EPRI / IWA / IPCC 2006 / GHG Protocol</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#7a9ab8;line-height:1.8">
        <b style="color:#5ab4f5">Scope 2 (Indirect – Grid-Powered):</b> Water abstraction/supply
        ({water_profile['supply_kwh_per_m3']} kWh/m³) + distribution pumping
        ({water_profile['distribution_kwh_per_m3']} kWh/m³) + wastewater treatment
        ({water_profile['treatment_kwh_per_m3']} kWh/m³ × {water_profile['wastewater_return_rate']*100:.0f}% return rate)
        — all multiplied by grid EF: {grid_ef} kg CO₂/kWh<br>
        <b style="color:#ffc04d">Scope 1 (Direct – Fugitive):</b> Anaerobic CH₄ from wastewater
        ({water_profile['ch4_ef_kg_per_m3']*1000:.1f} g CO₂e/m³ WW) + N₂O from nitrification/denitrification
        ({water_profile['n2o_ef_kg_co2e_per_m3']*1000:.1f} g CO₂e/m³ WW)
      </div>
    </div>""", unsafe_allow_html=True)

    wc1, wc2 = st.columns(2)
    with wc1:
        # Stacked bar – water emission components
        fig_w1 = go.Figure()
        for col_, clr, lbl in [
            ("Water Supply Emission","#5ab4f5","Supply & Abstraction"),
            ("Water Distribution Emission","#00d4d4","Distribution & Pumping"),
            ("Water WW Treatment Emission","#4ea8de","Wastewater Treatment"),
            ("Water CH4 Emission","#ffc04d","Fugitive CH₄"),
            ("Water N2O Emission","#ff9f43","Direct N₂O"),
        ]:
            fig_w1.add_trace(go.Bar(name=lbl, x=df["Month"], y=df[col_],
                                    marker_color=clr, marker_line_width=0))
        fig_w1.update_layout(**plo("Water Emission Components by Month (kg CO₂e)"),
                              barmode="stack", yaxis_title="kg CO₂e")
        st.plotly_chart(fig_w1, use_container_width=True)

    with wc2:
        avg_w = [
            df["Water Supply Emission"].mean(),
            df["Water Distribution Emission"].mean(),
            df["Water WW Treatment Emission"].mean(),
            df["Water CH4 Emission"].mean(),
            df["Water N2O Emission"].mean(),
        ]
        fig_w2 = go.Figure(go.Pie(
            labels=["Supply","Pumping","WW Treatment","CH₄ Fugitive","N₂O Direct"],
            values=avg_w, hole=0.58,
            marker=dict(colors=["#5ab4f5","#00d4d4","#4ea8de","#ffc04d","#ff9f43"],
                        line=dict(color="#0b1118", width=2)),
            textfont=dict(family="JetBrains Mono", color="#c8daea", size=10),
        ))
        fig_w2.update_layout(**plo("Avg Water Emission Share"))
        st.plotly_chart(fig_w2, use_container_width=True)

    # Water emission table
    w_tbl = df[["Month","Water (m³)","Water Supply Emission","Water Distribution Emission",
                "Water WW Treatment Emission","Water CH4 Emission","Water N2O Emission",
                "Water Total kWh","Water Emission"]].round(4).copy()
    w_tbl.columns = ["Month","Water (m³)","Supply (kg)","Pumping (kg)","WW Treat (kg)",
                     "CH₄ (kg CO₂e)","N₂O (kg CO₂e)","Total kWh","Total CO₂e (kg)"]
    st.dataframe(w_tbl, use_container_width=True, hide_index=True)

    # Water intensity metric
    total_water_kwh = df["Water Total kWh"].sum()
    total_water_m3  = df["Water (m³)"].sum()
    avg_intensity   = total_water_kwh / total_water_m3 if total_water_m3 > 0 else 0
    st.markdown("---")
    wk1, wk2, wk3, wk4 = st.columns(4)
    wk1.metric("💧 Total Water Consumed", f"{total_water_m3:,.0f} m³")
    wk2.metric("⚡ Total Water Energy", f"{total_water_kwh:,.1f} kWh")
    wk3.metric("📊 Effective EI", f"{avg_intensity:.3f} kWh/m³")
    wk4.metric("🌊 WW Volume Treated", f"{total_water_m3 * water_profile['wastewater_return_rate']:,.0f} m³")

    # Waste donut by category
    st.markdown("---")
    st.markdown("#### 🗑️ Waste Emissions by Category & Disposal Method")
    waste_labels_clean = []
    waste_vals = []
    for wtype in ["organic","paper","plastic","glass","metal","general","hazardous"]:
        em_col = f"Em Waste {wtype}"
        if em_col in df.columns:
            total_em = df[em_col].sum()
            if total_em > 0:
                waste_labels_clean.append(WASTE_LABELS[wtype][0].split(" ",1)[1])
                waste_vals.append(total_em)
    if waste_vals:
        ww1, ww2 = st.columns([1,2])
        with ww1:
            fig_ww = go.Figure(go.Pie(
                labels=waste_labels_clean, values=waste_vals, hole=0.55,
                marker=dict(colors=["#ff9f43","#00e5a0","#a78bfa","#5ab4f5","#ff5f5f","#b09fff","#ffc04d"],
                            line=dict(color="#0b1118", width=2)),
                textfont=dict(family="JetBrains Mono", color="#c8daea", size=9),
            ))
            fig_ww.update_layout(**plo("Waste CO₂e by Category (Total)"))
            st.plotly_chart(fig_ww, use_container_width=True)
        with ww2:
            # Show waste EF comparison
            wef_data = []
            for wtype in ["organic","paper","plastic","glass","metal","general","hazardous"]:
                for method, ef in WASTE_EF_MATRIX.get(wtype,{}).items():
                    wef_data.append({"Category": wtype, "Disposal": method.replace("_"," ").title(), "EF": ef})
            wef_df = pd.DataFrame(wef_data)
            fig_ef = go.Figure()
            colors_map = {
                "Landfill": "#ff5f5f", "Recycling": "#00e5a0", "Composting": "#00b37a",
                "Incineration": "#ffc04d", "Anaerobic Digestion": "#5ab4f5",
                "Specialist Treatment": "#a78bfa",
            }
            for method in wef_df["Disposal"].unique():
                subset = wef_df[wef_df["Disposal"] == method]
                fig_ef.add_trace(go.Bar(
                    name=method, x=subset["Category"], y=subset["EF"],
                    marker_color=colors_map.get(method, "#7a9ab8"), marker_line_width=0
                ))
            fig_ef.update_layout(**plo("Waste EF by Category & Disposal Method (kg CO₂e/kg)"),
                                  barmode="group", yaxis_title="kg CO₂e/kg")
            st.plotly_chart(fig_ef, use_container_width=True)

# ── CHARTS ────────────────────────────────────────────────────────────────────
with t5:
    ch1, ch2 = st.columns(2)
    with ch1:
        fig1 = go.Figure()
        for col_, clr, lbl in [
            ("Elec Emission","#00e5a0","Electricity"),
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
        fig2.update_layout(**plo("Avg Emission Share Across Months"))
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["Month"], y=df["Total Emission"], mode="lines+markers",
        line=dict(color="#00e5a0", width=2.5),
        marker=dict(size=7, color="#00e5a0", line=dict(color="#060a0e", width=2)),
        fill="tozeroy", fillcolor="rgba(0,229,160,.07)", name="Total CO₂e"
    ))
    fig3.update_layout(**plo("Total Monthly CO₂e Trend (kg)"), yaxis_title="kg CO₂e")
    st.plotly_chart(fig3, use_container_width=True)

    if df["Renewables (kWh)"].sum() > 0:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Total Grid (kWh)"], name="Grid Draw", marker_color="#ff5f5f"))
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Renewables (kWh)"], name="Renewable Gen", marker_color="#00e5a0"))
        fig4.update_layout(**plo("Grid Draw vs Renewable Generation (kWh)"),
                           barmode="group", yaxis_title="kWh")
        st.plotly_chart(fig4, use_container_width=True)

# ── RECOMMENDATIONS ───────────────────────────────────────────────────────────
with t6:
    st.markdown(f"#### 💡 Location-Aware Recommendations — {state_country}")
    any_tip = False

    if grid_ef > 0.85:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            📡 <b>High grid emission factor ({grid_ef} kg/kWh)</b> for {state_country}.
            Prioritise on-site solar, RECs, or a green PPA. Each 1 MWh of renewable avoided = {grid_ef:.2f} tCO₂.
        </div>""", unsafe_allow_html=True)

    avg_hvac_pct = (df["Em HVAC"].sum() / df["Elec Emission"].sum() * 100) if df["Elec Emission"].sum() > 0 else 0
    if avg_hvac_pct > 45:
        any_tip = True
        st.markdown(f"""<div class="tip danger">
            🌡️ <b>HVAC is {avg_hvac_pct:.0f}% of electricity emissions</b>.
            Upgrade to inverter chillers (COP ≥ 5.0), deploy BMS setback, improve envelope insulation. Target: cut cooling load 20–35%.
        </div>""", unsafe_allow_html=True)

    if df["Renewable %"].mean() < 10:
        any_tip = True
        st.markdown(f"""<div class="tip info">
            ☀️ <b>Renewable offset only {df['Renewable %'].mean():.1f}% avg</b>.
            At {grid_ef} kg/kWh, a 50 kWp rooftop system avoids ~{grid_ef*6000:.0f} kg CO₂/month.
        </div>""", unsafe_allow_html=True)

    # Water-specific tips
    avg_water_em = df["Water Emission"].mean()
    avg_water_kwh_per_m3 = (df["Water Total kWh"].sum() / df["Water (m³)"].sum()) if df["Water (m³)"].sum() > 0 else 0
    if avg_water_em > 50:
        any_tip = True
        st.markdown(f"""<div class="tip water">
            💧 <b>Water emissions average {avg_water_em:.1f} kg CO₂e/month</b> (incl. supply, pumping, wastewater treatment, CH₄ + N₂O).
            Water-efficient fixtures (4-star WELS) reduce consumption 30–40%, cutting all downstream emission components proportionally.
            Greywater recycling can reduce wastewater return volume, cutting WW treatment emissions by 20–50%.
        </div>""", unsafe_allow_html=True)

    ww_em = df["Water WW Treatment Emission"].mean()
    ch4_em = df["Water CH4 Emission"].mean()
    if ch4_em > 0.01:
        any_tip = True
        st.markdown(f"""<div class="tip water">
            🌫️ <b>Wastewater CH₄ + N₂O average {(ch4_em + df['Water N2O Emission'].mean()):.4f} kg CO₂e/month</b>.
            Install on-site STP with biogas capture to convert fugitive CH₄ into energy, turning a liability into an asset.
            Aerobic treatment significantly reduces both CH₄ and N₂O direct emissions.
        </div>""", unsafe_allow_html=True)

    # Waste-specific tips
    plastic_em = df["Em Waste plastic"].sum() if "Em Waste plastic" in df.columns else 0
    organic_em = df["Em Waste organic"].sum() if "Em Waste organic" in df.columns else 0
    if plastic_em > 0:
        avg_plastic = df["Waste plastic (kg)"].mean() if "Waste plastic (kg)" in df.columns else 0
        any_tip = True
        st.markdown(f"""<div class="tip waste">
            🧴 <b>Plastic waste: {avg_plastic:.0f} kg/month avg</b>.
            EF varies dramatically by disposal: recycling (0.043) vs incineration (2.948 kg CO₂e/kg) — <b>68× difference</b>.
            Verify your recycler has certified mechanical recycling; chemical recycling has different EF.
        </div>""", unsafe_allow_html=True)

    if organic_em > 0:
        avg_org = df["Waste organic (kg)"].mean() if "Waste organic (kg)" in df.columns else 0
        any_tip = True
        st.markdown(f"""<div class="tip waste">
            🥦 <b>Organic waste: {avg_org:.0f} kg/month avg</b>.
            Landfill EF (0.587) is 10× higher than composting (0.055) and 29× higher than anaerobic digestion (0.020).
            Shift to in-vessel composting or biogas digester to capture methane and produce compost or energy.
        </div>""", unsafe_allow_html=True)

    if df["Fuel Emission"].mean() > 100:
        any_tip = True
        st.markdown(f"""<div class="tip">
            🔥 <b>Fuel emissions avg {df['Fuel Emission'].mean():,.0f} kg CO₂/month</b>.
            Replace diesel gensets with grid-tied UPS + Li-ion backup. LPG boilers → heat pump: 60–70% reduction.
        </div>""", unsafe_allow_html=True)

    if not any_tip:
        st.markdown(f"""<div class="tip good">
            🎉 <b>Building performance looks solid for {state_country}</b>.
            All categories within healthy ranges. Target 5–10% annual reduction via ISO 50001 energy audits.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 🏆 Emission Intensity Benchmarks")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Your Avg Monthly", f"{df['Total Emission'].mean():,.0f} kg CO₂e")
    b2.metric("IGBC Green Rating", "< 1,800 kg/floor")
    b3.metric("LEED Gold Reference", "< 1,200 kg/floor")
    b4.metric("Net-Zero Target", "< 500 kg/floor")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"🌱 Building Carbon Tracker · 📍 {state_country} · Grid EF: {grid_ef} kg CO₂/kWh · "
    "Water EI: EPRI/IWA · Waste: IPCC 2006/DEFRA 2023/GHG Protocol · "
    "Sources: India CEA 2022-23 · IEA 2023 · IPCC AR6 · DEFRA 2023 · BEE India · PPAC"
)
