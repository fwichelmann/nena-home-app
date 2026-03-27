import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(
    page_title="Nena Home", 
    page_icon="app-icon.png", 
    layout="centered",
    initial_sidebar_state="auto"
)

# 2. DESIGN & BRANDING (Nena Style)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #ffffff; }
        h1, h2 { color: #2c2c2c; text-align: center; font-family: serif; }
        
        /* Nena Gold Buttons */
        .stButton>button { 
            height: 60px; width: 100%; border-radius: 12px; 
            font-size: 18px; background-color: #c5a059; color: white; border: none;
            font-weight: bold; margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover { background-color: #2c2c2c; color: #c5a059; border: 1px solid #c5a059; }
        
        /* Input Fields */
        .stTextInput>div>div>input { border-radius: 10px; height: 45px; }
        .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATEI-KONFIGURATION
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

# Hilfsfunktion: Anfrage speichern
def save_request(user_data, typ, details):
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'),
        "Unit": str(user_data.get('unit', '-')), # Speichert Sil-101 / Wilh-101
        "Typ": typ, 
        "Details": details, 
        "Status": "Offen"
    }])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_excel(LOG_FILE, index=False)

# 4. SESSION STATE (Gedächtnis der App)
if "user" not in st.session_state:
    st.session_state.user = None

# 5. LOGIN-BEREICH
if st.session_state.user is None:
    logo_file = "nena-home-by-lesa-logo.png"
    if os.path.exists(logo_file):
        st.image(logo_file, use_container_width=True)
    
    st.title("Willkommen Zuhause")
    email_input = st.text_input("Ihre E-Mail Adresse", placeholder="z.B. mieter@nena.de").strip().lower()
    
    if st.button("Anmelden"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            # Spaltennamen säubern
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            
            # Login-Check
            mail_col = [c for c in df_apt.columns if "mail" in c]
            if mail_col:
                user_row = df_apt[df_apt[mail_col[0]].astype(str).str.lower() == email_input]
                if not user_row.empty:
                    u_data = user_row.iloc[0].to_dict()
                    st.session_state.user = {
                        "mieter": u_data.get('mieter', 'Gast'),
                        "unit": u_data.get('unit', '000'),
                        "haus": u_data.get('haus', 'Nena Home'),
                        "rolle": str(u_data.get('rolle', 'user')).lower().strip()
                    }
                    st.rerun()
                else:
                    st.error("E-Mail nicht gefunden. Bitte prüfen Sie Ihre Eingabe.")
            else:
                st.error("Fehler: Spalte 'mail' nicht in Excel gefunden.")
        else:
            st.error(f"Datei '{USER_FILE}' nicht gefunden.")

# 6. HAUPTBEREICH (Eingeloggt)
else:
    user = st.session_state.user
    is_admin = user.get('rolle') == 'admin'
    
    # Seitennavigation für Admins
    if is_admin:
        choice = st.sidebar.radio("Menü", ["Mieter-Ansicht", "Admin Dashboard"])
    else:
        choice = "Mieter-Ansicht"

    # --- SEITE: ADMIN DASHBOARD ---
    if choice == "Admin Dashboard":
        st.title("🛡️ Admin Dashboard")
        st.subheader("Übersicht aller Service-Anfragen")
        
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            
            # Schnellfilter nach Haus
            haus_filter = st.multiselect("Haus filtern:", 
                                       options=["Silbersteinstraße", "Wilhelmstraße"],
                                       default=["Silbersteinstraße", "Wilhelmstraße"])
            
            filtered_df = df_log[df_log['Haus'].isin(haus_filter)]
            
            # Metriken
            c1, c2 = st.columns(2)
            c1.metric("Anfragen", len(filtered_df))
            c2.metric("Offen", len(filtered_df[filtered_df['Status'] == 'Offen']))
            
            st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
            
            # Export
            with open(LOG_FILE, "rb") as f:
                st.download_button("Gesamtes Log herunterladen", f, file_name="nena_log.xlsx")
        else:
            st.info("Noch keine Anfragen vorhanden.")

    # --- SEITE: MIETER-ANSICHT ---
    else:
        st.title(f"Hallo {user['mieter']}!")
        st.markdown(f"**{user['haus']}** | Apartment: **{user['unit']}**")
        st.divider()

        # Feature 1: Schaden melden
        with st.expander("🛠️ Schaden melden"):
            s_typ = st.selectbox("Was ist das Problem?", ["Heizung", "Licht/Strom", "Wasser", "Möbel", "Sonstiges"])
            s_desc = st.text_area("Details zum Schaden")
            st.camera_input("Foto aufnehmen") # Foto-Speicherung folgt im nächsten Schritt
            
            if st.button("Meldung jetzt absenden"):
                save_request(user, f"Schaden: {s_typ}", s_desc)
                st.success("Meldung wurde gespeichert. Das Office kümmert sich!")

        # Feature 2: Reinigung
        if st.button("✨ Reinigung bestellen"):
            save_request(user, "Reinigung", "Standard Paket angefordert")
            st.success("Reinigung erfolgreich gebucht!")

        # Feature 3: Office Kontakt
        if st.button("💬 Nachricht an das Office"):
            st.info("Messenger-Funktion kommt in Kürze.")

    # Logout Button in der Sidebar
    st.sidebar.divider()
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.rerun()
