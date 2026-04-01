import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Carbon Footprint Tracker", layout="wide")

# Title
st.title("🌍 Personal Carbon Footprint Tracker")
st.markdown("Track, analyze, and reduce your carbon emissions 🚀")

st.divider()

# Layout
col1, col2 = st.columns(2)

with col1:
    travel = st.number_input("🚗 Travel (km/month)", min_value=0, value=0)
    electricity = st.number_input("⚡ Electricity usage (kWh/month)", min_value=0, value=0)

with col2:
    food = st.selectbox("🍔 Diet Type", ["Vegetarian", "Non-Vegetarian"])

# --- Calculation ---
travel_emission = travel * 0.21
electricity_emission = electricity * 0.82
food_emission = 100 if food == "Non-Vegetarian" else 50

total_carbon = travel_emission + electricity_emission + food_emission

st.divider()

# --- Results ---
st.subheader("📊 Your Carbon Footprint")

col3, col4 = st.columns(2)

with col3:
    st.metric("Total CO₂ Emission (kg/month)", f"{total_carbon:.2f}")

with col4:
    score = max(0, 100 - total_carbon / 10)
    st.metric("🏆 Sustainability Score", f"{int(score)}/100")

# Progress bar
st.progress(int(score))

# --- Chart ---
st.subheader("📈 Emission Breakdown")

data = {
    "Category": ["Travel", "Electricity", "Food"],
    "CO2 Emission": [travel_emission, electricity_emission, food_emission]
}

df = pd.DataFrame(data)
st.bar_chart(df.set_index("Category"))

# --- Suggestions ---
st.subheader("💡 Smart Suggestions")

if travel > 100:
    st.warning("🚶 Reduce car usage or switch to public transport.")

if electricity > 200:
    st.warning("💡 Use energy-efficient appliances and turn off unused devices.")

if food == "Non-Vegetarian":
    st.warning("🌱 Try more plant-based meals to lower your footprint.")

if total_carbon < 100:
    st.success("🎉 Great job! Your carbon footprint is low!")

# --- Footer ---
st.divider()
st.caption("🌱 Built with Streamlit | Sustainable Future Project")
