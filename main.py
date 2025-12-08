from managers.app_manager import AppManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

# Inicjalizuj AppManager
app_manager = AppManager()

# Pokaż okno logowania
login_window = LoginWindow(app_manager)
login_window.run()

# Po zamknięciu okna logowania:
# W main.py po zalogowaniu (tymczasowo):
if app_manager.is_authenticated:
    # Dodaj testowego runa jeśli baza pusta
    runs = app_manager.db.get_runs()
    if len(runs) == 0:
        from datetime import datetime

        app_manager.db.create_run(
            "Test Run #1",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1000,
            50,
            25,
            mt5_account_id=1
        )

    main_window = MainWindow(app_manager)
    main_window.run()