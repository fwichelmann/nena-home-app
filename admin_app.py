import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home Admin", page_icon="app-icon.png", layout="wide")

# Ordner-Check
if not os.path.exists("temp_pics"): os.makedirs("temp_pics")

# E-MAIL KONFIGURATION (Hier deine Daten eintragen)
SMTP_SERVER = "smtp.gmail.com" # Beispiel für Gmail
SMTP_PORT = 587
SENDER_EMAIL = "deine-email@gmail.com"
SENDER_PASSWORD = "dein-app-passwort" # Nicht dein normales Passwort!
RECEIVER_EMAIL = "deine-ziel-email@nena.de"

# 2. HILFSFUNKTIONEN
def send_report(df):
    try:
        done_df = df[df['Status'] == 'Erledigt']
        perf = done_df['Bearbeiter'].value_counts().to_string()
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"Nena Home Wochenbericht - {datetime.now().strftime('%d.%m.%Y')}"
        
        body = f"Hallo Admin,\n\nhier ist die Auswertung der Woche:\n\nErledigte Tickets pro Mitarbeiter:\n{perf}\n\nGesamtanzahl offener Tickets: {len(df[df['Status'] == 'Offen'])}\n\nBeste Grüße,\nDeine Nena Home App"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"E-Mail Fehler: {e}")
        return False

LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details, termin="Keiner", foto_path="Kein Foto"):
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
    else:
        df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Termin", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": user_data.get('haus', '-'),
        "Unit": str(user_data.get('unit', '-')),
        "Typ": typ, "Details": details, "Termin": termin, "Status": "Offen",
        "Bearbeiter": "", "Chat": "", "Foto": foto_path, "Erledigt_Am": ""
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

if "user" not in st.session_state: st.session_state.user = None

# --- LOGIN ---
if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"): st.image("nena-home-by-lesa-logo.png", width=300)
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

    # A: ADMIN DASHBOARD
    if user['rolle'] == 'admin':
        st.title("📊 Nena Home Intelligence")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tickets Gesamt", len(df_log))
            c2.metric("Offen", len(df_log[df_log['Status'] == 'Offen']))
            c3.metric("Erledigt", len(df_log[df_log['Status'] == 'Erledigt']))
            
            if c4.button("📧 Wochenbericht senden"):
                if send_report(df_log): st.success("Bericht wurde per E-Mail gesendet!")
            
            st.divider()
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("Performance Hausmeister")
                done_df = df_log[df_log['Status'] == 'Erledigt']
                if not done_df.empty: st.bar_chart(done_df['Bearbeiter'].value_counts())
            with col_r:
                st.subheader("Tickets pro Standort")
                st.bar_chart(df_log['Haus'].value_counts())
            
            st.dataframe(df_log.sort_index(ascending=False), use_container_width=True)
        else: st.info("Keine Daten vorhanden.")

    # B: HAUSMEISTER
    elif user['rolle'] == 'hausmeister':
        st.title(f"🛠 Service-Pool: {user['haus']}")
        if os.path.exists(LOG_FILE):
            df_log = pd.read_excel(LOG_FILE)
            mask = (df_log['Haus'] == user['haus']) & (df_log['Status'] != "Erledigt")
            pool = df_log[mask]
            for idx, row in pool.iterrows():
                is_busy = str(row['Bearbeiter']) != "nan" and str(row['Bearbeiter']) != ""
                with st.expander(f"{'⏳' if is_busy else '🆕'} {row['Unit']} - {row['Typ']}"):
                    col_info, col_img = st.columns(2)
                    with col_info:
                        st.write(f"**Details:** {row['Details']}\n**Termin:** {row['Termin']}")
                        if str(row['Chat']) != "nan" and row['Chat'] != "": st.info(row['Chat'])
                    with col_img:
                        if str(row['Foto']) != "Kein Foto" and os.path.exists(row['Foto']): st.image(row['Foto'])
                    
                    if not is_busy:
                        if st.button("Übernehmen", key=f"take_{idx}"):
                            df_log.at[idx, 'Bearbeiter'], df_log.at[idx, 'Status'] = user['mieter'], "In Arbeit"
                            df_log.to_excel(LOG_FILE, index=False); st.rerun()
                    else:
                        msg = st.text_input("Nachricht", key=f"msg_{idx}")
                        if st.button("Senden", key=f"send_{idx}"):
                            df_log.at[idx, 'Chat'] = f"Hausmeister: {msg}"
                            df_log.to_excel(LOG_FILE, index=False); st.rerun()
                        if st.button("Erledigt ✅", key=f"done_{idx}"):
                            df_log.at[idx, 'Status'], df_log.at[idx, 'Erledigt_Am'] = "Erledigt", datetime.now().strftime("%d.%m.%Y %H:%M")
                            df_log.to_excel(LOG_FILE, index=False); st.rerun()

    # C: MIETER
    else:
        st.title(f"Hallo {user['mieter']}!")
        t1, t2 = st.tabs(["Meldung", "Status"])
        with t1:
            s_typ = st.selectbox("Problem", ["Wasserschaden 💧", "Heizung 🔥", "Internet 🌐", "Licht 💡", "Sonstiges"])
            s_desc = st.text_area("Beschreibung")
            s_termin = st.text_input("Wunschtermin")
            cam = st.camera_input("Foto")
            if st.button("Absenden"):
                path = f"temp_pics/{user['unit']}_{datetime.now().strftime('%H%M%S')}.png" if cam else "Kein Foto"
                if cam: 
                    with open(path, "wb") as f: f.write(cam.getbuffer())
                save_request(user, s_typ, s_desc, s_termin, path)
                st.success("Gesendet!")
        with t2:
            if os.path.exists(LOG_FILE):
                logs = pd.read_excel(LOG_FILE)
                for _, r in logs[logs['Unit'] == str(user['unit'])].sort_index(ascending=False).iterrows():
                    st.write(f"**{r['Typ']}** - Status: {r['Status']}")
                    if str(r['Chat']) != "nan" and r['Chat'] != "": st.info(f"Hausmeister: {r['Chat']}")
                    st.divider()
