import customtkinter as ctk
from tkinter import messagebox

from database import initialize_database
from ui.dashboard import Dashboard


# =========================================================
# APPLICATION SETTINGS
# =========================================================

APP_NAME = "Financial Shop Software"
APP_VERSION = "1.0.0"


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    try:
        # ---------------------------------------------
        # CUSTOMTKINTER SETTINGS
        # ---------------------------------------------

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ---------------------------------------------
        # INITIALIZE DATABASE
        # ---------------------------------------------

        initialize_database()

        # ---------------------------------------------
        # START DASHBOARD
        # ---------------------------------------------

        app = Dashboard()

        app.title(
            f"{APP_NAME} v{APP_VERSION}"
        )

        # Center window on screen
        center_window(
            app,
            width=1300,
            height=750
        )

        app.mainloop()

    except Exception as error:

        try:
            messagebox.showerror(
                "Application Error",
                f"Software চালু করা যায়নি।\n\n{error}"
            )

        except Exception:
            print(
                "Application Error:",
                error
            )


# =========================================================
# CENTER WINDOW
# =========================================================

def center_window(
        window,
        width,
        height
):

    window.update_idletasks()

    screen_width = (
        window.winfo_screenwidth()
    )

    screen_height = (
        window.winfo_screenheight()
    )

    x = (
        screen_width - width
    ) // 2

    y = (
        screen_height - height
    ) // 2

    # Prevent negative position
    x = max(x, 0)
    y = max(y, 0)

    window.geometry(
        f"{width}x{height}+{x}+{y}"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    main()