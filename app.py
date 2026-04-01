import streamlit as st

st.title("🌍 Carbon Footprint Tracker")

st.header("Enter your data")

travel = st.number_input("Km traveled by car per month")
electricity = st.number_input("Electricity usage (kWh)")
food = st.selectbox("Diet type", ["Vegetarian", "Non-Vegetarian"])

# Simple calculation
carbon = (travel * 0.21) + (electricity * 0.82)

if food == "Non-Vegetarian":
    carbon += 100
else:
    carbon += 50

st.subheader(f"Estimated CO₂ Emission: {carbon:.2f} kg/month")
