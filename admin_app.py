import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="centered")

# 2. HILFSFUNKTION: BILD IN BASE64 UMWANDELN
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. SESSION STATE & NAVIGATION-LOGIK
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home" # Startseite nach Login

# Hintergrund festlegen
bg_file = "bg_default.jpg"
if st.session_state.user:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus: bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus: bg_file = "bg_silber.jpg"

img_base64 = get_base64_image(bg_file)

# 4. VISUELLES DESIGN (Custom CSS für die großen Buttons)
st.markdown(f"""
    <style>
    /* Hintergrund FIX */
    .stAppViewContainer {{
        background-image: url("data:image/jpg;base64,{img_base64 if img_base64 else ''}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    .stAppViewMain {{ background-color: rgba(0, 0, 0, 0.3); }}
    
    /* Die weiße Card */
    .block-container {{
        background: rgba(255, 255, 255, 0.98);
        padding: 3rem !important; border-radius: 2px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        margin-top: 5vh; max-width: 500px !important; text-align: center;
    }}
    
    h1, h2 {{ font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 2px; color: #2c2c2c; }}
    
    /* Große Nena-Buttons Styling */
    .stButton>button {{ 
        height: 80px; border-radius: 0px; background-color: #c5a059; color: white; border: none;
        text-transform: uppercase; letter-spacing: 2px; width: 100%; transition: 0.3s;
        font-size: 16px !important; font-weight: 400; margin-bottom: 15px;
    }}
    .stButton>button:hover {{ background-color: #2c2c2c; color: #c5a059; }}
    
    /* Spezieller Zurück-Button */
    .back-btn>div>button {{ background-color: #f0f2f6 !important; color: #2c2c2c !important; height: 40px !important; font-size: 12px !important; }}

    section[data-testid="stSidebar"] {{ display: none; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. DATEI-LOGIK
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details, termin="Sofort"):
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    new_entry = pd.DataFrame([{"Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"), "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')), "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen", "Bearbeiter": "", "Chat": "", "Foto": "Kein Foto", "Erledigt_Am": ""}])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 6. LOGIN / HAUPTBEREICH
if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"): st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    st.markdown("<h2>Anmelden</h2>", unsafe_allow_html=True)
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("JETZT EINLOGGEN"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
            else: st.error("E-Mail nicht gefunden.")
else:
    user = st.session_state.user
    
    # Header mit Logo & Begrüßung
    if os.path.exists("nena-home-by-lesa-logo.png"): st.image("nena-home-by-lesa-logo.png", width=150)
    st.markdown(f"<h2>HALLO {str(user.get('mieter', 'Gast')).split()[0]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#666; margin-bottom:2rem;'>{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>", unsafe_allow_html=True)

    # --- NAVIGATION ---
    
    # Variante A: STARTSEITE (Die 3 großen Buttons)
    if st.session_state.page == "home":
        if st.button("✨ REINIGUNG BESTELLEN"):
            st.session_state.page = "clean"
            st.rerun()
            
        if st.button("🛠 SCHADEN MELDEN"):
            st.session_state.page = "repair"
            st.rerun()
            
        if st.button("👤 MEIN MIETERKONTO"):
            st.session_state.page = "account"
            st.rerun()
        
        st.divider()
        if st.button("🚪 ABMELDEN", key="logout_main"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # Variante B: REINIGUNG
    elif st.session_state.page == "clean":
        st.subheader("Reinigungsservice")
        st.write("Möchten Sie eine Zwischenreinigung buchen?")
        if st.button("JETZT KOSTENPFLICHTIG BUCHEN"):
            save_request(user, "Reinigung", "Standard Reinigung angefordert")
            st.success("Vielen Dank! Wir kommen vorbei.")
        
        if st.button("← ZURÜCK", key="back_clean"):
            st.session_state.page = "home"
            st.rerun()

    # Variante C: SCHADEN
    elif st.session_state.page == "repair":
        st.subheader("Schaden melden")
        s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden", "Heizung", "Licht", "Möbel", "Internet"])
        s_desc = st.text_area("Kurze Beschreibung")
        if st.button("MELDUNG ABSENDEN"):
            save_request(user, f"Schaden: {s_typ}", s_desc)
            st.success("Der Hausmeister wurde informiert.")
        
        if st.button("← ZURÜCK", key="back_repair"):
            st.session_state.page = "home"
            st.rerun()

    # Variante D: MIETERKONTO
    elif st.session_state.page == "account":
        st.subheader("Mein Mieterkonto")
        st.write(f"**Name:** {user.get('mieter')}")
        st.write(f"**Apartment:** {user.get('unit')}")
        st.write(f"**Standort:** {user.get('haus')}")
        st.info("Rechnungen und Dokumente folgen in Kürze.")
        
        if st.button("← ZURÜCK", key="back_acc"):
            st.session_state.page = "home"
            st.rerun()
