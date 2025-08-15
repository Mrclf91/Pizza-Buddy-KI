import streamlit as st
import os, time, json
from datetime import datetime, timedelta
from PIL import Image
import openai

# --------------------- Konfiguration ---------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Beispiel-Rezepte
rezepte = {
    "Basic Margherita": [{"schritt": "Teig kneten", "dauer_min": 10},
                         {"schritt": "Stockgare", "dauer_min": 60},
                         {"schritt": "Backen", "dauer_min": 12}],
    "Pepperoni Special": [{"schritt": "Teig kneten", "dauer_min": 12},
                          {"schritt": "Stockgare", "dauer_min": 90},
                          {"schritt": "Backen", "dauer_min": 15}],
}

# --------------------- Sidebar ---------------------
st.sidebar.title("🍕 PizzaBuddy KI")
rezept_name = st.sidebar.selectbox("Rezept wählen", list(rezepte.keys()))
st.sidebar.markdown("---")

# KI-Rezept-Vorschlag
if st.sidebar.button("Neues Rezept vorschlagen"):
    prompt = f"Schlage mir ein kreatives Pizzarezept vor, ähnlich wie {rezept_name}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}]
    )
    st.sidebar.info(response['choices'][0]['message']['content'])

# --------------------- Hauptbereich ---------------------
st.title(f"🍕 PizzaBuddy Dashboard: {rezept_name}")

# --------------------- Schritte ---------------------
aktueller_schritt_idx = st.session_state.get("schritt_idx", 0)
aktueller = rezepte[rezept_name][aktueller_schritt_idx]
st.subheader(f"Schritt {aktueller_schritt_idx+1}: {aktueller['schritt']}")
st.write(f"Dauer: {aktueller['dauer_min']} Minuten")

# Timer
if "timer_end" not in st.session_state:
    st.session_state.timer_end = None

if st.button("Timer starten"):
    st.session_state.timer_end = datetime.now() + timedelta(minutes=aktueller["dauer_min"])
    st.success(f"Timer gestartet! Ende um {st.session_state.timer_end.strftime('%H:%M:%S')}")

if st.session_state.timer_end:
    verbleibend = st.session_state.timer_end - datetime.now()
    if verbleibend.total_seconds() > 0:
        st.info(f"Verbleibende Zeit: {str(verbleibend).split('.')[0]}")
    else:
        st.balloons()
        st.success("🎉 Zeit abgelaufen! Nächster Schritt starten.")
        st.session_state.timer_end = None

# Schritt vor / zurück
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Zurück"):
        st.session_state.schritt_idx = max(0, aktueller_schritt_idx-1)
with col2:
    if st.button("➡️ Weiter"):
        st.session_state.schritt_idx = min(len(rezepte[rezept_name])-1, aktueller_schritt_idx+1)

# --------------------- Bild-Upload ---------------------
st.subheader("📸 Bild hochladen")
hochgeladenes_bild = st.file_uploader("Teig oder Pizza hochladen", type=["png","jpg","jpeg"])
if hochgeladenes_bild:
    image = Image.open(hochgeladenes_bild)
    st.image(image, caption="Hochgeladenes Bild", use_column_width=True)
    os.makedirs("uploads", exist_ok=True)
    save_path = f"uploads/{hochgeladenes_bild.name}"
    image.save(save_path)
    st.success(f"Bild gespeichert unter {save_path}")
