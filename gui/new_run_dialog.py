import customtkinter as ctk
from tkinter import messagebox


class NewRunDialog:
    def __init__(self, parent, app_manager):
        self.app_manager = app_manager

        # Okno dialogowe
        self.window = ctk.CTkToplevel(parent)
        self.window.geometry("500x650")
        self.window.title("➕ Nowy Run")
        self.window.grab_set()  # Modal - blokuje główne okno

        self.create_widgets()

    def create_widgets(self):
        # Tytuł
        title = ctk.CTkLabel(
            self.window,
            text="Utwórz nowy Run",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Frame główny
        form_frame = ctk.CTkFrame(self.window)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # ===== SEKCJA: INFORMACJE O RUNIE =====
        section_label = ctk.CTkLabel(
            form_frame,
            text="📊 Informacje o Runie",
            font=("Arial", 16, "bold")
        )
        section_label.pack(pady=(20, 10), anchor="w", padx=20)

        # Nazwa runa
        self.create_field(form_frame, "Nazwa runa:", "run_name_entry", "Run")

        # Kapitał początkowy
        self.create_field(form_frame, "Kapitał początkowy:", "initial_capital_entry", "1000")

        # Max Loss %
        default_max_loss = self.app_manager.settings.get_setting('default_max_loss_percentage')
        self.create_field(form_frame, "Ogólny Stop Loss (%):", "max_loss_entry", str(default_max_loss))

        # Max Daily Loss %
        default_daily_loss = self.app_manager.settings.get_setting('default_max_daily_loss_percentage')
        self.create_field(form_frame, "Dzienny Stop Loss (%):", "max_daily_loss_entry", str(default_daily_loss))

        # ===== SEKCJA: KONTO MT5 =====
        section_label2 = ctk.CTkLabel(
            form_frame,
            text="🔌 Dane konta MT5",
            font=("Arial", 16, "bold")
        )
        section_label2.pack(pady=(20, 10), anchor="w", padx=20)

        # MT5 Login
        self.create_field(form_frame, "Login MT5:", "mt5_login_entry")

        # MT5 Password
        self.create_field(form_frame, "Hasło MT5:", "mt5_password_entry", password=True)

        # MT5 Server
        self.create_field(form_frame, "Serwer MT5:", "mt5_server_entry", "FusionMarkets-Live")

        # ===== PRZYCISKI =====
        buttons_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        buttons_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Anuluj",
            command=self.window.destroy,
            width=150,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=10)

        create_btn = ctk.CTkButton(
            buttons_frame,
            text="Utwórz Run",
            command=self.create_run,
            width=150
        )
        create_btn.pack(side="left", padx=10)

    def create_field(self, parent, label_text, entry_name, default_value="", password=False):
        """Pomocnicza metoda do tworzenia pola formularza"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=20, pady=5)

        label = ctk.CTkLabel(field_frame, text=label_text, width=200, anchor="w")
        label.pack(side="left", padx=5)

        entry = ctk.CTkEntry(
            field_frame,
            width=250,
            show="*" if password else ""
        )
        entry.pack(side="left", padx=5)

        if default_value:
            entry.insert(0, default_value)

        # Zapisz referencję do entry
        setattr(self, entry_name, entry)

    def create_run(self):
        """Walidacja i utworzenie runa"""
        # Pobierz wartości z pól
        run_name = self.run_name_entry.get().strip()
        initial_capital = self.initial_capital_entry.get().strip()
        max_loss = self.max_loss_entry.get().strip()
        max_daily_loss = self.max_daily_loss_entry.get().strip()
        mt5_login = self.mt5_login_entry.get().strip()
        mt5_password = self.mt5_password_entry.get()
        mt5_server = self.mt5_server_entry.get().strip()

        # Walidacja
        if not run_name:
            messagebox.showerror("Błąd", "Podaj nazwę runa!")
            return

        try:
            initial_capital = float(initial_capital)
            max_loss = float(max_loss)
            max_daily_loss = float(max_daily_loss)
            mt5_login = int(mt5_login)
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe wartości liczbowe!")
            return

        if not mt5_password or not mt5_server:
            messagebox.showerror("Błąd", "Wypełnij wszystkie dane MT5!")
            return

        # Utwórz run
        try:
            success = self.app_manager.run_manager.create_run_with_account(
                run_name=run_name,
                initial_capital=initial_capital,
                max_loss_pct=max_loss,
                max_daily_loss_pct=max_daily_loss,
                mt5_login=mt5_login,
                mt5_password=mt5_password,
                mt5_server=mt5_server
            )

            if success:
                messagebox.showinfo("Sukces", f"✅ Run '{run_name}' został utworzony!")
                self.window.destroy()
            else:
                messagebox.showerror("Błąd", "Nie udało się połączyć z MT5. Sprawdź dane logowania.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")