from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
import secrets
import os

class PasswordCrypto:
    def __init__(self, work_key):
        self.cipher_suite_storage = Fernet(work_key)

    def encrypt_password_storage(self, password_plaintext):
        if isinstance(password_plaintext, str):
            password_plaintext = password_plaintext.encode('utf-8') 
        encrypted_bytes = self.cipher_suite_storage.encrypt(password_plaintext)
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

    def decrypt_password_storage(self, password_encrypted_base64):
        try:
            encrypted_bytes = base64.urlsafe_b64decode(password_encrypted_base64.encode('utf-8'))
            decrypted_bytes = self.cipher_suite_storage.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return None

    @staticmethod
    def generate_salt():
        return secrets.token_hex(16)

    @staticmethod
    def hash_password_sha256(password_plaintext, salt=None):
        if salt is None:
            salt = ''
        if isinstance(password_plaintext, str):
            password_plaintext = password_plaintext.encode('utf-8')
        if isinstance(salt, str):
            salt = salt.encode('utf-8')
        pwd_salt = password_plaintext + salt
        hash_obj = hashlib.sha256(pwd_salt)
        return hash_obj.hexdigest()

    @staticmethod
    def derive_transmission_key(random_num, password_hash_hex):
        if isinstance(random_num, int):
            random_num_bytes = random_num.to_bytes((random_num.bit_length() + 7) // 8, byteorder='big')
        elif isinstance(random_num, str):
            random_num_bytes = random_num.encode('utf-8')
        else:
            random_num_bytes = random_num

        if isinstance(password_hash_hex, str):
            password_hash_bytes = bytes.fromhex(password_hash_hex)
        else:
            password_hash_bytes = password_hash_hex

        spliced_material = random_num_bytes + password_hash_bytes
        salt = b'transmission_key_derivation_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=10000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(spliced_material))
        return key