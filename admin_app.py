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

# 4. VISUELLES DESIGN (LAYOUT & LOGO FIX)
st.markdown(f"""
    <style>
    /* Hintergrund */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64 if img_base64 else ''}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: rgba(0, 0, 0, 0.05); }}

    /* Content-Bereich */
    .block-container {{ padding-top: 1rem !important; max-width: 1200px !important; }}

    /* Obere Leiste (Logo & Logout) */
    .top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        width: 100%;
    }}

    /* Begrüßungs-Banner */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95);
        padding: 40px; border-radius: 25px;
        text-align: center; margin-top: 20px; margin-bottom: 50px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }}
    .welcome-banner h1 {{ 
        font-family: 'Playfair Display', serif; color: #2c2c2c; 
        font-size: 3.5rem; margin: 0; text-transform: uppercase; letter-spacing: 5px;
    }}

    /* Die 3 Haupt-Buttons (Stabilisiertes Grid) */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 140px !important;
        width: 100% !important;
        border-radius: 30px !important;
        background-color: #f7e3b5 !important;
        color: #2c2c2c !important;
        border: none !important;
        font-family: 'Playfair Display', serif;
        font-size: 22px !important;
        line-height: 1.3 !important;
        padding: 20px !important;
        box-shadow: 0 12px 25px rgba(0,0,0,0.12) !important;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }}
    
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        transform: translateY(-8px);
        background-color: #c5a059 !important;
        color: white !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2) !important;
    }}

    /* Spezifisches Logout Button Styling */
    div.stButton > button[key="logout_btn"] {{
        background-color: rgba(255,255,255,0.85) !important;
        color: #2c2c2c !important;
        border-radius: 12px !important;
        width: 120px !important;
        height: 45px !important;
        font-size: 14px !important;
        border: 1px solid #eee !important;
    }}

    /* Unterseiten Card */
    .content-card {{
        background: rgba(255, 255, 255, 0.98);
        padding: 4rem; border-radius: 25px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.3);
    }}

    section[data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. LOGIK
USER_FILE = "apartments.xlsx"

if st.session_state.user is None:
    st.markdown("<h1 style='color:white; text-align:center; margin-top:25vh; font-family:serif; letter-spacing:10px;'>NENA HOME</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            mail = st.text_input("E-Mail").strip().lower()
            if st.form_submit_button("LOGIN"):
                if os.path.exists(USER_FILE):
                    df = pd.read_excel(USER_FILE)
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    user = df[df['mail'].astype(str).str.lower() == mail]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("E-Mail Adresse unbekannt.")
else:
    user = st.session_state.user
    
    # --- HEADER LEISTE (LOGO LINKS, LOGOUT RECHTS) ---
    col_logo, col_empty, col_logout = st.columns([2, 6, 2])
    
    with col_logo:
        logo_path = "nena-home-by-lesa-logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
            
    with col_logout:
        if st.button("Logout ⮕", key="logout_btn"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # --- BEGRÜSSUNG ---
    st.markdown(f"""
        <div class="welcome-banner">
            <h1>HALLO {str(user.get('mieter', 'Gast')).split()[0]}!</h1>
            <p style="margin-top:10px; color:#888; font-size: 1.3rem; letter-spacing:1px;">{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- HAUPTSEITE ---
    if st.session_state.page == "home":
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Reinigung\nbuchen", key="nav_clean"):
                st.session_state.page = "clean"; st.rerun()
        with col2:
            if st.button("Schaden\nmelden", key="nav_repair"):
                st.session_state.page = "repair"; st.rerun()
        with col3:
            if st.button("Mein\nKonto", key="nav_acc"):
                st.session_state.page = "account"; st.rerun()
                
    # --- UNTERSEITEN ---
    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        if st.button("← Zurück", key="global_back"):
            st.session_state.page = "home"; st.rerun()
            
        if st.session_state.page == "clean":
            st.subheader("Reinigung buchen")
            st.write("Wann sollen wir Ihr Apartment reinigen?")
            # Hier weitere Logik...
            
        elif st.session_state.page == "repair":
            st.subheader("Schaden melden")
            # Hier Schadens-Logik...
            
        elif st.session_state.page == "account":
            st.subheader("Mein Mieterkonto")
            # Hier Konto-Infos...
            
        st.markdown('</div>', unsafe_allow_html=True)
