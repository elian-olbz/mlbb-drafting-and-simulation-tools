from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
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
from ui.dialogs.board_selector import OpenBoardSelector
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
        self.board_selector_dialog = OpenBoardSelector()
        
        ui_path = os.path.join(script_dir,  "main_page.ui")

        uic.loadUi(ui_path, self)

        self.draft_window = None
        self.quick_draft = None
        self.heatmap = None
        self.board = None

        self.practice_button.clicked.connect(self.open_practice_dialog)
        self.quick_button.clicked.connect(self.open_quick_draft)
        self.heatmap_button.clicked.connect(self.open_heatmap)
        self.board_button.clicked.connect(self.open_board_selector)
        
        self.practice_dialog.start_button.clicked.connect(self.open_practice_page)
        self.board_selector_dialog.create_btn.clicked.connect(self.open_board)
        self.menu_button.clicked.connect(self.toggle_home_menu)

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
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        self.title_bar.uiDefinitions(self)
        self.showMaximized()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

#######################################################################
    
    # Dialog for setting up parameters(player type, intelligence) before opening the practice draft window
    def open_practice_dialog(self):
        self.practice_dialog.show()

    # Dialog for selecting what type of board to create
    def open_board_selector(self):
        self.board_selector_dialog.show()

#########################################################################
    # Initialize and open practice draft window
    def open_practice_page(self):
        self.draft_window = DraftWindow()
        self.draft_window.home_btn.clicked.connect(self.close_practice_draft)
        
        # set the player types from the combo box index/value
        if self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_human()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 0 and self.practice_dialog.red_combo_box.currentIndex() == 1:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_ai()
        elif self.practice_dialog.blue_combo_box.currentIndex() == 1 and self.practice_dialog.red_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_human()
        else:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_ai()

        self.practice_dialog.close()
        self.draft_window.showMaximized()
        self.hide()

    def close_practice_draft(self):
        self.draft_window.close()
        self.show()

########################################################################
    # Initialize and open quick draft window
    def open_quick_draft(self):
        self.quick_draft = QuickDraftWindow()
        self.quick_draft.home_btn.clicked.connect(self.close_quick_draft)
        self.quick_draft.showMaximized()
        self.hide()

    def close_quick_draft(self):
        self.quick_draft.close()
        self.show()

########################################################################
    # Initialize and open heatmap window
    def open_heatmap(self):
        self.heatmap = HeatMapWindow()
        self.heatmap.home_btn.clicked.connect(self.close_heatmap)
        self.heatmap.showMaximized()
        self.hide()

    def close_heatmap(self):
        self.heatmap.close()
        self.show()
#########################################################################
    # Initialize and open coaching board window
    def open_board(self):
        self.board = BoardWindow()
        self.board.home_btn.clicked.connect(self.close_board)
        self.board_selector_dialog.close()
        self.board.showMaximized()
        self.hide()
            
    def close_board(self):
        self.board.close()
        self.show()
##########################################################################

    # Toggle the side menu
    def toggle_home_menu(self):
        if self.menu_width == 55:
            self.menu_width = 150  # New width when menu is collapsed
        else:
            self.menu_width = 55  # Original width when menu is expanded

        self.left_menu_subcontainer.setFixedWidth(self.menu_width)
