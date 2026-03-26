import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION (Muss die allererste Streamlit-Zeile sein!)
st.set_page_config(
    page_title="Nena Home", 
    page_icon="app-icon.png", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. APPLE-ICON-FIX & CLEAN UI (Nena Branding)
# Dieser Block zwingt das iPhone, dein quadratisches Logo als App-Icon zu erkennen
ICON_URL = "https://raw.githubusercontent.com"

st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{ICON_URL}">
        <link rel="apple-touch-icon" sizes="180x180" href="{ICON_URL}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
    </head>
    <style>
        /* Verstecke Streamlit Branding (Menü, Footer, Header) */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Hintergrund & Schriften */
        .stApp {{ background-color: #ffffff; }}
        h1, h2 {{ color: #2c2c2c; text-align: center; font-family: serif; }}
        
        /* Nena Gold Buttons (Handy-optimiert) */
        .stButton>button {{ 
            height: 75px; width: 100%; border-radius: 15px; 
            font-size: 18px; background-color: #c5a059; color: white; border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
            font-weight: bold;
        }}
        .stButton>button:hover {{ background-color: #2c2c2c; color: #c5a059; }}
        
        /* Eingabefelder Design */
        .stTextInput>div>div>input {{ border-radius: 10px; height: 50px; border: 1px solid #e0e0e0; }}
        
        /* Abstand oben korrigieren */
        .block-container {{ padding-top: 2rem; }}
    </style>
    """, unsafe_allow_html=True)

# 3. DATEN-LOGIK (Log-Datei für Service-Anfragen)
LOG_FILE = "service_log.xlsx"

def save_request(user_data, typ, details):
    # Lade bestehendes Log oder erstelle neues
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', 'Silbersteinstraße'),
        "Unit": str(user_data.get('unit', '101')).upper(),
        "Typ": typ, 
        "Details": details, 
        "Status": "Offen"
    }])
    
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_excel(LOG_FILE, index=False)

# 4. LOGIN-SYSTEM & NAVIGATION
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # Logo auf der Login-Seite anzeigen
    logo_file = "nena-home-by-lesa-logo.png"
    if os.path.exists(logo_file):
        st.image(logo_file, use_container_width=True)
    
    st.title("Willkommen Zuhause")
    email = st.text_input("Ihre E-Mail Adresse", placeholder="z.B. test@nena.de").strip().lower()
    
    if st.button("Jetzt Anmelden"):
        # Login gegen deine apartments.xlsx
        if os.path.exists("apartments.xlsx"):
            df_apt = pd.read_excel("apartments.xlsx")
            # Spaltennamen säubern
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            mail_col = [c for c in df_apt.columns if "mail" in c]
            
            if mail_col:
                user_row = df_apt[df_apt[mail_col[0]].astype(str).str.lower() == email]
                if not user_row.empty:
                    u_data = user_row.iloc[0].to_dict()
                    # Profil in Session speichern
                    st.session_state.user = {
                        "mieter": u_data.get('mieter', 'Gast'),
                        "unit": u_data.get('unit', '000'),
                        "haus": u_data.get('haus', 'Silbersteinstraße')
                    }
                    st.rerun()
                else:
                    st.error("E-Mail nicht in der Mieterliste gefunden.")
            else:
                st.error("Spalte 'E-Mail' in Excel nicht gefunden!")
        else:
            st.error("Datei 'apartments.xlsx' fehlt im System.")

else:
    # --- MIETER-BEREICH (EINGELOGGT) ---
    user = st.session_state.user
    st.title(f"Hallo {user['mieter']}!")
    st.write(f"📍 **{user['haus']}** | Apartment **{user['unit']}**")
    
    st.divider()

    # SERVICE MODULE (Akkordeon-Stil für Handy)
    with st.expander("🛠️ Schaden melden (Kamera nutzen)"):
        s_typ = st.selectbox("Was ist defekt?", ["Heizung", "Licht/Strom", "Wasser/Abfluss", "Möbel", "Internet"])
        s_desc = st.text_area("Details zum Schaden")
        # Öffnet am Handy direkt die Kamera
        foto = st.camera_input("Foto aufnehmen")
        if st.button("Schadensmeldung absenden"):
            save_request(user, "Reparatur", f"{s_typ}: {s_desc}")
            st.success("Vielen Dank! Der Hausmeister wurde informiert.")

    if st.button("✨ Reinigung bestellen"):
        save_request(user, "Reinigung", "Standard Paket angefordert")
        st.success("Buchung erhalten! Wir kommen vorbei.")

    if st.button("💬 Nachricht an das Office"):
        st.info("Funktion für Nachrichten kommt in Kürze!")

    st.divider()
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.rerun()
