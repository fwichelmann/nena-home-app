import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. HANDY-OPTIMIERTES DESIGN
st.set_page_config(page_title="Nena Home App", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    /* Große Service-Buttons */
    .stButton>button { 
        height: 80px; 
        border-radius: 12px; 
        font-size: 18px; 
        background-color: #c5a059; 
        color: white; 
        border: none;
        margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #2c2c2c; color: #c5a059; }
    h1, h2 { color: #2c2c2c; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATEN-FUNKTIONEN
def save_service_request(user_data, typ, details):
    log_file = "service_log.xlsx"
    df = pd.read_excel(log_file) if os.path.exists(log_file) else pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status"])
    
    # Wir ziehen die Infos aus dem User-Profil
    unit = user_data.get('unit', 'Unbekannt')
    haus = user_data.get('haus', 'Silbersteinstraße')
    
    new_entry = pd.DataFrame([{
        "Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "Haus": haus,
        "Unit": str(unit).upper(),
        "Typ": typ,
        "Details": details,
        "Status": "Offen"
    }])
    pd.concat([df, new_entry], ignore_index=True).to_excel(log_file, index=False)

# 3. LOGIN-LOGIK
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    if os.path.exists("nena-home-by-lesa-logo.png"):
        st.image("nena-home-by-lesa-logo.png", use_container_width=True)
    st.title("Willkommen Zuhause")
    email_input = st.text_input("E-Mail Adresse").strip().lower()
    if st.button("Jetzt Anmelden"):
        if os.path.exists("apartments.xlsx"):
            df_apt = pd.read_excel("apartments.xlsx")
            df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
            mail_col = [c for c in df_apt.columns if "mail" in c][0]
            user_row = df_apt[df_apt[mail_col].astype(str).str.lower() == email_input]
            if not user_row.empty:
                st.session_state.user = user_row.iloc[0].to_dict()
                st.rerun()
            else: st.error("E-Mail nicht gefunden.")
else:
    # --- EINGELOGGT: DAS HAUPTMENÜ ---
    user = st.session_state.user
    # Namen finden
    name_col = [c for c in user.keys() if "mieter" in c or "name" in c][0]
    vorname = str(user[name_col]).split()[0] # Nur Vorname für die Begrüßung
    
    st.title(f"Hallo {vorname}!")
    st.write(f"📍 Apartment {user.get('unit', '')}")
    
    st.divider()

    # SERVICE BUTTONS (Groß für Handy)
    if st.button("🛠️ Schaden melden"):
        st.session_state.page = "schaden"
        st.rerun()
    
    if st.button("✨ Reinigung bestellen"):
        st.session_state.page = "reinigung"
        st.rerun()
        
    if st.button("💬 Nachricht an Office"):
        st.session_state.page = "nachricht"
        st.rerun()

    # UNTERSEITEN LOGIK
    if "page" in st.session_state:
        if st.session_state.page == "schaden":
            st.subheader("Was ist defekt?")
            desc = st.text_area("Details (z.B. Heizung geht nicht)")
            if st.button("Absenden"):
                save_service_request(user, "Reparatur", desc)
                st.success("Erledigt! Der Hausmeister kommt.")
                del st.session_state.page # Zurück zum Menü
                
        elif st.session_state.page == "reinigung":
            st.subheader("Reinigung anfordern")
            if st.button("Bestätigen (Standard Clean)"):
                save_service_request(user, "Reinigung", "Standard Paket angefordert")
                st.success("Gebucht! Wir kommen vorbei.")
                del st.session_state.page

    st.divider()
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.rerun()
