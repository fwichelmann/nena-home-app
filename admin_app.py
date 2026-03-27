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

# 4. VISUELLES DESIGN (Nena Premium UI)
st.markdown(f"""
    <style>
    /* Hintergrund */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64 if img_base64 else ''}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: rgba(0, 0, 0, 0.2); }}

    /* Content-Bereich */
    .block-container {{
        padding-top: 5vh !important;
        max-width: 1000px !important;
    }}

    /* Begrüßungs-Banner (Weiß hinterlegt) */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 5vh;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .welcome-banner h1 {{ 
        font-family: 'Playfair Display', serif; 
        color: #2c2c2c; margin: 0; text-transform: uppercase; letter-spacing: 2px;
    }}

    /* Die 3 Haupt-Buttons (Gleichgroß & Abgerundet) */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        height: 120px !important;
        width: 100% !important;
        border-radius: 20px !important; /* Abgerundete Ecken wie im Bild */
        background-color: #f7e3b5 !important; /* Helleres Gold/Beige */
        color: #2c2c2c !important;
        border: none !important;
        font-family: 'Playfair Display', serif;
        font-size: 18px !important;
        text-transform: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: transform 0.2s;
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        transform: translateY(-5px);
        background-color: #c5a059 !important;
        color: white !important;
    }}

    /* Kleiner Logout Button oben rechts */
    .logout-container {{
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 999;
    }}
    .logout-container button {{
        background: rgba(255,255,255,0.8) !important;
        color: #2c2c2c !important;
        border-radius: 10px !important;
        padding: 5px 15px !important;
        font-size: 12px !important;
        border: 1px solid #ddd !important;
    }}

    /* Unterseiten Card */
    .content-card {{
        background: rgba(255, 255, 255, 0.98);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    }}

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
    # Login Bereich
    st.markdown("<h1 style='color:white; text-align:center; margin-bottom:20px;'>NENA HOME</h1>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        email_input = st.text_input("E-Mail Adresse").strip().lower()
        if st.button("Anmelden"):
            if os.path.exists(USER_FILE):
                df_apt = pd.read_excel(USER_FILE)
                df_apt.columns = [str(c).strip().lower() for c in df_apt.columns]
                user_row = df_apt[df_apt['mail'].astype(str).str.lower() == email_input]
                if not user_row.empty:
                    st.session_state.user = user_row.iloc[0].to_dict()
                    st.rerun()
                else: st.error("E-Mail unbekannt.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    user = st.session_state.user
    
    # 7. LOGOUT BUTTON (OBEN RECHTS)
    col_empty, col_logout = st.columns([10, 1])
    with col_logout:
        if st.button("Logout ⮕"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # 8. BEGRÜSSUNG (WEISS HINTERLEGT)
    st.markdown(f"""
        <div class="welcome-banner">
            <h1>Hallo {str(user.get('mieter', 'Gast')).split()[0]}!</h1>
            <p style="margin:0; color:#666;">{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>
        </div>
    """, unsafe_allow_html=True)

    # 9. NAVIGATION
    if st.session_state.page == "home":
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Reinigung\nbuchen"):
                st.session_state.page = "clean"; st.rerun()
        with col2:
            if st.button("Schaden\nmelden"):
                st.session_state.page = "repair"; st.rerun()
        with col3:
            if st.button("Mein\nKonto"):
                st.session_state.page = "account"; st.rerun()

    # UNTERSEITEN
    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if st.session_state.page == "clean":
            st.subheader("Reinigungsservice")
            if st.button("Kostenpflichtige Reinigung bestellen"):
                save_request(user, "Reinigung", "Standard")
                st.success("Erfolgreich gebucht!")
        
        elif st.session_state.page == "repair":
            st.subheader("Schaden melden")
            s_typ = st.selectbox("Was ist defekt?", ["Wasser", "Licht", "Heizung", "Internet", "Möbel"])
            s_desc = st.text_area("Details")
            if st.button("Meldung absenden"):
                save_request(user, f"Schaden: {s_typ}", s_desc)
                st.success("Meldung erhalten!")
        
        elif st.session_state.page == "account":
            st.subheader("Mein Mieterkonto")
            st.write(f"Apartment: {user['unit']}")
            st.info("Ihre Dokumente werden geladen...")

        if st.button("← Zurück"):
            st.session_state.page = "home"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
