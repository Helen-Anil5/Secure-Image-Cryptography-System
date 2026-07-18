import sqlite3
import os

def init_db():
  
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            encrypted_password BLOB NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, encrypted_password, password_hash, salt):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, encrypted_password, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username, encrypted_password, password_hash, salt)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
    
    return success

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT encrypted_password, password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    return result