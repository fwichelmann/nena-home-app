import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. APP-KONFIGURATION
st.set_page_config(page_title="Nena Home", page_icon="app-icon.png", layout="wide")

# 2. HILFSFUNKTIONEN
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def save_request(user_data, typ, details):
    LOG_FILE = "service_log.xlsx"
    if os.path.exists(LOG_FILE): df = pd.read_excel(LOG_FILE)
    else: df = pd.DataFrame(columns=["Zeitstempel", "Haus", "Unit", "Typ", "Details", "Status", "Bearbeiter", "Chat", "Foto", "Erledigt_Am"])
    new_entry = pd.DataFrame([{"Zeitstempel": datetime.now().strftime("%d.%m.%Y %H:%M"), "Haus": user_data.get('haus', '-'), "Unit": str(user_data.get('unit', '-')), "Typ": typ, "Details": details, "Status": "Offen", "Bearbeiter": "", "Chat": "", "Foto": "Kein Foto", "Erledigt_Am": ""}])
    pd.concat([df, new_entry], ignore_index=True).to_excel(LOG_FILE, index=False)

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "home"

# Hintergrund-Logik
if st.session_state.user is None:
    bg_file = "startseite.jpg"
else:
    haus = st.session_state.user.get('haus', '')
    bg_file = "bg_wilhelm.jpg" if "Wilhelm" in haus else "bg_silber.jpg" if "Silberstein" in haus else "bg_default.jpg"

img_base64 = get_base64_image(bg_file)
logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")

# 4. GLOBALER HEADER & CSS
st.markdown(f"""
    <style>
    /* Hintergrund */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"], [data-testid="stVerticalBlock"], .stMainContainer {{ 
        background-color: transparent !important; 
    }}

    /* Weißer Header (140px) */
    .nena-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: white !important; height: 140px;
        display: flex; justify-content: flex-start; align-items: center;
        padding-left: 50px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); z-index: 9999;
    }}
    .nena-logo-img {{ height: 100px; width: auto; }}

    /* Content-Abstand */
    .block-container {{ padding-top: 180px !important; max-width: 1200px !important; }}

    /* Mieter-Begrüßung (Weißes Banner) */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95);
        padding: 40px; border-radius: 25px; text-align: center;
        margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    .welcome-banner h1 {{ font-family: 'Inter', sans-serif; font-weight: 700; color: #2c2c2c; font-size: 3.5rem; margin: 0; }}

    /* Große Gold-Buttons */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 150px !important; border-radius: 30px !important;
        background-color: #f7e3b5 !important; color: #2c2c2c !important;
        font-family: 'Inter', sans-serif; font-size: 22px !important; font-weight: 700;
        border: none !important; box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        background-color: #c5a059 !important; color: white !important; transform: translateY(-5px);
    }}

    /* Logout Text oben rechts */
    button[key="logout_btn"] {{
        position: fixed !important; top: 50px !important; right: 50px !important;
        z-index: 10000 !important; background: transparent !important;
        color: #666 !important; border: none !important; text-transform: uppercase !important;
    }}

    /* Login Balken */
    .login-bar-wrapper {{
        background-color: white !important; padding: 25px 40px !important; 
        border-radius: 15px !important; box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
        max-width: 900px; margin: 40px auto !important;
    }}

    /* Unterseiten Card */
    .content-card {{ background: white; padding: 3rem; border-radius: 25px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); }}

    section[data-testid="stSidebar"], [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER (Immer sichtbar)
st.markdown(f'<div class="nena-header"><img src="data:image/png;base64,{logo_base64}" class="nena-logo-img"></div>', unsafe_allow_html=True)

# 6. LOGIK
if st.session_state.user is None:
    # --- LOGIN SEITE ---
    st.markdown('<div style="text-align:center; color:white; margin-top:10vh; text-shadow:2px 2px 10px rgba(0,0,0,0.8); font-family:Inter;"><h1>Unterwegs und doch zu Hause</h1><p style="font-size:1.4rem;">Nena Apartments by LESA – privat oder beruflich, kurz oder lang</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-bar-wrapper">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1: email = st.text_input("MAIL", placeholder="Ihre E-Mail...", label_visibility="collapsed").strip().lower()
    with col2: 
        if st.button("LOGIN", key="lg_btn"):
            if os.path.exists("apartments.xlsx"):
                df = pd.read_excel("apartments.xlsx")
                df.columns = [str(c).strip().lower() for c in df.columns]
                user_match = df[df['mail'].astype(str).str.lower() == email]
                if not user_match.empty:
                    st.session_state.user = user_match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Email unbekannt.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- MIETER BEREICH (Eingeloggt) ---
    # Logout oben rechts
    col_l, col_r = st.columns([9, 1])
    with col_r:
        if st.button("Abmelden ⮕", key="logout_btn"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    if st.session_state.page == "home":
        # Begrüßung
        st.markdown(f"""<div class="welcome-banner"><h1>HALLO {str(st.session_state.user['mieter']).split()[0].upper()}!</h1><p style="color:#888; font-size:1.3rem;">{st.session_state.user['haus']} | UNIT {st.session_state.user['unit']}</p></div>""", unsafe_allow_html=True)
        
        # 3 Große Buttons
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Reinigung\nbuchen", key="nav_c"): st.session_state.page = "clean"; st.rerun()
        with c2:
            if st.button("Schaden\nmelden", key="nav_r"): st.session_state.page = "repair"; st.rerun()
        with c3:
            if st.button("Mein\nKonto", key="nav_a"): st.session_state.page = "account"; st.rerun()
    
    else:
        # Unterseiten
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if st.button("← ZURÜCK"): st.session_state.page = "home"; st.rerun()
        
        if st.session_state.page == "clean":
            st.subheader("REINIGUNG BESTELLEN")
            if st.button("Jetzt Reinigung anfordern"):
                save_request(st.session_state.user, "Reinigung", "Standard")
                st.success("Erfolgreich gebucht!")
        
        elif st.session_state.page == "repair":
            st.subheader("SCHADEN MELDEN")
            typ = st.selectbox("Was ist defekt?", ["Licht", "Wasser", "Heizung", "Internet", "Möbel"])
            desc = st.text_area("Details")
            if st.button("Absenden"):
                save_request(st.session_state.user, f"Schaden: {typ}", desc)
                st.success("Meldung erhalten!")
                
        elif st.session_state.page == "account":
            st.subheader("MEIN KONTO")
            st.write(f"Mieter: {st.session_state.user['mieter']}")
            st.write(f"Apartment: {st.session_state.user['unit']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
