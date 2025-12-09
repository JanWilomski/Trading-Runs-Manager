from gui.current_run_tab import CurrentRunTab
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab
from gui.current_run_tab import CurrentRunTab
import customtkinter as ctk

class MainWindow:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.window = ctk.CTk()
        self.window.geometry("1200x700")
        self.window.title("Trading Runs Manager")

        self.create_widgets()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Dashboard
        self.tabview.add("Dashboard")
        dashboard_label = ctk.CTkLabel(self.tabview.tab("Dashboard"),
                                       text="Dashboard - TODO",
                                       font=("Arial", 20))
        dashboard_label.pack(pady=20)

        # Current Run
        self.tabview.add("Current Run")
        self.current_run_tab = CurrentRunTab(self)

        # History
        self.tabview.add("History")
        self.history_tab=HistoryTab(self)

        # Settings
        self.tabview.add("Settings")
        self.settings_tab = SettingsTab(self)

    def run(self):
        self.window.mainloop()