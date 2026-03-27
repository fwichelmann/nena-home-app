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

# 4. VISUELLES DESIGN (DER PERFEKTE HEADER)
st.markdown(f"""
    <style>
    /* Hintergrund-Bild */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stAppViewMain"] {{ background-color: transparent !important; }}

    /* Fixierter Weißer Header wie auf der Website */
    .nena-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        height: 120px; /* Höher für größeres Logo */
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        z-index: 999999;
    }}
    
    .nena-logo-img {{ 
        height: 85px !important; /* Deutlich vergrößert */
        margin-top: 5px;
    }}

    /* Content-Abstand wegen des hohen Headers */
    .block-container {{ 
        padding-top: 160px !important; 
        max-width: 1100px !important; 
    }}

    /* Begrüßungs-Banner */
    .welcome-banner {{
        background: rgba(255, 255, 255, 0.95);
        padding: 40px; border-radius: 25px;
        text-align: center; margin-bottom: 50px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }}
    .welcome-banner h1 {{ 
        font-family: 'Playfair Display', serif; color: #2c2c2c; 
        font-size: 3.5rem; margin: 0; text-transform: uppercase; letter-spacing: 5px;
    }}

    /* Die 3 Haupt-Buttons (Gold/Beige) */
    div[data-testid="stHorizontalBlock"] .stButton>button {{
        min-height: 150px !important;
        width: 100% !important;
        border-radius: 30px !important;
        background-color: #f7e3b5 !important;
        color: #2c2c2c !important;
        border: none !important;
        font-family: 'Playfair Display', serif;
        font-size: 22px !important;
        line-height: 1.3 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover {{
        transform: translateY(-8px);
        background-color: #c5a059 !important;
        color: white !important;
    }}

    /* Logout Button Styling im Header */
    button[key="logout_btn"] {{
        background: transparent !important;
        color: #444 !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 8px 15px !important;
        width: auto !important;
        margin-top: 35px !important; /* Zentrierung im Header-Bereich */
    }}
    button[key="logout_btn"]:hover {{ 
        color: #c5a059 !important; 
        border-color: #c5a059 !important;
        background: #f9f9f9 !important;
    }}

    /* Streamlit UI ausblenden */
    section[data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"], footer {{ visibility: hidden; }}
    </style>
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    """, unsafe_allow_html=True)

# 5. LOGIK & LOGIN
USER_FILE = "apartments.xlsx"

if st.session_state.user is None:
    st.markdown("<h1 style='color:white; text-align:center; margin-top:25vh; font-family:serif; letter-spacing:10px;'>NENA HOME</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login_nena"):
            email = st.text_input("E-Mail Adresse").strip().lower()
            if st.form_submit_button("LOGIN"):
                if os.path.exists(USER_FILE):
                    df = pd.read_excel(USER_FILE)
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    user = df[df['mail'].astype(str).str.lower() == email]
                    if not user.empty:
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("E-Mail nicht in der Mieterliste gefunden.")

else:
    user = st.session_state.user
    
    # --- HEADER BAUEN (LOGO LINKS, LOGOUT RECHTS) ---
    logo_base64 = get_base64_image("nena-home-by-lesa-logo.png")
    
    # Der Header wird per HTML gezeichnet
    st.markdown(f"""
        <div class="nena-header">
            <img src="data:image/png;base64,{logo_base64}" class="nena-logo-img">
        </div>
    """, unsafe_allow_html=True)

    # Der funktionale Logout-Button wird über Streamlit positioniert (overlay)
    # Er "schwebt" technisch gesehen über dem Header
    col_l, col_r = st.columns([8.5, 1.5])
    with col_r:
        if st.button("LOGOUT ⮕", key="logout_btn"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # --- BEGRÜSSUNG ---
    st.markdown(f"""
        <div class="welcome-banner">
            <h1>HALLO {str(user.get('mieter', 'Gast')).split()[0]}!</h1>
            <p style="margin:5px 0 0 0; color:#888; font-size: 1.3rem; letter-spacing:1px;">{user.get('haus', 'Berlin')} | Unit {user.get('unit', '000')}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- HAUPTSEITE ---
    if st.session_state.page == "home":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Reinigung\nbuchen", key="btn_cl"): st.session_state.page = "clean"; st.rerun()
        with c2:
            if st.button("Schaden\nmelden", key="btn_rp"): st.session_state.page = "repair"; st.rerun()
        with c3:
            if st.button("Mein\nKonto", key="btn_ac"): st.session_state.page = "account"; st.rerun()
    else:
        # UNTERSEITEN (Weiße Card)
        st.markdown('<div style="background:white; padding:3rem; border-radius:25px; box-shadow:0 20px 50px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
        if st.button("← ZURÜCK", key="back"): st.session_state.page = "home"; st.rerun()
        
        if st.session_state.page == "clean":
            st.subheader("REINIGUNG BUCHEN")
            st.info("Hier können Sie eine Zwischenreinigung anfordern.")
            
        elif st.session_state.page == "repair":
            st.subheader("SCHADEN MELDEN")
            st.write("Bitte beschreiben Sie den Defekt.")
            
        elif st.session_state.page == "account":
            st.subheader("MEIN MIETERKONTO")
            st.write(f"Mieter: {user['mieter']}")
            
        st.markdown('</div>', unsafe_allow_html=True)
