import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QPalette, QColor
from draft_ui import Ui_MainWindow
import os
import csv
from PyQt6.QtCore import Qt, QSize, QRectF, pyqtSignal
from functools import partial


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

        self.hero_roles = {}
        self.hero_types = {}
        self.hero_names = []
        self.hero_icons = []
        self.remaining_clicks = 20

        self.current_clicked_label = None
        self.clickable_labels = {}
        self.label_images = {} # Dictionary to track QLabel images
        self.selected_id = None
        self.unavailable_hero_ids = []

        # Initialize the current_tab_index to the index of the first tab (All)
        self.current_tab_index = 0
        self.pick_button_clicked = False

        self.load_hero_roles("data/hero_roles.csv")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.populate_tabs()
        # Connect the pick_button click signal to display_clicked_image with the last stored hero_id
        self.ui.pick_button.clicked.connect(self.display_clicked_image)

        # Connect the currentChanged signal of hero_tab to update_current_tab method
        self.ui.hero_tab.currentChanged.connect(self.update_current_tab)

        # Make the window full-screen at start
        self.showMaximized()


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
                hero_image_path = self.get_icon(hero_id)

                # Load the hero image using QPixmap
                pixmap = QPixmap(hero_image_path)

                # Apply a circular mask to the hero image
                rounded_pixmap = self.rounded_pixmap(pixmap=pixmap, size=97, border_thickness=4)

                # Create a widget to hold the image and name QLabel
                hero_widget = QWidget()
                hero_layout = QVBoxLayout(hero_widget)

                # Create a QLabel for the hero image and set its properties
                hero_image_label = ClickableLabel(hero_id)

                # Add the custom class selector to the label
                hero_image_label.setObjectName("clicked-label")

                hero_image_label.setPixmap(rounded_pixmap)
                hero_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hero_image_label.setFixedSize(100, 100)  # Set a fixed size for uniformity

                # Connect the clicked signal of each ClickableLabel to the display_clicked_image method
                hero_image_label.clicked.connect(partial(self.store_hero_id, hero_id))

                # Store the ClickableLabel instance and its hero_id in the dictionary
                self.clickable_labels[hero_id] = hero_image_label

                # Create a QLabel for the hero name and set its properties
                hero_name_label = QLabel(self.get_name(hero_id))
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

    
    def display_clicked_image(self):
        self.pick_button_clicked = True
        if self.selected_id and self.selected_id not in self.unavailable_hero_ids:

            pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]

            if self.remaining_clicks <= 0:
                return

            qlabel = self.get_next_empty_qlabel()
            if qlabel:
                if abs(self.remaining_clicks - 20) in pick_indices:
                    image_path = self.get_image(self.selected_id)
                    pixmap = QPixmap(image_path)
                    # Get the size of the QLabel and scale the pixmap to fit
                    label_size = qlabel.size()
                    scaled_pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    qlabel.setPixmap(scaled_pixmap)
                    self.label_images[qlabel] = self.selected_id  # Update the label_images dictionary
                    self.unavailable_hero_ids.append(self.selected_id)
                else:
                    image_path = self.get_icon(self.selected_id)
                    pixmap = QPixmap(image_path)
                    round_pix = self.rounded_pixmap(pixmap, 97)
                    # Get the size of the QLabel and scale the pixmap to fit
                    label_size = qlabel.size()
                    scaled_pixmap = round_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    qlabel.setPixmap(scaled_pixmap)
                    self.label_images[qlabel] = self.selected_id  # Update the label_images dictionary
                    self.unavailable_hero_ids.append(self.selected_id)
                self.remaining_clicks -= 1

                if self.current_clicked_label is not None:
                    self.current_clicked_label.setStyleSheet("")
                    self.current_clicked_label = None


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

    def rounded_pixmap(self, pixmap, size, border_thickness=0):
        # Create a transparent mask and painter
        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a circle on the mask using QPainterPath with an increased border thickness
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(border_thickness, border_thickness, size - 2 * border_thickness, size - 2 * border_thickness))
        painter.setClipPath(clip_path)

        # Use the mask to draw the pixmap as a rounded shape
        rounded_pixmap = QPixmap(size, size)
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(clip_path)  # Set the same clip path for the pixmap
        painter.drawPixmap(0, 0, pixmap)

        return rounded_pixmap
    
    def load_hero_roles(self, hero_roles_path):
        with open(hero_roles_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hero_id = int(row['HeroID'])
                roles = [role.strip() for role in row['Role'].split('/')]
                self.hero_roles[hero_id] = roles
                hero_name = row['Name']
                self.hero_names.append(hero_name)
                hero_icon = row['Icon']
                self.hero_icons.append(hero_icon)
                types = [type.strip() for type in row['Type'].split('/')]
                self.hero_types[hero_id] = types
 

    def get_name(self, hero_id):
        return self.hero_names[hero_id - 1]
    
    def get_role(self, hero_id):
        return self.hero_roles.get(hero_id, [])
    
    def get_icon(self, hero_id):
        image_filename = 'hero_icon ({})'.format(hero_id) + '.jpg'
        image_path = os.path.join('D:/python_projects/gui/images/hero_icons/', image_filename)
        return image_path
    
    def get_image(self, hero_id):
        image_filename = 'hero_image ({})'.format(hero_id) + '.jpg'
        image_path = os.path.join('D:/python_projects/gui/images/hero_images/', image_filename)
        return image_path

    def get_type(self, hero_id):
        return self.hero_types.get(hero_id, [])


def load_theme(theme_path):
    with open(theme_path, 'r') as file:
        theme = file.read()
    return theme
    


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