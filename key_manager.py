import os
import logging
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

KEY_FILE = "encrypted_work_key.bin"
SALT_FILE = "master_key_salt.bin"
WORK_KEY_LENGTH = 32

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self):
        self.master_key_password = b'demo_master_password_for_dev_purpose_only'
        self.master_key_salt = self._ensure_salt()
        self.master_key = self._derive_master_key()
        self.work_key = self._ensure_work_key()

    def _ensure_salt(self):
        if os.path.exists(SALT_FILE):
            with open(SALT_FILE, 'rb') as sf:
                return sf.read()
        else:
            salt = secrets.token_bytes(16)
            with open(SALT_FILE, 'wb') as sf:
                sf.write(salt)
            logger.info(f"New master key salt generated and stored in {SALT_FILE}")
            return salt

    def _derive_master_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.master_key_salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key_password))
        logger.info("Master key derived using PBKDF2.")
        return key

    def _ensure_work_key(self):
        if os.path.exists(KEY_FILE):
            logger.info(f"Loading existing encrypted work key from {KEY_FILE}")
            return self._load_and_decrypt_work_key()
        else:
            logger.info("No work key found, generating a new one.")
            return self._generate_and_store_work_key()

    def _generate_and_store_work_key(self):
        work_key_plaintext = Fernet.generate_key()
        f = Fernet(self.master_key)
        encrypted_work_key = f.encrypt(work_key_plaintext)
        with open(KEY_FILE, 'wb') as kf:
            kf.write(encrypted_work_key)
        logger.info(f"New work key generated and stored encrypted in {KEY_FILE}")
        return work_key_plaintext

    def _load_and_decrypt_work_key(self):
        try:
            with open(KEY_FILE, 'rb') as kf:
                encrypted_work_key = kf.read()
            f = Fernet(self.master_key)
            work_key_plaintext = f.decrypt(encrypted_work_key)
            logger.info("Work key loaded and decrypted successfully.")
            return work_key_plaintext
        except Exception as e:
            logger.error(f"Error loading or decrypting work key: {e}")
            raise

    def get_work_key(self):
        return self.work_key