import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="centered")

# 2. HILFSFUNKTION: BILD IN BASE64 UMWANDELN (Für stabilen Hintergrund)
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. SESSION STATE & HINTERGRUND-LOGIK
if "user" not in st.session_state:
    st.session_state.user = None

# Welches Bild soll geladen werden?
bg_file = "bg_default.jpg"
if st.session_state.user:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus:
        bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus:
        bg_file = "bg_silber.jpg"

img_base64 = get_base64_image(bg_file)

# 4. VISUELLES DESIGN (CSS FIX MIT LOKALEM BILD)
if img_base64:
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stAppViewMain {{
            background-color: rgba(0, 0, 0, 0.35); /* Dezentes Dunkel-Overlay */
        }}
        .block-container {{
            background: rgba(255, 255, 255, 0.98);
            padding: 3rem !important;
            border-radius: 2px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            margin-top: 8vh;
            max-width: 480px !important;
            text-align: center;
        }}
        h1, h2 {{ font-family: 'Playfair Display', serif; text-transform: uppercase; letter-spacing: 2px; color: #2c2c2c; }}
        .stButton>button {{ 
            height: 60px; border-radius: 0px; background-color: #c5a059; color: white; border: none;
            text-transform: uppercase; letter-spacing: 2px; width: 100%; transition: 0.3s;
        }}
        .stButton>button:hover {{ background-color: #2c2c2c; color: #c5a059; }}
        section[data-testid="stSidebar"] {{ display: none; }}
        </style>
        <link href="https://fonts.googleapis.com" rel="stylesheet">
        """, unsafe_allow_html=True)

# 5. DATEI-PFADE
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details, termin="Sofort", foto_path="Kein Foto"):
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    new_entry = pd.DataFrame([{"Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"), "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')), "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen", "Bearbeiter": "", "Chat": "", "Foto": foto_path, "Erledigt_Am": ""}])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 6. LOGIN / HAUPTBEREICH
if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    else:
        st.markdown("<h1>NENA HOME</h1>", unsafe_allow_html=True)
    
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("ANMELDEN"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
            else: st.error("E-Mail nicht gefunden.")
        else: st.error("Systemfehler: apartments.xlsx fehlt.")

else:
    user = st.session_state.user
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", width=180)

    st.markdown(f"<h2>HALLO {user.get('mieter', 'Gast').split()[0]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#666;'>{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>", unsafe_allow_html=True)
    st.divider()

    # ROLLEN-CHECK
    rolle = user.get('rolle', 'user')

    if rolle == 'admin':
        st.subheader("Admin Dashboard")
        if os.path.exists(LOG_FILE): st.dataframe(pd.read_excel(LOG_FILE))
    
    elif rolle == 'hausmeister':
        st.subheader(f"Service Pool {user['haus']}")
        # (Hier Pool-Logik einfügen)

    else:
        with st.expander("🛠 SCHADEN MELDEN"):
            s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden", "Heizung", "Internet", "Licht", "Möbel"])
            s_desc = st.text_area("Details")
            if st.button("MELDUNG ABSENDEN"):
                save_request(user, s_typ, s_desc)
                st.success("Erfolgreich übermittelt.")

    if st.button("ABMELDEN"):
        st.session_state.user = None
        st.rerun()
