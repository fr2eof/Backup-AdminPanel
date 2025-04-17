import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from backup_log_system_back import settings

secure_dir = os.path.join(
    settings.BASE_BACKUP_DIR['location'], "/secure".lstrip('/')
)
KEY_FILE = secure_dir + '/keyfile.key'


def generate_key():
    return os.urandom(32)


def save_key(key):
    with open(KEY_FILE, 'wb') as f:
        f.write(key)


def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = generate_key()
        save_key(key)
        return key


def encrypt_file(file_path, key):
    iv = os.urandom(16)
    cipher = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend()
    )
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open(file_path + '.enc', 'wb') as f:
        f.write(iv + encrypted_data)


def decrypt_file(encrypted_file_path, key):
    with open(encrypted_file_path, 'rb') as f:
        iv = f.read(16)
        encrypted_data = f.read()

    cipher = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend()
    )
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()

    with open(encrypted_file_path.replace('.enc', ''), 'wb') as f:
        f.write(data)


def verify_encrypted_file(file_path, key):
    try:
        with open(file_path, 'rb') as f:
            iv = f.read(16)
            encrypted_data = f.read()

        cipher = Cipher(
            algorithms.AES(key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        decrypted_padded_data = (
                decryptor.update(encrypted_data) + decryptor.finalize()
        )

        unpadder = padding.PKCS7(128).unpadder()
        unpadder.update(decrypted_padded_data)
        return True

    except ValueError as e:
        return False
