import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from app import AppWindow

def main():
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()