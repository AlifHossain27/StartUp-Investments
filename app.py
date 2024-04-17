import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

# Page Configs
st.set_page_config(page_title="App", page_icon="📊", layout='wide', initial_sidebar_state='expanded')

# Remove Default theme
theme_plotly = None

# CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Side bar
def sidebar():
    st.sidebar.header("Dashboard")

if __name__ == "__main__":
    sidebar()