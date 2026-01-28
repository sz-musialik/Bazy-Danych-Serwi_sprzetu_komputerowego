import sys
import os

# Dodanie katalogu glownego do sciezki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from frontend.ui.login_window import LoginWindow
from frontend.ui.main_window import MainWindow


def show_main_window():
    global main_win
    main_win = MainWindow()
    main_win.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Najpierw pokazujemy logowanie.
    # Przekazujemy funkcje show_main_window jako callback po udanym logowaniu.
    login_win = LoginWindow(on_success_callback=show_main_window)
    login_win.show()

    sys.exit(app.exec())
