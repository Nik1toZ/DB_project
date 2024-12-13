import streamlit as st
from utils.dispatcher_functions import get_orders_in_progress, get_orders_new, complete_order, cancel_order

def dispatcher_page():
    st.empty()

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    if "selected_function_dispatcher" not in st.session_state:
        st.session_state.selected_function_dispatcher = "Заказы в пути"

    current_user = str(st.session_state.get("current_username"))
    with st.sidebar:
        st.header("Профиль диспетчера")
        st.write(current_user)
        st.header("Меню")
        selected_function_dispatcher = st.radio(
            "Выберите действие:",
            ("Заказы в пути", "Назначить заказ", "Завершить заказ", "Отменить заказ"),
            index=("Заказы в пути", "Назначить заказ", "Завершить заказ", "Отменить заказ").index(st.session_state.selected_function_dispatcher),
        )
        st.session_state.selected_function_dispatcher = selected_function_dispatcher
        if st.button("Выйти"):
            st.success("Нажмите на кнопку еще раз.")
            st.session_state.page = "login"

    if st.session_state.selected_function_dispatcher == "Заказы в пути":
        get_orders_in_progress()
    elif st.session_state.selected_function_dispatcher == "Назначить заказ":
        get_orders_new()
    elif st.session_state.selected_function_dispatcher == "Завершить заказ":
        complete_order()
    elif st.session_state.selected_function_dispatcher == "Отменить заказ":
        cancel_order()