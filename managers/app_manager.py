import hashlib
from database.db_manager import DBManager
from managers.settings_manager import SettingsManager
from managers.encryption_manager import EncryptionManager
from managers.mt5_manager import MT5Manager
from managers.run_manager import RunManager
import base64


class AppManager:
    def __init__(self):
        self.db = DBManager('data/test.db')
        self.settings = SettingsManager('data/settings.json')
        self.encryption_manager = None
        self.is_authenticated = False
        self.mt5_manager = None
        self.run_manager = None
        self.db.create_tables()

    def authenticate(self, master_password):
        password_hash = hashlib.sha256(master_password.encode()).hexdigest()
        saved_hash = self.settings.get_setting('master_password_hash')

        if password_hash == saved_hash:
            saved_salt = self.settings.get_setting('salt')
            salt_bytes = base64.b64decode(saved_salt)

            self.encryption_manager = EncryptionManager(master_password, salt=salt_bytes)
            self.is_authenticated = True
            self.run_manager = RunManager(self)
            return True
        else:
            return False


    def setup_master_password(self, master_password):
        password_hash = hashlib.sha256(master_password.encode()).hexdigest()
        self.settings.set_setting('master_password_hash', password_hash)
        self.encryption_manager = EncryptionManager(master_password)
        self.settings.set_setting('salt', self.encryption_manager.get_salt())
        self.is_authenticated = True
        self.run_manager = RunManager(self)

    def add_mt5_account(self, account_id, password, server, name=None):
        if not self.is_authenticated:
            raise Exception("Musisz być zalogowany aby dodać konto!")

        encrypted_pass = self.encryption_manager.encrypt(password)
        self.db.add_account(account_id, encrypted_pass, server, name)

    def get_mt5_account_password(self, account_id):
        account = self.db.get_account(account_id)
        if account:
            encrypted_pass = account[2]
            return self.encryption_manager.decrypt(encrypted_pass)
        return None

    def is_first_run(self):
        return not self.settings.get_setting('master_password_hash')

    def connect_mt5_account(self, account_id):
        if not self.is_authenticated:
            print("❌ Nie zalogowano - brak encryption managera")
            return False

        account = self.db.get_account(account_id)
        if not account:
            print(f"❌ Nie znaleziono konta {account_id} w bazie")
            return False

        print(f"🔍 Znaleziono konto: {account}")  # DEBUG

        acc_id = account[1]
        encrypted_pass = account[2]
        server = account[4]

        print(f"🔍 Próba deszyfrowania hasła...")  # DEBUG
        try:
            password = self.encryption_manager.decrypt(encrypted_pass)
            print(f"✅ Hasło odszyfrowane")  # DEBUG
        except Exception as e:
            print(f"❌ Błąd deszyfrowania: {e}")
            return False

        print(f"🔍 Łączenie z MT5: login={acc_id}, server={server}")  # DEBUG

        self.mt5_manager = MT5Manager()
        result = self.mt5_manager.connect(acc_id, password, server)

        print(f"🔍 Wynik połączenia MT5: {result}")  # DEBUG

        return result

