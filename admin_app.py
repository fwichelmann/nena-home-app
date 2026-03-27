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

# 4. DAS RADIKALE CSS (ENTFERNT ALLE ZWISCHENRÄUME)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    /* ALLES TRANSPARENT & ABSTÄNDE AUF NULL */
    [data-testid="stAppViewMain"], [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"], .stMainContainer,
    [data-testid="stColumn"] {{ 
        background-color: transparent !important; 
        border: none !important;
        gap: 0rem !important; /* Entfernt den Spalt zwischen Elementen */
        padding: 0 !important;
    }}

    /* Nena Header (140px, Logo Links) */
    .nena-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: white !important; height: 140px;
        display: flex; justify-content: flex-start; align-items: center;
        padding-left: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1); z-index: 9999;
    }}
    .nena-logo-img {{ height: 100px; width: auto; }}

    /* Hero Text Bereich */
    .hero-container {{
        text-align: center; color: white;
        margin-top: 25vh; /* Tieferer Start */
        font-family: 'Inter', sans-serif;
    }}
    .hero-container h1 {{ 
        font-size: 4.2rem !important; font-weight: 700; margin: 0; 
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
    }}
    .hero-container p {{ 
        font-size: 1.5rem; opacity: 0.95; margin-bottom: 40px;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.8);
    }}

    /* DER WEISSE LOGIN-BALKEN (Kompakt & Symmetrisch) */
    .login-bar {{
        background-color: white !important;
        padding: 10px 10px 10px 30px !important; /* Weniger Padding oben/unten */
        border-radius: 15px;
        max-width: 900px;
        margin: 0 auto !important;
        display: flex;
        align-items: center;
        box-shadow: 0 15px 45px rgba(0,0,0,0.5);
    }}

    /* Input Feld Styling */
    .stTextInput {{ width: 100% !important; }}
    .stTextInput > div > div > input {{
        height: 65px !important;
        border: none !important; /* Kein Rand im weißen Balken */
        font-size: 1.2rem !important;
        background-color: transparent !important;
    }}
    .stTextInput label {{ display: none !important; }}

    /* Login Button Styling */
    .stButton > button {{
        background-color: #e66b45 !important; /* Suche-Orange */
        color: white !important;
        border-radius: 10px !important;
        height: 65px !important; 
        min-width: 180px !important;
        font-weight: bold !important;
        font-size: 1.3rem !important;
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
    # Textbereich
    st.markdown("""
        <div class="hero-container">
            <h1>Unterwegs und doch zu Hause</h1>
            <p>Nena Apartments by LESA – privat oder beruflich, kurz oder lang</p>
        </div>
    """, unsafe_allow_html=True)

    # Login-Balken (Ein einziger Container verhindert Geister-Elemente)
    # Wir bündeln alles in einem HTML-Block
    with st.container():
        st.markdown('<div class="login-bar">', unsafe_allow_html=True)
        # E-Mail Feld
        email = st.text_input("MAIL", placeholder="Ihre E-Mail Adresse eingeben...", label_visibility="collapsed").strip().lower()
        # Login Button
        if st.button("LOGIN"):
            if os.path.exists("apartments.xlsx"):
                df = pd.read_excel("apartments.xlsx")
                df.columns = [str(c).strip().lower() for c in df.columns]
                user = df[df['mail'].astype(str).str.lower() == email]
                if not user.empty:
                    st.session_state.user = user.iloc.to_dict()
                    st.rerun()
                else: st.error("Email unbekannt.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Mieter-Bereich
    st.markdown(f"<h1 style='text-align:center; color:white; margin-top:50px;'>Willkommen {st.session_state.user.get('mieter', '')}</h1>", unsafe_allow_html=True)
    if st.button("Abmelden"):
        st.session_state.user = None
        st.rerun()
