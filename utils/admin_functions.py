import streamlit as st
import pandas as pd
import os
import subprocess
import plotly.graph_objects as go
from utils.db import get_db_connection, DB_CONFIG
from utils.auth import register_user, is_user_exists, get_user_id
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time

def add_user(username, password, confirm_password, company, role):
    """Функция для добавления нового пользователя"""
    if not username or not password or not confirm_password or (not company and role == 'client'):
        st.error("Все поля обязательны для заполнения!")
        return
    if password != confirm_password:
        st.error("Пароли не совпадают!")
        return
    if is_user_exists(username):
        st.error("Пользователь с таким именем уже существует!")
        return

    if register_user(username, password, company, role):
        st.success("Пользователь успешно зарегистрирован!")
        st.session_state.selected_function_admin = "Просмотр базы данных"
    else:
        st.error("Ошибка регистрации. Попробуйте позже.")


def is_vehicle_exists(number_plate):
    """Проверка существования автомобиля по номерному знаку"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT number_plate FROM vehicles WHERE number_plate = %s"
                cursor.execute(query, (number_plate,))
                vehicle = cursor.fetchone()
        return vehicle is not None
    except Exception as e:
        st.error(f"Ошибка проверки автомобиля: {e}")
        return False


def add_vehicle(number_plate, vehicle_type, capacity, status):
    """Функция для добавления нового автомобиля"""
    if not number_plate or not vehicle_type or not capacity or not status:
        st.error("Все поля обязательны для заполнения!")
        return
    if is_vehicle_exists(number_plate):
        st.error("Автомобиль с таким номером уже существует!")
        return
    username = st.session_state.get("current_username")
    user_id = get_user_id(username)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SET session.user_id = {user_id};")
                query = """
                    INSERT INTO vehicles (number_plate, type, capacity, status) 
                    VALUES (%s, %s, %s, %s)
                    """
                cursor.execute(query, (number_plate, vehicle_type, capacity, status))
                conn.commit()
        st.success("Автомобиль успешно добавлен!")
        st.session_state.selected_function_admin = "Просмотр базы данных"
    except Exception as e:
        st.error(f"Ошибка добавления автомобиля: {e}")


def add_users_from_csv(file):
    """Функция для добавления пользователей из CSV-файла"""
    try:
        df = pd.read_csv(file, sep=";")

        if 'Компания' not in df.columns or 'Имя' not in df.columns or 'Пароль' not in df.columns:
            st.error("Файл должен содержать столбцы 'Компания', 'Имя', 'Пароль'")
            return

        for _, row in df.iterrows():
            username = row['Имя']
            password = row['Пароль']
            confirm_password = row['Пароль']
            company = row['Компания']
            role = 'client'

            add_user(username, str(password), str(confirm_password), company, role)

        st.success("Добавление окончено! Нажмите на кнопку еще раз.")
        st.session_state.selected_function_admin = "Просмотр базы данных"

    except Exception as e:
        st.error(f"Ошибка при добавлении пользователей: {e}")

def add_vehicles_from_csv(file):
    """Функция для добавления пользователей из CSV-файла"""
    try:
        df = pd.read_csv(file, sep=";")

        if 'Тип' not in df.columns or 'Номерной знак' not in df.columns or 'Вместительность(кг)' not in df.columns:
            st.error("Файл должен содержать столбцы 'Компания', 'Имя', 'Пароль'")
            return

        for _, row in df.iterrows():
            number_plate = row['Номерной знак']
            type = row['Тип']
            capacity = row['Вместительность(кг)']
            status = 'Доступен'

            add_vehicle(number_plate, type, capacity, status)

        st.success("Добавление окончено! Нажмите на кнопку еще раз.")
        st.session_state.selected_function_admin = "Просмотр базы данных"

    except Exception as e:
        st.error(f"Ошибка при добавлении пользователей: {e}")

def add_functions():
    """Интерфейс для добавления пользователей и автомобилей"""
    st.header("Добавление компонентов")

    option = st.selectbox("Выбор добавления", ["Пользователя", "Автомобиль", "Несколько пользователей", "Несколько автомобилей"])

    if option == "Пользователя":
        st.subheader("Добавление пользователя")
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        company = st.text_input("Компания")
        role = st.selectbox("Роль", ["client", "dispatcher", "admin"])

        if st.button("Добавить пользователя"):
            add_user(username, password, confirm_password, company, role)

    elif option == "Автомобиль":
        st.subheader("Добавление автомобиля")
        number_plate = st.text_input("Номерной знак")
        vehicle_type = st.selectbox("Тип", ['Фура', 'Фургон', 'Пикап'])
        capacity = st.number_input("Грузоподъемность(кг)", min_value=0, step=500)
        status = st.selectbox("Статус", ['Доступен', 'Не доступен'])

        if st.button("Добавить автомобиль"):
            add_vehicle(number_plate, vehicle_type, capacity, status)

    elif option == "Несколько пользователей":
        uploaded_file = st.file_uploader("Загрузите файл CSV", type=["csv"])
        if uploaded_file is not None:
            if st.button("Добавить пользователей"):
                add_users_from_csv(uploaded_file)

    elif option == "Несколько автомобилей":
        uploaded_file = st.file_uploader("Загрузите файл CSV", type=["csv"])
        if uploaded_file is not None:
            if st.button("Добавить автомобили"):
                add_vehicles_from_csv(uploaded_file)


def view_table(table_name):
    """Функция для просмотра таблицы из базы данных"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns=columns)
        df.reset_index(drop=True, inplace=True)
        df.index += 1
        st.dataframe(df)
    except Exception as e:
        st.error(f"Ошибка при получении данных из таблицы {table_name}: {e}")


def view_db():
    """Интерфейс для просмотра данных из базы"""
    st.subheader("Просмотр таблиц")
    table_name = st.selectbox("Выберите таблицу",
                              ["users", "companies", "orders", "order_details", "vehicles", "routes",
                               "company_users", "company_orders"])

    if st.button("Показать данные"):
        view_table(table_name)


def view_company_data():
    """Просмотр данных компании"""
    st.header("Просмотр данных компании")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = "SELECT company_name FROM companies"
            cursor.execute(query)
            companies = [row["company_name"] for row in cursor.fetchall()]

    company_name = st.selectbox("Выберите компанию:", companies)
    data_type = st.selectbox("Что хотите увидеть?", ["Заказы компании", "Пользователи компании"])

    if st.button("Показать данные"):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if data_type == "Заказы компании":
                    query = """
                        SELECT o.order_name, o.status, o.created_time, o.updated_time 
                        FROM orders o 
                        JOIN company_orders co ON o.order_id = co.order_id 
                        JOIN companies c ON co.company_id = c.company_id 
                        WHERE c.company_name = %s
                    """
                    cursor.execute(query, (company_name,))
                    orders = cursor.fetchall()
                    if orders:
                        columns = ["Order Name", "Status", "Created Time", "Updated Time"]
                        rows = [list(row.values()) for row in orders]
                        df = pd.DataFrame(rows, columns=columns)
                        df.reset_index(drop=True, inplace=True)
                        df.index += 1
                        st.write(df)
                    else:
                        st.warning("У выбранной компании нет заказов.")
                elif data_type == "Пользователи компании":
                    query = """
                        SELECT u.username, u.role, u.created_time 
                        FROM users u
                        JOIN company_users cu ON u.user_id = cu.user_id
                        JOIN companies c ON cu.company_id = c.company_id
                        WHERE c.company_name = %s
                    """
                    cursor.execute(query, (company_name,))
                    users = cursor.fetchall()
                    if users:
                        columns = ["Username", "Role", "Created Time"]
                        rows = [list(row.values()) for row in users]
                        df = pd.DataFrame(rows, columns=columns)
                        df.reset_index(drop=True, inplace=True)
                        df.index += 1
                        st.write(df)
                    else:
                        st.warning("У выбранной компании нет пользователей.")

def view_completed_shipments_stats():
    """Статистика завершённых перевозок по месяцам"""
    st.header("Статистика завершённых перевозок по месяцам")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT
                    TO_CHAR(o.created_time, 'YYYY-MM') AS month,
                    COUNT(o.order_id) AS completed_shipments
                FROM orders o
                WHERE o.status = 'Доставлен'
                GROUP BY TO_CHAR(o.created_time, 'YYYY-MM')
                ORDER BY month DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()

    if not results:
        st.warning("Нет завершённых перевозок за последние месяцы.")
        return

    columns = ["Месяц", "Количество завершённых перевозок"]
    rows = [list(row.values()) for row in results]
    df = pd.DataFrame(rows, columns=columns)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Месяц"],
        y=df["Количество завершённых перевозок"],
        mode='lines+markers',
        name='Завершённые перевозки',
        line=dict(color='blue'),
        marker=dict(size=8, color='red')
    ))

    fig.update_layout(
        title="Статистика завершённых перевозок по месяцам",
        xaxis_title="Месяц",
        yaxis_title="Количество завершённых перевозок",
        xaxis=dict(tickmode='array', tickvals=df["Месяц"], ticktext=df["Месяц"]),
        autosize=True,
        showlegend=True,
        template="plotly_dark",
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

def delete_component(component_type, identifier):
    """Функция для удаления компонента (пользователь, компания, транспорт)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                username = st.session_state.get("current_username")
                user_id = get_user_id(username)
                if component_type == "Пользователь":
                    cursor.execute(f"SET session.user_id = {user_id};")
                    query = "DELETE FROM users WHERE username = %s"
                    cursor.execute(query, (identifier,))
                elif component_type == "Компания":
                    query = """
                        DELETE FROM users
                        WHERE user_id IN (
                            SELECT user_id 
                            FROM company_users 
                            JOIN companies ON companies.company_id = company_users.company_id
                            WHERE companies.company_name = %s
                        );
                        DELETE FROM companies
                        WHERE company_name = %s;
                    """
                    cursor.execute(f"SET session.user_id = {user_id};")
                    cursor.execute(query, (identifier, identifier))
                elif component_type == "Транспорт":
                    cursor.execute(f"SET session.user_id = {user_id};")
                    query = "DELETE FROM vehicles WHERE number_plate = %s"
                    cursor.execute(query, (identifier,))
                else:
                    st.error("Неверный тип компонента!")
                    return
                conn.commit()
        st.success(f"{component_type} успешно удален.")
    except Exception as e:
        st.error(f"Ошибка при удалении: {str(e)}")


def get_selectbox_data(component_type):
    """Функция для работы с удалением"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if component_type == "Пользователь":
                    query = "SELECT username FROM users WHERE role not in ('admin')"
                elif component_type == "Компания":
                    query = "SELECT company_name FROM companies"
                elif component_type == "Транспорт":
                    query = "SELECT number_plate FROM vehicles"
                else:
                    return []

                cursor.execute(query)
                results = cursor.fetchall()
                return [row[list(row.keys())[0]] for row in results]
    except Exception as e:
        st.error(f"Ошибка при получении данных: {str(e)}")
        return []


def delete_functions():
    """Функция для удаления компонентов"""
    st.header("Удаление данных")

    component_type = st.selectbox("Выберите тип компонента для удаления:", [
        "Пользователь",
        "Компания",
        "Транспорт"
    ])

    selectbox_data = get_selectbox_data(component_type)

    identifier = st.selectbox(f"Выберите {component_type.lower()} для удаления:", selectbox_data)

    if st.button("Удалить"):
        if identifier:
            delete_component(component_type, identifier)
        else:
            st.error("Пожалуйста, выберите элемент для удаления.")


def backup_database():
    """Функция для архивирования БД"""
    try:
        if st.button("Архивировать базу данных"):
            time.sleep(15)
            backup_file = "backup.sql"
            os.environ["PGPASSWORD"] = DB_CONFIG["password"]
            command = [
                r'C:\Program Files\PostgreSQL\17\bin\pg_dump',
                '-U', DB_CONFIG["user"],
                '-h', DB_CONFIG["host"],
                '-p', str(DB_CONFIG["port"]),
                '-b',
                '--encoding', 'UTF8',
                '-f', backup_file,
                DB_CONFIG["dbname"],
            ]

            with st.spinner('Создание резервной копии базы данных...'):
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode == 0:
                    st.success(f"Резервная копия базы данных создана успешно. Файл: {backup_file}")

                    with open(backup_file, "rb") as file:
                        st.download_button(
                            label="Скачать резервную копию",
                            data=file,
                            file_name=backup_file,
                            mime="application/octet-stream"
                        )
                else:
                    st.error(f"Ошибка при создании резервной копии: {result.stderr}")
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def get_logs_by_date(selected_date):
    """Функция для получения логов"""
    query = """
        SELECT log_id, user_id, action, time
        FROM logs
        WHERE DATE(time) = %s
        ORDER BY time;
    """

    formatted_date = selected_date.strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (formatted_date,))
            logs = pd.DataFrame(cursor.fetchall(), columns=['log_id', 'user_id', 'action', 'time'])

    return logs

def view_logs():
    """Функция для отображения логов"""
    st.header("Просмотр логов по дням")

    selected_date = st.date_input("Выберите дату", datetime.today())

    logs = get_logs_by_date(selected_date)

    if not logs.empty:
        st.write(f"Логи за {selected_date.strftime('%Y-%m-%d')}:")
        st.dataframe(logs.set_index('log_id'))
    else:
        st.write(f"Нет логов для {selected_date.strftime('%Y-%m-%d')}.")