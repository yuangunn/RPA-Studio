import sys
from PyQt6.QtWidgets import QApplication
from rpa_studio.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RPA Studio")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
