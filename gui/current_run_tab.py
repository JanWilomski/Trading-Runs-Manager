import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class CurrentRunTab:
    def __init__(self, parent):
        self.parent = parent
        self.app_manager = parent.app_manager
        self.active_run = None
        self.auto_refresh_enabled = True
        self.refresh_job = None

        self.create_widgets()
        self.load_current_run()
        self.start_auto_refresh()

    def create_widgets(self):
        # Główny scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent.tabview.tab("Current Run")
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Przyciski na górze
        buttons_frame = ctk.CTkFrame(self.parent.tabview.tab("Current Run"), fg_color="transparent")
        buttons_frame.place(relx=1.0, x=-20, y=10, anchor="ne")

        # Przycisk toggle auto-refresh
        self.auto_refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="⏸️ Pauza",
            command=self.toggle_auto_refresh,
            width=100,
            height=35
        )
        self.auto_refresh_btn.pack(side="right", padx=5)

        # Przycisk ręcznego odświeżania
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Odśwież",
            command=self.refresh_data,
            width=100,
            height=35
        )
        refresh_btn.pack(side="right", padx=5)

    def start_auto_refresh(self):
        """Uruchom automatyczne odświeżanie co 1 sekundę"""
        if self.auto_refresh_enabled and self.active_run:
            # Synchronizuj dane z MT5
            run_id = self.active_run[0]
            self.app_manager.run_manager.sync_trades_from_mt5(run_id)

            # Odśwież wyświetlanie
            self.load_current_run()

            # Zaplanuj następne odświeżenie za 1000ms (1 sekunda)
            self.refresh_job = self.parent.window.after(1000, self.start_auto_refresh)

    def stop_auto_refresh(self):
        """Zatrzymaj automatyczne odświeżanie"""
        self.auto_refresh_enabled = False
        if self.refresh_job:
            self.parent.window.after_cancel(self.refresh_job)
            self.refresh_job = None

    def toggle_auto_refresh(self):
        """Przełącz auto-refresh ON/OFF"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled

        if self.auto_refresh_enabled:
            self.auto_refresh_btn.configure(text="⏸️ Pauza")
            self.start_auto_refresh()
        else:
            self.auto_refresh_btn.configure(text="▶️ Wznów")
            self.stop_auto_refresh()

    def load_current_run(self):
        """Wczytaj aktywny run"""
        self.active_run = self.app_manager.db.get_active_run()

        # Wyczyść poprzednią zawartość
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if not self.active_run:
            self.show_no_active_run()
        else:
            self.display_run_info()

    def show_no_active_run(self):
        """Pokaż komunikat gdy brak aktywnego runa"""
        no_run_label = ctk.CTkLabel(
            self.main_frame,
            text="📭 Brak aktywnego runa\n\nUtwórz nowy run w zakładce History",
            font=("Arial", 18),
            text_color="gray"
        )
        no_run_label.pack(expand=True, pady=100)

    def display_run_info(self):
        """Wyświetl informacje o aktywnym runie"""
        # Rozpakuj dane runa
        run_id = self.active_run[0]
        name = self.active_run[1]
        start_date = self.active_run[2]
        initial_capital = self.active_run[4]
        current_capital = self.active_run[5]
        max_loss_pct = self.active_run[6]
        max_daily_loss_pct = self.active_run[7]

        # Obliczenia
        profit = current_capital - initial_capital
        profit_pct = (profit / initial_capital * 100) if initial_capital > 0 else 0

        # Stop loss ogólny
        max_loss_amount = initial_capital * (max_loss_pct / 100)
        current_loss = initial_capital - current_capital if current_capital < initial_capital else 0
        stop_loss_remaining = max_loss_amount - current_loss
        stop_loss_used_pct = (current_loss / max_loss_amount * 100) if max_loss_amount > 0 else 0

        # ===== NAGŁÓWEK =====
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header_frame,
            text=f"📊 {name}",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=15)

        date_label = ctk.CTkLabel(
            header_frame,
            text=f"Start: {start_date}",
            font=("Arial", 12),
            text_color="gray"
        )
        date_label.pack(pady=(0, 10))

        # ===== SEKCJA: KAPITAŁ =====
        capital_frame = ctk.CTkFrame(self.main_frame)
        capital_frame.pack(fill="x", pady=10)

        section_title = ctk.CTkLabel(
            capital_frame,
            text="💰 Kapitał",
            font=("Arial", 18, "bold")
        )
        section_title.pack(pady=(15, 10), anchor="w", padx=20)

        # Grid z danymi kapitału
        capital_grid = ctk.CTkFrame(capital_frame, fg_color="transparent")
        capital_grid.pack(fill="x", padx=20, pady=(0, 15))

        self.create_stat_row(capital_grid, "Początkowy:", f"{initial_capital:.2f}", 0)
        self.create_stat_row(capital_grid, "Aktualny:", f"{current_capital:.2f}", 1)

        profit_color = "green" if profit >= 0 else "red"
        self.create_stat_row(
            capital_grid,
            "Profit/Loss:",
            f"{profit:+.2f} ({profit_pct:+.1f}%)",
            2,
            value_color=profit_color
        )

        # ===== SEKCJA: STOP LOSSY =====
        stop_loss_frame = ctk.CTkFrame(self.main_frame)
        stop_loss_frame.pack(fill="x", pady=10)

        section_title2 = ctk.CTkLabel(
            stop_loss_frame,
            text="🛑 Stop Loss",
            font=("Arial", 18, "bold")
        )
        section_title2.pack(pady=(15, 10), anchor="w", padx=20)

        # Ogólny stop loss
        self.create_stop_loss_bar(
            stop_loss_frame,
            "Ogólny Stop Loss",
            stop_loss_used_pct,
            f"{stop_loss_remaining:.2f} pozostało z {max_loss_amount:.2f}"
        )

        # Dzienny stop loss (TODO: trzeba obliczyć na podstawie dzisiejszych trade'ów)
        self.create_stop_loss_bar(
            stop_loss_frame,
            "Dzienny Stop Loss",
            0,  # TODO: oblicz
            f"0.00 / {initial_capital * (max_daily_loss_pct / 100):.2f}"
        )

        # ===== SEKCJA: OTWARTE POZYCJE =====
        positions_frame = ctk.CTkFrame(self.main_frame)
        positions_frame.pack(fill="x", pady=10)

        section_title3 = ctk.CTkLabel(
            positions_frame,
            text="📈 Otwarte Pozycje",
            font=("Arial", 18, "bold")
        )
        section_title3.pack(pady=(15, 10), anchor="w", padx=20)

        self.display_open_positions(positions_frame)

        # ===== SEKCJA: HISTORIA TRADE'ÓW =====
        trades_frame = ctk.CTkFrame(self.main_frame)
        trades_frame.pack(fill="x", pady=10)

        section_title4 = ctk.CTkLabel(
            trades_frame,
            text="📜 Historia Trade'ów",
            font=("Arial", 18, "bold")
        )
        section_title4.pack(pady=(15, 10), anchor="w", padx=20)

        self.display_trade_history(trades_frame, run_id)

        # ===== PRZYCISKI AKCJI =====
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=20)

        stop_run_btn = ctk.CTkButton(
            actions_frame,
            text="⚠️ Zakończ Run",
            command=self.emergency_stop,
            fg_color="red",
            hover_color="darkred",
            width=200,
            height=40
        )
        stop_run_btn.pack(pady=10)

    def create_stat_row(self, parent, label, value, row, value_color=None):
        """Pomocnicza funkcja do tworzenia wiersza statystyk"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=3)

        label_widget = ctk.CTkLabel(
            row_frame,
            text=label,
            font=("Arial", 14),
            width=150,
            anchor="w"
        )
        label_widget.pack(side="left", padx=10)

        value_widget = ctk.CTkLabel(
            row_frame,
            text=value,
            font=("Arial", 14, "bold"),
            text_color=value_color if value_color else None
        )
        value_widget.pack(side="left", padx=10)

    def create_stop_loss_bar(self, parent, title, percentage, description):
        """Progress bar dla stop lossa"""
        bar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        bar_frame.pack(fill="x", padx=20, pady=10)

        # Tytuł
        title_label = ctk.CTkLabel(
            bar_frame,
            text=title,
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")

        # Progress bar
        progress = ctk.CTkProgressBar(bar_frame, width=400, height=20)
        progress.pack(pady=5)
        progress.set(percentage / 100)

        # Kolor w zależności od wypełnienia
        if percentage < 50:
            progress.configure(progress_color="green")
        elif percentage < 80:
            progress.configure(progress_color="orange")
        else:
            progress.configure(progress_color="red")

        # Opis
        desc_label = ctk.CTkLabel(
            bar_frame,
            text=description,
            font=("Arial", 11),
            text_color="gray"
        )
        desc_label.pack(anchor="w")

    def display_open_positions(self, parent):
        """Wyświetl otwarte pozycje z MT5"""
        if not self.app_manager.mt5_manager or not self.app_manager.mt5_manager.is_connected():
            no_connection = ctk.CTkLabel(
                parent,
                text="❌ Brak połączenia z MT5",
                text_color="red"
            )
            no_connection.pack(padx=20, pady=10)
            return

        positions = self.app_manager.mt5_manager.get_open_positions()

        if not positions or len(positions) == 0:
            no_positions = ctk.CTkLabel(
                parent,
                text="Brak otwartych pozycji",
                text_color="gray"
            )
            no_positions.pack(padx=20, pady=10)
            return

        # Nagłówki tabeli
        headers_frame = ctk.CTkFrame(parent, fg_color=("gray75", "gray30"))
        headers_frame.pack(fill="x", padx=20, pady=(0, 5))

        headers = ["Symbol", "Typ", "Volume", "Cena wejścia", "Aktualny P/L"]
        for header in headers:
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=("Arial", 12, "bold"),
                width=100
            )
            label.pack(side="left", padx=10, pady=5)

        # Pozycje
        for pos in positions:
            pos_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
            pos_frame.pack(fill="x", padx=20, pady=2)

            symbol = ctk.CTkLabel(pos_frame, text=pos.symbol, width=100)
            symbol.pack(side="left", padx=10, pady=5)

            pos_type = "BUY" if pos.type == 0 else "SELL"
            type_label = ctk.CTkLabel(pos_frame, text=pos_type, width=100)
            type_label.pack(side="left", padx=10, pady=5)

            volume = ctk.CTkLabel(pos_frame, text=f"{pos.volume:.2f}", width=100)
            volume.pack(side="left", padx=10, pady=5)

            price = ctk.CTkLabel(pos_frame, text=f"{pos.price_open:.5f}", width=100)
            price.pack(side="left", padx=10, pady=5)

            profit_color = "green" if pos.profit >= 0 else "red"
            profit = ctk.CTkLabel(
                pos_frame,
                text=f"{pos.profit:+.2f}",
                width=100,
                text_color=profit_color
            )
            profit.pack(side="left", padx=10, pady=5)

    def display_trade_history(self, parent, run_id):
        """Wyświetl historię trade'ów z bazy"""
        trades = self.app_manager.db.get_trades(run_id)

        if not trades or len(trades) == 0:
            no_trades = ctk.CTkLabel(
                parent,
                text="Brak zamkniętych trade'ów",
                text_color="gray"
            )
            no_trades.pack(padx=20, pady=10)
            return

        # Prosta lista trade'ów
        for trade in trades[-10:]:  # Ostatnie 10
            trade_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
            trade_frame.pack(fill="x", padx=20, pady=2)

            symbol = trade[2]
            trade_type = trade[3]
            profit = trade[9] if trade[9] else 0

            profit_color = "green" if profit >= 0 else "red"

            info_text = f"{symbol} | {trade_type} | P/L: {profit:+.2f}"
            label = ctk.CTkLabel(
                trade_frame,
                text=info_text,
                text_color=profit_color
            )
            label.pack(padx=10, pady=8)

    def refresh_data(self):
        """Ręczne odświeżenie (przycisk)"""
        if self.active_run:
            run_id = self.active_run[0]
            new_trades = self.app_manager.run_manager.sync_trades_from_mt5(run_id)
            self.load_current_run()
            print(f"🔄 Odświeżono ręcznie. Nowych trade'ów: {new_trades}")

    def emergency_stop(self):
        """Awaryjne zakończenie runa"""
        if not self.active_run:
            return

        result = messagebox.askyesno(
            "Potwierdzenie",
            "Czy na pewno chcesz zakończyć ten run?\nTa akcja jest nieodwracalna!"
        )

        if result:
            run_id = self.active_run[0]
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.app_manager.db.close_run(run_id, end_date, "stopped")

            messagebox.showinfo("Sukces", "Run został zakończony")
            self.load_current_run()

    def __del__(self):
        """Zatrzymaj auto-refresh przy usunięciu obiektu"""
        self.stop_auto_refresh()