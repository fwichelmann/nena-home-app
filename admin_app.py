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
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "home"

# Hintergrund-Logik
bg_file = "bg_default.jpg"
if st.session_state.user:
    haus = st.session_state.user.get('haus', '')
    if "Wilhelm" in haus: bg_file = "bg_wilhelm.jpg"
    elif "Silberstein" in haus: bg_file = "bg_silber.jpg"

img_base64 = get_base64_image(bg_file)

# 4. VISUELLES DESIGN (HEADER-FIX & NENA STYLE)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64 if img_base64 else ''}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Fixierter Weißer Header */
    .nena-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        height: 100px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 50px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        z-index: 1000;
    }}
    
    .nena-logo {{ height: 60px; }}

    /* Content-Abstand wegen Header */
    .block-container {{ 
        padding-top: 140px !important; 
        max-width: 1100px !important; 
    }}

    /* Begrüßungs-Banner */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95);
        padding: 40px; border-radius: 20px;
        text-align: center; margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    .welcome-banner h1 {{ 
        font-family: 'Playfair Display', serif; color: #2c2c2c; 
        font-size: 3rem; margin: 0; text-transform: uppercase; letter-spacing: 4px;
    }}

    /* Die 3 Haupt-Buttons (Gold/Beige) */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 140px !important;
        width: 100% !important;
        border-radius: 20px !important;
        background-color: #f7e3b5 !important;
        color: #2c2c2c !important;
        border: none !important;
        font-family: 'Playfair Display', serif;
        font-size: 20px !important;
        line-height: 1.3 !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease;
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        transform: translateY(-5px);
        background-color: #c5a059 !important;
        color: white !important;
    }}

    /* Unsichtbarer Logout-Button als Text-Link-Stil */
    button[key="logout_btn"] {{
        background: transparent !important;
        color: #666 !important;
        border: none !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 0 !important;
        width: auto !important;
    }}
    button[key="logout_btn"]:hover {{ color: #c5a059 !important; }}

    section[data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER COMPONENT (HTML & Streamlit)
if st.session_state.user:
    # Wir bauen den Header direkt ein
    logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")
    
    st.markdown(f"""
        <div class="nena-header">
            <img src="data:image/png;base64,{logo_base64 if logo_base64 else ''}" class="nena-logo">
            <div id="logout-placeholder"></div>
        </div>
    """, unsafe_allow_html=True)

# 6. LOGIK & LOGIN
USER_FILE = "apartments.xlsx"

if st.session_state.user is None:
    st.markdown("<h1 style='color:white; text-align:center; margin-top:20vh; letter-spacing:10px;'>NENA HOME</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login_nena"):
            email = st.text_input("E-Mail").strip().lower()
            if st.form_submit_button("JETZT EINLOGGEN"):
                if os.path.exists(USER_FILE):
                    df = pd.read_excel(USER_FILE)
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    user = df[df['mail'].astype(str).str.lower() == email]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Benutzer nicht gefunden.")

else:
    user = st.session_state.user
    
    # Der echte Logout-Button wird über den Platzhalter im Header gesteuert (über Streamlit Columns)
    # Da Streamlit keine HTML-Buttons als Trigger nutzt, setzen wir ihn oben rechts in ein Column-Layout
    # das wir mit CSS so verschieben, dass es im weißen Header liegt.
    
    col_l, col_empty, col_r = st.columns([1, 8, 1.5])
    with col_r:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        if st.button("Abmelden ⮕", key="logout_btn"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # BEGRÜSSUNG
    st.markdown(f"""
        <div class="welcome-banner">
            <h1>HALLO {str(user.get('mieter', 'Gast')).split()[0]}!</h1>
            <p style="margin:0; color:#888; font-size: 1.2rem;">{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.page == "home":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Reinigung\nbuchen"): st.session_state.page = "clean"; st.rerun()
        with c2:
            if st.button("Schaden\nmelden"): st.session_state.page = "repair"; st.rerun()
        with c3:
            if st.button("Mein\nKonto"): st.session_state.page = "account"; st.rerun()
    else:
        # (Unterseiten-Logik hier...)
        if st.button("← Zurück"): st.session_state.page = "home"; st.rerun()
