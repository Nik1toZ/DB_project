import streamlit as st
from utils.client_functions import get_company, create_order, get_orders

def client_page():
    st.empty()

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    username = str(st.session_state.get("current_username"))
    company = str(get_company(username))

    st.title(company)

    # Используем состояние для переключения вкладок
    if "selected_function_client" not in st.session_state:
        st.session_state.selected_function_client = "Заказы"

    with st.sidebar:
        st.header("Профиль")
        st.write(username)
        st.header("Меню")
        selected_function_client = st.radio(
            "Выберите действие:",
            ("Заказы", "Создать заказ"),
            index=("Заказы", "Создать заказ").index(st.session_state.selected_function_client),
        )
        st.session_state.selected_function_client = selected_function_client

        if st.button("Выйти"):
            st.success("Нажмите на кнопку еще раз.")
            st.session_state.page = "login"

    # Отображаем выбранную вкладку
    if st.session_state.selected_function_client == "Заказы":
        get_orders()
    elif st.session_state.selected_function_client == "Создать заказ":
        create_order()
