import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION & CLEAN UI
st.set_page_config(
    page_title="Nena Home", 
    page_icon="app-icon.png", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: NENA BRANDING & UI CLEANUP ---
st.markdown(f"""
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com">
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

# 2. DATEN-LOGIK
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

# 3. LOGIN & NAVIGATION
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    # Logo auf Login-Seite
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    
    st.title("Willkommen Zuhause")
    email = st.text_input("Ihre E-Mail", placeholder="z.B. test@nena.de").strip().lower()
    
    if st.button("Anmelden"):
        # Login gegen Excel
        if os.path.exists("apartments.xlsx"):
            df_apt = pd.read_excel("apartments.xlsx")
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            mail_col = [c for c in df_apt.columns if "mail" in c]
            if mail_col:
                user_row = df_apt[df_apt[mail_col[0]].astype(str).str.lower() == email]
                if not user_row.empty:
                    u_data = user_row.iloc[0].to_dict()
                    st.session_state.user = {
                        "mieter": u_data.get('mieter', 'Gast'),
                        "unit": u_data.get('unit', '000'),
                        "haus": u_data.get('haus', 'Silbersteinstraße')
                    }
                    st.rerun()
                else: st.error("E-Mail nicht gefunden.")
        else: st.error("Systemfehler: Mieterliste fehlt.")

else:
    # --- MIETER MENÜ ---
    user = st.session_state.user
    st.title(f"Hallo {user['mieter']}!")
    st.write(f"📍 **{user['haus']}** | Unit **{user['unit']}**")
    
    st.divider()

    # SERVICE MODULE
    with st.expander("🛠️ Schaden melden (Kamera nutzen)"):
        s_typ = st.selectbox("Was ist defekt?", ["Heizung", "Strom", "Wasser", "Möbel", "Sonstiges"])
        s_desc = st.text_area("Details")
        foto = st.camera_input("Foto aufnehmen")
        if st.button("Meldung absenden"):
            save_request(user, "Reparatur", f"{s_typ}: {s_desc}")
            st.success("Hausmeister wurde informiert!")

    if st.button("✨ Reinigung bestellen"):
        save_request(user, "Reinigung", "Standard Paket")
        st.success("Reinigung gebucht!")

    st.divider()
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.rerun()
