import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap
from draft_ui import Ui_MainWindow
import os
import csv
from PyQt6.QtCore import Qt, QSize



class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.hero_roles = {}
        self.hero_types = {}
        self.hero_names = []
        self.hero_icons = []

        self.load_hero_roles("data/hero_roles.csv")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.populate_tabs()

        # Make the window full-screen at start
        self.showMaximized()


    def clear_tabs(self):
        # Clear all existing tabs from the "hero_tab" widget
        while self.ui.hero_tab.count() > 0:
            self.ui.hero_tab.removeTab(0)


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
            tab_layout.setSpacing(10)  # Set the spacing value as per your preference

            # Get all hero IDs for the current tab
            hero_ids_for_tab = list(range(1, len(self.hero_names) + 1)) if tab_name == "All" else [
                hero_id for hero_id, types in self.hero_types.items() if tab_name in types]

            row = 0
            column = 0

            for hero_id in hero_ids_for_tab:
                # Get the hero image path based on the hero_id
                hero_image_path = self.get_image(hero_id)

                # Load the hero image using QPixmap
                pixmap = QPixmap(hero_image_path)

                # Create a QLabel and set its properties
                hero_image_label = QLabel()
                hero_image_label.setPixmap(pixmap)
                hero_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                hero_image_label.setFixedSize(100, 100)  # Set a fixed size for uniformity

                # Add the QLabel to the grid layout
                tab_layout.addWidget(hero_image_label, row, column)
                column += 1

                # Move to the next row if the current row is filled
                if column == 7:
                    row += 1
                    column = 0

            # Add the container widget with the layout to the existing "hero_tab" using addTab
            scroll_area.setWidget(tab_widget)
            self.ui.hero_tab.addTab(scroll_area, tab_name)



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
    
    def get_image(self, hero_id):
        image_filename = 'hero_icon ({})'.format(hero_id) + '.jpg'
        image_path = os.path.join('D:/python_projects/gui/images/heroes/', image_filename)
        return image_path
    
    def get_type(self, hero_id):
        return self.hero_types.get(hero_id, [])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())

