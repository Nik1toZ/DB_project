import streamlit as st
import pandas as pd
from utils.db import get_db_connection
from utils.auth import get_user_id

def get_company(username):
    """Получить имя компании пользователя"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT c.company_name
                    FROM companies c
                    JOIN company_users cu ON c.company_id = cu.company_id
                    JOIN users u ON cu.user_id = u.user_id
                    WHERE u.username = %s
                    """
                cursor.execute(query, (username,))
                company = cursor.fetchone()

                if company is None:
                    raise ValueError(f"No company found for username '{username}'.")

                return company["company_name"]

    except Exception as e:
        st.error(f"Ошибка получения компании: {e}")
        return False

def get_company_id(username):
    """Получить ID компании по имени пользователя"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT c.company_id
                FROM companies c
                JOIN company_users cu ON c.company_id = cu.company_id
                JOIN users u ON cu.user_id = u.user_id
                WHERE u.username = %s
                """
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                if result:
                    return result["company_id"]
                return None
    except Exception as e:
        st.error(f"Ошибка получения компании: {e}")
        return None

def create_order():
    """Создание нового заказа"""
    st.header("Создание заказа")

    order_name = st.text_input("Название товара")
    start_point = st.text_input("Откуда")
    end_point = st.text_input("Куда")
    weight = st.text_input("Вес(кг)")

    if st.button("Создать заказ"):
        if not (order_name and start_point and end_point and weight):
            st.warning("Заполните все поля перед созданием заказа.")
            return

        try:
            username = st.session_state.get("current_username")
            user_id = get_user_id(username)

            if not username:
                st.error("Не удалось определить текущего пользователя.")
                return

            company_id = get_company_id(username)
            if not company_id:
                st.error("Не удалось найти компанию для пользователя.")
                return

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    conn.autocommit = False

                    order_query = """
                    INSERT INTO orders (order_name, status) 
                    VALUES (%s, 'Новый') 
                    RETURNING order_id
                    """
                    cursor.execute(f"SET session.user_id = {user_id};")
                    cursor.execute(order_query, (order_name,))
                    order_id = cursor.fetchone()["order_id"]

                    company_order_query = """
                    INSERT INTO company_orders (company_id, order_id) 
                    VALUES (%s, %s)
                    """
                    cursor.execute(company_order_query, (company_id, order_id))

                    route_query = """
                    INSERT INTO routes (start_point, end_point) 
                    VALUES (%s, %s) 
                    RETURNING route_id
                    """
                    cursor.execute(route_query, (start_point, end_point))
                    route_id = cursor.fetchone()["route_id"]

                    order_details_query = """
                    INSERT INTO order_details (order_id, vehicle_id, route_id, weight) 
                    VALUES (%s, NULL, %s, %s)
                    """
                    cursor.execute(order_details_query, (order_id, route_id, weight))

                    conn.commit()
                    st.success(f"Заказ «{order_name}» успешно создан! Нажмите на кнопку еще раз.")

                    st.session_state.selected_function_client = "Заказы"

        except Exception as e:
            st.error(f"Ошибка создания заказа: {e}")

def get_orders():
    """Отображает таблицу заказов компании за последние три месяца"""
    st.header("Заказы за последние три месяца")

    username = st.session_state.get("current_username")
    if not username:
        st.error("Не удалось определить текущего пользователя.")
        return

    company_id = get_company_id(username)
    if not company_id:
        st.error("Не удалось найти компанию для пользователя.")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT 
                    o.order_id,
                    o.order_name,
                    r.start_point,
                    r.end_point,
                    od.weight,
                    o.status,
                    o.created_time,
                    o.updated_time
                FROM orders o
                JOIN company_orders co ON o.order_id = co.order_id
                JOIN order_details od ON o.order_id = od.order_id
                JOIN routes r ON od.route_id = r.route_id
                WHERE co.company_id = %s
                  AND o.created_time >= NOW() - INTERVAL '3 months'
                ORDER BY o.created_time
                """
                cursor.execute(query, (company_id,))
                results = cursor.fetchall()

                if not results:
                    st.warning("За последние три месяца заказы отсутствуют.")
                    return

                columns = ["ID заказа", "Название", "Откуда", "Куда", "Вес (кг)", "Статус", "Создано", "Обновлено"]
                rows = [list(row.values()) for row in results]
                df = pd.DataFrame(rows, columns=columns)

                df["Создано"] = pd.to_datetime(df["Создано"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                df["Обновлено"] = pd.to_datetime(df["Обновлено"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                html_table = df.to_html(index=False, escape=False)
                st.markdown(html_table, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ошибка при получении заказов: {e}")