from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic

from PyQt6.QtWebEngineWidgets import QWebEngineView
from math import ceil
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys
import os
from ui.rsc_rc import *
from run_draft_logic.utils import load_theme
from run_draft_logic.modes import *

from ui.pages.practice_draft import DraftWindow
from ui.pages.quick_draft import QuickDraftWindow
from ui.pages.heatmap import HeatMapWindow
from ui.pages.board import BoardWindow

from ui.dialogs.open_practice_draft import OpenPracticeDraft
from ui.misc.titlebar import*
from ui.dialogs.open_board import *
from ui.dialogs.hero_selector_tab import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.WINDOW_MAXED = True
        self.menu_width = 55

        self.title_bar = TitleBar(self)
        self.player1 = None
        self.player2 = None
     
        # Dialogs
        self.practice_dialog = OpenPracticeDraft()
        
        ui_path = os.path.join(script_dir,  "ui/pages/main_page.ui")

        uic.loadUi(ui_path, self)

        self.practice_button.clicked.connect(self.open_practice_dialog)
        self.quick_button.clicked.connect(self.open_quick_draft)
        self.heatmap_button.clicked.connect(self.open_heatmap)
        self.board_button.clicked.connect(self.open_board)
        
        self.practice_dialog.start_button.clicked.connect(self.open_practice_page)
        self.menu_button.clicked.connect(self.toggle_home_menu)
        
        self.dial = OpenPracticeDraft()
        self.ai_button.clicked.connect(self.test_dialog)
        

#############################################################       
        # MOVE WINDOW
        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if self.title_bar.returnStatus() == True:
                self.title_bar.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

            self.WINDOW_MAXED = False

        # SET TITLE BAR
        #-----------------
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        self.title_bar.uiDefinitions(self)
        self.showMaximized()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

#######################################################################
    def test_dialog(self):
        self.dial.show()

    def open_practice_dialog(self):
        self.practice_dialog.show()

    def open_practice_page(self):
        self.draft_window = DraftWindow()
        
        if self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_human()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 1:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_ai()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 1 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_human()
        else:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_ai()

        self.practice_dialog.close()
        if self.isMaximized():
            self.draft_window.showMaximized()
        else:
            self.draft_window.central_layout.setContentsMargins(10, 10, 10, 10)
            self.draft_window.drop_shadow.setStyleSheet(self.title_bar.shadow_style)
            self.draft_window.btn_max.setToolTip("Maximize")
            self.draft_window.show()
        #self.hide()

    def open_quick_draft(self):
        self.quick_draft = QuickDraftWindow()
        self.quick_draft.logo_btn.clicked.connect(self.test_dialog)
        if self.isMaximized():
            self.quick_draft.showMaximized()
        else:
            self.quick_draft.central_layout.setContentsMargins(10, 10, 10, 10)
            self.quick_draft.drop_shadow.setStyleSheet(self.title_bar.shadow_style)
            self.quick_draft.btn_max.setToolTip("Maximize")
            self.quick_draft.show()

    def open_heatmap(self):
        self.heatmap = HeatMapWindow()
        if self.isMaximized():
            self.heatmap.showMaximized()
        else:
            self.heatmap.central_layout.setContentsMargins(10, 10, 10, 10)
            self.heatmap.drop_shadow.setStyleSheet(self.title_bar.shadow_style)
            self.heatmap.btn_max.setToolTip("Maximize")
            self.heatmap.show()
    
    def open_board(self):
        board = BoardWindow()
        if self.isMaximized():
            board.showMaximized()
        else:
            board.central_layout.setContentsMargins(10, 10, 10, 10)
            board.drop_shadow.setStyleSheet(self.title_bar.shadow_style)
            board.btn_max.setToolTip("Maximize")
            board.show()
            board.show()

    def toggle_home_menu(self):
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