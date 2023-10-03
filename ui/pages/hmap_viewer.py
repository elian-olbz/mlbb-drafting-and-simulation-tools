import sys
import csv
import os
import typing
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QGraphicsItemGroup ,QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem, QHBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QPainterPath, QColor, QPen, QIcon
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal, QThread, QSize
from PyQt6 import uic
from ui.rsc_rc import *
from ui.misc.titlebar import TitleBar
from run_draft_logic.utils import get_icon, rounded_pixmap, load_names, get_name
script_dir = os.path.dirname(os.path.abspath(__file__))

ORIGINAL_SIZE = 720
FRAME_SKIP = 3
DELAY = 40
VISIBLE_HEROES = [110, 25, 16] #[110, 36, 18, 116, 25, 119, 87, 16, 64, 88]

class VideoThread(QThread):
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.running = True
        self.paused = False  # Add a paused flag

    def run(self):
        while self.running:
            if not self.paused:  # Check if the thread is paused
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    self.frame_ready.emit(pixmap)
                    self.msleep(30)
            else:
                return

    def stop(self):
        self.running = False
        self.wait()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

class RawVideo(QLabel):
    def __init__(self, video_path, qlabel):
        super().__init__()
        self.video_path = video_path
        self.qlabel = qlabel
        self.video_thread = None
        self.setup_video_thread()

    def setup_video_thread(self):
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread = None
        self.video_thread = VideoThread(self.video_path)
        self.video_thread.frame_ready.connect(self.update_frame)

    def update_frame(self, pixmap=None):
        if pixmap:
            # Scale the pixmap to fit the size of self.video_label
            pixmap = pixmap.scaled(self.qlabel.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.qlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.qlabel.setPixmap(pixmap)

    def __del__(self):
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()

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
        self.menu_width = 120
        self.title_bar = TitleBar(self)

        self.is_running = False
        self.video_path = None
        self.csv_path = None

        ui_path = os.path.join(script_dir, "hmap_viewer.ui")
        uic.loadUi(ui_path, self)

        self.hide_btn.clicked.connect(self.toggle_menu)
        self.hero_buttons = [self.hero_button1, self.hero_button2, 
                             self.hero_button3, self.hero_button4, 
                             self.hero_button5, self.hero_button6, 
                             self.hero_button7, self.hero_button8, 
                             self.hero_button9, self.hero_button10]

        self.class_colors = None
        self.add_colors()

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        scene_rect = QRectF(0, 0, self.graphics_view.width(), self.graphics_view.height())
        self.scene.setSceneRect(scene_rect)
        self.graphics_view.setScene(self.scene)

        self.ICON_OFFSET =  None
        self.set_icon_offset()

        # Load the background image
        background_image = QPixmap('icons/map.png')
        self.background_item = BackgroundItem(background_image, self.graphics_view)

        self.video = None
        self.open_vid_btn.clicked.connect(self.open_video_file)
        self.open_csv_btn.clicked.connect(self.open_csv_file)

        # Add the background item to the scene
        self.scene.addItem(self.background_item)

        self.data = None
        self.hero_names = load_names("data/hero_map.csv")
        self.class_names = []
        self.class_images = {}
        self.class_img_items = {}
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_objects)
        self.play_btn.clicked.connect(self.play_pause)
        self.object_group = QGraphicsItemGroup()  # Create a group for the objects

        # Add the object group to the scene
        self.scene.addItem(self.object_group)

        self.resizeEvent = self.resize_event
        self.closeEvent = self.cleanup_event

        def moveWindow(event):
            if self.title_bar.returnStatus() == True:
                self.title_bar.maximize_restore(self)

            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

        self.header_container.mouseMoveEvent = moveWindow
        self.title_bar.uiDefinitions(self)

    def toggle_menu(self):
        if self.menu_width == 0:
            self.right_frame.setFixedWidth(120)
            self.menu_width = 120
        else:
            self.right_frame.setFixedWidth(0)
            self.menu_width = 0

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def clean(self):
        if self.video and self.video.video_thread:
            self.video.video_thread.stop()
            self.video.video_thread.wait()

    def cleanup_event(self, event):
        # Stop the video thread and wait for it to finish
        self.clean()
        event.accept()
    
    def resize_event(self, event):
        super().resizeEvent(event)  
        self.scene.setSceneRect(0, 0, self.graphics_view.width(), self.graphics_view.height())
        self.set_icon_offset()
        self.background_item.set_scale_factor()
        self.load_classes()
        self.display_first_frame()

    def set_icon_offset(self):
        self.ICON_OFFSET = int((75 / ORIGINAL_SIZE) * min(self.graphics_view.height(), self.graphics_view.width()))
    
    def play_pause(self):
        if self.csv_path is not None and self.video_path is not None:
            if not self.is_running:
                self.is_running = True
                if not self.video.video_thread.isRunning():
                    # Start the video thread only if it's not already running
                    self.video.video_thread.start()
                self.video.video_thread.resume()  # Resume the video thread
                self.timer.start(DELAY)  # Adjust the timer interval
                self.play_btn.setIcon(QIcon('icons/pause.svg'))
                self.play_btn.setIconSize(QSize(20, 20))
            else:
                self.is_running = False
                self.video.video_thread.pause()  # Pause the video thread
                self.timer.stop()
                self.play_btn.setIcon(QIcon('icons/play.svg'))
                self.play_btn.setIconSize(QSize(20, 20))

    def update_file_name_label(self, path, qlabel):
        file_name = os.path.basename(path)
        qlabel.setText(f"{file_name}")
        qlabel.setFixedWidth(120)

    def open_video_file(self):
        if self.is_running == True:
            return
        else:
            video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
            if video_path:
                if self.is_running:
                    self.stop_video()
                
                self.video_path = video_path
                self.video = RawVideo(self.video_path, self.video_label)
                self.update_file_name_label(self.video_path, self.vid_name)
                self.display_first_frame()
            else:
                return

    def open_csv_file(self):
        if self.is_running == True:
            return
        else:
            csv_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
            if csv_path:
                self.csv_path = csv_path
                self.draw_objects_from_dataset()
                self.load_classes()
                self.update_btn_texts()
                self.update_file_name_label(self.csv_path, self.csv_name)
            else:
                return
            
    def display_first_frame(self):
        if not self.is_running:
            if self.video_path:
                cap = cv2.VideoCapture(self.video_path)
                ret, frame = cap.read()
                cap.release()

                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame.shape
                    bytes_per_line = 3 * width
                    q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)

                    # Scale the pixmap to fit the size of self.video_label
                    pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
                    self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.video_label.setPixmap(pixmap)


    def load_classes(self):
        class_ids = set()

        if self.csv_path is not None:
            with open(self.csv_path, "r") as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip the header row

                for row in csv_reader:
                    obj_class = int(row[2])
                    class_ids.add(obj_class)

            for class_id in class_ids:
                image_path = get_icon(class_id + 1) # image files are named after the class names
                pixmap = QPixmap(image_path)
                scaled_pix = pixmap.scaled(self.ICON_OFFSET, self.ICON_OFFSET, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                r_pix = rounded_pixmap(scaled_pix, self.ICON_OFFSET, 1)
                self.class_images[class_id] = r_pix

            id_list = list(self.class_images.keys())
            for item in id_list:
                self.class_names.append(get_name(item + 1, self.hero_names))

    def draw_objects_from_dataset(self):
        if self.csv_path is not None:
            with open(self.csv_path, "r") as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip the header row
                self.data = list(csv_reader)

    def update_btn_texts(self):
        if self.class_names is not None:
            for i in range(10):
                self.hero_buttons[i].setText(list(self.class_names)[i])
                color = self.class_colors[i + 1]
                color_hex = color.name()  # Get the hexadecimal representation of the QColor
                parent_name = self.hero_buttons[i].parent().objectName()
                style = f"QFrame #{parent_name} {{border: 2px solid; border-color: {color_hex}; border-radius:10px}}"
                self.hero_buttons[i].parent().setStyleSheet(style)


    def update_objects(self):
        ratio = min(self.graphics_view.height(), self.graphics_view.width()) / ORIGINAL_SIZE
        MAP_OFFSET = int((35 / ORIGINAL_SIZE) * min(self.scene.height(), self.scene.width()))
        if self.current_frame < len(self.data):
            current_frame_data = []

            # Collect data for the current frame
            frame = int(self.data[self.current_frame][0])  # Get the frame number of the current row
            while self.current_frame < len(self.data) and int(self.data[self.current_frame][0]) == frame:
                current_frame_data.append(self.data[self.current_frame])
                self.current_frame += FRAME_SKIP

            background_position = self.background_item.pos()

            for row in current_frame_data:
                _, _, class_id, x, y = row[0], row[1], int(row[2]), float(row[3]), float(row[4])
                if class_id in self.class_images and class_id in VISIBLE_HEROES:
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
                        object_x + (self.ICON_OFFSET / 2),
                        object_y + (self.ICON_OFFSET / 2),
                        dot_size,
                        dot_size
                    )
                    dot.setZValue(-1)

                    color_index = list(self.class_images.keys()).index(class_id)
                    dot.setPen(QPen(Qt.GlobalColor.transparent))
                    dot.setBrush(QBrush(self.class_colors[color_index + 1]))
                    self.scene.addItem(dot)  # Add the dot to the object group
        else:
            self.timer.stop()

    def add_colors(self):
        self.class_colors = {
            1: QColor(255, 0, 0, 75),      # Red
            2: QColor(0, 255, 0, 75),      # Green
            3: QColor(0, 0, 255, 75),      # Blue
            4: QColor(255, 255, 0, 75),    # Yellow
            5: QColor(255, 0, 255, 75),    # Magenta
            6: QColor(0, 255, 255, 75),    # Cyan
            7: QColor(255, 255, 255, 75),    # Orange
            8: QColor(128, 0, 255, 75),    # Purple
            9: QColor(0, 192, 192, 75),    # Lighter Teal
            10: QColor(255, 128, 128, 75)  # Pink
        }

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatmapViewerWindow()
    window.show()
    sys.exit(app.exec())