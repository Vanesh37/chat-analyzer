import streamlit as st
import whatsapp
import telegram


st.sidebar.title("Chat Analyser")

app_list = ['WhatsApp', 'Telegram']
selected_app = st.sidebar.selectbox("Select app", app_list)

if selected_app == 'WhatsApp':
    st.set_page_config(page_title="WhatsApp Chat Analyzer")
    whatsapp.whatsapp()
else:
    st.set_page_config(page_title="Telegram Chat Analyzer")
    telegram.telegram()
