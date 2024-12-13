import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

DB_CONFIG = {
    "dbname": "TC_project",
    "user": "postgres",
    "password": "12345",
    "host": "localhost",
    "port": 5432,
}

def get_db_connection():
    """Функция для конекта с БД"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        st.error(f"Ошибка подключения к базе данных! {e}")
        st.stop()
