import streamlit as st
from utils.auth import register_user, is_user_exists

def registration_page():
    st.empty()
    st.title("Регистрация")

    no_sidebar_style = """
            <style>
                div[data-testid="stSidebarNav"] {display: none;}
            </style>
        """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    username = st.text_input("Имя")
    password = st.text_input("Пароль", type="password")
    confirm_password = st.text_input("Подтверждение пароля", type="password")
    company = st.text_input("Название компании")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Зарегистрироваться"):
            if not username or not password or not confirm_password or not company:
                st.error("Все поля обязательны для заполнения!")
            elif password != confirm_password:
                st.error("Пароли не совпадают!")
            elif is_user_exists(username):
                st.error("Пользователь с таким именем уже существует!")
            else:
                if register_user(username, password, company, "client"):
                    st.success("Регистрация успешна! Вы можете войти в систему. Нажмите на кнопку еще раз.")
                    st.session_state.page = "login"
                else:
                    st.error("Ошибка регистрации. Попробуйте позже.")
                    print(register_user(username, password, company, "client"))
    with col2:
        if st.button("Выйти"):
            st.success("Нажмите на кнопку еще раз.")
            st.session_state.page = "login"