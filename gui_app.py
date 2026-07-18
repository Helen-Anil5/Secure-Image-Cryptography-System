import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import socket
import json
import base64
import re
import threading
import time
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

HOST = 'localhost'
PORT = 12345

class SecurePasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Security System")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#2C3E50")
        self.current_user = None
        self.show_home_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_home_page(self):
        self.clear_window()
        self.root.configure(bg="#2C3E50")
        container = tk.Frame(self.root, bg="#2C3E50")
        container.pack(expand=True)

        tk.Label(container, text="Hybrid Security System", font=("Helvetica", 32, "bold"), fg="#ECF0F1", bg="#2C3E50").pack(pady=(50, 40))
        tk.Label(container, text="Secure your passwords and protect your images with advanced encryption.", font=("Arial", 14), fg="#BDC3C7", bg="#2C3E50").pack(pady=(0, 60))

        btn_frame = tk.Frame(container, bg="#2C3E50")
        btn_frame.pack()
        tk.Button(btn_frame, text="Register", command=self.show_register_page, bg="#3498DB", fg="white", font=("Arial", 14, "bold"), height=2, width=15, cursor="hand2", relief="flat", bd=0).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="Login", command=self.show_login_page, bg="#E74C3C", fg="white", font=("Arial", 14, "bold"), height=2, width=15, cursor="hand2", relief="flat", bd=0).pack(side=tk.LEFT, padx=20)

    def show_register_page(self):
        self.clear_window()
        self.root.configure(bg="#34495E")
        container = tk.Frame(self.root, bg="#34495E")
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Create Account", font=("Helvetica", 24, "bold"), fg="#ECF0F1", bg="#34495E").grid(row=0, column=0, columnspan=2, pady=(0, 30))
        tk.Label(container, text="Username:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.u_reg = tk.Entry(container, font=("Arial", 12), width=30)
        self.u_reg.grid(row=1, column=1, pady=5, padx=10)
        tk.Label(container, text="Password:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.p_reg = tk.Entry(container, show="*", font=("Arial", 12), width=30)
        self.p_reg.grid(row=2, column=1, pady=5, padx=10)
        tk.Label(container, text="• Min 8 chars • Upper • Lower • Digit • Special", bg="#34495E", fg="#7F8C8D", font=("Arial", 9)).grid(row=3, column=0, columnspan=2, pady=(5,10), sticky="w")

        self.btn_reg = tk.Button(container, text="Register", command=self._reg_with_loader, bg="#3498DB", fg="white", font=("Arial", 12, "bold"), height=2, width=20, cursor="hand2", relief="flat", bd=0)
        self.btn_reg.grid(row=4, column=0, columnspan=2, pady=20)

        self.lbl_reg_status = tk.Label(container, text="", bg="#34495E", fg="#ECF0F1", font=("Arial", 12))
        self.lbl_reg_status.grid(row=6, column=0, columnspan=2, pady=10)

        tk.Button(container, text="Back to Home", command=self.show_home_page, bg="#95A5A6", fg="white", font=("Arial", 10), cursor="hand2", relief="flat", bd=0).grid(row=7, column=0, columnspan=2, pady=(10, 0))

    def show_login_page(self):
        self.clear_window()
        self.root.configure(bg="#34495E")
        container = tk.Frame(self.root, bg="#34495E")
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Login to Your Account", font=("Helvetica", 24, "bold"), fg="#ECF0F1", bg="#34495E").grid(row=0, column=0, columnspan=2, pady=(0, 30))
        tk.Label(container, text="Username:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.u_login = tk.Entry(container, font=("Arial", 12), width=30)
        self.u_login.grid(row=1, column=1, pady=5, padx=10)
        tk.Label(container, text="Password:", bg="#34495E", fg="#ECF0F1", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.p_login = tk.Entry(container, show="*", font=("Arial", 12), width=30)
        self.p_login.grid(row=2, column=1, pady=5, padx=10)

        self.btn_login = tk.Button(container, text="Login via Server", command=self._login_with_loader, bg="#E74C3C", fg="white", font=("Arial", 12, "bold"), height=2, width=20, cursor="hand2", relief="flat", bd=0)
        self.btn_login.grid(row=3, column=0, columnspan=2, pady=20)

        self.lbl_login_status = tk.Label(container, text="", bg="#34495E", fg="#ECF0F1", font=("Arial", 12))
        self.lbl_login_status.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(container, text="Back to Home", command=self.show_home_page, bg="#95A5A6", fg="white", font=("Arial", 10), cursor="hand2", relief="flat", bd=0).grid(row=6, column=0, columnspan=2, pady=(10, 0))

    def show_main_app(self):
        self.clear_window()
        self.root.configure(bg="#2C3E50")
        header_frame = tk.Frame(self.root, bg="#34495E", height=80)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=f"Welcome, {self.current_user}!", font=("Arial", 16, "bold"), fg="#ECF0F1", bg="#34495E").pack(side=tk.LEFT, padx=20, pady=20)

        nav_frame = tk.Frame(header_frame, bg="#34495E")
        nav_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        tk.Button(nav_frame, text="Dashboard", command=self.show_main_app, bg="#3498DB", fg="white", font=("Arial", 10, "bold"), cursor="hand2", relief="flat", bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Logout", command=self.logout, bg="#E74C3C", fg="white", font=("Arial", 10, "bold"), cursor="hand2", relief="flat", bd=0, width=10).pack(side=tk.LEFT, padx=5)

        main_container = tk.Frame(self.root, bg="#2C3E50")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        tk.Label(main_container, text="Image Protection Suite", font=("Helvetica", 24, "bold"), fg="#ECF0F1", bg="#2C3E50").pack(pady=(0, 30))
        tk.Label(main_container, text="Encrypt or decrypt your sensitive images securely.", font=("Arial", 14), fg="#BDC3C7", bg="#2C3E50").pack(pady=(0, 40))

        btn_frame = tk.Frame(main_container, bg="#2C3E50")
        btn_frame.pack()
        self.btn_encrypt = tk.Button(btn_frame, text="Encrypt Image", command=self._encrypt_image_with_auth, bg="#3498DB", fg="white", font=("Arial", 14, "bold"), height=2, width=15, cursor="hand2", relief="flat", bd=0)
        self.btn_encrypt.pack(side=tk.LEFT, padx=20)
        self.btn_decrypt = tk.Button(btn_frame, text="Decrypt Image", command=self._decrypt_image_with_auth, bg="#E74C3C", fg="white", font=("Arial", 14, "bold"), height=2, width=15, cursor="hand2", relief="flat", bd=0)
        self.btn_decrypt.pack(side=tk.LEFT, padx=20)

        self.lbl_image_status = tk.Label(main_container, text="", bg="#2C3E50", fg="#ECF0F1", font=("Arial", 12))
        self.lbl_image_status.pack(pady=30)

    def logout(self):
        self.current_user = None
        self.show_home_page()

    def _is_strong(self, pwd):
        if len(pwd) < 8: return False, "Min 8 characters"
        if not re.search(r'[A-Z]', pwd): return False, "At least one uppercase letter"
        if not re.search(r'[a-z]', pwd): return False, "At least one lowercase letter"
        if not re.search(r'[0-9]', pwd): return False, "At least one digit"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd): return False, "At least one special character"
        return True, ""

    def _show_loader(self, msg):
        for lbl in ['lbl_reg_status', 'lbl_login_status', 'lbl_image_status']:
            if hasattr(self, lbl) and getattr(self, lbl).winfo_exists():
                getattr(self, lbl).config(text=msg)
                break
        for btn in ['btn_reg', 'btn_login', 'btn_encrypt', 'btn_decrypt']:
            if hasattr(self, btn) and getattr(self, btn).winfo_exists():
                getattr(self, btn).config(state=tk.DISABLED)

    def _hide_loader(self):
        for btn in ['btn_reg', 'btn_login', 'btn_encrypt', 'btn_decrypt']:
            if hasattr(self, btn) and getattr(self, btn).winfo_exists():
                getattr(self, btn).config(state=tk.NORMAL)
        for lbl in ['lbl_reg_status', 'lbl_login_status', 'lbl_image_status']:
            if hasattr(self, lbl) and getattr(self, lbl).winfo_exists():
                getattr(self, lbl).config(text="")

    def _reg_with_loader(self):
        u = self.u_reg.get().strip()
        p = self.p_reg.get()
        if not u or not p:
            messagebox.showwarning("Input", "Username/password empty.")
            return
        ok, msg = self._is_strong(p)
        if not ok:
            messagebox.showwarning("Policy", msg) 
            return
        self._show_loader("Registering...")
        threading.Thread(target=self._do_register, args=(u, p), daemon=True).start()

    def _do_register(self, username, password):
        try:
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()
            private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode()
            user_dir = os.path.join("user_keys", username)
            os.makedirs(user_dir, exist_ok=True)
            with open(os.path.join(user_dir, "public.pem"), 'w') as f: f.write(public_pem)
            with open(os.path.join(user_dir, "private.pem"), 'w') as f: f.write(private_pem)
            self.root.after(0, self._on_reg_done, True, username)
        except Exception as e:
            self.root.after(0, self._on_reg_error, str(e))

    def _on_reg_done(self, success, user):
        self._hide_loader()
        if success:
            messagebox.showinfo("Success", f"Registration successful!\nWelcome, {user}.")
            self.show_home_page()
        else:
            messagebox.showerror("Registration Failed", "Username already exists.")

    def _on_reg_error(self, err):
        self._hide_loader()
        messagebox.showerror("Error", err)

    def _login_with_loader(self):
        u = self.u_login.get().strip()
        p = self.p_login.get()
        if not u or not p:
            messagebox.showwarning("Input", "Username/password empty.")
            return
        self._show_loader("Authenticating...")
        threading.Thread(target=self._do_login, args=(u, p), daemon=True).start()

    def _do_login(self, username, password):
        try:
            time.sleep(1)
            success = os.path.exists(os.path.join("user_keys", username))
            result = {"status": "success" if success else "failure", "message": "Login successful" if success else "Invalid credentials"}
            self.root.after(0, self._on_login_done, result, username)
        except Exception as e:
            self.root.after(0, self._on_login_error, str(e))

    def _on_login_done(self, result, username):
        self._hide_loader()
        if result["status"] == "success":
            self.current_user = username
            messagebox.showinfo("Login", "Access granted!")
            self.show_main_app()
        else:
            messagebox.showerror("Login", result["message"])

    def _on_login_error(self, err):
        self._hide_loader()
        messagebox.showerror("Error", err)

    def _encrypt_image_with_auth(self):
        if not self.current_user:
            messagebox.showwarning("Auth Required", "Please log in first.")
            return
        file_path = filedialog.askopenfilename(title="Select Image to Encrypt", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if not file_path: return
        self._show_loader("Encrypting...")
        threading.Thread(target=self._do_image_operation, args=(file_path, 'encrypt'), daemon=True).start()

    def _decrypt_image_with_auth(self):
        if not self.current_user:
            messagebox.showwarning("Auth Required", "Please log in first.")
            return
        file_path = filedialog.askopenfilename(title="Select Encrypted File to Decrypt", filetypes=[("Encrypted files", "*.enc")])
        if not file_path: return
        self._show_loader("Decrypting...")
        threading.Thread(target=self._do_image_operation, args=(file_path, 'decrypt'), daemon=True).start()

    def _do_image_operation(self, file_path, operation):
        try:
            dir_name = os.path.dirname(file_path)
            name, ext = os.path.splitext(os.path.basename(file_path))

            if operation == 'encrypt':
                result_file = os.path.join(dir_name, f"{name}{ext}.enc")
                with open(file_path, 'rb') as f: data = f.read()
                user_dir = os.path.join("user_keys", self.current_user)
                with open(os.path.join(user_dir, "public.pem"), 'r') as f: public_pem = f.read()
                encrypted_data = self._rsa_encrypt_image(data, public_pem)
                with open(result_file, 'wb') as f: f.write(encrypted_data)
                message = f"Encrypted: {os.path.basename(result_file)}\nSaved in: {dir_name}"

            elif operation == 'decrypt':
                if not file_path.endswith('.enc'):
                    raise ValueError("File must have .enc extension")
                base_no_enc = os.path.basename(file_path).rstrip('.enc')
                name_no_ext, ext_no_ext = os.path.splitext(base_no_enc)
                ext_out = ext_no_ext if ext_no_ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif'] else '.png'
                result_file = os.path.join(dir_name, f"{name_no_ext}_decrypted{ext_out}")
                with open(file_path, 'rb') as f: encrypted_data = f.read()
                user_dir = os.path.join("user_keys", self.current_user)
                with open(os.path.join(user_dir, "private.pem"), 'r') as f: private_pem = f.read()
                decrypted_data = self._rsa_decrypt_image(encrypted_data, private_pem)
                with open(result_file, 'wb') as f: f.write(decrypted_data)
                message = f"Decrypted: {os.path.basename(result_file)}\nSaved in: {dir_name}"

            else:
                raise ValueError("Invalid operation")

            self.root.after(0, self._on_image_operation_success, message)
        except Exception as e:
            self.root.after(0, self._on_image_operation_error, str(e))

    def _rsa_encrypt_image(self, data: bytes, public_pem: str) -> bytes:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.fernet import Fernet
        public_key = serialization.load_pem_public_key(public_pem.encode())
        aes_key = Fernet.generate_key()
        f = Fernet(aes_key)
        pad_len = (16 - len(data) % 16) % 16
        padded_data = data + b'\x00' * pad_len
        encrypted_img = f.encrypt(padded_data)
        encrypted_aes_key = public_key.encrypt(aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        key_len = len(encrypted_aes_key).to_bytes(4, 'big')
        return key_len + encrypted_aes_key + encrypted_img

    def _rsa_decrypt_image(self, encrypted_data: bytes, private_pem: str) -> bytes:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.fernet import Fernet
        private_key = serialization.load_pem_private_key(private_pem.encode(), password=None)
        key_len = int.from_bytes(encrypted_data[:4], 'big')
        offset = 4
        encrypted_aes_key = encrypted_data[offset:offset+key_len]
        encrypted_img = encrypted_data[offset+key_len:]
        aes_key = private_key.decrypt(encrypted_aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        f = Fernet(aes_key)
        padded_data = f.decrypt(encrypted_img)
        return padded_data.rstrip(b'\x00')

    def _on_image_operation_success(self, message):
        self._hide_loader()
        self.lbl_image_status.config(text=message)
        messagebox.showinfo("Success", message)

    def _on_image_operation_error(self, err):
        self._hide_loader()
        messagebox.showerror("Error", f"Operation failed:\n{err}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SecurePasswordApp(root)
    root.mainloop()