import streamlit as st
from pages.login import login_page
from pages.registration import registration_page
from pages.client import client_page
from pages.dispatcher import dispatcher_page
from pages.admin import admin_page

def main():
    st.set_page_config(page_title="Авторизация", layout="wide", initial_sidebar_state="collapsed")

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "registration":
        registration_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "client":
        client_page()
    elif st.session_state.page == "dispatcher":
        dispatcher_page()
    elif st.session_state.page == "admin":
        admin_page()

if __name__ == "__main__":
    main()