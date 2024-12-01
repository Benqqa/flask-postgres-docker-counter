import time
import psycopg2
from flask import Flask, request, jsonify
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from functools import wraps

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'db',
    'database': 'counter_db',
    'user': 'postgres',
    'password': 'example'
}

class DatabaseError(Exception):
    """Базовый класс для ошибок работы с БД"""
    pass

def db_connection_decorator(func):
    """Декоратор для обработки подключений к БД"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            return func(conn, *args, **kwargs)
        except psycopg2.Error as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(str(e))
        finally:
            if conn:
                conn.close()
    return wrapper

def get_db_connection():
    """Создает подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS counter (
                    id SERIAL PRIMARY KEY,
                    datetime TIMESTAMP NOT NULL,
                    client_info TEXT
                )
            ''')
        conn.commit()
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise DatabaseError(f"Could not connect to database: {e}")

def retry_on_failure(retries: int = 5, delay: float = 0.5):
    """Декоратор для повторных попыток выполнения функции"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = retries
            while attempts > 0:
                try:
                    return func(*args, **kwargs)
                except psycopg2.OperationalError as e:
                    attempts -= 1
                    if attempts == 0:
                        logger.error(f"All retry attempts failed: {e}")
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure()
@db_connection_decorator
def get_hit_count(conn) -> Optional[int]:
    """Увеличивает и возвращает количество посещений"""
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO counter (datetime, client_info) VALUES (NOW(), %s) RETURNING id',
            (request.headers.get('User-Agent'),)
        )
        count = cur.fetchone()[0]
        conn.commit()
        return count

@app.route('/')
def hello():
    """Главная страница с счетчиком посещений"""
    try:
        count = get_hit_count()
        return f'Hello World! I have been seen {count} times.'
    except DatabaseError as e:
        logger.error(f"Error in hello route: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in hello route: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/db')
@db_connection_decorator
def show_counter(conn) -> Dict[str, List[Any]]:
    """Возвращает все записи счетчика"""
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM counter')
        rows = cur.fetchall()
        return jsonify({
            'counter': [
                {
                    'id': row[0],
                    'datetime': row[1].isoformat(),
                    'client_info': row[2]
                }
                for row in rows
            ]
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)