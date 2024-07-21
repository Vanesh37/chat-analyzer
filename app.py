import streamlit as st
import whatsapp
import telegram


st.sidebar.title("Chat Analyser")

app_list = ['WhatsApp', 'Telegram']
selected_app = st.sidebar.selectbox("Select app", app_list)

if selected_app == 'WhatsApp':
    whatsapp.whatsapp()
else:
    telegram.telegram()
