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

# 2. DESIGN & BRANDING (Nena Gold Style)
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
        .stBadge { background-color: #f0f2f6; padding: 5px; border-radius: 5px; }
        .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATEI-PFADE & LOGIK
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details):
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status", "Bearbeiter", "Erledigt_Am"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'),
        "Unit": str(user_data.get('unit', '-')),
        "Typ": typ, 
        "Details": details, 
        "Status": "Offen",
        "Bearbeiter": "",
        "Erledigt_Am": ""
    }])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_excel(LOG_FILE, index=False)

# 4. SESSION STATE
if "user" not in st.session_state:
    st.session_state.user = None

# 5. LOGIN-SYSTEM
if st.session_state.user is None:
    logo_file = "nena-home-by-lesa-logo.png"
    if os.path.exists(logo_file):
        st.image(logo_file, use_container_width=True)
    
    st.title("Willkommen Zuhause")
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    
    if st.button("Anmelden"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
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
                    st.error("E-Mail nicht gefunden.")
        else:
            st.error(f"Datei '{USER_FILE}' fehlt.")

# 6. HAUPTBEREICH (Eingeloggt)
else:
    user = st.session_state.user
    rolle = user['rolle']

    # Logout in der Sidebar
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.rerun()

    # --- A: ADMIN ANSICHT (Tracking & Performance) ---
    if rolle == 'admin':
        st.title("📊 Admin Zentrale")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            
            st.subheader("Performance-Übersicht")
            col1, col2 = st.columns(2)
            col1.metric("Tickets Gesamt", len(df_log))
            col2.metric("Offen", len(df_log[df_log['Status'] != 'Erledigt']))
            
            st.write("Alle Vorgänge:")
            st.dataframe(df_log.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Noch keine Daten vorhanden.")

    # --- B: HAUSMEISTER ANSICHT (Ticket-Pool) ---
    elif rolle == 'hausmeister':
        st.title(f"🛠 Service-Pool: {user['haus']}")
        st.write(f"Mitarbeiter: **{user['mieter']}**")
        
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            # Filter: Nur Schäden am eigenen Standort, die nicht erledigt sind
            mask = (df_log['Haus'] == user['haus']) & (df_log['Status'] != "Erledigt") & (df_log['Typ'].str.contains("Schaden", na=False))
            pool = df_log[mask].copy()

            if not pool.empty:
                for idx, row in pool.iterrows():
                    is_busy = str(row['Bearbeiter']) != "nan" and str(row['Bearbeiter']) != ""
                    with st.expander(f"{'⏳' if is_busy else '🆕'} {row['Unit']} - {row['Typ']}"):
                        st.write(f"**Details:** {row['Details']}")
                        st.write(f"**Eingang:** {row['Zeitstempel']}")
                        
                        if is_busy:
                            st.warning(f"In Arbeit bei: {row['Bearbeiter']}")
                            if row['Bearbeiter'] == user['mieter']:
                                if st.button("Erledigt ✅", key=f"done_{idx}"):
                                    df_log.at[idx, 'Status'] = "Erledigt"
                                    df_log.at[idx, 'Erledigt_Am'] = datetime.now().strftime("%d.%m.%Y %H:%M")
                                    df_log.to_excel(LOG_FILE, index=False)
                                    st.rerun()
                        else:
                            if st.button("Übernehmen 🚀", key=f"take_{idx}"):
                                df_log.at[idx, 'Bearbeiter'] = user['mieter']
                                df_log.at[idx, 'Status'] = "In Arbeit"
                                df_log.to_excel(LOG_FILE, index=False)
                                st.rerun()
            else:
                st.success("Keine offenen Reparaturen! ☕")

    # --- C: REINIGUNG ANSICHT ---
    elif rolle == 'cleaner':
        st.title(f"✨ Reinigungs-Pool: {user['haus']}")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            mask = (df_log['Haus'] == user['haus']) & (df_log['Typ'] == "Reinigung") & (df_log['Status'] != "Erledigt")
            pool = df_log[mask]
            
            if not pool.empty:
                for idx, row in pool.iterrows():
                    with st.expander(f"🧼 Reinigung: {row['Unit']}"):
                        st.write(f"Anfrage vom: {row['Zeitstempel']}")
                        if st.button("Erledigt ✅", key=f"clean_{idx}"):
                            df_log.at[idx, 'Status'] = "Erledigt"
                            df_log.at[idx, 'Bearbeiter'] = user['mieter']
                            df_log.at[idx, 'Erledigt_Am'] = datetime.now().strftime("%d.%m.%Y %H:%M")
                            df_log.to_excel(LOG_FILE, index=False)
                            st.rerun()
            else:
                st.success("Alle Apartments glänzen! ✨")

    # --- D: MIETER ANSICHT ---
    else:
        st.title(f"Hallo {user['mieter']}!")
        st.write(f"📍 **{user['haus']}** | Apartment: **{user['unit']}**")
        st.divider()

        with st.expander("🛠️ Schaden melden"):
            s_typ = st.selectbox("Was ist defekt?", 
                                ["Wasserschaden 💧", "Heizung defekt 🔥", "Möbel kaputt 🪑", 
                                 "TV läuft nicht 📺", "Internet ist langsam 🌐", "Licht/Strom 💡", "Sonstiges"])
            s_desc = st.text_area("Details zum Schaden")
            st.camera_input("Foto aufnehmen")
            if st.button("Meldung absenden"):
                save_request(user, f"Schaden: {s_typ}", s_desc)
                st.success("Der Hausmeister wurde informiert!")

        if st.button("✨ Reinigung bestellen"):
            save_request(user, "Reinigung", "Standard Paket")
            st.success("Reinigung gebucht!")

        if st.button("💬 Nachricht an Office"):
            st.info("Funktion folgt in Kürze.")
