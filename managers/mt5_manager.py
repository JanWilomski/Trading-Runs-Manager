import MetaTrader5 as mt


class MT5Manager:
    def __init__(self):
        self.connected = False
        self.login = None
        self.password = None
        self.server = None



    def connect(self, login, password, server):
        if not mt.initialize():
            print("❌ Nie udało się zainicjalizować MT5")
            return False
        self.login = login
        self.password = password
        self.server = server

        authorized = mt.login(login, password, server)
        if authorized:
            self.connected = True
            self.login = login
            self.server = server
            print(f"✅ Zalogowano do konta {login}")
            return True
        else:
            print(f"❌ Nie udało się zalogować")
            print(f"Błąd: {mt.last_error()}")
            self.connected = False
            return False

    def disconnect(self):
        mt.shutdown()

    def get_account_info(self):
        return mt.account_info()

    def get_open_positions(self):
        if not self.connected:
            return None
        return mt.positions_get()

    def get_closed_positions(self, from_date, to_date):
        if not self.connected:
            return []
        deals = mt.history_deals_get(from_date, to_date)
        return deals if deals else []

    def is_connected(self):
        return self.connected and mt.terminal_info() is not None
