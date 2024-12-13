import bcrypt
from utils.db import get_db_connection

def get_user_id(username):
    """Функция для получения ид пользователя"""
    query = "SELECT user_id FROM users WHERE username = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                if result:
                    return result['user_id']
                return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def hash_password(password):
    """Функция для хеширования пароля"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(hashed_password, password):
    """Функция для проверки пароля"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def check_credentials(username, password):
    """Функция для доступа к аккаунту"""
    query = "SELECT user_id, hashed_password FROM users WHERE username = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                if user and check_password(user["hashed_password"], password):
                    return True
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def check_role(username):
    """Функция для проверки роли"""
    query = "SELECT role FROM users WHERE username = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                role = cursor.fetchone()
                if role:
                    return role['role']
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def register_user(username, password, company, role):
    """Функция для регистрации нового пользователя"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                hashed_password = hash_password(password)
                query = "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s) RETURNING user_id"
                cursor.execute(query, (username, hashed_password, role),)
                user_id = cursor.fetchone()["user_id"]

                if role == "client":
                    query = "SELECT company_id FROM companies WHERE company_name = %s"
                    cursor.execute(query, (company,))
                    company_row = cursor.fetchone()

                    if company_row:
                        company_id = company_row["company_id"]
                    else:
                        query = "INSERT INTO companies (company_name) VALUES (%s) RETURNING company_id"
                        cursor.execute(query, (company,))
                        company_id = cursor.fetchone()["company_id"]
                    query = "INSERT INTO company_users (user_id, company_id) VALUES (%s, %s)"
                    cursor.execute(query, (user_id, company_id))

                conn.commit()
                return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def is_user_exists(username):
    """Функция для проверки уникальности имени"""
    query = "SELECT * FROM users WHERE username = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                return user is not None
    except Exception as e:
        print(f"Ошибка: {e}")
        return False