import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION (Muss als ALLERERSTES stehen)
# Wir nutzen dein Logo als Tab-Icon
st.set_page_config(
    page_title="Nena Home", 
    page_icon="app-icon.png", 
    layout="centered"
)

# 2. APPLE ICON & DESIGN (Direkter Link zu deinem GitHub)
# Ersetze 'fwichelmann' durch deinen GitHub-Namen, falls er anders ist
GITHUB_USER = "fwichelmann"
ICON_URL = f"https://raw.githubusercontent.com{GITHUB_USER}/nena-home-app/main/app-icon.png"

st.markdown(f"""
    <link rel="apple-touch-icon" href="{ICON_URL}">
    <style>
        .stApp {{ background-color: #ffffff; }}
        h1, h2 {{ color: #2c2c2c; text-align: center; font-family: serif; }}
        .stButton>button {{ 
            height: 75px; width: 100%; border-radius: 15px; 
            font-size: 18px; background-color: #c5a059; color: white; border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
            font-weight: bold;
        }}
    </style>
    """, unsafe_allow_html=True)
# --- CLEAN UI (VERSTECKT STREAMLIT BRANDING) ---
st.markdown("""
    <style>
        /* Versteckt das Streamlit-Menü (Hamburger oben rechts) */
        #MainMenu {visibility: hidden;}
        
        /* Versteckt den 'Made with Streamlit' Footer ganz unten */
        footer {visibility: hidden;}
        
        /* Versteckt den roten Strich oben am Rand */
        header {visibility: hidden;}
        
        /* Entfernt unnötigen Platz am oberen Rand */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
# 3. DATEN-LOGIK
LOG_FILE = "service_log.xlsx"

def save_request(user_data, typ, details):
    df = pd.read_excel(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', 'Silbersteinstraße'),
        "Unit": str(user_data.get('unit', '101')).upper(),
        "Typ": typ, "Details": details, "Status": "Offen"
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 4. LOGIN & MENÜ
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    st.title("Willkommen Zuhause")
    email = st.text_input("E-Mail Adresse", placeholder="z.B. test@nena.de").strip().lower()
    if st.button("Anmelden"):
        # Wir lassen dich zum Testen mit 'test@nena.de' immer rein
        if email == "test@nena.de" or "@nena-apartments.de" in email:
            st.session_state.user = {"mieter": "Test User", "unit": "S-105", "haus": "Silbersteinstraße"}
            st.rerun()
        else: st.error("E-Mail nicht gefunden.")
else:
    user = st.session_state.user
    st.title(f"Hallo {user['mieter']}!")
    st.write(f"📍 Apartment {user['unit']}")
    
    st.divider()
    if st.button("🛠️ Schaden melden (mit Foto)"):
        st.info("Kamera-Funktion wird geladen...")
        # Hier kannst du später st.camera_input() nutzen
        
    if st.button("✨ Reinigung bestellen"):
        save_request(user, "Reinigung", "Standard Paket")
        st.success("Gebucht!")

    st.divider()
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.rerun()
