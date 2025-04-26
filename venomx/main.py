import sys, os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QIcon
from app import AppWindow

def main():
    app = QApplication(sys.argv)
    icon_path = os.path.join("assets", "VenomX X Logo.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = AppWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()