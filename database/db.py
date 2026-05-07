import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_PATH, STATUS_PENDING, PAYMENT_UNPAID
from utils.logger import logger

def get_db_connection():
    """Returns a database connection based on the environment."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Use PostgreSQL (Render/Supabase)
        try:
            # Supabase and Render often require SSL
            if "sslmode" not in database_url:
                if "?" in database_url:
                    database_url += "&sslmode=require"
                else:
                    database_url += "?sslmode=require"
            
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            # Try without sslmode just in case
            try:
                conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
                return conn
            except:
                raise e
    else:
        # Use SQLite (Local)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise e

def init_db():
    """Initializes the database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tables for SQLite vs PostgreSQL (syntax slightly different)
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                service_type TEXT,
                title TEXT,
                description TEXT,
                budget TEXT,
                deadline TEXT,
                contact TEXT,
                status TEXT,
                payment_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_type TEXT,
                title TEXT,
                description TEXT,
                budget TEXT,
                deadline TEXT,
                contact TEXT,
                status TEXT,
                payment_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def add_user(user_id, username, first_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET username = EXCLUDED.username, first_name = EXCLUDED.first_name
        ''', (user_id, username, first_name))
    else:
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
    conn.commit()
    conn.close()

def create_order(user_id, service_type, title, description, budget, deadline, contact):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        cursor.execute('''
            INSERT INTO orders (user_id, service_type, title, description, budget, deadline, contact, status, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id
        ''', (user_id, service_type, title, description, budget, deadline, contact, STATUS_PENDING, PAYMENT_UNPAID))
        order_id = cursor.fetchone()['order_id']
    else:
        cursor.execute('''
            INSERT INTO orders (user_id, service_type, title, description, budget, deadline, contact, status, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, service_type, title, description, budget, deadline, contact, STATUS_PENDING, PAYMENT_UNPAID))
        order_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return order_id

def get_user_orders(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    query = "SELECT * FROM orders WHERE user_id = " + ("%s" if is_postgres else "?") + " ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_all_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_order_by_id(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    query = "SELECT * FROM orders WHERE order_id = " + ("%s" if is_postgres else "?")
    cursor.execute(query, (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_order_status(order_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    query = "UPDATE orders SET status = " + ("%s" if is_postgres else "?") + " WHERE order_id = " + ("%s" if is_postgres else "?")
    cursor.execute(query, (status, order_id))
    conn.commit()
    conn.close()

def update_payment_status(order_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    query = "UPDATE orders SET payment_status = " + ("%s" if is_postgres else "?") + " WHERE order_id = " + ("%s" if is_postgres else "?")
    cursor.execute(query, (status, order_id))
    conn.commit()
    conn.close()

def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use a helper to extract count from row
    def get_count(cursor, query):
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            return 0
        if isinstance(row, dict):
            return row.get('count', 0)
        return row[0]

    total_users = get_count(cursor, "SELECT COUNT(*) as count FROM users")
    total_orders = get_count(cursor, "SELECT COUNT(*) as count FROM orders")
    completed_orders = get_count(cursor, "SELECT COUNT(*) as count FROM orders WHERE status = 'Completed'")
    
    conn.close()
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "completed_orders": completed_orders
    }

def get_all_user_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    ids = [row['user_id'] if isinstance(row, dict) else row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def add_support_message(user_id, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    is_postgres = os.getenv("DATABASE_URL") is not None
    
    if is_postgres:
        cursor.execute("INSERT INTO support_messages (user_id, message) VALUES (%s, %s)", (user_id, message))
    else:
        cursor.execute("INSERT INTO support_messages (user_id, message) VALUES (?, ?)", (user_id, message))
        
    conn.commit()
    conn.close()
