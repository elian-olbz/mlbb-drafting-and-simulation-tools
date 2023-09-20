import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsColorizeEffect
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QPainter, QImage, QBrush, QPen, QPalette, QBitmap
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QSize
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
        x = min(self.width(), self.height())
        self.highlight_radius = x**2 / (2.00001 * x)  # Use the smaller dimension for radius

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

    def create_scaled_round_pixmap(self, qlabel, hero_id):
                    hero_image_path = get_icon(hero_id)
                    pixmap = QPixmap(hero_image_path)
                    round_pix = rounded_pixmap(pixmap=pixmap, size=97, border_thickness=4)
                    label_size = qlabel.size()
                    scaled_pixmap = round_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    return scaled_pixmap
            
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
            spacing = 5  # Set the spacing value as per your preference

            # Get all hero IDs for the current tab
            if tab_name == "All":
                hero_ids_for_tab = list(range(1, len(self.hero_names) + 1))
            else:
                hero_ids_for_tab = [hero_id for hero_id, types in self.hero_types.items() if tab_name in types]

            row = 0
            column = 0

            for hero_id in hero_ids_for_tab:
                # Create a widget to hold the image and name QLabel
                hero_widget = QWidget()
                hero_layout = QVBoxLayout(hero_widget)

                # Create a QLabel for the hero image and set its properties
                hero_image_label = ClickableLabel(hero_id)

                # Add the custom class selector to the label
                hero_image_label.setObjectName("clicked-label")
                scaled_pixmap = self.create_scaled_round_pixmap(hero_image_label, hero_id)

                hero_image_label.setPixmap(scaled_pixmap)
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
            while row < 30:  # 
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

        if parent.mode == 'HvH':
            self.highlight_image(hero_id, clicked_label)
        elif parent.mode == 'HvA' and get_curr_index(self.remaining_clicks) in self.blue_turn:
            self.highlight_image(hero_id, clicked_label)
        elif parent.mode == 'AvH' and get_curr_index(self.remaining_clicks) not in self.blue_turn:
            self.highlight_image(hero_id, clicked_label)
        else:
            return
        
    def highlight_image(self, hero_id, clicked_label):
        if clicked_label:
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
        white_border = "border-radius: 10px; border: 3px solid; border-color:rgb(255, 255, 255);"  # bring back the white border
        if hero_id is not None and hero_id not in self.unavailable_hero_ids:
            if self.remaining_clicks <= 0:
                return

            qlabel = self.get_next_empty_qlabel(parent)
            if qlabel:
                if get_curr_index(self.remaining_clicks) in self.pick_indices:
                    image_path = get_image(hero_id)
                    pixmap = QPixmap(image_path)
                    oval_pix = oval_pixmap(pixmap)
                    # Get the size of the QLabel and scale the pixmap to fit
                    label_size = qlabel.size()
                    scaled_pixmap = oval_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    qlabel.setStyleSheet(white_border)
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

                    image_overlay_path = "icons/x-circle.svg"
                    self.create_ban_overlay_indicator(qlabel, label_size, scaled_pixmap, image_overlay_path, 30) # indicator on the ban frame only
                    qlabel.setStyleSheet("border-radius: 0px;")

                    self.label_images[qlabel] = hero_id  # Update the label_images dictionary
                    self.unavailable_hero_ids.append(hero_id)
                self.remaining_clicks -= 1
                #self.update_labels_in_tabs(parent, hero_id) # indicator on the tabs that a hero is banned or picked

    def create_ban_overlay_indicator(self, qlabel, label_size, scaled_pixmap, image_overlay_path, image_overlay_size):
        # Create a QImage from the scaled pixmap
        composite_image = QImage(label_size, QImage.Format.Format_ARGB32)
        composite_image.fill(QColor(0, 0, 0, 0))  # Fill with transparent color

        # Create a QPainter to draw on the composite image
        painter = QPainter(composite_image)

        # Draw the scaled pixmap on the composite image
        painter.drawPixmap(0, 0, scaled_pixmap)

        # Load and draw the overlay image (x-circle.svg) on top of the scaled pixmap
        #overlay_pixmap = QPixmap("icons/x-circle.svg")
        overlay_pixmap = QPixmap(image_overlay_path)
        #overlay_size = QSize(30, 30)  # Replace with the dimensions you want
        overlay_size = QSize(image_overlay_size, image_overlay_size)
        scaled_overlay_pixmap = overlay_pixmap.scaled(overlay_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Create a QImage for the overlay pixmap
        overlay_image = QImage(overlay_size, QImage.Format.Format_ARGB32)
        overlay_image.fill(QColor(0, 0, 0, 0))  # Fill with transparent color

        # Create a QPainter to draw on the overlay image
        overlay_painter = QPainter(overlay_image)

        # Check if it's the "blue turn"
        is_blue_turn = get_curr_index(self.remaining_clicks) in self.blue_turn

        # Calculate the position based on the "blue turn" condition
        if is_blue_turn:
            overlay_x = label_size.width() - overlay_size.width()
        else:
            overlay_x = 0

        overlay_y = label_size.height() - overlay_size.height()

        # Draw the scaled overlay pixmap at the calculated position
        painter.drawPixmap(overlay_x, overlay_y, scaled_overlay_pixmap)

        # Draw the scaled overlay pixmap at the calculated position
        painter.drawPixmap(overlay_x, overlay_y, scaled_overlay_pixmap)

        # End painting for overlay image
        overlay_painter.end()

        # Draw the overlay image on top of the composite image
        painter.drawImage(0, 0, overlay_image)

        # End painting for the composite image
        painter.end()

        # Set the resulting composite image as the pixmap for the QLabel
        qlabel.setPixmap(QPixmap.fromImage(composite_image))

    def create_gray_overlay_indicator(self, qlabel, circular_pixmap, opacity):
        # Create a circular mask
        mask = QBitmap(circular_pixmap.size())
        mask.fill(Qt.GlobalColor.color0)
        painter = QPainter(mask)
        painter.setBrush(Qt.GlobalColor.color1)
        painter.drawEllipse(0, 0, circular_pixmap.width() - 2, circular_pixmap.width() - 2)
        painter.end()

        # Create a transparent gray overlay pixmap
        overlay_pixmap = QPixmap(circular_pixmap.size())
        overlay_pixmap.fill(QColor(0, 0, 0, opacity))  # Adjust opacity as needed
        overlay_pixmap.setMask(mask)

        # Combine the circular_pixmap and the overlay_pixmap
        combined_pixmap = QPixmap(circular_pixmap.size())
        combined_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, circular_pixmap)
        painter.drawPixmap(0, 0, overlay_pixmap)
        painter.end()

        # Set the combined_pixmap as the pixmap for the QLabel
        qlabel.setPixmap(combined_pixmap)
        

    def update_labels_in_tabs(self, parent, hero_idx): # indicator on the tabs that a hero is banned or picked
        # Iterate through all tabs
        print(hero_idx)
        for tab_index in range(parent.hero_tab.count()):
            tab_widget = parent.hero_tab.widget(tab_index)
            if tab_widget:
                # Iterate through all QLabels in the current tab
                for hero_label in tab_widget.findChildren(ClickableLabel):
                    if hero_label.hero_id == hero_idx:
                        # Check if the hero_id is in the unavailable_hero_ids list
                        if hero_idx in self.unavailable_hero_ids:
                            scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_idx)
                            self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 180)
                        else:   
                            # Reset the QLabel style if the hero is available
                            scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_idx)
                            self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 0) # remove gray overlay


    def get_next_empty_qlabel(self, parent):
        pd_qlabels_list = [parent.blue_ban1, parent.red_ban5, parent.blue_ban2, parent.red_ban4,
                        parent.blue_ban3, parent.red_ban3, parent.blue_pick1, parent.red_pick1,
                        parent.red_pick2, parent.blue_pick2, parent.blue_pick3, parent.red_pick3,
                        parent.red_ban2, parent.blue_ban4, parent.red_ban1, parent.blue_ban5,
                        parent.red_pick4, parent.blue_pick4, parent.blue_pick5, parent.red_pick5]
        for qlabel in pd_qlabels_list:
            if qlabel not in self.label_images or self.label_images[qlabel] is None:
                return qlabel
        return None

# Hero selector dialog for the quick draft
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
                round_pix = rounded_pixmap(pixmap, 97, 3)

                # Get the size of the QLabel and scale the pixmap to fit
                label_size = qlabel.size()
                scaled_pixmap = round_pix.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                qlabel.setPixmap(scaled_pixmap)
                qlabel.setFixedSize(50, 50)
                qlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.label_images[qlabel] = hero_id  # Update the label_images dictionary
                self.unavailable_hero_ids.append(hero_id)
                
    def store_hero_id(self, parent, hero_id):
        # Get the sender of the signal (i.e., the ClickableLabel instance that emitted the signal)
        clicked_label = self.sender()
        if self.remaining_clicks <= 0:
            return
        self.highlight_image(hero_id, clicked_label)

    def update_labels_in_tabs(self, parent, prev_id, is_swap): # indicator on the tabs that a hero is banned or picked
        # Iterate through all tabs
        hero_id = self.selected_id
        for tab_index in range(parent.hero_tab.count()):
            tab_widget = parent.hero_tab.widget(tab_index)
            if tab_widget:
                # Iterate through all QLabels in the current tab
                for hero_label in tab_widget.findChildren(ClickableLabel):
                    if is_swap == False:
                        if hero_label.hero_id == hero_id:
                            # Check if the hero_id is in the unavailable_hero_ids list
                            if hero_id in self.unavailable_hero_ids:
                                scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_id)
                                self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 180)
                            else:   
                                scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_id)
                                self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 0) # remove gray overlay
                    else:
                        if hero_label.hero_id == hero_id:
                            # Check if the hero_id is in the unavailable_hero_ids list
                            if hero_id in self.unavailable_hero_ids:
                                scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_id)
                                self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 180)
                            else:   
                                scaled_pixmap = self.create_scaled_round_pixmap(hero_label, hero_id)
                                self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 0) # remove gray overlay
                                
                        elif hero_label.hero_id == prev_id:
                                scaled_pixmap = self.create_scaled_round_pixmap(hero_label, prev_id)
                                self.create_gray_overlay_indicator(hero_label, scaled_pixmap, 0)
                    