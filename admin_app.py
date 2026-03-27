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
    return ""

# 3. SESSION STATE
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "home"

# Hintergrund-Logik
bg_file = "bg_default.jpg"
if st.session_state.user:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus: bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus: bg_file = "bg_silber.jpg"

img_base64 = get_base64_image(bg_file)
logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")

# 4. VISUELLES DESIGN (MEGA-HEADER & LOGO)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Fixierter Weißer Header (Höher für Mega-Logo) */
    .nena-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        height: 160px; /* Deutlich erhöht */
        display: flex;
        align-items: center;
        padding: 0 50px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.15);
        z-index: 9999;
    }}
    
    .nena-logo-img {{ 
        height: 120px !important; /* DOPPELT SO GROSS wie vorher */
        width: auto;
    }}

    /* Content-Abstand (muss tiefer anfangen wegen hohem Header) */
    .block-container {{ 
        padding-top: 200px !important; 
        max-width: 1200px !important; 
    }}

    /* Logout Button FIX im Header (oben rechts) */
    .stButton > button[key="logout_btn"] {{
        position: fixed !important;
        top: 55px !important; /* Mittig im 160px Header */
        right: 50px !important;
        z-index: 10000 !important;
        background: transparent !important;
        color: #2c2c2c !important;
        border: 1px solid #c5a059 !important;
        border-radius: 5px !important;
        width: 140px !important;
        height: 45px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
    }}
    .stButton > button[key="logout_btn"]:hover {{
        background: #c5a059 !important;
        color: white !important;
    }}

    /* Begrüßungs-Banner */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.96);
        padding: 50px; border-radius: 30px;
        text-align: center; margin-bottom: 60px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
    }}
    .welcome-banner h1 {{ 
        font-family: 'Playfair Display', serif; color: #2c2c2c; 
        font-size: 4rem; margin: 0; text-transform: uppercase; letter-spacing: 6px;
    }}

    /* Die 3 Haupt-Buttons */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 160px !important;
        border-radius: 35px !important;
        background-color: #f7e3b5 !important;
        color: #2c2c2c !important;
        font-family: 'Playfair Display', serif;
        font-size: 24px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        transition: all 0.4s ease;
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        transform: translateY(-10px);
        background-color: #c5a059 !important;
        color: white !important;
    }}

    /* Streamlit UI ausblenden */
    section[data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER (Nur wenn eingeloggt)
if st.session_state.user:
    st.markdown(f"""
        <div class="nena-header">
            <img src="data:image/png;base64,{logo_base64}" class="nena-logo-img">
        </div>
    """, unsafe_allow_html=True)

# 6. LOGIK & LOGIN
USER_FILE = "apartments.xlsx"

if st.session_state.user is None:
    st.markdown("<h1 style='color:white; text-align:center; margin-top:30vh; font-family:serif; letter-spacing:15px; font-size:4rem;'>NENA</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        with st.form("login_nena"):
            email = st.text_input("EMAIL").strip().lower()
            if st.form_submit_button("LOGIN"):
                if os.path.exists(USER_FILE):
                    df = pd.read_excel(USER_FILE)
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    user = df[df['mail'].astype(str).str.lower() == email]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Login fehlgeschlagen.")

else:
    user = st.session_state.user
    
    # Der Logout Button (technisch gesehen schwebt er über dem Header durch CSS)
    if st.button("LOGOUT ⮕", key="logout_btn"):
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    # BEGRÜSSUNG
    st.markdown(f"""
        <div class="welcome-banner">
            <h1>HALLO {str(user.get('mieter', 'Gast')).split()[0]}!</h1>
            <p style="margin:10px 0 0 0; color:#888; font-size: 1.5rem; letter-spacing:2px;">{user.get('haus', 'Berlin')} | UNIT {user.get('unit', '000')}</p>
        </div>
    """, unsafe_allow_html=True)

    # HAUPTSEITE
    if st.session_state.page == "home":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("REINIGUNG\nBUCHEN", key="b1"): st.session_state.page = "clean"; st.rerun()
        with c2:
            if st.button("SCHADEN\nMELDEN", key="b2"): st.session_state.page = "repair"; st.rerun()
        with c3:
            if st.button("MEIN\nKONTO", key="b3"): st.session_state.page = "account"; st.rerun()
    else:
        # Unterseiten-Card
        st.markdown('<div style="background:white; padding:4rem; border-radius:35px; box-shadow:0 30px 70px rgba(0,0,0,0.4);">', unsafe_allow_html=True)
        if st.button("← ZURÜCK", key="back_btn"): st.session_state.page = "home"; st.rerun()
        
        if st.session_state.page == "clean":
            st.subheader("REINIGUNG")
            st.write("Wählen Sie Ihren Wunschtermin.")
        elif st.session_state.page == "repair":
            st.subheader("SCHADEN MELDEN")
            st.selectbox("Kategorie", ["Licht", "Wasser", "Heizung"])
        elif st.session_state.page == "account":
            st.subheader("KONTO")
            st.write(f"Mieter: {user['mieter']}")
            
        st.markdown('</div>', unsafe_allow_html=True)
