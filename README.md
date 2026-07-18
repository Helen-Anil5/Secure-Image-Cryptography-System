# Secure Image Cryptography System

## Overview

Secure Image Cryptography System is a Python-based desktop application that enables secure image encryption and decryption using a hybrid cryptographic approach. The application combines RSA public-key cryptography with AES symmetric encryption to ensure secure key exchange, efficient image protection, and authenticated user access.

## Features

- User registration and login
- RSA (2048-bit) key pair generation
- Hybrid RSA-AES image encryption
- Secure image decryption
- SHA-256 password hashing
- PBKDF2-based key derivation
- SQLite database for user management
- Tkinter-based desktop graphical user interface

## Technologies Used

- Python 3
- Tkinter
- Cryptography
- SQLite
- Pillow (PIL)
- NumPy

## Project Structure

```
Secure-Image-Cryptography-System/
│
├── gui_app.py
├── server.py
├── database.py
├── image_crypto.py
├── password_crypto.py
├── key_manager.py
├── user_keys/
├── users.db
├── README.md
└── .gitignore
```

## Workflow

### User Registration
- Creates a new user account.
- Generates an RSA public/private key pair.
- Stores user credentials securely.

### Image Encryption
- User logs in.
- Selects an image for encryption.
- Generates a random AES key.
- Encrypts the image using AES.
- Encrypts the AES key using the user's RSA public key.
- Saves the encrypted image as a `.enc` file.

### Image Decryption
- User selects an encrypted image.
- RSA private key decrypts the AES key.
- AES decrypts the image.
- Restores the original image.

## Running the Application

Start the authentication server:

```bash
python server.py
```

Run the desktop application:

```bash
python gui_app.py
```

## Security Features

- Hybrid RSA-AES encryption
- RSA-2048 key management
- AES symmetric encryption
- SHA-256 password hashing
- PBKDF2 key derivation
- User-specific cryptographic keys
