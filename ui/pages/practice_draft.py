from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from run_draft_logic.draft_state import DraftState
from run_draft_logic.hero_selector import *
from ui.misc.titlebar import*


from run_draft_logic.utils import print_draft_status, print_final_draft, rounded_pixmap, get_icon, get_image, get_name, load_theme

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class AutoPlayer(QObject):
    auto_player_signal = pyqtSignal()

    def start(self):
        # Emit the signal to trigger the AI predictions and UI updates
        self.auto_player_signal.emit()

class DraftWindow(QMainWindow):
    def __init__(self):
        super(DraftWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.hero_selector = HeroSelector(self)
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir,  "practice_draft.ui")

        uic.loadUi(ui_path, self)

        self.draft_state = DraftState('data/hero_roles.csv')
        self.blue_player = None
        self.red_player = None
        self.mode = None

        self.hero_selector.hero_roles = self.draft_state.hero_roles
        self.hero_selector.hero_names = self.draft_state.hero_names
        self.hero_selector.hero_icons = self.draft_state.hero_icons
        self.hero_selector.hero_types = self.draft_state.hero_types

        self.hero_selector.populate_tabs(self)
        # Connect the pick_button click signal to display_clicked_image with the last stored hero_id
        self.pick_button.clicked.connect(self.on_button_click)

        # Connect the currentChanged signal of hero_tab to update_current_tab method
        self.hero_tab.currentChanged.connect(self.hero_selector.update_current_tab)

        self.auto_player = AutoPlayer()
        self.auto_player.auto_player_signal.connect(self.auto_player_pick_or_ban)
        # Start the automatic AI predictions and UI updates by calling the start method
        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.emit_auto_player_signal)

        # Create a QShortcut that triggers the button click event on "Enter" key press
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        shortcut.activated.connect(self.pick_button.click)

        self.auto_player.start()

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

        # SET TITLE BAR
        #-----------------
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        self.title_bar.uiDefinitions(self)
        #self.showMaximized()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

#######################################################################
            
    def emit_auto_player_signal(self):
        # Trigger the AI move after the delay
        if self.mode == 'HvH':
            pass
        elif self.mode == 'HvA':
            if abs(self.hero_selector.remaining_clicks - 20) not in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
        elif self.mode == 'AvH':
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
        elif self.mode == 'AvA':
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn or abs(self.hero_selector.remaining_clicks - 20) not in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()

    def on_button_click(self):
        self.pick_button_clicked = True

        if self.hero_selector.remaining_clicks <= 0 or self.hero_selector.selected_id is None:
            return
        if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.pick_indices:
            self.pick_or_ban(self.draft_state, self.hero_selector.selected_id, self.mode, True)
        else:
            self.pick_or_ban(self.draft_state, self.hero_selector.selected_id, self.mode, False)
        
        # Set the desired delay time (in milliseconds) before emitting the signal
        delay_milliseconds = 1000  # Adjust the delay time as needed
        self.delay_timer.start(delay_milliseconds)

        if self.hero_selector.current_clicked_label is not None:
            self.hero_selector.current_clicked_label.setStyleSheet("")
            self.hero_selector.current_clicked_label = None

    def auto_player_pick_or_ban(self):
        if self.hero_selector.remaining_clicks <= 0:
            return
        if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.pick_indices:
            self.pick_or_ban(self.draft_state, self.hero_selector.selected_id, self.mode, True)
        else:
            self.pick_or_ban(self.draft_state, self.hero_selector.selected_id, self.mode, False)

        # Set the desired delay time (in milliseconds) before emitting the signal
        delay_milliseconds = 1000  # Adjust the delay time as needed
        self.delay_timer.start(delay_milliseconds)


    def human_move(self, draft_state, selected_id, mode, is_pick):
        if mode == "HvA":
            if is_pick:
                self.blue_player.pick(draft_state, selected_id)
            else:
                self.blue_player.ban(draft_state, selected_id)
            self.hero_selector.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None

        elif mode == 'AvH':
            if is_pick:
                self.red_player.pick(draft_state, selected_id)
            else:
                self.red_player.ban(draft_state, selected_id)
            self.hero_selector.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None
        else:
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn:
                if is_pick:
                    self.blue_player.pick(draft_state, selected_id)
                else:
                    self.blue_player.ban(draft_state, selected_id)
            else:
                if is_pick:
                    self.red_player.pick(draft_state, selected_id)
                else:
                    self.red_player.ban(draft_state, selected_id)
            self.hero_selector.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None


    def ai_move(self, draft_state, mode, is_pick):
        if mode == 'AvH':
            if is_pick:
                self.hero_selector.hero_to_disp = self.blue_player.pick(draft_state)
            else:
                self.hero_selector.hero_to_disp = self.blue_player.ban(draft_state)
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None
        elif mode == 'HvA':
            if is_pick:
                self.hero_selector.hero_to_disp = self.red_player.pick(draft_state)
            else:
                self.hero_selector.hero_to_disp = self.red_player.ban(draft_state)
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None

        elif mode == 'AvA':
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn:
                if is_pick:
                    self.hero_selector.hero_to_disp = self.blue_player.pick(draft_state)
                else:
                    self.hero_selector.hero_to_disp = self.blue_player.ban(draft_state)
            else:
                if is_pick:
                    self.hero_selector.hero_to_disp = self.red_player.pick(draft_state)
                else:
                    self.hero_selector.hero_to_disp = self.red_player.ban(draft_state)
            print_draft_status(draft_state)
            self.hero_selector.display_clicked_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.hero_to_disp = None


            
    def pick_or_ban(self, draft_state, selected_id, mode, is_pick):

        if mode is not None and mode == 'HvH': # Human vs Human
            # blue player is human
            self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'HvA': # HUman vs Ai
            # blue player is human
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn:
                self.human_move(draft_state, selected_id, mode, is_pick)

            else:  # red player is AI
                self.ai_move(draft_state, mode, is_pick)

        elif mode is not None and mode == 'AvH':
            # blue player is AI
            if abs(self.hero_selector.remaining_clicks - 20) in self.hero_selector.blue_turn:
                self.ai_move(draft_state, mode, is_pick)

            else:  # red player is Human
                self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'AvA':
            self.ai_move(draft_state, mode, is_pick)
