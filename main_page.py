from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic

import sys
import os
from ui.rsc_rc import *
from run_draft_logic.utils import load_theme
from run_draft_logic.modes import human_vs_human, human_vs_ai, ai_vs_human, ai_vs_ai

from ui.pages.practice_draft import DraftWindow
from ui.pages.quick_draft import QuickDraftWindow
from ui.pages.heatmap import HeatMapWindow
from ui.pages.board import BoardWindow
#from ui.misc.titlebar import TitleBar

from ui.dialogs.open_practice_draft import OpenPracticeDraft
from ui.misc.titlebar import*

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #Load the theme
        theme_path = "ui/py_dracula_dark.qss"
        theme = load_theme(theme_path)
        self.setStyleSheet(theme)
        
        self.menu_width = 55

        self.player1 = None
        self.player2 = None

        self.practice_dialog = OpenPracticeDraft()
        ui_path = os.path.join(script_dir,  "ui/pages/main_page.ui")

        uic.loadUi(ui_path, self)

        self.practice_button.clicked.connect(self.open_practice_dialog)
        self.quick_button.clicked.connect(self.open_quick_draft)
        self.heatmap_button.clicked.connect(self.open_heatmap)
        self.board_button.clicked.connect(self.open_board)
        
        self.practice_dialog.start_button.clicked.connect(self.open_practice_page)
        self.menu_button.clicked.connect(self.toggle_menu)
        
        
        # MOVE WINDOW
        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if UIFunctions.returnStatus() == True:
                UIFunctions.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

        # SET TITLE BAR
        #-----------------
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)
        self.showMaximized()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()


#######################################################################

    def open_practice_dialog(self):
        self.practice_dialog.show()

    def open_practice_page(self):
        self.draft_window = DraftWindow(self)
        if self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_human()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 1:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_ai()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 1 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_human()
        else:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_ai()

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

    def toggle_menu(self):
        if self.menu_width == 55:
            self.menu_width = 150  # New width when menu is collapsed
        else:
            self.menu_width = 55  # Original width when menu is expanded

        self.left_menu_subcontainer.setFixedWidth(self.menu_width)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    #Apply the theme as a global stylesheet to the application
    window = MainWindow()
    #app.setStyle('Fusion')
    window.show()

    sys.exit(app.exec())