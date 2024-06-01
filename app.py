import streamlit as st
import whatsapp
import telegram

st.set_page_config(page_title="WhatsApp Chat Analyzer")
st.sidebar.title("Chat Analyser")

app_list = ['WhatsApp', 'Telegram']
selected_app = st.sidebar.selectbox("Select app", app_list)

if selected_app == 'WhatsApp':
    whatsapp.whatsapp()
else:
    telegram.telegram()
