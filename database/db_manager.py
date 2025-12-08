import sqlite3

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()


    def create_tables(self):
        self.create_runs_table()
        self.create_trades_table()
        self.create_accounts_table()

    def create_runs_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            initial_capital REAL NOT NULL,
            current_capital REAL NOT NULL,
            max_loss_percentage REAL NOT NULL,
            max_daily_loss_percentage REAL NOT NULL,
            status TEXT NOT NULL,
            mt5_account_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
    def create_trades_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            type TEXT NOT NULL,
            volume REAL NOT NULL,
            open_price REAL NOT NULL,
            close_price REAL,
            open_time TEXT NOT NULL,
            close_time TEXT,
            profit REAL,
            profit_pct REAL,
            mt5_ticket INTEGER,
            FOREIGN KEY (run_id) REFERENCES runs (id)
        )''')

    def create_accounts_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER UNIQUE NOT NULL,
            account_password TEXT NOT NULL,
            account_name TEXT,
            server TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')

    def close(self):
        self.conn.close()


    def create_run(self, run_name, start_date, initial_capital, max_loss_percentage, max_daily_loss_percentage, status='active', mt5_account_id=0):
        self.cursor.execute('''INSERT INTO runs (name, start_date, end_date, initial_capital, current_capital, max_loss_percentage, max_daily_loss_percentage, status, mt5_account_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (run_name, start_date, None, initial_capital, initial_capital, max_loss_percentage, max_daily_loss_percentage, status, mt5_account_id))
        self.conn.commit()


    #RUNS
    def get_runs(self):
        self.cursor.execute('''SELECT * FROM runs''')
        return self.cursor.fetchall()
    def get_run(self, run_id):
        self.cursor.execute('''SELECT * FROM runs WHERE id=?''', (run_id,))
        return self.cursor.fetchone()

    def update_run_capital(self, run_id, new_capital):
        self.cursor.execute('''UPDATE runs SET current_capital=? WHERE id=?''', (new_capital, run_id))
        self.conn.commit()


    def close_run(self, run_id, end_date, final_status):
        self.cursor.execute('''UPDATE runs SET end_date=?, status=? WHERE id=?''', (end_date, final_status, run_id))
        self.conn.commit()

    def get_active_run(self):
        self.cursor.execute('''SELECT * FROM runs WHERE status=?''', ('active',))
        return self.cursor.fetchone()

    #ACCOUNTS

    def add_account(self, account_id, account_password, server, account_name=None):
        self.cursor.execute('''INSERT INTO accounts (account_id, account_password, account_name, server) VALUES (?, ?, ?, ?)''', (account_id, account_password, account_name, server))
        self.conn.commit()

    def get_accounts(self):
        self.cursor.execute('''SELECT * FROM accounts''')
        return self.cursor.fetchall()

    def get_account(self, account_id):
        self.cursor.execute('''SELECT * FROM accounts WHERE account_id=?''', (account_id,))
        return self.cursor.fetchone()


    #TRADES

    def add_trade(self, run_id, symbol, type, volume, open_price, close_price, open_time, close_time, profit, profit_pct, mt5_ticket):
        self.cursor.execute('''INSERT INTO trades (run_id, symbol, type, volume, open_price, close_price, open_time, close_time, profit, profit_pct, mt5_ticket) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (run_id, symbol, type, volume, open_price, close_price, open_time, close_time, profit, profit_pct, mt5_ticket))
        self.conn.commit()

    def get_trades(self, run_id):
        self.cursor.execute('''SELECT * FROM trades WHERE run_id=?''', (run_id,))
        return self.cursor.fetchall()

    def get_trade(self, trade_id):
        self.cursor.execute('''SELECT * FROM trades WHERE id=?''', (trade_id,))
        return self.cursor.fetchone()

    def update_trade_close_price(self, trade_id, close_price, close_time, profit, profit_pct):
        self.cursor.execute('''UPDATE trades SET close_price=?, close_time=?, profit=?, profit_pct=? WHERE id=?''', (close_price, close_time, profit, profit_pct, trade_id))
        self.conn.commit()

    def get_open_trades(self, run_id=None):
        if run_id:
            self.cursor.execute('''SELECT * FROM trades WHERE close_time IS NULL AND run_id=?''', (run_id,))
        else:
            self.cursor.execute('''SELECT * FROM trades WHERE close_time IS NULL''')
        return self.cursor.fetchall()

    def delete_account(self, account_id):
        self.cursor.execute('''DELETE FROM accounts WHERE account_id=?''', (account_id,))
        self.conn.commit()







