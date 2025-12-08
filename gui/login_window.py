import customtkinter as ctk

class LoginWindow:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.window = ctk.CTk()
        self.window.geometry("500x400")
        self.window.title("Trading Runs Manager - Login")

        self.is_first_run = self.app_manager.is_first_run()

        self.create_widgets()


    def create_widgets(self):
        if self.is_first_run:
            title = ctk.CTkLabel(self.window, text="Utwórz Master Password", font=("Arial", 20, "bold"))
            title.pack(pady=30)

            label1 = ctk.CTkLabel(self.window, text="Hasło:")
            label1.pack(pady=5)
            self.password_entry = ctk.CTkEntry(self.window, show="*", width=300)
            self.password_entry.pack(pady=5)

            label2 = ctk.CTkLabel(self.window, text="Powtórz hasło:")
            label2.pack(pady=5)
            self.password_entry_check = ctk.CTkEntry(self.window, show="*", width=300)
            self.password_entry_check.pack(pady=5)

            self.button = ctk.CTkButton(self.window, command=self.on_setup_click, text="Utwórz", width=200)
            self.button.pack(pady=20)
            self.error_label = ctk.CTkLabel(self.window, text="", text_color="red")
            self.error_label.pack(pady=10)

            self.password_entry.bind("<Return>", lambda event: self.on_setup_click())
            self.password_entry_check.bind("<Return>", lambda event: self.on_setup_click())
            self.password_entry.focus()


        else:
            self.label = ctk.CTkLabel(self.window, text="Podaj hasło:")
            self.label.pack(pady=20)
            self.password_entry = ctk.CTkEntry(self.window, show="*")
            self.password_entry.pack(pady=10)

            self.button = ctk.CTkButton(self.window, command=self.on_login_click, text="Zaloguj")
            self.button.pack(pady=10)
            self.error_label = ctk.CTkLabel(self.window, text="", text_color="red")
            self.error_label.pack(pady=10)
            self.password_entry.bind("<Return>", lambda event: self.on_login_click())
            self.password_entry.focus()

    def on_login_click(self):
        password = self.password_entry.get()

        if not password:
            self.show_error("❌ Hasło nie może być puste!")
            return

        if self.app_manager.authenticate(password):
            self.show_success("✅ Zalogowano pomyślnie!")
            self.window.after(500, self.window.destroy)
        else:
            self.show_error("❌ Błędne hasło!")

    def on_setup_click(self):
        password = self.password_entry.get()
        password_check = self.password_entry_check.get()

        if not password or not password_check:
            self.show_error("❌ Hasło nie może być puste!")
            return

        if password != password_check:
            self.show_error("❌ Hasła się nie zgadzają!")
            return



        self.app_manager.setup_master_password(password)
        self.show_success("✅ Master password utworzone!")
        self.window.after(500, self.window.destroy)

    def run(self):
        self.window.mainloop()

    def show_error(self, message):
        self.error_label.configure(text=message)

    def show_success(self, message):
        self.error_label.configure(text=message, text_color="green")
