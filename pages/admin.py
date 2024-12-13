import streamlit as st
from utils.admin_functions import (add_functions, view_db, view_company_data,
                                   view_completed_shipments_stats, delete_functions,
                                   backup_database, view_logs)

def admin_page():
    st.empty()

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    if "selected_function_admin" not in st.session_state:
        st.session_state.selected_function_admin = "Просмотр базы данных"

    current_user = str(st.session_state.get("current_username"))
    with st.sidebar:
        st.header("Профиль администратора")
        st.write(current_user)
        st.header("Меню")
        selected_function_admin = st.radio(
            "Выберите действие:",
            ("Просмотр базы данных", "Просмотр данных компаний", "Просмотр статистики", "Просмотр логов", "Добавление данных",  "Удаление данных", "Архивирование данных"),
            index=("Просмотр базы данных", "Просмотр данных компаний", "Просмотр статистики", "Просмотр логов", "Добавление данных",  "Удаление данных", "Архивирование данных").index(st.session_state.selected_function_admin),
        )
        st.session_state.selected_function_admin = selected_function_admin
        if st.button("Выйти"):
            st.success("Нажмите на кнопку еще раз.")
            st.session_state.page = "login"

    if st.session_state.selected_function_admin == "Просмотр базы данных":
        view_db()
    elif st.session_state.selected_function_admin == "Просмотр данных компаний":
        view_company_data()
    elif st.session_state.selected_function_admin == "Просмотр статистики":
        view_completed_shipments_stats()
    elif st.session_state.selected_function_admin == "Просмотр логов":
        view_logs()
    elif st.session_state.selected_function_admin == "Добавление данных":
        add_functions()
    elif st.session_state.selected_function_admin == "Удаление данных":
        delete_functions()
    elif st.session_state.selected_function_admin == "Архивирование данных":
        backup_database()
