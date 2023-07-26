import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor
from draft_ui import Ui_MainWindow
from PyQt6.QtCore import Qt, pyqtSignal
from functools import partial
from run_draft_logic.draft_state import DraftState

from run_draft_logic.utils import print_draft_status, print_final_draft, rounded_pixmap, get_icon, get_image, get_name, load_theme
from run_draft_logic.player import HumanPlayer, AIPlayer
from run_draft_logic.modes import human_vs_human, human_vs_ai, ai_vs_ai


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, hero_id):
        super().__init__()
        self.hero_id = hero_id

    def mousePressEvent(self, event):
        self.clicked.emit(self.hero_id)

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.blue_player, self.red_player = human_vs_ai()

        self.hero_roles = self.draft_state.hero_roles
        self.hero_names = self.draft_state.hero_names
        self.hero_icons = self.draft_state.hero_icons
        self.hero_types = self.draft_state.hero_types

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.populate_tabs()
        # Connect the pick_button click signal to display_clicked_image with the last stored hero_id
        self.ui.pick_button.clicked.connect(self.on_button_click)

        # Connect the currentChanged signal of hero_tab to update_current_tab method
        self.ui.hero_tab.currentChanged.connect(self.update_current_tab)

        # Make the window full-screen at start
        #self.showMaximized()
        #self.play_draft()


    def clear_tabs(self):
        # Clear all existing tabs from the "hero_tab" widget
        while self.ui.hero_tab.count() > 0:
            self.ui.hero_tab.removeTab(0)
    
    def update_current_tab(self, index):
        # Update the current_tab_index with the index of the current tab
        self.current_tab_index = index


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
            self.ui.hero_tab.addTab(scroll_area, tab_name)


    def store_hero_id(self, hero_id):
        # Get the sender of the signal (i.e., the ClickableLabel instance that emitted the signal)
        clicked_label = self.sender()

        if self.remaining_clicks <= 0:
                return
        
        if clicked_label:
            # Get the current tab index
            current_tab_index = self.ui.hero_tab.currentIndex()

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
        print("display_clicked_image called with hero_id:", hero_id)
        
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
                print(abs(self.remaining_clicks - 20))
                self.remaining_clicks -= 1
            
    
    def on_button_click(self):
        self.pick_button_clicked = True

        pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
        if self.remaining_clicks <= 0 or self.selected_id is None:
            return
        if abs(self.remaining_clicks - 20) in pick_indices:
            self.player_pick(self.draft_state, self.selected_id)
        else:
            self.player_ban(self.draft_state, self.selected_id)

        if self.current_clicked_label is not None:
                    self.current_clicked_label.setStyleSheet("")
                    self.current_clicked_label = None


    def player_pick(self, draft_state, selected_id):
        print("player pick called")
        blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]

        if type(self.blue_player) is HumanPlayer:  # If blue player is human
            if abs(self.remaining_clicks - 20) in blue_turn:
                self.blue_player.pick(draft_state, selected_id)
                self.hero_to_disp = selected_id
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None

        else: # If blue player is AI
            if abs(self.remaining_clicks - 20) in blue_turn:
                self.hero_to_disp = self.blue_player.pick(draft_state)
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None

        if type(self.red_player) is HumanPlayer:  # If red player is human
            if abs(self.remaining_clicks - 20) not in blue_turn:
                self.red_player.pick(draft_state, selected_id)
                self.hero_to_disp = selected_id
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None

        else:  # If red player is AI
            if abs(self.remaining_clicks - 20) not in blue_turn:
                self.hero_to_disp = self.red_player.pick(draft_state)
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None

    def player_ban(self, draft_state, selected_id):
        print("player ban called")
        blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]

        if type(self.blue_player) is HumanPlayer:  # If blue player is human
            if abs(self.remaining_clicks - 20) in blue_turn:
                self.blue_player.ban(draft_state, selected_id)
                self.hero_to_disp = selected_id
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None
        else: # If blue player is AI
            if abs(self.remaining_clicks - 20) in blue_turn:
                self.hero_to_disp = self.blue_player.ban(draft_state)
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None

        if type(self.red_player) is HumanPlayer:  # If red player is human
            if abs(self.remaining_clicks - 20) not in blue_turn:
                self.red_player.ban(draft_state, selected_id)
                self.hero_to_disp = selected_id
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None
        else:  # If red player is AI
            if abs(self.remaining_clicks - 20) not in blue_turn:
                self.hero_to_disp = self.red_player.ban(draft_state)
                print_draft_status(draft_state)
                self.display_clicked_image(self.hero_to_disp)
                self.hero_to_disp = None
                
    def get_next_empty_qlabel(self):
        qlabels_list = [self.ui.blue_ban1, self.ui.red_ban1, self.ui.blue_ban2, self.ui.red_ban2,
                        self.ui.blue_ban3, self.ui.red_ban3, self.ui.blue_pick1, self.ui.red_pick1,
                        self.ui.red_pick2, self.ui.blue_pick2, self.ui.blue_pick3, self.ui.red_pick3,
                        self.ui.red_ban4, self.ui.blue_ban4, self.ui.red_ban5, self.ui.blue_ban5,
                        self.ui.red_pick4, self.ui.blue_pick4, self.ui.blue_pick5, self.ui.red_pick5]
        for qlabel in qlabels_list:
            if qlabel not in self.label_images or self.label_images[qlabel] is None:
                return qlabel

        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)

    #Load the theme
    theme_path = "ui/dark.qss"
    theme = load_theme(theme_path)

    #Apply the theme as a global stylesheet to the application
    app.setStyleSheet(theme)

    window = MyMainWindow()
    window.show()

    sys.exit(app.exec())