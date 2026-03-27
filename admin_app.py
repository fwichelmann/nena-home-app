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

# Hintergrund-Logik (Korrektur auf .jpg)
if st.session_state.user is None:
    bg_file = "startseite.jpg"  # Korrigierte Dateiendung
else:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus: bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus: bg_file = "bg_silber.jpg"
    else: bg_file = "bg_default.jpg"

img_base64 = get_base64_image(bg_file)
logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")

# 4. VISUELLES DESIGN (140px Header & Startseite Fix)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild erzwingen */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Fixierter Weißer Header (140px hoch) */
    .nena-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        height: 140px;
        display: flex;
        align-items: center;
        padding: 0 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        z-index: 9999;
    }}
    
    .nena-logo-img {{ 
        height: 120px !important; 
        width: auto;
    }}

    /* Content-Abstand */
    .block-container {{ 
        padding-top: 170px !important; 
        max-width: 1200px !important; 
    }}

    /* Logout Button oben rechts im Header */
    button[key="logout_btn"] {{
        position: fixed !important;
        top: 45px !important;
        right: 50px !important;
        z-index: 10000 !important;
        background: white !important;
        color: #2c2c2c !important;
        border: 1px solid #c5a059 !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
    }}

    /* Login & Content Cards */
    .content-card {{
        background: rgba(255, 255, 255, 0.96);
        padding: 50px; border-radius: 30px;
        text-align: center;
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        max-width: 500px;
        margin: 0 auto;
    }}

    /* Die 3 Haupt-Buttons im Nena Gold */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 160px !important;
        border-radius: 35px !important;
        background-color: #f7e3b5 !important;
        color: #2c2c2c !important;
        font-family: 'Playfair Display', serif;
        font-size: 24px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        border: none !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        background-color: #c5a059 !important;
        color: white !important;
    }}

    section[data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER (Immer sichtbar)
st.markdown(f"""
    <div class="nena-header">
        <img src="data:image/png;base64,{logo_base64}" class="nena-logo-img">
    </div>
""", unsafe_allow_html=True)

# 6. LOGIK: LOGIN ODER CONTENT
USER_FILE = "apartments.xlsx"

if st.session_state.user is None:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:serif; letter-spacing:2px;'>ANMELDEN</h2>", unsafe_allow_html=True)
    
    email = st.text_input("EMAIL ADRESSE").strip().lower()
    if st.button("LOGIN", key="login_main"):
        if os.path.exists(USER_FILE):
            df = pd.read_excel(USER_FILE)
            df.columns = [str(c).strip().lower() for c in df.columns]
            user = df[df['mail'].astype(str).str.lower() == email]
            if not user.empty:
                st.session_state.user = user.iloc[0].to_dict()
                st.rerun()
            else: st.error("Email unbekannt.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Logout Button im Header
    if st.button("LOGOUT ⮕", key="logout_btn"):
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    # Begrüßung
    st.markdown(f"""
        <div style="background: rgba(255,255,255,0.95); padding:50px; border-radius:30px; text-align:center; margin-bottom:50px; box-shadow:0 10px 40px rgba(0,0,0,0.1);">
            <h1 style="font-family:'Playfair Display', serif; font-size:3.5rem; margin:0; text-transform: uppercase;">HALLO {str(st.session_state.user.get('mieter', 'Gast')).split()[0].upper()}!</h1>
            <p style="color:#888; font-size:1.4rem;">{st.session_state.user.get('haus')} | UNIT {st.session_state.user.get('unit')}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.page == "home":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("REINIGUNG\nBUCHEN", key="b1"): st.session_state.page = "clean"; st.rerun()
        with c2:
            if st.button("SCHADEN\nMELDEN", key="b2"): st.session_state.page = "repair"; st.rerun()
        with c3:
            if st.button("MEIN\nKONTO", key="b3"): st.session_state.page = "account"; st.rerun()
    else:
        st.markdown('<div class="content-card" style="max-width:800px;">', unsafe_allow_html=True)
        if st.button("← ZURÜCK", key="back"): st.session_state.page = "home"; st.rerun()
        
        if st.session_state.page == "clean": st.subheader("REINIGUNG")
        elif st.session_state.page == "repair": st.subheader("SCHADEN MELDEN")
        elif st.session_state.page == "account": st.subheader("MIETERKONTO")
        st.markdown('</div>', unsafe_allow_html=True)
