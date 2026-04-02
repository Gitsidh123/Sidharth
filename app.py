import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Building Carbon Footprint Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.main-header {
    background: linear-gradient(135deg, #0d2818 0%, #0d1117 50%, #0a1a0a 100%);
    border: 1px solid #238636;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(35,134,54,0.25) 0%, transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: #3fb950 !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #8b949e;
    margin: 0.5rem 0 0 0;
    font-weight: 300;
    font-size: 1rem;
}

.section-header {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #3fb950 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.5rem 0 1rem 0 !important;
    padding-left: 12px;
    border-left: 3px solid #238636;
}

.emission-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.emission-card:hover { border-color: #3fb950; }
.emission-card .label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'DM Mono', monospace;
}
.emission-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    color: #e6edf3;
    margin: 0.2rem 0;
}
.emission-card .unit {
    font-size: 0.8rem;
    color: #3fb950;
    font-family: 'DM Mono', monospace;
}

.total-card {
    background: linear-gradient(135deg, #0d2818, #0a1a0a);
    border: 2px solid #3fb950;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    text-align: center;
}
.total-card .total-value {
    font-size: 3rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    color: #3fb950;
}
.total-card .total-label {
    font-size: 0.85rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.tip-box {
    background: #161b22;
    border-left: 4px solid #d29922;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #e6edf3;
    font-size: 0.9rem;
}
.tip-box.good {
    border-left-color: #3fb950;
}
.tip-box.warn {
    border-left-color: #f85149;
}

.month-badge {
    display: inline-block;
    background: #238636;
    color: #fff;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 500;
}

.ef-table td { font-family: 'DM Mono', monospace; font-size: 0.8rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #21262d;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stSlider label {
    color: #8b949e !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #8b949e;
}
.stTabs [aria-selected="true"] {
    color: #3fb950 !important;
    border-bottom-color: #3fb950 !important;
}

/* Metric overrides */
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #3fb950 !important;
}
[data-testid="stMetricLabel"] {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ─── Emission Factors ────────────────────────────────────────────────────────
EF = {
    "electricity":    0.82,   # kg CO₂ / kWh  (India grid average)
    "renewable":      0.00,   # kg CO₂ / kWh  (solar/wind)
    "diesel":         2.68,   # kg CO₂ / litre
    "lpg":            2.98,   # kg CO₂ / kg
    "natural_gas":    2.03,   # kg CO₂ / m³
    "water":          0.344,  # kg CO₂ / m³
    "food_organic":   0.10,   # kg CO₂ / kg waste
    "paper":          1.06,   # kg CO₂ / kg waste
    "plastic":        6.00,   # kg CO₂ / kg waste
    "general":        0.46,   # kg CO₂ / kg waste
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🏢 Building Carbon Footprint Tracker</h1>
  <p>Monthly operational emissions · Electricity · Fuel · Water · Waste · Renewables</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar – Building Info ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    building_name = st.text_input("Building Name", value="Block A – Main Office")
    num_months = st.slider("Months to Track", 1, 12, 3)
    st.markdown("---")
    st.markdown("### 📋 Emission Factors")
    st.markdown("""
| Source | Factor |
|--------|--------|
| Grid Electricity | 0.82 kg/kWh |
| Diesel | 2.68 kg/L |
| LPG | 2.98 kg/kg |
| Natural Gas | 2.03 kg/m³ |
| Water | 0.344 kg/m³ |
| Paper Waste | 1.06 kg/kg |
| Plastic Waste | 6.00 kg/kg |
| Organic Waste | 0.10 kg/kg |
| General Waste | 0.46 kg/kg |
""")
    st.markdown("---")
    st.caption("Factors based on IPCC, DEFRA & India CEA guidelines.")

# ─── Monthly Input Form ───────────────────────────────────────────────────────
st.markdown('<p class="section-header">📥 Monthly Operational Data</p>', unsafe_allow_html=True)

monthly_data = []

tabs = st.tabs([f"📅 {MONTHS[i]}" for i in range(num_months)])

for i, tab in enumerate(tabs):
    with tab:
        month_label = MONTHS[i]
        st.markdown(f"#### Data for **{month_label}** – *{building_name}*")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("**⚡ Electricity**")
            elec = st.number_input(f"Grid Electricity (kWh)", min_value=0.0, value=5000.0, step=100.0, key=f"elec_{i}")
            renew = st.number_input(f"Renewable Generation (kWh)", min_value=0.0, value=0.0, step=50.0, key=f"renew_{i}")

        with c2:
            st.markdown("**🔥 Fuel Usage**")
            diesel = st.number_input(f"Diesel (litres)", min_value=0.0, value=0.0, step=10.0, key=f"diesel_{i}")
            lpg = st.number_input(f"LPG (kg)", min_value=0.0, value=0.0, step=5.0, key=f"lpg_{i}")
            natgas = st.number_input(f"Natural Gas (m³)", min_value=0.0, value=0.0, step=5.0, key=f"natgas_{i}")

        with c3:
            st.markdown("**💧 Water**")
            water_m3 = st.number_input(f"Water Consumption (m³)", min_value=0.0, value=200.0, step=10.0, key=f"water_{i}")
            st.markdown("**🗑️ Waste (kg)**")
            w_organic = st.number_input(f"Organic / Food Waste (kg)", min_value=0.0, value=50.0, step=5.0, key=f"worg_{i}")
            w_paper   = st.number_input(f"Paper / Cardboard (kg)", min_value=0.0, value=30.0, step=5.0, key=f"wpap_{i}")
            w_plastic = st.number_input(f"Plastic (kg)", min_value=0.0, value=20.0, step=5.0, key=f"wpla_{i}")
            w_general = st.number_input(f"General / Mixed (kg)", min_value=0.0, value=40.0, step=5.0, key=f"wgen_{i}")

        # ── Compute ──────────────────────────────────────────────────────────
        net_elec        = max(0.0, elec - renew)
        em_electricity  = net_elec  * EF["electricity"]
        em_diesel       = diesel    * EF["diesel"]
        em_lpg          = lpg       * EF["lpg"]
        em_natgas       = natgas    * EF["natural_gas"]
        em_fuel         = em_diesel + em_lpg + em_natgas
        em_water        = water_m3  * EF["water"]
        em_waste        = (w_organic * EF["food_organic"] +
                           w_paper   * EF["paper"] +
                           w_plastic * EF["plastic"] +
                           w_general * EF["general"])
        em_total        = em_electricity + em_fuel + em_water + em_waste
        renewable_pct   = (renew / elec * 100) if elec > 0 else 0.0

        monthly_data.append({
            "Month":            month_label,
            "Grid Elec (kWh)":  elec,
            "Renewables (kWh)": renew,
            "Net Elec (kWh)":   net_elec,
            "Diesel (L)":       diesel,
            "LPG (kg)":         lpg,
            "Nat Gas (m³)":     natgas,
            "Water (m³)":       water_m3,
            "Organic Waste (kg)": w_organic,
            "Paper Waste (kg)": w_paper,
            "Plastic Waste (kg)":w_plastic,
            "General Waste (kg)":w_general,
            "Elec Emission":    em_electricity,
            "Fuel Emission":    em_fuel,
            "Water Emission":   em_water,
            "Waste Emission":   em_waste,
            "Total Emission":   em_total,
            "Renewable %":      renewable_pct,
        })

# ─── Build DataFrame ──────────────────────────────────────────────────────────
df = pd.DataFrame(monthly_data)

# ─── Results ──────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Results & Analysis</p>', unsafe_allow_html=True)

tab_summary, tab_breakdown, tab_charts, tab_tips = st.tabs([
    "📋 Summary Table", "🔬 Month Detail", "📈 Charts", "💡 Recommendations"
])

# ── Tab 1: Summary Table ──────────────────────────────────────────────────────
with tab_summary:
    st.markdown(f"#### Monthly CO₂ Emissions Summary — *{building_name}*")

    display_df = df[["Month","Elec Emission","Fuel Emission","Water Emission","Waste Emission","Total Emission","Renewable %"]].copy()
    display_df.columns = ["Month","Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)","Total CO₂ (kg)","Renewable %"]
    display_df = display_df.round(2)

    # Totals row
    totals = display_df[["Electricity (kg)","Fuel (kg)","Water (kg)","Waste (kg)","Total CO₂ (kg)"]].sum()
    totals_row = pd.DataFrame([["— TOTAL —", totals["Electricity (kg)"], totals["Fuel (kg)"],
                                 totals["Water (kg)"], totals["Waste (kg)"], totals["Total CO₂ (kg)"], "—"]],
                              columns=display_df.columns)
    display_df = pd.concat([display_df, totals_row], ignore_index=True)

    st.dataframe(
        display_df.style
            .format({"Electricity (kg)": "{:.2f}", "Fuel (kg)": "{:.2f}",
                     "Water (kg)": "{:.2f}", "Waste (kg)": "{:.2f}",
                     "Total CO₂ (kg)": "{:.2f}"})
            .background_gradient(subset=["Total CO₂ (kg)"], cmap="RdYlGn_r"),
        use_container_width=True,
        height=min(400, (num_months + 3) * 38),
    )

    # KPI row
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    total_all    = df["Total Emission"].sum()
    avg_monthly  = df["Total Emission"].mean()
    max_month    = df.loc[df["Total Emission"].idxmax(), "Month"]
    avg_renew    = df["Renewable %"].mean()

    k1.metric("🌍 Total CO₂ (all months)", f"{total_all:,.1f} kg")
    k2.metric("📅 Avg Monthly Emission", f"{avg_monthly:,.1f} kg")
    k3.metric("📌 Highest Emission Month", max_month)
    k4.metric("☀️ Avg Renewable Share", f"{avg_renew:.1f}%")

# ── Tab 2: Month Detail ───────────────────────────────────────────────────────
with tab_breakdown:
    selected_month = st.selectbox("Select Month to Inspect", df["Month"].tolist())
    row = df[df["Month"] == selected_month].iloc[0]

    st.markdown(f"#### Detailed Breakdown — **{selected_month}**")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="emission-card">
        <div class="label">⚡ Electricity</div>
        <div class="value">{row['Elec Emission']:,.1f}</div>
        <div class="unit">kg CO₂ &nbsp;|&nbsp; Net {row['Net Elec (kWh)']:,.0f} kWh</div>
    </div>""", unsafe_allow_html=True)

    c2.markdown(f"""<div class="emission-card">
        <div class="label">🔥 Fuel</div>
        <div class="value">{row['Fuel Emission']:,.1f}</div>
        <div class="unit">kg CO₂ &nbsp;|&nbsp; Diesel + LPG + Gas</div>
    </div>""", unsafe_allow_html=True)

    c3.markdown(f"""<div class="emission-card">
        <div class="label">💧 Water</div>
        <div class="value">{row['Water Emission']:,.1f}</div>
        <div class="unit">kg CO₂ &nbsp;|&nbsp; {row['Water (m³)']:,.0f} m³</div>
    </div>""", unsafe_allow_html=True)

    c4.markdown(f"""<div class="emission-card">
        <div class="label">🗑️ Waste</div>
        <div class="value">{row['Waste Emission']:,.1f}</div>
        <div class="unit">kg CO₂ &nbsp;|&nbsp; All types</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="total-card">
        <div class="total-label">Total Monthly Carbon Footprint</div>
        <div class="total-value">{row['Total Emission']:,.2f} kg CO₂</div>
        <div class="total-label" style="margin-top:0.5rem">≈ {row['Total Emission']/1000:.3f} tonnes CO₂</div>
    </div>""", unsafe_allow_html=True)

    # Renewable offset callout
    renew_saved = row["Renewables (kWh)"] * EF["electricity"]
    if renew_saved > 0:
        st.success(f"☀️ Renewable generation offset **{renew_saved:,.1f} kg CO₂** this month ({row['Renewable %']:.1f}% of grid draw).")

    # Sub-breakdown table
    st.markdown("##### Component Detail")
    detail_data = {
        "Component": ["Grid Electricity", "Renewable Offset", "Net Electricity Emission",
                       "Diesel", "LPG", "Natural Gas", "Water", "Organic Waste",
                       "Paper Waste", "Plastic Waste", "General Waste"],
        "Quantity": [
            f"{row['Grid Elec (kWh)']:.1f} kWh", f"-{row['Renewables (kWh)']:.1f} kWh", f"{row['Net Elec (kWh)']:.1f} kWh",
            f"{row['Diesel (L)']:.1f} L", f"{row['LPG (kg)']:.1f} kg", f"{row['Nat Gas (m³)']:.1f} m³",
            f"{row['Water (m³)']:.1f} m³",
            f"{row['Organic Waste (kg)']:.1f} kg", f"{row['Paper Waste (kg)']:.1f} kg",
            f"{row['Plastic Waste (kg)']:.1f} kg", f"{row['General Waste (kg)']:.1f} kg",
        ],
        "Emission (kg CO₂)": [
            row['Grid Elec (kWh)'] * EF['electricity'],
            -row['Renewables (kWh)'] * EF['electricity'],
            row['Elec Emission'],
            row['Diesel (L)'] * EF['diesel'],
            row['LPG (kg)'] * EF['lpg'],
            row['Nat Gas (m³)'] * EF['natural_gas'],
            row['Water Emission'],
            row['Organic Waste (kg)'] * EF['food_organic'],
            row['Paper Waste (kg)'] * EF['paper'],
            row['Plastic Waste (kg)'] * EF['plastic'],
            row['General Waste (kg)'] * EF['general'],
        ]
    }
    detail_df = pd.DataFrame(detail_data)
    detail_df["Emission (kg CO₂)"] = detail_df["Emission (kg CO₂)"].round(2)
    st.dataframe(detail_df, use_container_width=True, hide_index=True)

# ── Tab 3: Charts ─────────────────────────────────────────────────────────────
with tab_charts:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Stacked bar – emission by category per month
        fig1 = go.Figure()
        colors = {"Elec Emission":"#3fb950","Fuel Emission":"#f0883e","Water Emission":"#58a6ff","Waste Emission":"#bc8cff"}
        labels = {"Elec Emission":"Electricity","Fuel Emission":"Fuel","Water Emission":"Water","Waste Emission":"Waste"}
        for col, color in colors.items():
            fig1.add_trace(go.Bar(
                name=labels[col], x=df["Month"], y=df[col],
                marker_color=color, marker_line_width=0,
            ))
        fig1.update_layout(
            barmode="stack", title="Monthly Emissions by Category",
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(color="#8b949e", family="DM Mono"),
            title_font=dict(color="#e6edf3", family="Syne", size=15),
            legend=dict(bgcolor="#0d1117", bordercolor="#30363d", borderwidth=1),
            yaxis_title="kg CO₂", xaxis_title="Month",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        # Donut – average category share
        avg_vals = [df["Elec Emission"].mean(), df["Fuel Emission"].mean(),
                    df["Water Emission"].mean(), df["Waste Emission"].mean()]
        fig2 = go.Figure(go.Pie(
            labels=["Electricity","Fuel","Water","Waste"],
            values=avg_vals,
            hole=0.55,
            marker=dict(colors=["#3fb950","#f0883e","#58a6ff","#bc8cff"],
                        line=dict(color="#161b22", width=2)),
            textfont=dict(family="DM Mono", color="#e6edf3"),
        ))
        fig2.update_layout(
            title="Avg Emission Share (All Months)",
            paper_bgcolor="#161b22",
            font=dict(color="#8b949e", family="DM Mono"),
            title_font=dict(color="#e6edf3", family="Syne", size=15),
            legend=dict(bgcolor="#0d1117", bordercolor="#30363d", borderwidth=1),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Total emission trend line
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["Month"], y=df["Total Emission"],
        mode="lines+markers",
        line=dict(color="#3fb950", width=3),
        marker=dict(size=8, color="#3fb950", line=dict(color="#0d1117", width=2)),
        fill="tozeroy", fillcolor="rgba(63,185,80,0.08)",
        name="Total CO₂"
    ))
    fig3.update_layout(
        title="Total Monthly CO₂ Trend",
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#8b949e", family="DM Mono"),
        title_font=dict(color="#e6edf3", family="Syne", size=15),
        yaxis_title="kg CO₂", xaxis_title="Month",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    if df["Renewables (kWh)"].sum() > 0:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Grid Elec (kWh)"], name="Grid Draw", marker_color="#f85149"))
        fig4.add_trace(go.Bar(x=df["Month"], y=df["Renewables (kWh)"], name="Renewable Gen", marker_color="#3fb950"))
        fig4.update_layout(
            barmode="group", title="Grid Electricity vs Renewable Generation",
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(color="#8b949e", family="DM Mono"),
            title_font=dict(color="#e6edf3", family="Syne", size=15),
            legend=dict(bgcolor="#0d1117", bordercolor="#30363d", borderwidth=1),
            yaxis_title="kWh", xaxis_title="Month",
            margin=dict(l=10, r=10, t=50, b=10),
            yaxis=dict(gridcolor="#21262d"),
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── Tab 4: Recommendations ────────────────────────────────────────────────────
with tab_tips:
    st.markdown("#### 💡 Smart Recommendations Based on Your Data")

    high_elec   = df[df["Elec Emission"] > df["Elec Emission"].mean() * 1.1]
    high_fuel   = df[df["Fuel Emission"] > 50]
    high_waste  = df[df["Waste Emission"] > df["Waste Emission"].mean() * 1.1]
    low_renew   = df["Renewable %"].mean() < 10

    any_tip = False

    if not high_elec.empty:
        any_tip = True
        months_str = ", ".join(high_elec["Month"].tolist())
        st.markdown(f"""<div class="tip-box warn">
            ⚡ <b>High electricity emissions</b> in {months_str}. 
            Consider LED retrofits, HVAC scheduling, and BMS (Building Management Systems) to cut grid draw.
        </div>""", unsafe_allow_html=True)

    if not high_fuel.empty:
        any_tip = True
        months_str = ", ".join(high_fuel["Month"].tolist())
        st.markdown(f"""<div class="tip-box warn">
            🔥 <b>Significant fuel usage</b> in {months_str}. 
            Evaluate switching diesel generators to grid or solar+battery backup; audit LPG boiler efficiency.
        </div>""", unsafe_allow_html=True)

    if not high_waste.empty:
        any_tip = True
        months_str = ", ".join(high_waste["Month"].tolist())
        st.markdown(f"""<div class="tip-box">
            🗑️ <b>Above-average waste emissions</b> in {months_str}. 
            Implement source-segregation, composting for organic waste, and plastic reduction initiatives.
        </div>""", unsafe_allow_html=True)

    if low_renew:
        any_tip = True
        st.markdown(f"""<div class="tip-box">
            ☀️ <b>Low renewable generation ({df["Renewable %"].mean():.1f}% avg)</b>. 
            Rooftop solar or a Power Purchase Agreement (PPA) could offset significant grid emissions.
        </div>""", unsafe_allow_html=True)

    if df["Water Emission"].mean() > 100:
        any_tip = True
        st.markdown(f"""<div class="tip-box">
            💧 <b>High water-related emissions</b>. 
            Rainwater harvesting and water recycling systems can reduce both consumption and associated emissions.
        </div>""", unsafe_allow_html=True)

    if not any_tip:
        st.markdown(f"""<div class="tip-box good">
            🎉 <b>Your building is performing well!</b> Emissions are within reasonable ranges. 
            Continue monitoring monthly and target incremental reductions each quarter.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 🏆 Emission Intensity Benchmarks")
    intensity = df["Total Emission"].mean()
    bench_col1, bench_col2, bench_col3 = st.columns(3)
    bench_col1.metric("Your Avg Monthly CO₂", f"{intensity:,.1f} kg")
    bench_col2.metric("Typical Office (ASHRAE ref)", "~2,000 kg/floor")
    bench_col3.metric("Net-Zero Target", "< 500 kg/floor")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🌱 Building Carbon Footprint Tracker · "
    "Emission factors: IPCC AR6, DEFRA 2023, India CEA 2022-23 · "
    "For professional carbon accounting, consult a certified auditor."
)
