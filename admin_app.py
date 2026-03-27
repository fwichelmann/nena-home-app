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

# 4. DAS NEUE LAYOUT (WEISSER BALKEN & WEISSER TEXT)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild Fix */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Nena Header */
    .nena-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: white; height: 140px;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1); z-index: 9999;
    }}
    .nena-logo-img {{ height: 100px; width: auto; }}

    /* Weißer Text auf dem Bild */
    .hero-text {{
        text-align: center;
        color: white;
        margin-top: 15vh;
        margin-bottom: 5vh;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.6);
    }}
    .hero-text h1 {{ font-size: 4.5rem !important; font-family: 'Playfair Display', serif; letter-spacing: 2px; }}
    .hero-text p {{ font-size: 1.5rem; opacity: 0.9; font-weight: 300; }}

    /* Login Balken (Der weiße Kasten unten) */
    .login-bar {{
        background-color: white;
        padding: 30px 50px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        max-width: 1000px;
        margin: 0 auto;
    }}

    /* Input-Styling für den Balken-Look */
    div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
    
    .stTextInput input {{
        border: none !important;
        border-bottom: 2px solid #eee !important;
        border-radius: 0px !important;
        font-size: 1.1rem !important;
    }}

    .stButton>button {{
        background-color: #e66b45 !important; /* Das Orange aus dem "Suche" Button */
        color: white !important;
        border-radius: 10px !important;
        height: 60px !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        border: none !important;
    }}

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
    # Weißer Text im Hero-Bereich
    st.markdown("""
        <div class="hero-text">
            <h1>Unterwegs und doch zu Hause</h1>
            <p>Nena Apartments by LESA – privat oder beruflich, kurz oder lang</p>
        </div>
    """, unsafe_allow_html=True)

    # Der weiße Balken (Login-Bereich)
    st.markdown('<div class="login-bar">', unsafe_allow_html=True)
    
    # Grid für E-Mail und Button nebeneinander
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email = st.text_input("IHRE E-MAIL ADRESSE", placeholder="name@beispiel.de").strip().lower()
    
    with col2:
        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Spacer
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
    st.markdown(f"<h1 style='text-align:center; color:white; margin-top:50px;'>Hallo {st.session_state.user['mieter']}</h1>", unsafe_allow_html=True)
    if st.button("Abmelden"):
        st.session_state.user = None
        st.rerun()
