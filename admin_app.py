import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="centered")

# Hintergrundbild-URL (Hier kannst du ein Bild von der Nena-Website oder ein eigenes nutzen)
BG_IMAGE_URL = "https://www.nena-apartments.de"

# 2. VISUELLES DESIGN (Custom CSS für Ken-Burns & Nena Style)
st.markdown(f"""
    <style>
        /* Ken-Burns Hintergrund Animation */
        .stApp {{
            background: none;
        }}
        
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background-image: url("{BG_IMAGE_URL}");
            background-size: cover;
            background-position: center;
            animation: kenburns 20s infinite alternate ease-in-out;
        }}

        @keyframes kenburns {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.15); }}
        }}

        /* Overlay für bessere Lesbarkeit */
        .stApp::after {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: rgba(255, 255, 255, 0.75); /* Helles Overlay wie auf der Website */
        }}

        /* Content Container Styling */
        .block-container {{
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }}

        /* Nena Schriften & Farben */
        h1, h2, h3 {{ 
            font-family: 'Playfair Display', serif; 
            color: #2c2c2c; 
            letter-spacing: 1px;
        }}
        
        .stButton>button {{ 
            height: 60px; border-radius: 0px; /* Eckig wie das Nena-Branding */
            background-color: #c5a059; color: white; border: none;
            font-weight: 400; text-transform: uppercase; letter-spacing: 2px;
            transition: all 0.4s;
        }}
        
        .stButton>button:hover {{ 
            background-color: #2c2c2c; color: #c5a059;
        }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 3. DATEI-LOGIK
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

if not os.path.exists("temp_pics"): os.makedirs("temp_pics")

def save_request(user_data, typ, details, termin="Keiner", foto_path="Kein Foto"):
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')),
        "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen",
        "Bearbeiter": "", "Chat": "", "Foto": foto_path, "Erledigt_Am": ""
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 4. SESSION STATE & LOGIN
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;'>NENA HOME</h1>", unsafe_allow_html=True)
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("ANMELDEN"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                u_data = user_row.iloc[0].to_dict()
                st.session_state.user = {"mieter": u_data.get('mieter'), "unit": u_data.get('unit'), "haus": u_data.get('haus'), "rolle": str(u_data.get('rolle')).lower()}
                st.rerun()
        else: st.error("Systemfehler: Mieterliste fehlt.")

# 5. HAUPTBEREICH
else:
    user = st.session_state.user
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.rerun()

    # ADMIN
    if user['rolle'] == 'admin':
        st.title("📊 Intelligence Dashboard")
        if os.path.exists(LOG_FILE):
            st.dataframe(pd.read_excel(LOG_FILE).sort_index(ascending=False), use_container_width=True)

    # HAUSMEISTER
    elif user['rolle'] == 'hausmeister':
        st.title(f"🛠 Service-Pool: {user['haus']}")
        # ... (Restlicher Hausmeister-Code wie zuvor)

    # MIETER
    else:
        st.title(f"Willkommen, {user['mieter']}")
        st.write(f"Apartment **{user['unit']}** | {user['haus']}")
        st.divider()
        
        with st.expander("🛠 SCHADEN MELDEN"):
            s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden", "Heizung", "Internet", "Licht", "Möbel"])
            s_desc = st.text_area("Details")
            s_termin = st.text_input("Terminwunsch")
            cam = st.camera_input("Foto")
            if st.button("MELDUNG ABSENDEN"):
                path = f"temp_pics/{user['unit']}_{datetime.now().strftime('%H%M%S')}.png" if cam else "Kein Foto"
                if cam: 
                    with open(path, "wb") as f: f.write(cam.getbuffer())
                save_request(user, s_typ, s_desc, s_termin, path)
                st.success("Übermittelt.")
