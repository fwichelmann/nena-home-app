import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="wide")

# 2. HILFSFUNKTION: BILD IN BASE64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. SESSION STATE
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Hintergrund-Logik
bg_file = "bg_default.jpg"
if st.session_state.user:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus: bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus: bg_file = "bg_silber.jpg"

img_base64 = get_base64_image(bg_file)

# 4. VISUELLES DESIGN (Minimalist UI)
st.markdown(f"""
    <style>
    /* Hintergrund erzwingen */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64 if img_base64 else ''}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: rgba(0, 0, 0, 0.2); }}

    /* Content-Bereich anpassen */
    .block-container {{
        padding-top: 10vh !important;
        max-width: 900px !important;
    }}

    /* Nena Typography */
    h1, h2 {{ 
        font-family: 'Playfair Display', serif; 
        text-transform: uppercase; 
        color: white; 
        text-align: center; 
        letter-spacing: 4px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }}

    /* Weiße Card (nur sichtbar wenn nicht auf Home) */
    .content-card {{
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 0px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        color: #2c2c2c;
    }}

    /* Die 3 Haupt-Buttons nebeneinander */
    .stButton>button {{
        height: 100px;
        border-radius: 0px;
        background-color: rgba(197, 160, 89, 0.9); /* Nena Gold leicht transparent */
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px !important;
        transition: all 0.4s;
    }}
    .stButton>button:hover {{
        background-color: #2c2c2c;
        border-color: #c5a059;
    }}

    /* Sidebar & Streamlit Branding verstecken */
    section[data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. DATEI-LOGIK
LOG_FILE = "service_log.xlsx"
USER_FILE = "apartments.xlsx"

def save_request(user_data, typ, details):
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    new_entry = pd.DataFrame([{"Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"), "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')), "Typ": typ, "Details": details, "Status": "Offen", "Bearbeiter": "", "Chat": "", "Foto": "Kein Foto", "Erledigt_Am": ""}])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 6. LOGIN / HAUPTBEREICH
if st.session_state.user is None:
    # Zentrierter Login-Bereich auf dem Hintergrund
    st.markdown("<h1>NENA HOME</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        email_input = st.text_input("E-Mail Adresse").strip().lower()
        if st.button("LOGIN"):
            if os.path.exists(USER_FILE):
                df_apt = pd.read_excel(USER_FILE)
                df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
                user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
                if not user_row.empty:
                    st.session_state.user = user_row.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Unbekannte E-Mail")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    user = st.session_state.user
    
    # Header immer weiß/gold auf dem Bild
    st.markdown(f"<h1>HALLO {str(user.get('mieter', 'Mieter')).split()[0]}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:white; letter-spacing:2px; margin-bottom:4rem;'>{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>", unsafe_allow_html=True)

    # --- NAVIGATION ---
    
    if st.session_state.page == "home":
        # Die 3 Buttons nebeneinander
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Reinigung\nbestellen"):
                st.session_state.page = "clean"
                st.rerun()
                
        with col2:
            if st.button("Schaden\nmelden"):
                st.session_state.page = "repair"
                st.rerun()
                
        with col3:
            if st.button("Mein\nMieterkonto"):
                st.session_state.page = "account"
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Logout", key="lo"):
            st.session_state.user = None
            st.rerun()

    # --- UNTERSEITEN (In der weißen Card) ---
    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        if st.session_state.page == "clean":
            st.subheader("REINIGUNG")
            st.write("Wünschen Sie eine Zwischenreinigung Ihres Apartments?")
            if st.button("KOSTENPFLICHTIG BESTELLEN"):
                save_request(user, "Reinigung", "Standard Reinigung")
                st.success("Erfolgreich gebucht!")
        
        elif st.session_state.page == "repair":
            st.subheader("SCHADEN MELDEN")
            s_typ = st.selectbox("Typ", ["Wasser", "Licht", "Heizung", "Internet", "Möbel"])
            s_desc = st.text_area("Details")
            if st.button("MELDUNG ABSENDEN"):
                save_request(user, f"Schaden: {s_typ}", s_desc)
                st.success("Hausmeister informiert.")
        
        elif st.session_state.page == "account":
            st.subheader("MEIN KONTO")
            st.write(f"**Mieter:** {user['mieter']}")
            st.write(f"**Unit:** {user['unit']}")
            st.info("Ihre Dokumente werden geladen...")

        # Zurück-Button immer unten in der Card
        if st.button("← ZURÜCK"):
            st.session_state.page = "home"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
