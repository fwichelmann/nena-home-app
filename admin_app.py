import streamlit as st
# Spezieller Apple-Trick für das Home-Bildschirm-Icon
st.markdown(f"""
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com">
    """, unsafe_allow_html=True)
import pandas as pd
import os
from datetime import datetime

# 1. STABILE KONFIGURATION (Das fixe Logo-Icon oben)
st.set_page_config(
    page_title="Nena Home App", 
    page_icon="nena-home-by-lesa-logo.png", 
    layout="centered"
)

# 2. DESIGN-FIX (Nena Farben & Große Buttons)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2 { color: #2c2c2c; text-align: center; font-family: serif; }
    /* Goldene Buttons für das iPhone */
    .stButton>button { 
        height: 70px; width: 100%; border-radius: 15px; 
        font-size: 18px; background-color: #c5a059; color: white; border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #2c2c2c; color: #c5a059; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATEN-LOGIK
LOG_FILE = "service_log.xlsx"

def save_to_log(user_data, typ, details, photo=None):
    df = pd.read_excel(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', 'Silbersteinstraße'),
        "Unit": str(user_data.get('unit', '101')).upper(),
        "Typ": typ, "Details": details, "Status": "Offen"
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 4. LOGIN & MIETER-PROFIL
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    logo_file = "nena-home-by-lesa-logo.png"
    if os.path.exists(logo_file):
        st.image(logo_file, use_container_width=True)
    st.title("Willkommen Zuhause")
    email = st.text_input("Ihre E-Mail", placeholder="test@nena.de").strip().lower()
    if st.button("Anmelden"):
        # Wir nutzen hier einen schnellen Test-Login für dein iPhone
        if email == "test@nena.de" or "@nena-apartments.de" in email:
            st.session_state.user = {"mieter": "Test User", "unit": "S-105", "haus": "Silbersteinstraße"}
            st.rerun()
        else: st.error("E-Mail nicht gefunden.")
else:
    # --- HAUPTMENÜ (MOBILE VIEW) ---
    st.title(f"Hallo {st.session_state.user['mieter']}!")
    st.write(f"📍 Apartment {st.session_state.user['unit']}")
    
    st.divider()

    # DIE NEUE KAMERA-FUNKTION (Foto-Upload)
    with st.expander("🛠️ Schaden melden (mit Foto)"):
        s_typ = st.selectbox("Was ist defekt?", ["Heizung", "Wasser", "Strom", "Möbel"])
        s_desc = st.text_area("Beschreibung")
        # Hier öffnet sich am Handy automatisch die Kamera!
        foto = st.camera_input("Foto vom Schaden machen")
        if st.button("Meldung absenden"):
            save_to_log(st.session_state.user, "Reparatur", f"{s_typ}: {s_desc}")
            st.success("Erfolgreich gemeldet!")

    if st.button("✨ Reinigung bestellen"):
        save_to_log(st.session_state.user, "Reinigung", "Standard Clean")
        st.success("Reinigung gebucht!")

    st.divider()
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.rerun()
