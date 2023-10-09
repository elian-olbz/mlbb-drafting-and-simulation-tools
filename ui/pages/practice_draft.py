from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from run_draft_logic.draft_state import DraftState
from run_draft_logic.setup_selector import *
from run_draft_logic.utils import get_curr_index
from ui.misc.titlebar import*
from ui.dialogs.reset_heroes import*


from run_draft_logic.utils import print_draft_status, print_final_draft, rounded_pixmap, get_icon, get_image, get_name, load_theme, get_curr_index

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class AIThread(QThread):
    def __init__(self, parent, draft_state, mode, is_pick):
        super(AIThread, self).__init__(parent)
        self.draft_state = draft_state
        self.mode = mode
        self.is_pick = is_pick

    def run(self):
        # Call the ai_move() function here
        self.parent().ai_move(self.draft_state, self.mode, self.is_pick)

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
        self.title_bar = TitleBar(self)
        self.delay = 2000

        ui_path = os.path.join(script_dir,  "practice_draft.ui")

        uic.loadUi(ui_path, self)

        self.draft_state = DraftState('data/hero_roles.csv')
        self.blue_player = None
        self.red_player = None
        self.mode = None
        self.hero_selector = SetupHeroSelector(self)
        self.reset_dialog = ResetDialog()

        self.hero_selector.hero_roles = self.draft_state.hero_roles
        self.hero_selector.hero_names = self.draft_state.hero_names
        self.hero_selector.hero_icons = self.draft_state.hero_icons
        self.hero_selector.hero_types = self.draft_state.hero_types

        self.qlabel_list = [self.blue_ban1, self.red_ban5, self.blue_ban2, self.red_ban4,
                        self.blue_ban3, self.red_ban3, self.blue_pick1, self.red_pick1,
                        self.red_pick2, self.blue_pick2, self.blue_pick3, self.red_pick3,
                        self.red_ban2, self.blue_ban4, self.red_ban1, self.blue_ban5,
                        self.red_pick4, self.blue_pick4, self.blue_pick5, self.red_pick5]

        self.hero_selector.populate_tabs(self, 90)
        # Connect the pick_button click signal to disp_selected_image with the last stored hero_id
        self.pick_button.clicked.connect(self.filter_btn_click)
        self.undo_button.clicked.connect(self.undo_move)

        self.reset_btn.clicked.connect(self.show_reset_dialog)
        self.reset_dialog.okay_btn.clicked.connect(self.reset_all)
        self.reset_dialog.cancel_btn.clicked.connect(self.close_reset_dialog)

        # Connect the currentChanged signal of hero_tab to update_current_tab method
        self.hero_tab.currentChanged.connect(self.hero_selector.update_current_tab)

        self.auto_player = AutoPlayer()
        self.auto_player.auto_player_signal.connect(self.auto_player_next_move)
        # Start the automatic AI predictions and UI updates by calling the start method
        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.emit_auto_player_signal)

        # Create a QShortcut that triggers the button click event on "Enter" key press
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut.activated.connect(self.pick_button.click)

        undo_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Z), self)
        undo_shortcut.activated.connect(self.undo_button.click)

        reset_shortcut = QShortcut(QKeySequence(Qt.Key.Key_R), self)
        reset_shortcut.activated.connect(self.reset_btn.click)

        self.ai_thread = None

        self.auto_player.start()
        self.highlight_next_qlabel()

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

    def resizeEvent(self, event):
        self.hero_selector.update_current_tab(self.hero_tab.currentIndex)

    def stop_ai_thread(self):
        if self.ai_thread is not None and self.ai_thread.isRunning():
            self.ai_thread.quit()
            self.ai_thread.wait()

    def closeEvent(self, event):
        # Stop and quit the thread when the window is closed
        self.stop_ai_thread()
        self.delay_timer.stop()
        event.accept()

#######################################################################

    def show_reset_dialog(self):
        if len(self.draft_state.draft_sequence) > 0:
            self.delay_timer.stop()
            self.reset_dialog.show()
        else:
            return
    def close_reset_dialog(self):
        self.reset_dialog.close()
            
    def emit_auto_player_signal(self):
        # Trigger the AI move after the delay
        if self.ai_thread is not None and self.ai_thread.isRunning():
            return
        if self.mode == 'HvH':
            pass
        elif self.mode == 'HvA':
            if get_curr_index(self.hero_selector.remaining_clicks) not in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
                if self.ai_thread is not None:
                    self.ai_thread.start()
        elif self.mode == 'AvH':
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
                if self.ai_thread is not None:
                    self.ai_thread.start()
        elif self.mode == 'AvA':
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn or get_curr_index(self.hero_selector.remaining_clicks) not in self.hero_selector.blue_turn and self.hero_selector.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
                if self.ai_thread is not None:
                    self.ai_thread.start()

    def filter_btn_click(self):
        index = get_curr_index(self.hero_selector.remaining_clicks)
        if self.mode == "HvA" and index in self.hero_selector.blue_turn:
            self.on_button_click()
        elif self.mode == "AvH" and index not in self.hero_selector.blue_turn:
            self.on_button_click()
        elif self.mode == "HvH":
            self.on_button_click()

    def on_button_click(self):
        self.pick_button_clicked = True
        if self.hero_selector.remaining_clicks <= 0 or self.hero_selector.selected_id is None:
            return
        if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.pick_indices:
            self.next_move(self.draft_state, self.hero_selector.selected_id, self.mode, True)
        else:
            self.next_move(self.draft_state, self.hero_selector.selected_id, self.mode, False)

        if self.hero_selector.current_clicked_label is not None:
            self.hero_selector.current_clicked_label.setStyleSheet("")
            self.hero_selector.update_labels_in_tabs(self, self.hero_selector.hero_to_disp)
            self.hero_selector.current_clicked_label = None
            self.update_button_text()
        else:
            return

        # Set the delay time before emitting the signal
        delay_milliseconds = self.delay 
        self.delay_timer.start(delay_milliseconds)

    def auto_player_next_move(self):
        if self.hero_selector.remaining_clicks <= 0:
            return
        if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.pick_indices:
            self.next_move(self.draft_state, self.hero_selector.selected_id, self.mode, True)
        else:
            self.next_move(self.draft_state, self.hero_selector.selected_id, self.mode, False)
        
        delay_milliseconds = self.delay
        self.delay_timer.start(delay_milliseconds)


    def human_move(self, draft_state, selected_id, mode, is_pick):
        if mode == "HvA":
            if is_pick:
                self.blue_player.pick(draft_state, selected_id)
            else:
                self.blue_player.ban(draft_state, selected_id)
            self.hero_selector.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)

        elif mode == 'AvH':
            if is_pick:
                self.red_player.pick(draft_state, selected_id)
            else:
                self.red_player.ban(draft_state, selected_id)
            self.hero_selector.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)
            
        else:
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
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
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)

    def ai_move(self, draft_state, mode, is_pick):
        if mode == 'AvH':
            if is_pick:
                self.hero_selector.hero_to_disp = self.blue_player.pick(draft_state)
            else:
                self.hero_selector.hero_to_disp = self.blue_player.ban(draft_state)
            
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.update_labels_in_tabs(self, self.hero_selector.hero_to_disp)
            self.update_button_text()
            print_draft_status(draft_state)
        
        elif mode == 'HvA':
            if is_pick:
                self.hero_selector.hero_to_disp = self.red_player.pick(draft_state)
            else:
                self.hero_selector.hero_to_disp = self.red_player.ban(draft_state)
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.update_labels_in_tabs(self, self.hero_selector.hero_to_disp)
            self.update_button_text()
            print_draft_status(draft_state)

        elif mode == 'AvA':
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
                if is_pick:
                    self.hero_selector.hero_to_disp = self.blue_player.pick(draft_state)
                else:
                    self.hero_selector.hero_to_disp = self.blue_player.ban(draft_state)
            else:
                if is_pick:
                    self.hero_selector.hero_to_disp = self.red_player.pick(draft_state)
                else:
                    self.hero_selector.hero_to_disp = self.red_player.ban(draft_state)
            self.hero_selector.disp_selected_image(self, self.hero_selector.hero_to_disp)
            self.hero_selector.update_labels_in_tabs(self, self.hero_selector.hero_to_disp)
            self.update_button_text()
            print_draft_status(draft_state)
            
            
    def next_move(self, draft_state, selected_id, mode, is_pick):
        if mode is not None and mode == 'HvH': # Human vs Human
            # blue player is human
            self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'HvA': # HUman vs Ai
            # blue player is human
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
                self.human_move(draft_state, selected_id, mode, is_pick)

            else:  # red player is AI
                self.ai_thread = AIThread(self, draft_state, mode, is_pick)

        elif mode is not None and mode == 'AvH':
            # blue player is AI
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
                self.ai_thread = AIThread(self, draft_state, mode, is_pick)

            else:  # red player is Human
                self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'AvA':
            self.ai_thread = AIThread(self, draft_state, mode, is_pick)

    def update_button_text(self):
        self.highlight_next_qlabel()
        if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.pick_indices:
            self.pick_button.setText("Pick")
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
                self.top_text.setText("Blue Team Pick")
                self.top_text.setStyleSheet("font-size: 14pt; font-weight: bold; color: rgb(255, 255, 255);")

            elif get_curr_index(self.hero_selector.remaining_clicks) not in self.hero_selector.blue_turn:
                self.top_text.setText("Red Team Pick")
                self.top_text.setStyleSheet("font-size: 14pt; font-weight: bold; color: rgb(255, 255, 255);")
        else:
            self.pick_button.setText("Ban")
            if get_curr_index(self.hero_selector.remaining_clicks) in self.hero_selector.blue_turn:
                self.top_text.setText("Blue Team Ban")
                self.top_text.setStyleSheet("font-size: 14pt; font-weight: bold; color: rgb(255, 255, 255);")
            
            elif get_curr_index(self.hero_selector.remaining_clicks) not in self.hero_selector.blue_turn:
                self.top_text.setText("Red Team Ban")
                self.top_text.setStyleSheet("font-size: 14pt; font-weight: bold; color: rgb(255, 255, 255);")

    def highlight_next_qlabel(self):
        style = ""
        ban_style = "background-color: rgb(85, 255, 127); border-radius: 28px; border: 3px solid; image: url(:/icons/icons/question_mark.png); border-color:rgb(255, 255, 255);"
        pick_style = "background-color: rgb(85, 255, 127); border-radius: 10px; border: 3px solid; border-color:rgb(255, 255, 255);"
        index = get_curr_index(self.hero_selector.remaining_clicks)
        blue_turn = self.hero_selector.blue_turn
        pick_turn = self.hero_selector.pick_indices

        qlabels_list = self.qlabel_list
        
        if index in pick_turn:
            style = pick_style
        else:
            style = ban_style

        if index in blue_turn and index + 1 in blue_turn:
            qlabels_list[index].setStyleSheet(style)
            qlabels_list[index + 1].setStyleSheet(style)

        elif index not in blue_turn and index + 1 not in blue_turn:
            if index < 19 and index != 11:
                qlabels_list[index].setStyleSheet(style)
                qlabels_list[index + 1].setStyleSheet(style)
            elif index == 11 or index == 19:
                qlabels_list[index].setStyleSheet(style)
        else:
            qlabels_list[index].setStyleSheet(style)
                
    def undo_move(self):
        pick_style = "background-color: rgb(170, 170, 255); border-radius: 10px; border: 3px solid; border-color:rgb(255, 255, 255);"
        ban_style = "border-radius: 28px; border: 3px solid; image: url(:/icons/icons/question_mark.png); border-color:rgb(255, 255, 255);"
        
        blue_turn = self.hero_selector.blue_turn
        pick_turn = self.hero_selector.pick_indices

        if len(self.draft_state.draft_sequence) > 0:
            index = len(self.draft_state.draft_sequence) - 1

            if index in blue_turn and index in pick_turn:
                if len(self.draft_state.blue_actions[1]) > 0:
                    self.draft_state.blue_actions[1].pop()
                    if len(self.draft_state.blue_pick_roles) > 0:
                        self.draft_state.blue_pick_roles.pop()

            elif index in blue_turn and index not in pick_turn:
                if len(self.draft_state.blue_actions[0]) > 0:
                    self.draft_state.blue_actions[0].pop()

            elif index not in blue_turn and index in pick_turn:
                if len(self.draft_state.red_actions[1]) > 0:
                    self.draft_state.red_actions[1].pop()
                    if len(self.draft_state.red_pick_roles) > 0:
                        self.draft_state.red_pick_roles.pop()
            else:
                if len(self.draft_state.red_actions[0]) > 0:
                    self.draft_state.red_actions[0].pop()

            self.hero_selector.unavailable_hero_ids.pop()
            self.hero_selector.label_images.pop(list(self.hero_selector.label_images.keys())[-1])

            curr_qlabel = self.qlabel_list[index]
            curr_qlabel.clear()
            
            if index < 19:
                if index + 1 in pick_turn:
                    self.qlabel_list[index + 1].setStyleSheet(pick_style)
                else:
                    self.qlabel_list[index + 1].setStyleSheet(ban_style)

            if index < 18:
                if index + 2 in pick_turn:
                    self.qlabel_list[index + 2].setStyleSheet(pick_style)
                else:
                    self.qlabel_list[index + 2].setStyleSheet(ban_style)
                    
            self.hero_selector.update_labels_in_tabs(self, self.draft_state.draft_sequence[-1])
            self.draft_state.draft_sequence.pop()
            if self.hero_selector.remaining_clicks < 20:
                self.hero_selector.remaining_clicks += 1
                
            self.highlight_next_qlabel()
            self.update_button_text()
            self.hero_selector.selected_id = None
            self.hero_selector.hero_to_disp = None

            if self.hero_selector.current_clicked_label is not None:
                self.hero_selector.current_clicked_label.setStyleSheet("")
            print_draft_status(self.draft_state)

    def reset_all(self):
        self.reset_dialog.close()
        self.delay_timer.start(self.delay)
        pick_style = "background-color: rgb(170, 170, 255); border-radius: 10px; border: 3px solid; border-color:rgb(255, 255, 255);"
        ban_style = "border-radius: 28px; border: 3px solid; image: url(:/icons/icons/question_mark.png); border-color:rgb(255, 255, 255);"

        pick_turn = self.hero_selector.pick_indices

        if len(self.draft_state.draft_sequence) > 0:
            for qlabel in self.qlabel_list:
                if self.qlabel_list.index(qlabel) < len(self.draft_state.draft_sequence) + 2:
                    qlabel.clear()
                    if self.qlabel_list.index(qlabel) in pick_turn:
                        qlabel.setStyleSheet(pick_style)
                    else:
                        qlabel.setStyleSheet(ban_style)

            self.draft_state.draft_sequence.clear()
            self.draft_state.blue_actions[0].clear()
            self.draft_state.blue_actions[1].clear()
            self.draft_state.blue_pick_roles.clear()

            self.draft_state.red_actions[0].clear()
            self.draft_state.red_actions[1].clear()
            self.draft_state.red_pick_roles.clear()

            self.hero_selector.label_images.clear()

            self.hero_selector.selected_id = None
            self.hero_selector.hero_to_disp = None

            if self.hero_selector.current_clicked_label is not None:
                self.hero_selector.current_clicked_label.setStyleSheet("")

            self.hero_selector.remaining_clicks = 20
            self.highlight_next_qlabel()
            self.update_button_text()
            self.hero_selector.unavailable_hero_ids.clear()
            self.hero_selector.populate_tabs(self, 90)

            print_draft_status(self.draft_state)
