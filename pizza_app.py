import streamlit as st
import os
from datetime import datetime
from PIL import Image
import openai

# ------------------ OpenAI API ------------------
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generiere_rezept(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein kreativer Kochassistent."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der Rezeptgenerierung: {e}"

# ------------------ Sidebar ------------------
st.sidebar.title("🍕 PizzaBuddy KI")
rezept_name = st.sidebar.selectbox("Rezept wählen", ["Margherita", "Salami", "Veggie", "Neues Rezept generieren"])

# ------------------ Session State ------------------
if "rezepte" not in st.session_state:
    st.session_state.rezepte = {
        "Margherita": ["Teig ausrollen", "Tomatensauce auftragen", "Mozzarella hinzufügen", "Backen bei 220°C für 12 min"],
        "Salami": ["Teig ausrollen", "Tomatensauce auftragen", "Salami & Käse hinzufügen", "Backen bei 220°C für 12 min"],
        "Veggie": ["Teig ausrollen", "Tomatensauce auftragen", "Gemüse & Käse hinzufügen", "Backen bei 220°C für 12 min"]
    }

# ------------------ Rezeptanzeige ------------------
if rezept_name != "Neues Rezept generieren":
    steps = st.session_state.rezepte[rezept_name]
    st.subheader(f"{rezept_name} Rezept")
    for i, step in enumerate(steps, 1):
        st.write(f"{i}. {step}")
else:
    prompt = st.text_area("Beschreibe, welche Art von Pizza du möchtest", "Eine kreative vegetarische Pizza")
    if st.button("Rezept generieren"):
        neues_rezept = generiere_rezept(prompt)
        st.session_state.rezepte["Neues Rezept"] = neues_rezept.split("\n")
        st.subheader("Generiertes Rezept")
        for i, step in enumerate(st.session_state.rezepte["Neues Rezept"], 1):
            st.write(f"{i}. {step}")
