from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from run_draft_logic.draft_state import DraftState
from ui.misc.titlebar import*

from run_draft_logic.utils import print_draft_status, print_final_draft, rounded_pixmap, get_icon, get_image, get_name, load_theme

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, hero_id):
        super().__init__()
        self.hero_id = hero_id

    def mousePressEvent(self, event):
        self.clicked.emit(self.hero_id)

class AutoPlayer(QObject):
    auto_player_signal = pyqtSignal()

    def start(self):
        # Emit the signal to trigger the AI predictions and UI updates
        self.auto_player_signal.emit()

class DraftWindow(QMainWindow):
    def __init__(self, parent):
        super(DraftWindow, self).__init__(parent)

        self.WINDOW_MAXED = True
        self.menu_width = 55
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir,  "practice_draft.ui")

        uic.loadUi(ui_path, self)

        self.pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
        self.blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]

        self.hero_roles = {}
        self.hero_types = {}
        self.hero_names = []
        self.hero_icons = []
        self.remaining_clicks = 20

        self.current_clicked_label = None
        self.clickable_labels = {}
        self.label_images = {} # Dictionary to track QLabel images
        self.selected_id = None
        self.hero_to_disp = None
        self.ai_prediction = None
        self.unavailable_hero_ids = []
        self.ai_prediction = None

        # Initialize the current_tab_index to the index of the first tab (All)
        self.current_tab_index = 0
        self.pick_button_clicked = False


        self.draft_state = DraftState('data/hero_roles.csv')
        self.blue_player = None
        self.red_player = None
        self.mode = None

        self.hero_roles = self.draft_state.hero_roles
        self.hero_names = self.draft_state.hero_names
        self.hero_icons = self.draft_state.hero_icons
        self.hero_types = self.draft_state.hero_types

        self.populate_tabs()
        # Connect the pick_button click signal to display_clicked_image with the last stored hero_id
        self.pick_button.clicked.connect(self.on_button_click)

        # Connect the currentChanged signal of hero_tab to update_current_tab method
        self.hero_tab.currentChanged.connect(self.update_current_tab)

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


    def clear_tabs(self):
        # Clear all existing tabs from the "hero_tab" widget
        while self.hero_tab.count() > 0:
            self.hero_tab.removeTab(0)
    
    def update_current_tab(self, index):
        # Update the current_tab_index with the index of the current tab
        self.current_tab_index = index
        if self.current_clicked_label is not None:
            self.current_clicked_label.setStyleSheet("")
            self.current_clicked_label = None
            self.selected_id = None


    def populate_tabs(self):

        tab_names = ["All", "Tank", "Fighter", "Assassin", "Marksman", "Mage", "Support"]

        # Clear existing tabs
        self.clear_tabs()

        for tab_name in tab_names:
            # Create a scroll area and grid layout for each tab
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            tab_widget = QWidget()
            tab_layout = QGridLayout(tab_widget)
            spacing = 4  # Set the spacing value as per your preference

            # Get all hero IDs for the current tab
            if tab_name == "All":
                hero_ids_for_tab = list(range(1, len(self.hero_names) + 1))
            else:
                hero_ids_for_tab = [hero_id for hero_id, types in self.hero_types.items() if tab_name in types]

            row = 0
            column = 0

            for hero_id in hero_ids_for_tab:
                # Get the hero image path based on the hero_id
                hero_image_path = get_icon(hero_id)

                # Load the hero image using QPixmap
                pixmap = QPixmap(hero_image_path)

                # Apply a circular mask to the hero image
                round_pix = rounded_pixmap(pixmap=pixmap, size=97, border_thickness=4)

                # Create a widget to hold the image and name QLabel
                hero_widget = QWidget()
                hero_layout = QVBoxLayout(hero_widget)

                # Create a QLabel for the hero image and set its properties
                hero_image_label = ClickableLabel(hero_id)

                # Add the custom class selector to the label
                hero_image_label.setObjectName("clicked-label")

                hero_image_label.setPixmap(round_pix)
                hero_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hero_image_label.setFixedSize(100, 100)  # Set a fixed size for uniformity

                # Connect the clicked signal of each ClickableLabel to the display_clicked_image method
                hero_image_label.clicked.connect(partial(self.store_hero_id, hero_id))

                # Store the ClickableLabel instance and its hero_id in the dictionary
                self.clickable_labels[hero_id] = hero_image_label

                # Create a QLabel for the hero name and set its properties
                hero_name_label = QLabel(get_name(hero_id, self.hero_names))
                hero_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hero_name_label.setWordWrap(True)
                hero_name_label.setFixedWidth(100)  # Set a fixed width to match the image width

                # Add the QLabel for the hero name below the image
                hero_layout.addWidget(hero_image_label)
                hero_layout.addWidget(hero_name_label)

                # Add the hero widget to the grid layout
                tab_layout.addWidget(hero_widget, row, column)
                column += 1

                # Move to the next row if the current row is filled
                if column == 7:
                    row += 1
                    column = 0

            # Add empty QSpacerItem to the last cell of the last row to keep spacing consistent
            spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            tab_layout.addItem(spacer, row, column)

            # Add fixed-sized widgets to fill empty spaces and ensure uniform spacing between rows
            while row < 3:  # Assuming you want a maximum of 5 rows in each tab
                empty_widget = QWidget()
                empty_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                tab_layout.addWidget(empty_widget, row, column)
                row += 1

            # Add spacing between rows and columns
            tab_layout.setVerticalSpacing(spacing)
            tab_layout.setHorizontalSpacing(spacing)

            # Add the container widget with the layout to the existing "hero_tab" using addTab
            scroll_area.setWidget(tab_widget)
            self.hero_tab.addTab(scroll_area, tab_name)


    def store_hero_id(self, hero_id):
        # Get the sender of the signal (i.e., the ClickableLabel instance that emitted the signal)
        clicked_label = self.sender()

        if self.remaining_clicks <= 0:
                return
        
        if clicked_label:
            # Get the current tab index
            current_tab_index = self.hero_tab.currentIndex()

            # Check if the clicked label is within the current tab
            if current_tab_index == self.current_tab_index or current_tab_index == 0:
                if self.current_clicked_label is not None:
                    # Reset the style of the previously clicked label
                    self.current_clicked_label.setStyleSheet("")

            if hero_id not in self.unavailable_hero_ids:
                # Apply a highlight style to the clicked label
                highlight_color = QColor(69, 202, 255)  # Replace with the desired highlight color
                highlight_radius = 50  # Adjust the radius as needed

                circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
                clicked_label.setStyleSheet(circular_style)
                #clicked_label.setStyleSheet(f"border: 2px solid {highlight_color.name()};")

                # Store the clicked label as the current clicked label for the current tab
                self.current_clicked_label = clicked_label

                self.selected_id = hero_id
            else:
                self.selected_id = None

    
    def display_clicked_image(self, hero_id):
        
        if hero_id is not None and hero_id not in self.unavailable_hero_ids:

            if self.remaining_clicks <= 0:
                return

            qlabel = self.get_next_empty_qlabel()
            if qlabel:
                if abs(self.remaining_clicks - 20) in self.pick_indices:
                    image_path = get_image(hero_id)
                    pixmap = QPixmap(image_path)
                    # Get the size of the QLabel and scale the pixmap to fit
                    label_size = qlabel.size()
                    scaled_pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    qlabel.setPixmap(scaled_pixmap)
                    self.label_images[qlabel] = hero_id  # Update the label_images dictionary
                    self.unavailable_hero_ids.append(hero_id)
                else:
                    image_path = get_icon(hero_id)
                    pixmap = QPixmap(image_path)
                    round_pix = rounded_pixmap(pixmap, 97)
                    # Get the size of the QLabel and scale the pixmap to fit
                    label_size = qlabel.size()
                    scaled_pixmap = round_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    qlabel.setPixmap(scaled_pixmap)
                    self.label_images[qlabel] = hero_id  # Update the label_images dictionary
                    self.unavailable_hero_ids.append(hero_id)
                self.remaining_clicks -= 1
            
    def emit_auto_player_signal(self):
        # Trigger the AI move after the delay
        if self.mode == 'HvH':
            pass
        elif self.mode == 'HvA':
            if abs(self.remaining_clicks - 20) not in self.blue_turn and self.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
        elif self.mode == 'AvH':
            if abs(self.remaining_clicks - 20) in self.blue_turn and self.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()
        elif self.mode == 'AvA':
            if abs(self.remaining_clicks - 20) in self.blue_turn or abs(self.remaining_clicks - 20) not in self.blue_turn and self.remaining_clicks > 0:
                self.auto_player.auto_player_signal.emit()

    def on_button_click(self):
        self.pick_button_clicked = True

        if self.remaining_clicks <= 0 or self.selected_id is None:
            return
        if abs(self.remaining_clicks - 20) in self.pick_indices:
            self.pick_or_ban(self.draft_state, self.selected_id, self.mode, True)
        else:
            self.pick_or_ban(self.draft_state, self.selected_id, self.mode, False)
        
        # Set the desired delay time (in milliseconds) before emitting the signal
        delay_milliseconds = 1000  # Adjust the delay time as needed
        self.delay_timer.start(delay_milliseconds)

        if self.current_clicked_label is not None:
            self.current_clicked_label.setStyleSheet("")
            self.current_clicked_label = None

    def auto_player_pick_or_ban(self):
        if self.remaining_clicks <= 0:
            return
        if abs(self.remaining_clicks - 20) in self.pick_indices:
            self.pick_or_ban(self.draft_state, self.selected_id, self.mode, True)
        else:
            self.pick_or_ban(self.draft_state, self.selected_id, self.mode, False)

        # Set the desired delay time (in milliseconds) before emitting the signal
        delay_milliseconds = 1000  # Adjust the delay time as needed
        self.delay_timer.start(delay_milliseconds)


    def human_move(self, draft_state, selected_id, mode, is_pick):
        if mode == "HvA":
            if is_pick:
                self.blue_player.pick(draft_state, selected_id)
            else:
                self.blue_player.ban(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

        elif mode == 'AvH':
            if is_pick:
                self.red_player.pick(draft_state, selected_id)
            else:
                self.red_player.ban(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None
        else:
            if abs(self.remaining_clicks - 20) in self.blue_turn:
                if is_pick:
                    self.blue_player.pick(draft_state, selected_id)
                else:
                    self.blue_player.ban(draft_state, selected_id)
            else:
                if is_pick:
                    self.red_player.pick(draft_state, selected_id)
                else:
                    self.red_player.ban(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None


    def ai_move(self, draft_state, mode, is_pick):
        if mode == 'AvH':
            if is_pick:
                self.hero_to_disp = self.blue_player.pick(draft_state)
            else:
                self.hero_to_disp = self.blue_player.ban(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None
        elif mode == 'HvA':
            if is_pick:
                self.hero_to_disp = self.red_player.pick(draft_state)
            else:
                self.hero_to_disp = self.red_player.ban(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

        elif mode == 'AvA':
            if abs(self.remaining_clicks - 20) in self.blue_turn:
                if is_pick:
                    self.hero_to_disp = self.blue_player.pick(draft_state)
                else:
                    self.hero_to_disp = self.blue_player.ban(draft_state)
            else:
                if is_pick:
                    self.hero_to_disp = self.red_player.pick(draft_state)
                else:
                    self.hero_to_disp = self.red_player.ban(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None


            
    def pick_or_ban(self, draft_state, selected_id, mode, is_pick):

        if mode is not None and mode == 'HvH': # Human vs Human
            # blue player is human
            self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'HvA': # HUman vs Ai
            # blue player is human
            if abs(self.remaining_clicks - 20) in self.blue_turn:
                self.human_move(draft_state, selected_id, mode, is_pick)

            else:  # red player is AI
                self.ai_move(draft_state, mode, is_pick)

        elif mode is not None and mode == 'AvH':
            # blue player is AI
            if abs(self.remaining_clicks - 20) in self.blue_turn:
                self.ai_move(draft_state, mode, is_pick)

            else:  # red player is Human
                self.human_move(draft_state, selected_id, mode, is_pick)

        elif mode is not None and mode == 'AvA':
            self.ai_move(draft_state, mode, is_pick)
    
    def get_next_empty_qlabel(self):
        qlabels_list = [self.blue_ban1, self.red_ban1, self.blue_ban2, self.red_ban2,
                        self.blue_ban3, self.red_ban3, self.blue_pick1, self.red_pick1,
                        self.red_pick2, self.blue_pick2, self.blue_pick3, self.red_pick3,
                        self.red_ban4, self.blue_ban4, self.red_ban5, self.blue_ban5,
                        self.red_pick4, self.blue_pick4, self.blue_pick5, self.red_pick5]
        for qlabel in qlabels_list:
            if qlabel not in self.label_images or self.label_images[qlabel] is None:
                return qlabel

        return None


