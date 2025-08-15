import streamlit as st
import time, json, os
from datetime import datetime, timedelta
from PIL import Image
import openai

# ------------------ Konfiguration ------------------
st.set_page_config(page_title="PizzaBuddy KI", page_icon="🍕", layout="wide")
REZEPTE_FILE = "rezepte.json"
FEEDBACK_FILE = "pizza_feedback.json"

# ------------------ OpenAI Key ------------------
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else ""

# ------------------ Helper: Rezepte laden ------------------
def lade_rezepte():
    if os.path.exists(REZEPTE_FILE):
        with open(REZEPTE_FILE, "r") as f:
            return json.load(f)
    return {}

def speichere_rezepte(data):
    with open(REZEPTE_FILE, "w") as f:
        json.dump(data, f, indent=2)

rezepte = lade_rezepte()

# ------------------ Helper: Zutatenrechner ------------------
def berechne_zutaten(anz_baelle=6, gewicht_pro_ball=250, hydration=0.72, salz_pct=0.028, hefe_pro_kg=2):
    total = anz_baelle * gewicht_pro_ball
    hefe_frac = hefe_pro_kg / 1000
    f = total / (1 + hydration + salz_pct + hefe_frac)
    w = f * hydration
    s = f * salz_pct
    y = f * hefe_frac
    return round(f), round(w), round(s), round(y)

# ------------------ Helper: Feedback ------------------
def lade_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def speichere_feedback(eintrag: dict):
    data = lade_feedback()
    data.append(eintrag)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------------ Sidebar ------------------
st.sidebar.title("🍕 PizzaBuddy KI")
rezept_name = st.sidebar.selectbox("Rezept wählen", list(rezepte.keys()))
steps = rezepte[rezept_name]

if "hydration" not in st.session_state:
    st.session_state.hydration = 0.72 if "72%" in rezept_name else 0.75
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

anz_baelle = st.sidebar.number_input("Anzahl Teigbällchen", 1, 24, 6)
gewicht_ball = st.sidebar.number_input("Gewicht pro Bällchen (g)", 180, 320, 250)
sec_pro_min = st.sidebar.slider("Zeitfaktor (Sek. pro Minute)", 1, 60, 1)

mehl, wasser, salz, hefe = berechne_zutaten(anz_baelle, gewicht_ball, st.session_state.hydration)
st.sidebar.subheader("Zutaten (geschätzt)")
st.sidebar.metric("Mehl (g)", mehl)
st.sidebar.metric("Wasser (g)", wasser)
st.sidebar.metric("Salz (g)", salz)
st.sidebar.metric("Hefe (g)", hefe)

# ------------------ Hauptbereich ------------------
st.title("Interaktiver Pizza-Assistent KI")
col1, col2, col3 = st.columns([2,1,1])
aktueller = steps[st.session_state.step_index]
with col1:
    st.subheader(f"Schritt {st.session_state.step_index+1} / {len(steps)}")
    st.write(f"**{aktueller['schritt']}** – Dauer: {aktueller['dauer_min']} min")
with col2:
    if st.button("◀️ Zurück", disabled=st.session_state.step_index==0):
        st.session_state.step_index -= 1
        st.experimental_rerun()
with col3:
    if st.button("Weiter ▶️", disabled=st.session_state.step_index==len(steps)-1):
        st.session_state.step_index += 1
        st.experimental_rerun()

# ------------------ Timer ------------------
kurz_timer = st.button("⏱️ Kurz-Timer starten (Demo)")
if kurz_timer:
    dauer = aktueller["dauer_min"]
    max_block = 600
    blockzeit = dauer * sec_pro_min
    if blockzeit <= max_block:
        prog = st.progress(0)
        for i in range(dauer):
            time.sleep(sec_pro_min)
            prog.progress(int(((i+1)/dauer)*100))
        st.success("Schritt abgeschlossen!")
    else:
        fz = datetime.now() + timedelta(seconds=blockzeit)
        st.info(f"Langer Schritt – Ende: **{fz.strftime('%H:%M')}**")

# ------------------ Feedback ------------------
if aktueller.get("feedback", True):
    st.subheader("Feedback & Tipps")
    fb = st.radio("Wie ist der Teig jetzt?", ["ok","weich","straff","zu klebrig"], index=0, horizontal=True)
    if st.button("Feedback speichern & Tipp anzeigen"):
        eintrag = {"zeit": datetime.now().isoformat(timespec="seconds"),
                   "rezept": rezept_name, "schritt": aktueller["schritt"], "feedback": fb,
                   "baelle": int(anz_baelle), "gewicht_pro_ball": int(gewicht_ball),
                   "hydration": st.session_state.hydration}
        speichere_feedback(eintrag)
        st.success("Feedback gespeichert ✅")
        if fb=="weich": st.info("💡 Knete länger oder reduziere Wasser")
        if fb=="straff": st.info("💡 Teig entspannen lassen")
        if fb=="zu klebrig": st.info("💡 Mehl sanft einarbeiten")

# ------------------ Foto-Upload ------------------
st.subheader("🍕 Foto hochladen (optional)")
uploaded_file = st.file_uploader("Bild vom Teig oder Pizza", type=["png","jpg","jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Hochgeladenes Bild", use_column_width=True)

# ------------------ KI-Rezeptvorschlag ------------------
st.subheader("🍕 Neues Rezept generieren")
stil = st.selectbox("Stil wählen", ["Neapolitanisch", "New York", "Sauerteig"])
mehl_neu = st.number_input("Mehl für neues Rezept (g)", 400, 2000, 500, key="neu_mehl")
hydration_neu = st.number_input("Hydration (%)", 60, 80, 72, key="neu_hydration")

if st.button("Neues Rezept generieren"):
    prompt = f"Erstelle ein Pizza-Rezept im Stil {stil} mit {mehl_neu}g Mehl und {hydration_neu}% Hydration. Gib die Schritte als Liste aus."
    try:
        response = openai.ChatCompletion.create(model="gpt-5-mini",
                                                messages=[{"role":"user","content":prompt}])
        neues_rezept = response.choices[0].message.content.split("\n")
        name = f"Neu: {stil} {datetime.now().strftime('%H:%M')}"
        rezepte[name] = [{"schritt": s, "dauer_min": 5, "feedback": True} for s in neues_rezept if s]
        speichere_rezepte(rezepte)
        st.success("Neues Rezept generiert & gespeichert ✅")
        st.write(neues_rezept)
    except Exception as e:
        st.error(f"Fehler: {e}")

# ------------------ Verlauf / Export ------------------
st.subheader("Verlauf & Export")
verlauf = lade_feedback()
if verlauf:
    st.table(verlauf[-5:])
    st.download_button("⬇️ Feedback als JSON", data=json.dumps(verlauf, indent=2), file_name="feedback.json")
