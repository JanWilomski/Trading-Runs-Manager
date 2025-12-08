from datetime import datetime


class RunManager:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.db = app_manager.db

    def create_run_with_account(self, run_name, initial_capital, max_loss_pct,
                                max_daily_loss_pct, mt5_login, mt5_password,
                                mt5_server, account_name=None):

        existing_account = self.db.get_account(mt5_login)
        if not existing_account:

            self.app_manager.add_mt5_account(
                account_id=mt5_login,
                password=mt5_password,
                server=mt5_server,
                name=account_name or f"Konto dla {run_name}"
            )


        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.create_run(
            run_name=run_name,
            start_date=start_date,
            initial_capital=initial_capital,
            max_loss_percentage=max_loss_pct,
            max_daily_loss_percentage=max_daily_loss_pct,
            status='active',
            mt5_account_id=mt5_login
        )

        print(f"✅ Utworzono run '{run_name}' z kontem MT5 {mt5_login}")

        if self.app_manager.connect_mt5_account(mt5_login):
            print(f"✅ Połączono z kontem MT5")
            return True
        else:
            print(f"❌ Nie udało się połączyć z MT5")
            return False