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
bg_file = "startseite.jpg" if st.session_state.user is None else "bg_default.jpg"
img_base64 = get_base64_image(bg_file)
logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")

# 4. DAS STABILE CSS (ERZWINGT WEISSE KARTE)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild Fix */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Fixierter Weißer Header */
    .nena-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        height: 140px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        z-index: 9999;
    }}
    .nena-logo-img {{ height: 100px; width: auto; }}

    /* LOGIN-KARTE (ERZWINGT WEISSEN HINTERGRUND) */
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 180px; /* Platz für Header */
    }}

    /* Diese Klasse überschreibt die Streamlit-Standard-Breite */
    div[data-testid="stVerticalBlock"] > div:has(div.login-card) {{
        max-width: 450px !important;
        margin: 0 auto !important;
    }}

    .login-card {{
        background-color: rgba(255, 255, 255, 0.98) !important;
        padding: 40px !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4) !important;
        text-align: center !important;
        border: 1px solid #eee;
    }}

    .login-card h2 {{
        font-family: 'Playfair Display', serif !important;
        color: #c5a059 !important; /* Nena Gold */
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }}

    /* Eingabefelder Fix */
    .stTextInput label {{
        color: #2c2c2c !important; /* Dunkle Schrift für Label */
        font-weight: bold;
    }}

    .stButton>button {{
        background-color: #c5a059 !important;
        color: white !important;
        border-radius: 5px !important;
        height: 55px !important;
        font-weight: bold !important;
        margin-top: 20px;
    }}

    /* Verstecke Streamlit Elemente */
    section[data-testid="stSidebar"], [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER
st.markdown(f"""
    <div class="nena-header">
        <img src="data:image/png;base64,{logo_base64}" class="nena-logo-img">
    </div>
""", unsafe_allow_html=True)

# 6. LOGIN LOGIK
if st.session_state.user is None:
    # Wir nutzen ein div mit der Klasse "login-card" als Wrapper
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Spalten nutzen, um die Breite in der Mitte zu begrenzen
    col_l, col_main, col_r = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2>Anmelden</h2>", unsafe_allow_html=True)
        
        # Das Login Formular
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("IHRE E-MAIL ADRESSE").strip().lower()
            submit = st.form_submit_button("JETZT EINLOGGEN")
            
            if submit:
                if os.path.exists("apartments.xlsx"):
                    df = pd.read_excel("apartments.xlsx")
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    user = df[df['mail'].astype(str).str.lower() == email]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("E-Mail nicht gefunden.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- MIETER BEREICH (Wenn eingeloggt) ---
    st.markdown(f"<h1 style='text-align:center; color:white; margin-top:50px;'>Hallo {st.session_state.user['mieter']}</h1>", unsafe_allow_html=True)
    if st.button("Abmelden"):
        st.session_state.user = None
        st.rerun()
