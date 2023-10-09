from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
import sys
import os
import random
from ui.rsc_rc import *
from run_draft_logic.utils import load_theme
from run_draft_logic.modes import *

from ui.pages.practice_draft import DraftWindow
from ui.pages.quick_draft import QuickDraftWindow
from ui.pages.heatmap import HeatMapWindow
from ui.pages.hmap_viewer import HeatmapViewerWindow

from ui.dialogs.open_practice_draft import OpenPracticeDraft
from ui.misc.titlebar import*
from ui.dialogs.hero_selector_tab import *
from ui.dialogs.exit_page import *

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
        self.exit_page_dialog = ExitDialog()

        self.exit_page_dialog.cancel_btn.clicked.connect(self.close_exit_dialog)
        
        ui_path = os.path.join(script_dir,  "main_page.ui")

        uic.loadUi(ui_path, self)

        self.draft_window = None
        self.quick_draft = None
        self.heatmap = None
        self.hmap_viewer = None

        # Connect the mousePressEvent events of the existing widgets to custom functions
        self.practice_widget.mousePressEvent = self.create_mousePressEvent(self.show_practice_dialog)
        self.quick_widget.mousePressEvent = self.create_mousePressEvent(self.open_quick_draft)
        self.tracker_widget.mousePressEvent = self.create_mousePressEvent(self.open_heatmap)
        self.hmap_viewer_widget.mousePressEvent = self.create_mousePressEvent(self.open_hmap_viewer)
        
        self.practice_dialog.start_button.clicked.connect(self.open_practice_page)

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

    def create_mousePressEvent(self, custom_function):
        # Create a new method that will call the custom function on mouse press event
        def mousePressEvent(event):
            if event.button() == Qt.MouseButton.LeftButton:
                custom_function()
        return mousePressEvent

#######################################################################
    
    # Dialog for setting up parameters(player type, intelligence) before opening the practice draft window
    def show_practice_dialog(self):
        self.practice_dialog.show()
    
    def show_exit_dialog(self):
        self.exit_page_dialog.show()

    def close_exit_dialog(self):
        self.exit_page_dialog.close()

#########################################################################
    # Initialize and open practice draft window
    def open_practice_page(self):
        self.draft_window = DraftWindow()
        self.draft_window.home_btn.clicked.connect(self.show_exit_dialog)
        self.exit_page_dialog.okay_btn.clicked.connect(self.close_practice_draft)
        
        # set the player types from the combo box index/value
        if self.practice_dialog.mode_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_human()
        elif self.practice_dialog.mode_combo_box.currentIndex() == 1 and self.practice_dialog.side_combo_box.currentIndex() == 0:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = human_vs_ai()
            self.draft_window.undo_button.setEnabled(False)
            self.draft_window.undo_button.setVisible(False)
            self.draft_window.draft_state.ai_level = self.practice_dialog.ai_slider.value()
        elif self.practice_dialog.mode_combo_box.currentIndex() == 1 and self.practice_dialog.side_combo_box.currentIndex() == 1:
            self.draft_window.blue_player, self.draft_window.red_player, self.draft_window.mode = ai_vs_human()
            self.draft_window.undo_button.setEnabled(False)
            self.draft_window.undo_button.setVisible(False)
            self.draft_window.draft_state.ai_level = self.practice_dialog.ai_slider.value()
            
        self.practice_dialog.close()
        self.draft_window.showMaximized()
        self.hide()

    def close_practice_draft(self):
        self.close_exit_dialog()
        self.draft_window.close()
        self.draft_window.stop_ai_thread()
        self.show()

########################################################################
    # Initialize and open quick draft window
    def open_quick_draft(self):
        self.quick_draft = QuickDraftWindow()
        self.quick_draft.home_btn.clicked.connect(self.show_exit_dialog)
        self.exit_page_dialog.okay_btn.clicked.connect(self.close_quick_draft)
        self.quick_draft.showMaximized()
        self.hide()

    def close_quick_draft(self):
        self.quick_draft.close()
        self.close_exit_dialog()
        self.show()

########################################################################
    # Initialize and open heatmap window
    def open_heatmap(self):
        self.heatmap = HeatMapWindow()
        self.heatmap.home_btn.clicked.connect(self.show_exit_dialog)
        self.exit_page_dialog.okay_btn.clicked.connect(self.close_heatmap)
        opened = self.heatmap.open_video_file()
        if opened:
            self.heatmap.showMaximized()
            self.hide()
        else:
            return

    def close_heatmap(self):
        self.heatmap.close()
        self.close_exit_dialog()
        self.show()
#########################################################################
    # Initialize and open heatmap viewer window
    def open_hmap_viewer(self):
        self.hmap_viewer = HeatmapViewerWindow()
        self.hmap_viewer.home_btn.clicked.connect(self.show_exit_dialog)
        self.exit_page_dialog.okay_btn.clicked.connect(self.close_hmap_viewer)
        self.hmap_viewer.showMaximized()
        self.hide()
            
    def close_hmap_viewer(self):
        self.hmap_viewer.close()
        self.close_exit_dialog()
        self.show()
##########################################################################