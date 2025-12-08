import customtkinter as ctk

class SettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.app_manager = parent.app_manager

        self.create_widgets()

    def create_widgets(self):
        max_loss_label = ctk.CTkLabel(
            self.parent.tabview.tab("Settings"),
            text="Ogólny Stop Loss (%)",
            font=("Arial", 16, "bold")
        )
        max_loss_label.pack(pady=(20, 5))

        self.max_loss_value_label = ctk.CTkLabel(
            self.parent.tabview.tab("Settings"),
            text=f"{self.app_manager.settings.get_setting('default_max_loss_percentage')}%"
        )
        self.max_loss_value_label.pack(pady=5)

        current_value = self.app_manager.settings.get_setting('default_max_loss_percentage')
        self.max_loss_slider = ctk.CTkSlider(
            self.parent.tabview.tab("Settings"),
            from_=0,
            to=100,
            command=self.max_loss_slider_event
        )
        self.max_loss_slider.set(current_value)
        self.max_loss_slider.pack(pady=10)


        daily_loss_label = ctk.CTkLabel(
            self.parent.tabview.tab("Settings"),
            text="Dzienny Stop Loss (%)",
            font=("Arial", 16, "bold")
        )
        daily_loss_label.pack(pady=(20, 5))

        self.max_daily_loss_value_label = ctk.CTkLabel(
            self.parent.tabview.tab("Settings"),
            text=f"{self.app_manager.settings.get_setting('default_max_daily_loss_percentage')}%"
        )
        self.max_daily_loss_value_label.pack(pady=5)

        current_daily_value = self.app_manager.settings.get_setting('default_max_daily_loss_percentage')
        self.max_daily_loss_slider = ctk.CTkSlider(
            self.parent.tabview.tab("Settings"),
            from_=0,
            to=100,
            command=self.max_daily_loss_slider_event
        )
        self.max_daily_loss_slider.set(current_daily_value)
        self.max_daily_loss_slider.pack(pady=10)

    def max_loss_slider_event(self, value):
        value = int(value)
        self.app_manager.settings.set_setting('default_max_loss_percentage', value)
        self.max_loss_value_label.configure(text=f"{value}%")

    def max_daily_loss_slider_event(self, value):
        value = int(value)
        self.app_manager.settings.set_setting('default_max_daily_loss_percentage', value)
        self.max_daily_loss_value_label.configure(text=f"{value}%")