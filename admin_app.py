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

# Hintergrund-Logik
bg_file = "startseite.jpg" if st.session_state.user is None else "bg_default.jpg"
img_base64 = get_base64_image(bg_file)
logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")

# 4. DAS FINALE LAYOUT (TRANSPARENZ-FIX)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild Fix */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    /* RADIKALE TRANSPARENZ: Entfernt alle weißen Zwischenflächen */
    [data-testid="stAppViewMain"], 
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"],
    .stMainContainer {{ 
        background-color: transparent !important; 
        border: none !important;
    }}

    /* Nena Header (140px, Logo Links) */
    .nena-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: white; height: 140px;
        display: flex; justify-content: flex-start; align-items: center;
        padding-left: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1); z-index: 9999;
    }}
    .nena-logo-img {{ height: 100px; width: auto; }}

    /* Weißer Text auf dem Bild */
    .hero-text {{
        text-align: center; color: white;
        margin-top: 18vh; margin-bottom: 2vh;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6);
        font-family: 'Inter', sans-serif;
    }}
    .hero-text h1 {{ font-size: 4rem !important; font-weight: 700; margin-bottom: 5px; }}
    .hero-text p {{ font-size: 1.4rem; opacity: 0.95; font-weight: 400; }}

    /* Login Balken (NUR dieser Bereich ist weiß) */
    .login-bar-container {{
        background-color: white !important;
        padding: 40px !important; 
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4) !important;
        max-width: 850px; 
        margin: 0 auto !important;
        display: block;
    }}

    /* Symmetrie: Input & Button */
    .stTextInput > div > div > input {{
        height: 65px !important;
        border: 1px solid #ccc !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        background-color: #f9f9f9 !important;
    }}
    .stTextInput label {{ display: none !important; }}

    .stButton > button {{
        background-color: #e66b45 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 65px !important; 
        width: 100% !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        border: none !important;
    }}

    /* Streamlit UI ausblenden */
    section[data-testid="stSidebar"], [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. HEADER (Logo Links)
st.markdown(f"""
    <div class="nena-header">
        <img src="data:image/png;base64,{logo_base64}" class="nena-logo-img">
    </div>
""", unsafe_allow_html=True)

# 6. LOGIK: LOGIN ODER CONTENT
if st.session_state.user is None:
    # Textbereich (Direkt auf dem Hintergrund)
    st.markdown("""
        <div class="hero-text">
            <h1>Unterwegs und doch zu Hause</h1>
            <p>Nena Apartments by LESA – privat oder beruflich, kurz oder lang</p>
        </div>
    """, unsafe_allow_html=True)

    # Login-Balken (Eingebettet in ein transparentes Streamlit-Container-System)
    st.markdown('<div class="login-bar-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1]) # E-Mail breiter als Button
    
    with col1:
        email = st.text_input("EMAIL", placeholder="Ihre E-Mail Adresse eingeben...").strip().lower()
    
    with col2:
        if st.button("LOGIN"):
            if os.path.exists("apartments.xlsx"):
                df = pd.read_excel("apartments.xlsx")
                df.columns = [str(c).strip().lower() for c in df.columns]
                user = df[df['mail'].astype(str).str.lower() == email]
                if not user.empty:
                    st.session_state.user = user.iloc.to_dict()
                    st.rerun()
                else:
                    st.error("E-Mail unbekannt.")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- MIETER-BEREICH ---
    st.markdown(f"<h1 style='text-align:center; color:white; margin-top:50px;'>Willkommen {st.session_state.user.get('mieter', '')}</h1>", unsafe_allow_html=True)
    if st.button("Abmelden"):
        st.session_state.user = None
        st.rerun()
