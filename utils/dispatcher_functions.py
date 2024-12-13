import streamlit as st
import pandas as pd
from utils.db import get_db_connection
from utils.auth import get_user_id

def get_orders_in_progress():
    """Отображает таблицу заказов компании за последние три месяца"""
    st.header("Заказы в пути")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT 
                    o.order_id,
                    o.order_name,
                    c.company_name,
                    o.created_time,
                    o.updated_time,
                    r.start_point,
                    r.end_point,
                    v.number_plate
                FROM orders o
                JOIN order_details od ON o.order_id = od.order_id
                JOIN routes r ON od.route_id = r.route_id
                JOIN vehicles v ON v.vehicle_id = od.vehicle_id
                JOIN company_orders co ON o.order_id = co.order_id
                JOIN companies c ON co.company_id = c.company_id
                WHERE o.status = 'В пути'
                ORDER BY o.updated_time
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if not results:
                    st.warning("Заказы в пути отсутствуют.")
                    return

                columns = ["ID заказа", "Название", "Компания" ,"Создано", "Отправлено", "Откуда", "Куда", "Транспорт"]
                rows = [list(row.values()) for row in results]
                df = pd.DataFrame(rows, columns=columns)

                df["Создано"] = pd.to_datetime(df["Создано"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                df["Отправлено"] = pd.to_datetime(df["Отправлено"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                html_table = df.to_html(index=False, escape=False)
                st.markdown(html_table, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ошибка при получении заказов: {e}")


def get_orders_new():
    """Отображает таблицу неназначенных заказов и позволяет назначать транспортные средства"""
    st.header("Неназначенные заказы")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        o.order_id,
                        o.order_name,
                        c.company_name,
                        o.created_time,
                        r.start_point,
                        r.end_point,
                        od.weight
                    FROM orders o
                    JOIN order_details od ON o.order_id = od.order_id
                    JOIN routes r ON od.route_id = r.route_id
                    JOIN company_orders co ON o.order_id = co.order_id
                    JOIN companies c ON co.company_id = c.company_id
                    WHERE o.status = 'Новый'
                    ORDER BY o.updated_time DESC
                    """
                cursor.execute(query)
                results = cursor.fetchall()

                if not results:
                    st.warning("Неназначенные заказы отсутствуют.")
                    return

                columns = ["ID заказа", "Название", "Компания", "Создано", "Откуда", "Куда", "Вес(кг)"]
                rows = [list(row.values()) for row in results]
                df = pd.DataFrame(rows, columns=columns)

                df["Создано"] = pd.to_datetime(df["Создано"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                html_table = df.to_html(index=False, escape=False)
                st.markdown(html_table, unsafe_allow_html=True)

                query_orders = """
                SELECT 
                    o.order_id,
                    o.order_name
                FROM orders o
                WHERE o.status = 'Новый'
                ORDER BY o.created_time
                """
                cursor.execute(query_orders)
                orders = cursor.fetchall()

                query_vehicles = """
                SELECT 
                    vehicle_id, 
                    type || ' - ' || capacity AS vehicle_info 
                FROM vehicles 
                WHERE status = 'Доступен'
                """
                cursor.execute(query_vehicles)
                vehicles = cursor.fetchall()

                if not vehicles:
                    st.warning("Нет доступных транспортных средств.")
                    return

                order = st.selectbox(
                    "Выберите заказ",
                    options=orders,
                    format_func=lambda x: f"Заказ {x['order_name']} (ID: {x['order_id']})"
                )
                order_id = order['order_id']

                vehicle = st.selectbox(
                    "Выберите транспортное средство",
                    options=vehicles,
                    format_func=lambda x: x['vehicle_info']
                )
                vehicle_id = vehicle['vehicle_id']

                if st.button("Назначить"):
                    try:
                        assign_query = """
                        UPDATE order_details 
                        SET vehicle_id = %s 
                        WHERE order_id = %s;

                        UPDATE vehicles 
                        SET status = 'Не доступен' 
                        WHERE vehicle_id = %s;

                        UPDATE orders 
                        SET status = 'В пути' 
                        WHERE order_id = %s;
                        """
                        username = st.session_state.get("current_username")
                        user_id = get_user_id(username)
                        cursor.execute(f"SET session.user_id = {user_id};")

                        cursor.execute(assign_query, (vehicle_id, order_id, vehicle_id, order_id))
                        conn.commit()
                        st.success(f"Заказ {order_id} успешно назначен на транспортное средство {vehicle_id}. Нажмите кнопку еще раз.")

                        st.session_state.selected_function_dispatcher = "Заказы в пути"

                    except Exception as e:
                        conn.rollback()
                        st.error(f"Ошибка назначения: {e}")

    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")


def complete_order():
    """Завершаем заказ и обновляем статус транспортного средства"""
    st.header("Завершение заказов")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query_in_progress_orders = """
                SELECT 
                    o.order_id,
                    o.order_name,
                    od.weight,
                    od.vehicle_id
                FROM orders o
                JOIN order_details od ON o.order_id = od.order_id
                WHERE o.status = 'В пути'
                ORDER BY o.created_time
                """
                cursor.execute(query_in_progress_orders)
                orders = cursor.fetchall()

                if not orders:
                    st.warning("Нет заказов в процессе выполнения.")
                    return

                selected_order = st.selectbox(
                    "Выберите заказ для завершения",
                    options=orders,
                    format_func=lambda x: f"ID: {x['order_id']}, Название: {x['order_name']}, Транспорт: {x['vehicle_id']}"
                )
                order_id = selected_order['order_id']
                vehicle_id = selected_order['vehicle_id']

                if st.button("Завершить заказ"):
                    try:
                        complete_query = """
                        UPDATE orders 
                        SET status = 'Доставлен' 
                        WHERE order_id = %s;

                        UPDATE vehicles 
                        SET status = 'Доступен' 
                        WHERE vehicle_id = %s;
                        """
                        username = st.session_state.get("current_username")
                        user_id = get_user_id(username)
                        cursor.execute(f"SET session.user_id = {user_id};")
                        cursor.execute(complete_query, (order_id, vehicle_id))
                        conn.commit()
                        st.success(f"Заказ {order_id} успешно завершён, транспортное средство {vehicle_id} теперь доступно. Нажмите кнопку еще раз.")
                        st.session_state.selected_function_dispatcher = "Заказы в пути"
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Ошибка завершения заказа: {e}")

    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")


def cancel_order():
    """Отмена заказов и удаление всех связанных данных"""
    st.header("Отмена заказов")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query_active_orders = """
                SELECT 
                    o.order_id,
                    o.order_name,
                    od.vehicle_id,
                    r.route_id,
                    c.company_name
                FROM orders o
                LEFT JOIN order_details od ON o.order_id = od.order_id
                LEFT JOIN routes r ON od.route_id = r.route_id
                LEFT JOIN company_orders co ON o.order_id = co.order_id
                LEFT JOIN companies c ON co.company_id = c.company_id
                WHERE o.status IN ('Новый', 'В пути')
                ORDER BY o.created_time
                """
                cursor.execute(query_active_orders)
                orders = cursor.fetchall()

                if not orders:
                    st.warning("Нет заказов для отмены.")
                    return

                selected_order = st.selectbox(
                    "Выберите заказ для отмены",
                    options=orders,
                    format_func=lambda x: f"ID: {x['order_id']}, Название: {x['order_name']}, Компания: {x['company_name']}"
                )
                order_id = selected_order['order_id']
                vehicle_id = selected_order['vehicle_id']
                route_id = selected_order['route_id']

                if st.button("Отменить заказ"):
                    try:
                        cancel_query = """
                        DELETE FROM order_details 
                        WHERE order_id = %s;

                        UPDATE vehicles 
                        SET status = 'Доступен' 
                        WHERE vehicle_id = %s;

                        DELETE FROM routes 
                        WHERE route_id = %s;

                        DELETE FROM company_orders 
                        WHERE order_id = %s;

                        DELETE FROM orders 
                        WHERE order_id = %s;
                        """
                        username = st.session_state.get("current_username")
                        user_id = get_user_id(username)
                        cursor.execute(f"SET session.user_id = {user_id};")
                        cursor.execute(cancel_query, (order_id, vehicle_id, route_id, order_id, order_id))
                        conn.commit()
                        st.success(f"Заказ {order_id} успешно отменён, все связанные данные удалены. Нажмите кнопку еще раз.")
                        st.session_state.selected_function_dispatcher = "Заказы в пути"
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Ошибка отмены заказа: {e}")

    except Exception as e:
        st.error(f"Ошибка при получении данных: {e}")
