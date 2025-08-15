# pizza_app_grid.py
import streamlit as st
import json, os
from PIL import Image
import openai
import base64
from io import BytesIO

# ------------------ OpenAI Setup ------------------
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
if st.sidebar.button("Neues KI-Rezept generieren"):
    rezept_name = list(rezepte.keys())[0]  # Ausgangsrezept für Vorschlag
    prompt = f"Schlage mir ein kreatives Pizzarezept vor, ähnlich wie {rezept_name}. Gib die Schritte als JSON-Liste mit 'schritt' und 'dauer_min' an."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ki_rezept_text = response['choices'][0]['message']['content']
        neues_rezept = json.loads(ki_rezept_text)
        ki_name = f"KI Rezept {len(rezepte)+1}"
        rezepte[ki_name] = neues_rezept
        with open(REZEPTE_DATEI, "w") as f:
            json.dump(rezepte, f, indent=4)
        st.sidebar.success(f"✅ Neues Rezept '{ki_name}' gespeichert!")

        # Bild generieren
        img_prompt = f"Eine leckere Pizza: {ki_name}, fotorealistisch, auf Holzbrett, italienische Küche"
        image_resp = openai.Image.create(
            prompt=img_prompt,
            n=1,
            size="512x512"
        )
        image_data = base64.b64decode(image_resp['data'][0]['b64_json'])
        with open(f"{ki_name.replace(' ', '_')}.png", "wb") as f:
            f.write(image_data)
    except Exception as e:
        st.sidebar.error(f"Fehler: {e}")

# ------------------ Hauptbereich ------------------
st.title("🍕 PizzaBuddy KI: Alle Rezepte")

# Grid anzeigen: 2 Spalten
cols = st.columns(2)
for i, (name, steps) in enumerate(rezepte.items()):
    col = cols[i % 2]
    with col:
        st.subheader(name)
        st.write("Schritte:")
        for s in steps:
            st.write(f"- {s['schritt']} ({s['dauer_min']} min)")

        # Bild anzeigen
        bild_name = f"{name.replace(' ', '_')}.png"
        if os.path.exists(bild_name):
            img = Image.open(bild_name)
            st.image(img, caption=name)
        else:
            st.info("📸 Noch kein Bild verfügbar")
