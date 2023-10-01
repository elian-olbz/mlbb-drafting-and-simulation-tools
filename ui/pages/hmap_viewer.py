import sys
import csv
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsItemGroup ,QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem, QHBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
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

        # Calculate the position of the background item based on the new scene rectangle size
        x = (self.view.width() - scale_factor * self.pix.width()) / 2
        y = (self.view.height() - scale_factor * self.pix.height()) / 2

        self.setPos(x, y)
        self.setScale(scale_factor)

class HeatmapViewerWindow(QMainWindow):
    def __init__(self):
        super(HeatmapViewerWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir, "hmap_viewer.ui")
        uic.loadUi(ui_path, self)

        self.class_colors = None
        self.add_colors()

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        scene_rect = QRectF(0, 0, self.graphics_view.width(), self.graphics_view.height())
        self.scene.setSceneRect(scene_rect)
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
        self.class_img_items = {}
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_objects)
        self.timer.start(30)  # Adjust the timer interval (milliseconds) 31

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
        super().resizeEvent(event)  # Call the base class method to handle the resizing
        # Update the scene rectangle to match the new size
        self.scene.setSceneRect(0, 0, self.graphics_view.width(), self.graphics_view.height())
        # Recalculate the icon size and update the background item scale factor
        self.set_icon_size()
        self.background_item.set_scale_factor()
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
        MAP_OFFSET = int((35 / ORIGINAL_SIZE) * min(self.scene.height(), self.scene.width()))
        if self.current_frame < len(self.data):
            current_frame_data = []

            # Collect data for the current frame
            frame = int(self.data[self.current_frame][0])  # Get the frame number of the current row
            while self.current_frame < len(self.data) and int(self.data[self.current_frame][0]) == frame:
                current_frame_data.append(self.data[self.current_frame])
                self.current_frame += 1

            background_scale_factor = self.background_item.scale()
            background_position = self.background_item.pos()

            for row in current_frame_data:
                _, _, class_id, x, y = row[0], row[1], int(row[2]), float(row[3]), float(row[4])
                if class_id in self.class_images:
                    pixmap = self.class_images[class_id]

                    if class_id in self.class_img_items:
                        img_item = self.class_img_items[class_id]
                        img_item.setPixmap(pixmap)  # Update the pixmap if needed
                    else:
                        img_item = QGraphicsPixmapItem(pixmap, None)
                        self.class_img_items[class_id] = img_item  # Store the reference

                    # Calculate the position relative to the background image
                    object_x = x * ratio + background_position.x() - MAP_OFFSET
                    object_y = (y * ratio + background_position.y()) - MAP_OFFSET

                    img_item.setPos(object_x, object_y)  # Update the position

                    # You can update other properties of img_item here if needed

                    if img_item not in self.object_group.childItems():
                        self.object_group.addToGroup(img_item)  # Add the item to the object group

                    # Create an ellipse (dot) at the calculated position
                    dot_size = 12  # Adjust the size of the dots as needed
                    dot = QGraphicsEllipseItem(
                        object_x + (self.ICON_SIZE / 2),
                        object_y + (self.ICON_SIZE / 2),
                        dot_size,
                        dot_size
                    )
                    dot.setZValue(-1)

                    color_index = list(self.class_images.keys()).index(class_id)
                    dot.setBrush(QBrush(self.class_colors[color_index + 1]))
                    self.scene.addItem(dot)  # Add the dot to the object group
        else:
            self.timer.stop()

    def add_colors(self):
        self.class_colors = {
            1: QColor(255, 0, 0),    # Red
            2: QColor(0, 255, 0),    # Green
            3: QColor(0, 0, 255),    # Blue
            4: QColor(255, 255, 0),  # Yellow
            5: QColor(255, 0, 255),  # Magenta
            6: QColor(0, 255, 255),  # Cyan
            7: QColor(128, 0, 0),    # Maroon
            8: QColor(0, 128, 0),    # Green (Dark)
            9: QColor(0, 0, 128),    # Navy
            10: QColor(128, 128, 0)  # Olive (Add more colors as needed)
        }

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatmapViewerWindow()
    window.show()
    sys.exit(app.exec())