import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from functools import partial
from run_draft_logic.utils import *
from math import ceil


# class for qlabels (hero icons) that will populate the tabs and can be clicked
class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, hero_id):
        super().__init__()
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)  # Disable scaled contents to maintain aspect ratio
        self.hero_id = hero_id
        self.highlight_radius = 0  # Initialize the highlight radius

    def hasHeightForWidth(self):
        return self.pixmap() is not None

    def heightForWidth(self, w):
        if self.pixmap():
            return int(w * (self.pixmap().height() / self.pixmap().width()))

    def mousePressEvent(self, event):
        self.clicked.emit(self.hero_id)

    def resizeEvent(self, event):
        # Calculate the new highlight radius based on the size of the smallest dimension
        min_dimension = min(self.width(), self.height())
        self.highlight_radius = min_dimension / 2  # Use the smaller dimension for radius



# Hero selector for the practice draft
class SetupHeroSelector(QMainWindow):
    def __init__(self, parent):
        super(SetupHeroSelector, self).__init__(parent)

        self.pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
        self.blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]
        self.remaining_clicks = 20

        self.hero_roles = {}
        self.hero_types = {}
        self.hero_names = []
        self.hero_icons = []

        self.current_clicked_label = None  # Clicked qlabel from the tab (the hero icon itself)
        self.clickable_labels = {}
        self.label_images = {} # Dictionary to track QLabel images
        self.selected_id = None
        self.hero_to_disp = None
        self.unavailable_hero_ids = []

        # Initialize the current_tab_index to the index of the first tab (All)
        self.current_tab_index = 0
        self.pick_button_clicked = False
        

    def clear_tabs(self, parent):
        #Clear existing tabs from the widget
        while parent.hero_tab.count() > 0:
            parent.hero_tab.removeTab(0)

    def update_current_tab(self, index):
        # Update the current_tab_index with the index of the current tab
        self.current_tab_index = index
        if self.current_clicked_label is not None:
            self.current_clicked_label.setStyleSheet("")
            self.current_clicked_label = None
            self.selected_id = None

            
    def populate_tabs(self, parent, img_size):

        tab_names = ["All", "Tank", "Fighter", "Assassin", "Marksman", "Mage", "Support"]

        # Clear existing tabs
        self.clear_tabs(parent)

        for tab_name in tab_names:
            # Create a scroll area and grid layout for each tab
            scroll_area = QScrollArea()
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setWidgetResizable(True)
            tab_widget = QWidget()
            tab_widget.setMinimumSize(500, 250)
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
                hero_image_label.setMinimumSize(int(img_size / 1.5), int(img_size / 1.5))
                hero_image_label.setMaximumSize(img_size, img_size)  # Set a fixed size for uniformity

                # Connect the clicked signal of each ClickableLabel to the display_clicked_image method
                hero_image_label.clicked.connect(partial(self.store_hero_id, parent, hero_id))

                # Store the ClickableLabel instance and its hero_id in the dictionary
                self.clickable_labels[hero_id] = hero_image_label

                # Create a QLabel for the hero name and set its properties
                hero_name_label = QLabel(get_name(hero_id, self.hero_names))
                hero_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hero_name_label.setWordWrap(True)
                hero_name_label.setMinimumWidth(img_size / 2)
                hero_name_label.setMaximumWidth(img_size)  # Set a fixed width to match the image width

                # Add the QLabel for the hero name below the image
                hero_layout.addWidget(hero_image_label)
                hero_layout.addWidget(hero_name_label)

                hero_widget.setLayout(hero_layout)
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
            while row < 30:  # Assuming you want a maximum of 5 rows in each tab
                empty_widget = QWidget()
                empty_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                tab_layout.addWidget(empty_widget, row, column)
                row += 1

            # Add spacing between rows and columns
            tab_layout.setVerticalSpacing(spacing)
            tab_layout.setHorizontalSpacing(spacing)

            # Add the container widget with the layout to the existing "hero_tab" using addTab
            scroll_area.setWidget(tab_widget)
            parent.hero_tab.addTab(scroll_area, tab_name)
            
    def store_hero_id(self, parent, hero_id):
        # Get the sender of the signal (i.e., the ClickableLabel instance that emitted the signal)
        clicked_label = self.sender()

        if self.remaining_clicks <= 0:
            return

        if clicked_label:
            # Get the current tab index
            current_tab_index = parent.hero_tab.currentIndex()

            # Check if the clicked label is within the current tab
            if current_tab_index == self.current_tab_index or current_tab_index == 0:
                if self.current_clicked_label is not None:
                    # Reset the style of the previously clicked label
                    self.current_clicked_label.setStyleSheet("")

            if hero_id not in self.unavailable_hero_ids:
                # Apply a highlight style to the clicked label
                highlight_color = QColor(69, 202, 255)  # Replace with the desired highlight color
                highlight_radius = clicked_label.highlight_radius  # Use the dynamically calculated radius

                circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
                clicked_label.setStyleSheet(circular_style)

                # Store the clicked label as the current clicked label for the current tab
                self.current_clicked_label = clicked_label

                self.selected_id = hero_id
            else:
                self.selected_id = None


    
    # Displaying images on the practice draft window
    def disp_selected_image(self, parent, hero_id):
        
        if hero_id is not None and hero_id not in self.unavailable_hero_ids:

            if self.remaining_clicks <= 0:
                return

            qlabel = self.get_next_empty_qlabel(parent)
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

    def get_next_empty_qlabel(self, parent):

        pd_qlabels_list = [parent.blue_ban1, parent.red_ban1, parent.blue_ban2, parent.red_ban2,
                        parent.blue_ban3, parent.red_ban3, parent.blue_pick1, parent.red_pick1,
                        parent.red_pick2, parent.blue_pick2, parent.blue_pick3, parent.red_pick3,
                        parent.red_ban4, parent.blue_ban4, parent.red_ban5, parent.blue_ban5,
                        parent.red_pick4, parent.blue_pick4, parent.blue_pick5, parent.red_pick5]
        for qlabel in pd_qlabels_list:
            if qlabel not in self.label_images or self.label_images[qlabel] is None:
                return qlabel

        return None

# Hero selector for the quick draft
class SetupHeroDialog(SetupHeroSelector):
    def __init__(self, parent):
        super(SetupHeroDialog, self).__init__(parent)

        ###################
        # Instance variables for quick draft only
        hero_roles_path = 'data/hero_roles.csv'
        self.hero_roles, self.hero_names, self.hero_icons, self.hero_types = load_hero_roles(hero_roles_path)
        ###################

    # Displaying images on the quick draft window
    def disp_selected_image(self,hero_id, qlabel):
        
        if hero_id is not None and hero_id not in self.unavailable_hero_ids:

            if self.remaining_clicks <= 0:
                return
            if qlabel:
                image_path = get_icon(hero_id)
                pixmap = QPixmap(image_path)
                round_pix = rounded_pixmap(pixmap, 97)
                # Get the size of the QLabel and scale the pixmap to fit
                label_size = qlabel.size()
                scaled_pixmap = round_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                qlabel.setPixmap(scaled_pixmap)
                self.label_images[qlabel] = hero_id  # Update the label_images dictionary
                self.unavailable_hero_ids.append(hero_id)
    