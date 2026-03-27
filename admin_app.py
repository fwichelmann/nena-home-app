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

# Hintergrund-Logik
current_bg = BG_IMAGES["Default"]
if st.session_state.user:
    haus = st.session_state.user.get('haus', 'Default')
    current_bg = BG_IMAGES.get(haus, BG_IMAGES["Default"])

# 3. VISUELLES DESIGN (CSS FINALE)
st.markdown(f"""
    <style>
        /* Ken-Burns Hintergrund */
        [data-testid="stAppViewContainer"] {{
            background: none !important;
        }}
        
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background-image: url("{current_bg}");
            background-size: cover;
            background-position: center;
            animation: kenburns 30s infinite alternate ease-in-out;
        }}

        @keyframes kenburns {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.2); }}
        }}

        /* Dunkleres Overlay für besseren Kontrast */
        [data-testid="stAppViewContainer"]::after {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: rgba(0, 0, 0, 0.25); 
        }}

        /* Die weiße Card */
        .block-container {{
            background: rgba(255, 255, 255, 0.98);
            padding: 3.5rem !important;
            border-radius: 0px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.3);
            margin-top: 8vh;
            max-width: 500px !important;
            text-align: center;
        }}

        /* Typography */
        h1, h2, h3 {{ 
            font-family: 'Playfair Display', serif; 
            text-transform: uppercase; 
            letter-spacing: 3px;
            color: #2c2c2c;
            margin-bottom: 0.5rem;
        }}
        
        p {{ font-family: 'Inter', sans-serif; color: #666; }}

        /* Nena Buttons */
        .stButton>button {{ 
            height: 60px; border-radius: 0px; 
            background-color: #c5a059; color: white; border: none;
            text-transform: uppercase; letter-spacing: 2px;
            width: 100%;
            margin-top: 10px;
            transition: all 0.3s;
        }}
        
        .stButton>button:hover {{ background-color: #2c2c2c; color: #c5a059; }}

        /* Input styling */
        input {{ border-radius: 0px !important; border: 1px solid #ddd !important; }}
        
        /* Sidebar Hide */
        [data-testid="stSidebar"] {{ display: none; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 4. DATEI-LOGIK & ORDNER
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"
if not os.path.exists("temp_pics"): os.makedirs("temp_pics")

def save_request(user_data, typ, details, termin="Sofort", foto_path="Kein Foto"):
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    new_entry = pd.DataFrame([{"Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"), "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')), "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen", "Bearbeiter": "", "Chat": "", "Foto": foto_path, "Erledigt_Am": ""}])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 5. LOGIN / HAUPTBEREICH
if st.session_state.user is None:
    # Logo auf der Login-Seite
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    else:
        st.markdown("<h1>NENA HOME</h1>", unsafe_allow_html=True)
    
    st.markdown("<p>Willkommen Zuhause</p>", unsafe_allow_html=True)
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    
    if st.button("ANMELDEN"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
            else: st.error("E-Mail unbekannt.")
        else: st.error("Systemfehler: Mieterliste fehlt.")

else:
    user = st.session_state.user
    
    # Logo auch im eingeloggten Bereich oben anzeigen
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", width=200)

    st.markdown(f"<h2>HALLO {user.get('mieter', 'Gast').split()[0]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p>{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>", unsafe_allow_html=True)
    st.divider()

    # --- HAUSMEISTER LOGIK ---
    if user.get('rolle') == 'hausmeister':
        st.subheader("Service Pool")
        # (Hier den Pool-Code einfügen, falls nötig)
    
    # --- MIETER LOGIK ---
    else:
        with st.expander("🛠 SCHADEN MELDEN"):
            s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden", "Heizung", "Internet", "Licht", "Möbel"])
            s_desc = st.text_area("Details zum Problem")
            cam = st.camera_input("Foto aufnehmen")
            if st.button("ABSENDEN"):
                path = f"temp_pics/{user['unit']}_{datetime.now().strftime('%H%M%S')}.png" if cam else "Kein Foto"
                if cam: 
                    with open(path, "wb") as f: f.write(cam.getbuffer())
                save_request(user, s_typ, s_desc, "Sofort", path)
                st.success("Meldung wurde übermittelt.")

    if st.button("ABMELDEN"):
        st.session_state.user = None
        st.rerun()
