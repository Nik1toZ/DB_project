import streamlit as st
from utils.auth import check_credentials, check_role

def login_page():
    st.title("Авторизация")

    no_sidebar_style = """
            <style>
                div[data-testid="stSidebarNav"] {display: none;}
            </style>
        """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    username = st.text_input("Имя", key="username")
    password = st.text_input("Пароль", type="password", key="password")

    st.session_state["current_username"] = username

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Войти"):
            if check_credentials(username, password):
                st.success("Вы вошли! Нажмите на кнопку еще раз.")
                if check_role(username) == "client":
                    st.session_state.page = "client"
                elif check_role(username) == "dispatcher":
                    st.session_state.page = "dispatcher"
                elif check_role(username) == "admin":
                    st.session_state.page = "admin"
            elif not username or not password:
                st.error("Введите имя и/или пароль.")
            else:
                st.error("Неверное имя и/или пароль. Попробуйте снова.")
    with col2:
        if st.button("Регистрация"):
            st.success("Нажмите на кнопку еще раз.")
            st.session_state.page = "registration"
