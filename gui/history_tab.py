import customtkinter as ctk

from gui.new_run_dialog import NewRunDialog


class HistoryTab:
    def __init__(self, parent):
        self.parent = parent
        self.app_manager = parent.app_manager

        self.create_widgets()

    def create_widgets(self):
        new_run_btn = ctk.CTkButton(
            self.parent.tabview.tab("History"),
            text="➕ Nowy Run",
            command=self.create_new_run,
            height=40
        )
        new_run_btn.pack(pady=20, padx=20, anchor="ne")

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.parent.tabview.tab("History"),
            label_text="Historia Runów"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_runs()



    def create_new_run(self):
        pass

    def load_runs(self):
        runs = self.app_manager.db.get_runs()

        if not runs:
            no_runs_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Brak runów. Kliknij '➕ Nowy Run' aby utworzyć pierwszy run.",
                font=("Arial", 14),
                text_color="gray"
            )
            no_runs_label.pack(pady=50)
            return

        for run in runs:
            run_id = run[0]
            name = run[1]
            start_date = run[2]
            end_date = run[3]
            initial_capital = run[4]
            current_capital = run[5]
            max_loss = run[6]
            max_daily_loss = run[7]
            status = run[8]

            # Oblicz profit
            profit = current_capital - initial_capital
            profit_pct = (profit / initial_capital) * 100 if initial_capital > 0 else 0

            # Główny frame runa
            run_frame = ctk.CTkFrame(
                self.scrollable_frame,
                cursor="hand2",
                fg_color=("gray90", "gray20")  # Domyślny kolor
            )
            run_frame.pack(fill="x", padx=10, pady=8)

            # ==== SEKCJA NAGŁÓWEK ====
            header_frame = ctk.CTkFrame(run_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(10, 5))

            # Nazwa i status
            name_label = ctk.CTkLabel(
                header_frame,
                text=f"📊 {name}",
                font=("Arial", 16, "bold"),
                anchor="w"
            )
            name_label.pack(side="left")

            # Status badge
            status_colors = {
                "active": "green",
                "completed": "blue",
                "stopped": "red"
            }
            status_badge = ctk.CTkLabel(
                header_frame,
                text=status.upper(),
                font=("Arial", 11, "bold"),
                text_color="white",
                fg_color=status_colors.get(status, "gray"),
                corner_radius=5,
                padx=10,
                pady=3
            )
            status_badge.pack(side="right", padx=5)

            # ==== SEKCJA STATYSTYKI ====
            stats_frame = ctk.CTkFrame(run_frame, fg_color="transparent")
            stats_frame.pack(fill="x", padx=15, pady=5)

            # Kolumna 1: Daty
            dates_text = f"🗓️ Start: {start_date[:10]}"
            if end_date:
                dates_text += f" | End: {end_date[:10]}"
            dates_label = ctk.CTkLabel(
                stats_frame,
                text=dates_text,
                font=("Arial", 12),
                anchor="w"
            )
            dates_label.pack(anchor="w")

            # Kolumna 2: Kapitał
            profit_color = "green" if profit >= 0 else "red"
            capital_text = f"💰 Kapitał: {initial_capital:.0f} → {current_capital:.0f} ({profit:+.0f} | {profit_pct:+.1f}%)"
            capital_label = ctk.CTkLabel(
                stats_frame,
                text=capital_text,
                font=("Arial", 12),
                text_color=profit_color,
                anchor="w"
            )
            capital_label.pack(anchor="w", pady=2)

            # Kolumna 3: Stop lossy
            stops_text = f"🛑 Stop Loss: Ogólny {max_loss}% | Dzienny {max_daily_loss}%"
            stops_label = ctk.CTkLabel(
                stats_frame,
                text=stops_text,
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            )
            stops_label.pack(anchor="w")

            # ==== HOVER EFFECTS ====
            def on_enter(event, frame=run_frame):
                frame.configure(fg_color=("gray80", "gray25"))  # Jaśniejszy przy hover

            def on_leave(event, frame=run_frame):
                frame.configure(fg_color=("gray90", "gray20"))  # Powrót do normalnego

            # Bind hover na frame i wszystkie dzieci
            run_frame.bind("<Enter>", on_enter)
            run_frame.bind("<Leave>", on_leave)
            for widget in [header_frame, name_label, status_badge, stats_frame, dates_label, capital_label,
                           stops_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

            # ==== KLIK ====
            def make_clickable(widget, r_id):
                widget.bind("<Button-1>", lambda event: self.show_run_details(r_id))

            for widget in [run_frame, header_frame, name_label, status_badge, stats_frame, dates_label, capital_label,
                           stops_label]:
                make_clickable(widget, run_id)

    def show_run_details(self, run_id):
        pass

    def create_new_run(self):
        NewRunDialog(self.parent.window, self.app_manager)