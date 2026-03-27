import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(
    page_title="Nena Home", 
    page_icon="app-icon.png", 
    layout="centered",
    initial_sidebar_state="auto" # Auf "auto", damit du die Sidebar als Admin siehst
)

# 2. STYLING (Nena Branding)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #ffffff; }
        h1, h2 { color: #2c2c2c; text-align: center; font-family: serif; }
        .stButton>button { 
            height: 60px; width: 100%; border-radius: 12px; 
            font-size: 18px; background-color: #c5a059; color: white; border: none;
            font-weight: bold; margin-bottom: 10px;
        }
        .stButton>button:hover { background-color: #2c2c2c; color: #c5a059; border: 1px solid #c5a059; }
        .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATEI-PFADE
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details):
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'),
        "Unit": str(user_data.get('unit', '-')),
        "Typ": typ, 
        "Details": details, 
        "Status": "Offen"
    }])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_excel(LOG_FILE, index=False)

# 4. LOGIN-LOGIK
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    logo_file = "nena-home-by-lesa-logo.png"
    if os.path.exists(logo_file):
        st.image(logo_file, use_container_width=True)
    
    st.title("Willkommen Zuhause")
    email_input = st.text_input("Ihre E-Mail Adresse").strip().lower()
    
    if st.button("Anmelden"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            # Spaltennamen normalisieren (Kleinschreibung, keine Leerzeichen)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            
            # Suche nach der Mail-Spalte
            mail_col = [c for c in df_apt.columns if "mail" in c]
            if mail_col:
                user_row = df_apt[df_apt[mail_col[0]].astype(str).str.lower() == email_input]
                if not user_row.empty:
                    u_data = user_row.iloc[0].to_dict()
                    # Profil inkl. ROLLE in Session speichern
                    st.session_state.user = {
                        "mieter": u_data.get('mieter', 'Gast'),
                        "unit": u_data.get('unit', '000'),
                        "haus": u_data.get('haus', 'Nena Home'),
                        "rolle": str(u_data.get('rolle', 'user')).lower().strip()
                    }
                    st.rerun()
                else:
                    st.error("E-Mail nicht gefunden.")
            else:
                st.error("Spalte 'mail' fehlt in der Excel!")
        else:
            st.error(f"Datei '{USER_FILE}' fehlt auf GitHub.")

else:
    # --- NAVIGATION FÜR ADMINS ---
    user = st.session_state.user
    is_admin = user.get('rolle') == 'admin'
    
    if is_admin:
        choice = st.sidebar.radio("Navigation", ["Mieter-Ansicht", "Admin Dashboard"])
    else:
        choice = "Mieter-Ansicht"

    # --- SEITE 1: ADMIN DASHBOARD ---
    if choice == "Admin Dashboard":
        st.title("🛡️ Admin Bereich")
        st.write("Hier siehst du alle eingegangenen Anfragen.")
        
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            st.dataframe(df_log.sort_index(ascending=False), use_container_width=True)
            
            # Download Button für dich
            with open(LOG_FILE, "rb") as f:
                st.download_button("Excel-Log herunterladen", f, file_name="nena_service_log.xlsx")
        else:
            st.info("Noch keine Einträge im Service-Log.")

    # --- SEITE 2: NORMALE MIETER-ANSICHT ---
    else:
        st.title(f"Hallo {user['mieter']}!")
        st.write(f"📍 **{user['haus']}** | Apartment **{user['unit']}**")
        st.divider()

        with st.expander("🛠️ Schaden melden"):
            s_typ = st.selectbox("Was ist defekt?", ["Heizung", "Licht/Strom", "Wasser", "Möbel", "Sonstiges"])
            s_desc = st.text_area("Details")
            foto = st.camera_input("Foto hinzufügen")
            if st.button("Meldung absenden"):
                save_request(user, f"Schaden: {s_typ}", s_desc)
                st.success("Erfolgreich gesendet!")

        if st.button("✨ Reinigung bestellen"):
            save_request(user, "Reinigung", "Standard Reinigung angefordert")
            st.success("Anfrage erhalten!")

    # Logout immer unten in der Sidebar
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
