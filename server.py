import socket
import threading
import json
import sqlite3
import hashlib
import secrets 
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from database import init_db, get_user

HOST = 'localhost'
PORT = 12345

def hash_password_sha256(password, salt):
    """Hash password with SHA-256 and salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def derive_transmission_key(random_num, password_hash):
    """Derive transmission key from random number and password hash."""
    salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive((str(random_num) + password_hash).encode())
    return base64.urlsafe_b64encode(key)

def start_server():
    init_db()  
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
                
            request = json.loads(data)
            
            if 'username_for_salt' in request:
                username = request['username_for_salt']
                
                user_data = get_user(username)
                if user_data:
                    _, password_hash, salt = user_data
                    random_num = secrets.randbelow(1000000) 
                    
                    response = {
                        "action": "send_random_and_salt",
                        "random_num": random_num,
                        "salt": salt
                    }
                else:
                   
                    random_num = secrets.randbelow(1000000)
                    dummy_salt = secrets.token_hex(16)
                    
                    response = {
                        "action": "send_random_and_salt",
                        "random_num": random_num,
                        "salt": dummy_salt
                    }
                
                client_socket.send(json.dumps(response).encode())
                
            elif 'action' in request and request['action'] == 'login_request':
                encrypted_password_b64 = request['encrypted_password']
               
                response = {"status": "success", "message": "Login successful"}
                client_socket.send(json.dumps(response).encode())
                break
                
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_server()