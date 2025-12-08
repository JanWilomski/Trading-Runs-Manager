from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class EncryptionManager:
    def __init__(self, master_password, salt=None):
        if salt is None:
            self.salt = os.urandom(16)
        else:
            self.salt = salt

        self.key = self._generate_key(master_password)
        self.cipher = Fernet(self.key)

    def _generate_key(self, master_password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data):
        try:
            return self.cipher.decrypt(encrypted_data).decode()
        except Exception as e:
            raise ValueError("Nie można odszyfrować - prawdopodobnie złe master password!")

    def get_salt(self):

        return base64.b64encode(self.salt).decode()