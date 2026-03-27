import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="centered")

# BILDER-DATENBANK (Direkt von der Nena-Website)
BG_IMAGES = {
    "Wilhelmstraße": "https://www.nena-apartments.de",
    "Silbersteinstraße": "https://www.nena-apartments.de",
    "Default": "https://www.nena-apartments.de"
}

# 2. SESSION STATE
if "user" not in st.session_state:
    st.session_state.user = None

# Hintergrund-Logik: Welches Bild soll gezeigt werden?
current_bg = BG_IMAGES["Default"]
if st.session_state.user:
    haus = st.session_state.user.get('haus', 'Default')
    current_bg = BG_IMAGES.get(haus, BG_IMAGES["Default"])

# 3. VISUELLES DESIGN (Ken-Burns & Responsive UI)
st.markdown(f"""
    <style>
        /* Ken-Burns Effekt im Hintergrund */
        .stApp {{ background: none; }}
        .stApp::before {{
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
            background-image: url("{current_bg}");
            background-size: cover; background-position: center;
            animation: kenburns 25s infinite alternate ease-in-out;
        }}
        @keyframes kenburns {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.18); }}
        }}
        /* Overlay für bessere Lesbarkeit auf dem iPhone */
        .stApp::after {{
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
            background: rgba(255, 255, 255, 0.7); 
        }}
        /* Card Design für den Content */
        .block-container {{
            background: rgba(255, 255, 255, 0.95);
            padding: 2.5rem; border-radius: 0px; /* Eckig wie auf der Website */
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            margin-top: 10vh;
        }}
        /* Nena Typography & Buttons */
        h1, h2 {{ font-family: 'Playfair Display', serif; color: #2c2c2c; text-transform: uppercase; letter-spacing: 2px; }}
        .stButton>button {{ 
            height: 65px; border-radius: 0px; background-color: #c5a059; color: white; border: none;
            font-weight: 400; text-transform: uppercase; letter-spacing: 2px; transition: 0.4s;
        }}
        .stButton>button:hover {{ background-color: #2c2c2c; color: #c5a059; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 4. DATEI-LOGIK
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

# 5. LOGIN ODER HAUPTBEREICH
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>NENA HOME</h1>", unsafe_allow_html=True)
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("ANMELDEN"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
        else: st.error("Login aktuell nicht möglich (Datei fehlt).")

else:
    user = st.session_state.user
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.rerun()

    # --- ROLLEN-LOGIK ---
    if user.get('rolle') == 'admin':
        st.title("📊 DASHBOARD")
        if os.path.exists(LOG_FILE): st.dataframe(pd.read_excel(LOG_FILE), use_container_width=True)
    
    elif user.get('rolle') == 'hausmeister':
        st.title(f"🛠 POOL: {user['haus']}")
        # ... (Hausmeister Logik hier)
    
    else:
        st.title(f"HALLO {user['mieter'].split()[0]}")
        st.write(f"Apartment **{user['unit']}** | {user['haus']}")
        st.divider()
        
        with st.expander("🛠 SCHADEN MELDEN"):
            s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden", "Heizung", "Internet", "Licht", "Sonstiges"])
            s_desc = st.text_area("Beschreibung")
            cam = st.camera_input("Foto")
            if st.button("ABSENDEN"):
                path = f"temp_pics/{user['unit']}_{datetime.now().strftime('%H%M%S')}.png" if cam else "Kein Foto"
                if cam: 
                    with open(path, "wb") as f: f.write(cam.getbuffer())
                save_request(user, s_typ, s_desc, "Sofort", path)
                st.success("Meldung übermittelt.")
