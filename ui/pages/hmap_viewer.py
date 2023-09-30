import sys
import csv
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsItemGroup ,QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QHBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6 import uic
from ui.rsc_rc import *
from ui.misc.titlebar import TitleBar
from run_draft_logic.utils import get_icon, rounded_pixmap
script_dir = os.path.dirname(os.path.abspath(__file__))


ORIGINAL_SIZE = 720

class BackgroundItem(QGraphicsPixmapItem):
    def __init__(self, pix, view):
        super().__init__(pix)
        self.pix = pix
        self.view = view

        # Make sure the background item is drawn behind other items
        self.setZValue(-1)

        self.set_scale_factor()
    
    def set_scale_factor(self):
        scale_factor = min(self.view.width() / self.pix.width(), self.view.height() / self.pix.height())
        print(self.view.height())
        # Set the position of the background item at the top-left corner
        MAP_OFFSET = int((30 / ORIGINAL_SIZE) * min(self.view.height(), self.view.width()))
        self.setPos(MAP_OFFSET, MAP_OFFSET) # set an offset to accomodate the size of the hero icons
        self.setScale(scale_factor)

class HeatmapViewerWindow(QMainWindow):
    def __init__(self):
        super(HeatmapViewerWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir, "hmap_viewer.ui")
        uic.loadUi(ui_path, self)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        self.ICON_SIZE =  None
        self.set_icon_size()

        # Load the background image
        background_image = QPixmap('icons/map.png')
        self.background_item = BackgroundItem(background_image, self.graphics_view)

        # Add the background item to the scene
        self.scene.addItem(self.background_item)

        self.dataset_filename = "outputs/new.csv"  # Replace with your dataset file's path
        self.data = None
        self.class_images = {}
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_objects)
        self.timer.start(31)  # Adjust the timer interval (milliseconds)

        self.load_class_images()
        self.draw_objects_from_dataset()
        self.object_group = QGraphicsItemGroup()  # Create a group for the objects

        # Add the object group to the scene
        self.scene.addItem(self.object_group)

        self.resizeEvent = self.resize_event

        def moveWindow(event):
            if self.title_bar.returnStatus() == True:
                self.title_bar.maximize_restore(self)

            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

        self.header_container.mouseMoveEvent = moveWindow
        self.title_bar.uiDefinitions(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()
    
    def resize_event(self, event):
        self.background_item.set_scale_factor()
        self.set_icon_size()
        self.load_class_images()

    def set_icon_size(self):
        self.ICON_SIZE = int((75 / ORIGINAL_SIZE) * min(self.graphics_view.height(), self.graphics_view.width()))

    def load_class_images(self):
        class_ids = set()
        
        with open(self.dataset_filename, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                obj_class = int(row[2])
                class_ids.add(obj_class)

        for class_id in class_ids:
            image_path = get_icon(class_id + 1) # image files are named after the class names
            pixmap = QPixmap(image_path)
            scaled_pix = pixmap.scaled(self.ICON_SIZE, self.ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            r_pix = rounded_pixmap(scaled_pix, self.ICON_SIZE)
            self.class_images[class_id] = r_pix

    def draw_objects_from_dataset(self):
        with open(self.dataset_filename, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            self.data = list(csv_reader)

    def update_objects(self):
        ratio = min(self.graphics_view.height(), self.graphics_view.width()) / ORIGINAL_SIZE
        if self.current_frame < len(self.data):
            # Remove items from the object group
            for item in self.object_group.childItems():
                self.object_group.removeFromGroup(item)

            current_frame_data = []

            # Collect data for the current frame
            frame = int(self.data[self.current_frame][0])  # Get the frame number of the current row
            while self.current_frame < len(self.data) and int(self.data[self.current_frame][0]) == frame:
                current_frame_data.append(self.data[self.current_frame])
                self.current_frame += 1

            for row in current_frame_data:
                _, _, class_id, x, y = row[0], row[1], int(row[2]), float(row[3]), float(row[4])
                if class_id in self.class_images:
                    pixmap = self.class_images[class_id]
                    item = QGraphicsPixmapItem(pixmap, None)  # Create a pixmap item for the object
                    item.setPos(x * ratio, y * ratio)
                    self.object_group.addToGroup(item)  # Add the item to the object group

        else:
            self.timer.stop()

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatmapViewerWindow()
    window.show()
    sys.exit(app.exec())