import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- APP CONFIG & ICON ---
st.set_page_config(
    page_title="Nena Home", 
    page_icon="nena-home-by-lesa-logo.png", # Das wird das Tab-Icon
    layout="centered"
)

# CSS für echtes App-Feeling (Kein Scrollen, schöner Look)
st.markdown("""
    <style>
    /* Hintergrund & Schrift */
    .stApp { background-color: #ffffff; }
    h1, h2 { color: #2c2c2c; font-family: 'Playfair Display', serif; text-align: center; }
    
    /* Große 'Touch-Friendly' Buttons für das Handy */
    .stButton>button { 
        height: 70px; 
        width: 100%;
        border-radius: 15px; 
        font-size: 20px; 
        background-color: #c5a059; 
        color: white; 
        border: none;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Eingabefelder abrunden */
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

