import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea
from PyQt6.QtGui import QPixmap
from draft_ui import Ui_MainWindow
import os

def group_images_by_letter(image_dir):
    image_files = os.listdir(image_dir)
    sorted_files = sorted(image_files, key=lambda x: x[0])
    grouped_images = {}
    for image_file in sorted_files:
        starting_letter = image_file[0].lower()
        if starting_letter.isalpha():
            grouped_images.setdefault(starting_letter, []).append(image_file)
    return grouped_images

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.populate_tabs()

        # Make the window full-screen at start
        self.showMaximized()

    def populate_tabs(self):
        tab_names = ["All", "Tank", "Fighter", "Assasin", "Marksman", "Mage", "Support"]

        # Get a list of image file names in the directory
        image_dir = "icons/"  # Replace with the path to the directory containing your images
        grouped_images = group_images_by_letter(image_dir)

        for i, tab_name in enumerate(tab_names):
            # Get the existing tab widget by index
            tab = self.ui.hero_tab.widget(i)

            # Create a scroll area for the tab
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            tab_layout = QVBoxLayout(tab)
            tab_layout.addWidget(scroll_area)

            # Create a container widget for the scroll area
            container = QWidget()
            scroll_area.setWidget(container)

            # Create a grid layout for the container
            grid_layout = QGridLayout(container)
            container.setLayout(grid_layout)

            # Populate the grid layout with QLabel for each image
            row, col = 0, 0
            if tab_name[0].isalpha():
                starting_letter = chr(ord('a') + i)
                if starting_letter in grouped_images:
                    for image_file in grouped_images[starting_letter]:
                        pixmap = QPixmap(os.path.join(image_dir, image_file))
                        label = QLabel()
                        label.setPixmap(pixmap)
                        grid_layout.addWidget(label, row, col)

                        col += 1
                        if col == 7:  # 7 columns per row
                            col = 0
                            row += 1

            # Set the tab title
            self.ui.hero_tab.setTabText(i, tab_name)

    
    def on_image_clicked_(self, widget: QWidget):
        self.selected_image_path = self.label_image_map.get(widget.objectName(), None)
        if isinstance(widget, QLabel):
            pixmap = QPixmap(self.selected_image_path)
            widget.setPixmap(pixmap)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())

