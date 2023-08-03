from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
import sys
import os
from ui.rsc_rc import *
from run_draft_logic.modes import human_vs_human, human_vs_ai, ai_vs_human, ai_vs_ai

from ui.pages.practice_draft import DraftWindow
from ui.pages.quick_draft import QuickDraftWindow
from ui.pages.heatmap import HeatMapWindow
from ui.pages.board import BoardWindow

from ui.dialogs.open_practice_draft import OpenPracticeDraft

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.practice_dialog = OpenPracticeDraft()

        ui_path = os.path.join(script_dir,  "ui/pages/main_page.ui")

        uic.loadUi(ui_path, self)

        self.practice_button.clicked.connect(self.open_practice_dialog)
        self.quick_button.clicked.connect(self.open_quick_draft)
        self.heatmap_button.clicked.connect(self.open_heatmap)
        self.board_button.clicked.connect(self.open_board)
        
        self.practice_dialog.start_button.clicked.connect(self.open_practice_page)
        self.showMaximized()

    def open_practice_dialog(self):
        self.practice_dialog.show()

    def open_practice_page(self):
        self.draft_window = DraftWindow(self)
        self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_human()
        self.practice_dialog.close()
        self.draft_window.show()
        #self.hide()

    def open_quick_draft(self):
        self.quick_draft = QuickDraftWindow(self)
        #self.hide()
        self.quick_draft.show()


    def open_heatmap(self):
        self.heatmap = HeatMapWindow()
        self.heatmap.show()
    
    def open_board(self):
        self.board = BoardWindow()
        self.board.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())