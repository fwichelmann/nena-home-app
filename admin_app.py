import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="centered")

# 2. DESIGN
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stApp { background-color: #ffffff; }
        .stButton>button { 
            height: 60px; width: 100%; border-radius: 12px; 
            font-size: 18px; background-color: #c5a059; color: white; border: none;
            font-weight: bold; margin-bottom: 10px;
        }
        .stButton>button:hover { background-color: #2c2c2c; color: #c5a059; }
        .chat-bubble { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 5px solid #c5a059; }
    </style>
    """, unsafe_allow_html=True)

LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details, termin="Keiner"):
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Erledigt_Am"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'),
        "Unit": str(user_data.get('unit', '-')),
        "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen",
        "Bearbeiter": "", "Chat": "", "Erledigt_Am": ""
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

if "user" not in st.session_state:
    st.session_state.user = None

# --- LOGIN ---
if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"): st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    st.title("Willkommen Zuhause")
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("Anmelden"):
        if os.path.exists(USER_FILE):
            df_apt = pd.read_excel(USER_FILE)
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
            if not user_row.empty:
                u_data = user_row.iloc[0].to_dict()
                st.session_state.user = {"mieter": u_data.get('mieter'), "unit": u_data.get('unit'), "haus": u_data.get('haus'), "rolle": str(u_data.get('rolle')).lower()}
                st.rerun()
        else: st.error("Systemfehler: Mieterliste fehlt.")

# --- HAUPTBEREICH ---
else:
    user = st.session_state.user
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.rerun()

    # A: ADMIN
    if user['rolle'] == 'admin':
        st.title("📊 Admin Zentrale")
        if os.path.exists(LOG_FILE):
            st.dataframe(pd.read_excel(LOG_FILE).sort_index(ascending=False), use_container_width=True)

    # B: HAUSMEISTER (Ticket-Pool + Chat)
    elif user['rolle'] == 'hausmeister':
        st.title(f"🛠 Service-Pool: {user['haus']}")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            mask = (df_log['Haus'] == user['haus']) & (df_log['Status'] != "Erledigt")
            pool = df_log[mask]
            for idx, row in pool.iterrows():
                is_busy = str(row['Bearbeiter']) != "nan" and str(row['Bearbeiter']) != ""
                with st.expander(f"{'⏳' if is_busy else '🆕'} {row['Unit']} - {row['Typ']}"):
                    st.write(f"**Problem:** {row['Details']}")
                    st.write(f"**Wunschtermin Mieter:** {row['Termin']}")
                    
                    # Chat-Verlauf anzeigen
                    if str(row['Chat']) != "nan" and row['Chat'] != "":
                        st.markdown(f"<div class='chat-bubble'>{row['Chat']}</div>", unsafe_allow_html=True)
                    
                    if not is_busy:
                        if st.button("Übernehmen", key=f"take_{idx}"):
                            df_log.at[idx, 'Bearbeiter'], df_log.at[idx, 'Status'] = user['mieter'], "In Arbeit"
                            df_log.to_excel(LOG_FILE, index=False); st.rerun()
                    else:
                        antwort = st.text_input("Nachricht an Mieter", key=f"msg_{idx}")
                        if st.button("Antwort senden", key=f"send_{idx}"):
                            df_log.at[idx, 'Chat'] = f"Hausmeister: {antwort}"
                            df_log.to_excel(LOG_FILE, index=False); st.success("Gesendet!"); st.rerun()
                        if st.button("Erledigt ✅", key=f"done_{idx}"):
                            df_log.at[idx, 'Status'], df_log.at[idx, 'Erledigt_Am'] = "Erledigt", datetime.now().strftime("%d.%m.%Y %H:%M")
                            df_log.to_excel(LOG_FILE, index=False); st.rerun()

    # C: MIETER (Meldung + Status-Check)
    else:
        st.title(f"Hallo {user['mieter']}!")
        tab1, tab2 = st.tabs(["Neuer Schaden", "Meine Meldungen"])
        
        with tab1:
            s_typ = st.selectbox("Was ist defekt?", ["Wasserschaden 💧", "Heizung 🔥", "Internet 🌐", "Licht 💡", "Sonstiges"])
            s_desc = st.text_area("Details")
            s_termin = st.text_input("Wunschtermin (z.B. Morgen ab 10:00 Uhr)")
            if st.button("Meldung absenden"):
                save_request(user, s_typ, s_desc, s_termin)
                st.success("Gesendet! Hausmeister informiert.")

        with tab2:
            if os.path.exists(LOG_FILE):
                my_logs = pd.read_excel(LOG_FILE)
                my_logs = my_logs[my_logs['Unit'] == str(user['unit'])]
                for _, r in my_logs.sort_index(ascending=False).iterrows():
                    color = "orange" if r['Status'] == "In Arbeit" else "green" if r['Status'] == "Erledigt" else "red"
                    with st.container():
                        st.markdown(f"**{r['Typ']}** - Status: :{color}[{r['Status']}]")
                        if str(r['Chat']) != "nan" and r['Chat'] != "":
                            st.info(f"Nachricht vom Hausmeister: {r['Chat']}")
                        st.divider()
