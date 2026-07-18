import numpy as np
import os
from PIL import Image
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

class ImageEncryption:
    @staticmethod
    def logistic_map(x, r=3.9):
        return r * x * (1 - x)

    @staticmethod
    def generate_chaotic_sequence(length, seed=0.1, r=3.9):
        seq = []
        x = seed
        for _ in range(length):
            x = ImageEncryption.logistic_map(x, r)
            seq.append(int(x * 256) % 256)
        return np.array(seq, dtype=np.uint8)

    @staticmethod
    def scramble_image(img_array, chaotic_seq):
        if img_array.ndim == 2:
            h, w = img_array.shape
            c = 1
            img_array = img_array.reshape(h, w, 1)  
        elif img_array.ndim == 3:
            h, w, c = img_array.shape
        else:
            raise ValueError("Image must be 2D or 3D")

        total_pixels = h * w * c
        if len(chaotic_seq) < total_pixels:
            chaotic_seq = np.tile(chaotic_seq, (total_pixels // len(chaotic_seq) + 1))[:total_pixels]

        flat = img_array.flatten()
        indices = np.argsort(chaotic_seq[:len(flat)])
        scrambled_flat = flat[indices]

        if c == 1:
            return scrambled_flat.reshape(h, w)
        else:
            return scrambled_flat.reshape(h, w, c)

    @staticmethod
    def unscramble_image(scrambled, chaotic_seq):
        if scrambled.ndim == 2:
            h, w = scrambled.shape
            c = 1
            scrambled = scrambled.reshape(h, w, 1)
        elif scrambled.ndim == 3:
            h, w, c = scrambled.shape
        else:
            raise ValueError("Scrambled image must be 2D or 3D")

        total_pixels = h * w * c
        if len(chaotic_seq) < total_pixels:
            chaotic_seq = np.tile(chaotic_seq, (total_pixels // len(chaotic_seq) + 1))[:total_pixels]

        flat = scrambled.flatten()
        indices = np.argsort(chaotic_seq[:len(flat)])
        original = np.empty_like(flat)
        original[indices] = flat

        if c == 1:
            return original.reshape(h, w)
        else:
            return original.reshape(h, w, c)

    @staticmethod
    def encrypt_image(image_path, public_key_pem):
       
        img = Image.open(image_path).convert('RGB')  
        img_array = np.array(img, dtype=np.uint8)  

        chaotic_seq = ImageEncryption.generate_chaotic_sequence(img_array.size)
        scrambled = ImageEncryption.scramble_image(img_array, chaotic_seq)

        aes_key = os.urandom(16)
        nonce = os.urandom(12)
        aesgcm = AESGCM(aes_key)
        ciphertext = aesgcm.encrypt(nonce, scrambled.tobytes(), None)

        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        encrypted_nonce = public_key.encrypt(
            nonce,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        base_name, ext = os.path.splitext(os.path.basename(image_path))
        encrypted_file = f"{base_name}_encrypted.dat"
        with open(encrypted_file, 'wb') as f:
            f.write(encrypted_aes_key)
            f.write(encrypted_nonce)
            f.write(ciphertext)
        return encrypted_file

    @staticmethod
    def decrypt_image(encrypted_path, private_key_pem):
        with open(encrypted_path, 'rb') as f:
            data = f.read()

        aes_key_len, nonce_len = 256, 256
        encrypted_aes_key = data[:aes_key_len]
        encrypted_nonce = data[aes_key_len:aes_key_len+nonce_len]
        ciphertext = data[aes_key_len+nonce_len:]

        private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        nonce = private_key.decrypt(
            encrypted_nonce,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        aesgcm = AESGCM(aes_key)
        scrambled_bytes = aesgcm.decrypt(nonce, ciphertext, None)

        h, w = 256, 256  
        total_bytes = len(scrambled_bytes)
        if total_bytes % 3 != 0:
            h, w = int(np.sqrt(total_bytes)), int(np.sqrt(total_bytes))
            scrambled_array = np.frombuffer(scrambled_bytes, dtype=np.uint8).reshape(h, w)
            chaotic_seq = ImageEncryption.generate_chaotic_sequence(h * w)
            original_array = ImageEncryption.unscramble_image(scrambled_array, chaotic_seq)
            mode = 'L'
        else:
            c = 3
            h = w = int(np.sqrt(total_bytes // c))
            scrambled_array = np.frombuffer(scrambled_bytes, dtype=np.uint8).reshape(h, w, c)
            chaotic_seq = ImageEncryption.generate_chaotic_sequence(h * w * c)
            original_array = ImageEncryption.unscramble_image(scrambled_array, chaotic_seq)
            mode = 'RGB'

        decrypted_img = Image.fromarray(original_array.astype(np.uint8), mode=mode)
        decrypted_file = encrypted_path.replace('_encrypted.dat', '_decrypted.png')
        decrypted_img.save(decrypted_file)
        return decrypted_file