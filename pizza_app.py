# pizza_app.py
import streamlit as st
import json, os, time
from datetime import datetime, timedelta
from PIL import Image
import openai

# ------------------ OpenAI Setup ------------------
# Du hast den API-Key schon bei Streamlit Secrets gespeichert
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ------------------ Daten laden ------------------
REZEPTE_DATEI = "rezepte.json"

if os.path.exists(REZEPTE_DATEI):
    with open(REZEPTE_DATEI, "r") as f:
        rezepte = json.load(f)
else:
    rezepte = {
        "Basic Margherita": [
            {"schritt": "Teig kneten", "dauer_min": 10},
            {"schritt": "Stockgare", "dauer_min": 60},
            {"schritt": "Backen", "dauer_min": 12},
        ]
    }
    with open(REZEPTE_DATEI, "w") as f:
        json.dump(rezepte, f, indent=4)

# ------------------ Sidebar ------------------
st.sidebar.title("🍕 PizzaBuddy KI")
rezept_name = st.sidebar.selectbox("Rezept wählen", list(rezepte.keys()))

if st.sidebar.button("Neues Rezept vorschlagen"):
    prompt = f"Schlage mir ein kreatives Pizzarezept vor, ähnlich wie {rezept_name}. Gib die Schritte als JSON-Liste mit 'schritt' und 'dauer_min' an."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ki_rezept_text = response['choices'][0]['message']['content']

        # KI-Antwort in Python-Objekt umwandeln
        neues_rezept = json.loads(ki_rezept_text)
        ki_name = f"KI Rezept {len(rezepte)+1}"
        rezepte[ki_name] = neues_rezept

        # Speichern
        with open(REZEPTE_DATEI, "w") as f:
            json.dump(rezepte, f, indent=4)
        st.sidebar.success(f"✅ Neues Rezept '{ki_name}' gespeichert!")
    except Exception as e:
        st.sidebar.error(f"Fehler beim Vorschlagen des Rezepts: {e}")

# ------------------ Hauptbereich ------------------
st.title(f"🍕 PizzaBuddy: {rezept_name}")

steps = rezepte.get(rezept_name, [])

# Timer initialisieren
if "aktiver_schritt" not in st.session_state:
    st.session_state.aktiver_schritt = 0
if "timer_start" not in st.session_state:
    st.session_state.timer_start = None

# Schritt anzeigen
if steps:
    current = st.session_state.aktiver_schritt
    st.header(f"Schritt {current+1}/{len(steps)}: {steps[current]['schritt']}")
    st.write(f"Dauer: {steps[current]['dauer_min']} Minuten")

    if st.button("Starte Schritt"):
        st.session_state.timer_start = datetime.now()

    if st.session_state.timer_start:
        elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
        remaining = steps[current]['dauer_min']*60 - elapsed
        if remaining > 0:
            st.progress(1 - remaining/(steps[current]['dauer_min']*60))
            st.write(f"Verbleibende Zeit: {int(remaining//60)}m {int(remaining%60)}s")
        else:
            st.success("✅ Schritt abgeschlossen!")
            if st.button("Zum nächsten Schritt"):
                st.session_state.aktiver_schritt += 1
                st.session_state.timer_start = None
else:
    st.write("Keine Schritte gefunden.")

# ------------------ Optional: Pizza-Bild ------------------
bild_name = f"{rezept_name.replace(' ', '_')}.png"
if os.path.exists(bild_name):
    img = Image.open(bild_name)
    st.image(img, caption=rezept_name)
