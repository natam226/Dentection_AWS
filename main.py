import streamlit as st
import runpy
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Dentection App", page_icon="🦷", layout="wide")


st.markdown("<h1 style='text-align:left; color:#274675; font-size:48px; margin:0.25rem 0;'>🦷 Dentection app </h1>", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Acerca de", "Detector de anomalías dentales"],
    icons=["info-circle", "image"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#F9F9F9"}, 
        "menu-title": {"font-size": "20px", "color": "#274675", "padding": "8px 20px", "font-weight": "bold"},
        "nav-link": {"font-size": "16px", "color": "#274675", "padding": "8px 20px"},
        "nav-link-selected": {"background-color": "#274675", "color": "white"},
        "icon": {"color": "#9B9B9B", "font-size": "18px"}
    }
)

if selected == "Acerca de":
    runpy.run_path("inicio.py", run_name="__main__")
else:
    runpy.run_path("app.py", run_name="__main__")