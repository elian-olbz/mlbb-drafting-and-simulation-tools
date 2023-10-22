import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.pages.main_page import MainWindow
from ui.misc import error_handler

if __name__ == "__main__":
    sys.excepthook = error_handler.excepthook
    app = QApplication(sys.argv)
    window = MainWindow()
    ICON = QIcon('icons/icon.png')
    window.setWindowIcon(ICON)

    window.show()

    sys.exit(app.exec())