import streamlit as st
import runpy

st.set_page_config(page_title="Dentection App", page_icon="🦷", layout="wide")
st.markdown("<h1 style='text-align:left; color:#274675; font-size:48px; margin:0.25rem 0;'>🦷 Dentection app</h1>", unsafe_allow_html=True)

# Reemplazar option_menu con tabs nativo de Streamlit
tab1, tab2 = st.tabs(["📋 Acerca de", "🔍 Detector de anomalías dentales"])

with tab1:
    runpy.run_path("inicio.py", run_name="__main__")

with tab2:
    runpy.run_path("app.py", run_name="__main__")