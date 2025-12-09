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


    def sync_trades_from_mt5(self, run_id):
        """
        Pobiera trade'y z MT5 i synchronizuje z bazą
        Zwraca liczbę nowych trade'ów
        """
        if not self.app_manager.mt5_manager or not self.app_manager.mt5_manager.is_connected():
            return 0

        # Pobierz run z bazy
        run = self.db.get_run(run_id)
        if not run:
            return 0

        start_date = run[2]
        initial_capital = run[4]

        # Konwertuj start_date na timestamp
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            start_timestamp = int(start_dt.timestamp())
            now_timestamp = int(datetime.now().timestamp())
        except:
            print("❌ Błąd parsowania daty")
            return 0

        # Pobierz zamknięte deale z MT5
        deals = self.app_manager.mt5_manager.get_closed_trades(start_timestamp, now_timestamp)

        if not deals:
            return 0

        # Pobierz istniejące tickety z bazy
        existing_trades = self.db.get_trades(run_id)
        existing_tickets = set([trade[11] for trade in existing_trades if trade[11]])

        # Filtruj i dodaj nowe trade'y
        new_count = 0
        total_profit = 0

        for deal in deals:
            # Tylko zamknięte pozycje (entry=1 to wejście, entry=0 to wyjście)
            if deal.entry != 1 and deal.ticket not in existing_tickets:
                # Oblicz profit % względem kapitału przy otwarciu
                current_capital_at_open = initial_capital + total_profit
                profit_pct = (deal.profit / current_capital_at_open * 100) if current_capital_at_open > 0 else 0

                # Konwertuj timestamp na datetime
                open_time = datetime.fromtimestamp(deal.time).strftime("%Y-%m-%d %H:%M:%S")

                # Typ transakcji
                deal_type = "buy" if deal.type == 0 else "sell"

                # Dodaj do bazy
                self.db.add_trade(
                    run_id=run_id,
                    symbol=deal.symbol,
                    type=deal_type,
                    volume=deal.volume,
                    open_price=deal.price,
                    close_price=deal.price,  # W deals price to cena zamknięcia
                    open_time=open_time,
                    close_time=open_time,  # Dla deals czas otwarcia = zamknięcia
                    profit=deal.profit,
                    profit_pct=profit_pct,
                    mt5_ticket=deal.ticket
                )

                total_profit += deal.profit
                new_count += 1

        # Zaktualizuj current_capital jeśli są nowe trade'y
        if new_count > 0:
            new_capital = initial_capital + sum([t[9] for t in self.db.get_trades(run_id) if t[9]])
            self.db.update_run_capital(run_id, new_capital)
            print(f"✅ Zsynchronizowano {new_count} nowych trade'ów")

            # Sprawdź stop loss
            self.check_stop_loss(run_id)

        return new_count

    def check_stop_loss(self, run_id):
        """Sprawdza czy osiągnięto stop loss"""
        run = self.db.get_run(run_id)
        if not run or run[8] != 'active':  # status
            return

        initial_capital = run[4]
        current_capital = run[5]
        max_loss_pct = run[6]

        # Oblicz stratę
        loss = initial_capital - current_capital
        loss_pct = (loss / initial_capital * 100) if initial_capital > 0 else 0

        # Sprawdź czy przekroczono stop loss
        if loss_pct >= max_loss_pct:
            print(f"🛑 STOP LOSS! Strata: {loss_pct:.1f}%")
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.close_run(run_id, end_date, 'stopped')
            return True

        return False