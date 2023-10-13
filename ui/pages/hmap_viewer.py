import sys
import csv
import os
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QGraphicsItemGroup ,QGraphicsScene, QGraphicsPathItem, QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem, QHBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QPainterPath, QColor, QPen, QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal, QThread, QSize
from PyQt6 import uic
from ui.rsc_rc import *
from ui.misc.titlebar import TitleBar
from run_draft_logic.utils import get_icon, rounded_pixmap, load_names, get_name
script_dir = os.path.dirname(os.path.abspath(__file__))

ORIGINAL_SIZE = 720
FRAME_SKIP = 1
DELAY = 80

PLAY_QSS = "QPushButton{\
                image: url(:/icons/icons/play-circle.svg);\
                text-align:center;\
                padding: 4px 4px;\
                border-radius: 23px;\
                }\
                QPushButton:hover {\
                    background-color:  #57578a;\
                }\
                QPushButton:pressed {	\
                    background-color:  #7676b2;\
                    color: rgb(255, 255, 255);\
                }"

PAUSE_QSS = "QPushButton{\
                image: url(:/icons/icons/pause-circle.svg);\
                text-align:center;\
                padding: 4px 4px;\
                border-radius: 23px;\
                }\
                QPushButton:hover {\
                    background-color:  #57578a;\
                }\
                QPushButton:pressed {	\
                    background-color:  #7676b2;\
                    color: rgb(255, 255, 255);\
                }"

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
                    self.msleep(27)
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
        self.v_timer = QTimer(self)
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

        self.is_video_running = False
        self.is_hmap_running = False

        self.heroes = []
        self.visible_heroes = {}

        self.video_path = None
        self.csv_path = None

        ui_path = os.path.join(script_dir, "hmap_viewer.ui")
        uic.loadUi(ui_path, self)

        self.hero_buttons = [self.hero_button1, self.hero_button2, 
                             self.hero_button3, self.hero_button4, 
                             self.hero_button5, self.hero_button6, 
                             self.hero_button7, self.hero_button8, 
                             self.hero_button9, self.hero_button10]
        self.class_colors = None
        self.add_colors()

        self.set_btn_colors()

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

        self.data = None
        self.hero_names = load_names("data/hero_map.csv")
        self.class_names = []
        self.class_images = {}
        self.class_img_items = {}
        self.current_row = 0
        self.total_frames = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_objects)
        self.video_play_btn.clicked.connect(self.video_play_pause)
        self.hmap_play_btn.clicked.connect(self.hmap_play_pause)
        self.object_group = QGraphicsItemGroup()  # Create a group for the objectssel
        self.object_group.setZValue(1)

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

        self.current_frame = 0
        
        self.create_heatmap_item()
        self.video_slider.valueChanged.connect(self.seek_video_frame)
        self.hmap_slider.valueChanged.connect(self.seek_hmap_frame)
        self.connect_hero_btns()

        # Create a QShortcut that triggers the button click event on "Enter" key press
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut.activated.connect(self.play_all_button)
    
    def play_all_button(self):
        if (self.is_hmap_running and self.is_video_running) or (not self.is_hmap_running and not self.is_video_running):
            self.hmap_play_pause()
            self.video_play_pause()
        elif not self.is_hmap_running and self.is_video_running:
            self.video_play_pause()
        elif self.is_hmap_running and not self.is_video_running:
            self.hmap_play_pause()

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
        self.hide_hero()

    def set_icon_offset(self):
        self.ICON_OFFSET = int((75 / ORIGINAL_SIZE) * min(self.graphics_view.height(), self.graphics_view.width()))
    
    def update_hmap_bar(self):
        val = int(self.current_row / len(self.data) * 100)

        if not len(self.data) - self.current_row < 10:
            self.hmap_bar.setValue(val)
        else:
            val = 100
            self.hmap_bar.setValue(val)

    def update_video_bar(self):
        f = int(self.video.video_thread.cap.get(cv2.CAP_PROP_POS_FRAMES))
        val = int((f / self.total_frames) * 100)
        self.video_bar.setValue(val)

    def video_play_pause(self):
        if self.video_path is not None:
            if not self.is_video_running:
                self.is_video_running = True
                if not self.video.video_thread.isRunning():
                    # Start the video thread only if it's not already running
                    self.video.video_thread.start()
                self.video.video_thread.resume()  # Resume the video thread
                self.video_play_btn.setStyleSheet(PAUSE_QSS)
                self.video_play_btn.setFixedSize(46, 46)
                self.video_play_btn.setToolTip("Pause")
                self.video.v_timer.start(27)
            else:
                self.is_video_running = False
                self.video.video_thread.pause()  # Pause the video thread
                self.video_play_btn.setStyleSheet(PLAY_QSS)
                self.video_play_btn.setFixedSize(46, 46)
                self.video_play_btn.setToolTip("Play")

    def hmap_play_pause(self):
        if self.csv_path is not None:
            if not self.is_hmap_running:
                self.is_hmap_running = True
                self.timer.start(DELAY)  
                self.hmap_play_btn.setStyleSheet(PAUSE_QSS)
                self.hmap_play_btn.setFixedSize(46, 46)
                self.hmap_play_btn.setToolTip("Pause")
            else:
                self.is_hmap_running = False
                self.timer.stop()
                self.hmap_play_btn.setStyleSheet(PLAY_QSS)
                self.hmap_play_btn.setFixedSize(46, 46)
                self.hmap_play_btn.setToolTip("Play")

    def seek_hmap_frame(self):
        #fr = int((self.hmap_slider.value() / 100) * self.total_frames)
        fr = int(self.hmap_slider.value())
        self.current_row = fr
        self.timer.stop()
        self.heatmap_pixmap.fill(Qt.GlobalColor.transparent)
        self.update_objects()
        self.update_hmap_bar()

        if self.is_hmap_running:
            self.hmap_play_btn.setStyleSheet(PAUSE_QSS)
            self.hmap_play_btn.setFixedSize(46, 46)
            self.hmap_play_btn.setToolTip("Pause")
            self.timer.start(DELAY)
            self.is_hmap_running = True
        else:
            self.hmap_play_btn.setStyleSheet(PLAY_QSS)
            self.hmap_play_btn.setFixedSize(46, 46)
            self.hmap_play_btn.setToolTip("Play")
            self.is_hmap_running = False
            self.timer.stop()
        self.hide_hero()

    def seek_video_frame(self):
        if self.video is not None:
            self.video.video_thread.pause()  # Pause the video thread
            # Update the current frame number
            #fr = int((self.video_slider.value() / 100) * self.total_frames)
            fr = int(self.video_slider.value())
            self.current_frame = fr

            # Display the frame corresponding to the slider value
            self.video.video_thread.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video.video_thread.cap.read()
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

            if not self.video.video_thread.isRunning():
                if self.is_video_running:
                    self.is_video_running = True
                    self.video.video_thread.start()
                    self.video.video_thread.resume()
                    self.video.v_timer.stop()
                    self.update_video_bar()
                    self.video.v_timer.start(27)
                else:
                    self.is_video_running = False
                    self.video.video_thread.pause()
                    self.video.v_timer.stop()
                    self.update_video_bar()
                    self.video.v_timer.start(27)
        else:
            return

    def update_file_name_label(self, path, qlabel):
        file_name = os.path.basename(path)
        qlabel.setText(f"{file_name}")
        qlabel.setFixedWidth(120)

    def open_video_file(self):
        if self.is_video_running == True:
            return
        else:
            video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
            if video_path:
                if self.is_video_running:
                    self.stop_video()
                
                self.video_path = video_path
                self.video = RawVideo(self.video_path, self.video_label)
                self.total_frames = int(self.video.video_thread.cap.get(cv2.CAP_PROP_FRAME_COUNT))   # Get the total number of frames in the video
                self.video_slider.setRange(0, self.total_frames)
                self.update_file_name_label(self.video_path, self.vid_name)
                self.display_first_frame()
                self.video.v_timer.timeout.connect(self.update_video_bar)
            else:
                return

    def open_csv_file(self):
        if self.is_hmap_running == True:
            return
        else:
            csv_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
            if csv_path:
                # Validate the CSV format
                if self.validate_csv_format(csv_path):
                    self.csv_path = csv_path
                    self.draw_objects_from_dataset()
                    self.load_classes()
                    self.update_btn_text()
                    self.update_file_name_label(self.csv_path, self.csv_name)
                    # Add the background item to the scene
                    if self.background_item not in self.scene.items():
                        self.scene.addItem(self.background_item)
                else:
                    QMessageBox.critical(self, "Error", "CSV format does not match the desired format.")
            else:
                return

    def validate_csv_format(self, csv_path):
        csv_format = ["Frame", "Class", "Class_ID", "X", "Y"]

        # Read the CSV file and check its format
        try:
            with open(csv_path, 'r', newline='') as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader)  # Read the header row

                # Check if the header matches the desired format
                if header == csv_format:
                    return True
                else:
                    return False
        except Exception as e:
            # Handle any exceptions that may occur during file reading or validation
            print(f"Error: {e}")
            return False
            
    def display_first_frame(self):
        if not self.is_video_running:
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

        self.heroes = list(class_ids)
        for i, hero in enumerate(self.heroes):
            self.visible_heroes[i] = hero

    def draw_objects_from_dataset(self):
        if self.csv_path is not None:
            with open(self.csv_path, "r") as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip the header row
                self.data = list(csv_reader)
                self.hmap_slider.setRange(0, len(self.data))

    def connect_hero_btns(self):
        for btn in self.hero_buttons:
            btn.toggled.connect(self.hide_hero)
    
    def hide_hero(self):
        for i, btn in enumerate(self.hero_buttons):
            if btn.isChecked() == False:
                self.visible_heroes[i] = 0
            else:
                self.visible_heroes[i] = self.heroes[i]

            for item in self.object_group.childItems():
                if self.visible_heroes[i] == 0:
                    cl = QPixmap(item.pixmap().size())
                    self.object_group.removeFromGroup(item)
                    cl.fill(Qt.GlobalColor.transparent)
                    item.setPixmap(cl)

    def update_btn_text(self):
            self.set_btn_colors()
            for i in range(10):
                if self.class_names is not None:
                    self.hero_buttons[i].setText(list(self.class_names)[i])
                    self.hero_buttons[i].setChecked(True)
                else:
                    return
            
    def set_btn_colors(self):
        for i in range(10):
            color = self.class_colors[i + 1]
            color_hex = color.name()  # Get the hexadecimal representation of the QColor
            style = f"background-color: {color_hex}; border-radius:10px"
            self.hero_buttons[i].parent().setStyleSheet(style)

    def create_heatmap_item(self):
        self.prev_x = None
        self.prev_y = None
        self.prev_pixmap = None
        self.heatmap_pixmap = QPixmap(self.background_item.pixmap().size())
        self.heatmap_pixmap.fill(Qt.GlobalColor.transparent)
        self.heatmap_painter = QPainter(self.heatmap_pixmap)
        self.heatmap_item = QGraphicsPixmapItem(self.heatmap_pixmap)
        self.heatmap_item.setZValue(0)
        self.scene.addItem(self.heatmap_item)

    def update_objects(self):
        ratio = min(self.graphics_view.height(), self.graphics_view.width()) / ORIGINAL_SIZE
        MAP_OFFSET = int((35 / ORIGINAL_SIZE) * min(self.scene.height(), self.scene.width()))
        if self.data is not None and self.current_row < len(self.data):
            current_frame_data = []
            self.update_hmap_bar()

            # Collect data for the current frame
            frame = int(self.data[self.current_row][0])  # Get the frame number of the current row
            while self.current_row < len(self.data) and int(self.data[self.current_row][0]) == frame:
                current_frame_data.append(self.data[self.current_row])
                self.current_row += FRAME_SKIP

            background_position = self.background_item.pos()

            if self.prev_pixmap is not None:
                self.heatmap_pixmap = self.prev_pixmap

            for row in current_frame_data:
                _, _, class_id, x, y = row[0], row[1], int(row[2]), float(row[3]), float(row[4])
                if class_id in self.class_images and class_id in self.visible_heroes.values():
                    pixmap = self.class_images[class_id]

                    if class_id in self.class_img_items:
                        img_item = self.class_img_items[class_id]
                        img_item.setPixmap(pixmap)
                    else:
                        img_item = QGraphicsPixmapItem(pixmap, None)
                        self.class_img_items[class_id] = img_item  # Store the reference

                    # Calculate the position relative to the background image
                    object_x = x * ratio + background_position.x() - MAP_OFFSET
                    object_y = (y * ratio + background_position.y()) - MAP_OFFSET

                    img_item.setPos(object_x, object_y)  # Update the position

                    if img_item not in self.object_group.childItems():
                        self.object_group.addToGroup(img_item)  # Add the item to the object group

            # Paint the heatmap based on object positions for all frames
                    color_index = list(self.class_images.keys()).index(class_id)
                    self.heatmap_painter.setPen(Qt.GlobalColor.transparent)
                    self.heatmap_painter.setBrush(QBrush(self.class_colors[color_index + 1]))
                    self.heatmap_painter.drawEllipse(
                        int(object_x + (self.ICON_OFFSET / 2)), int(object_y + (self.ICON_OFFSET / 2)), 8, 8)

            # Update the pixmap of the heatmap item in the scene
            self.heatmap_item.setPixmap(self.heatmap_pixmap)
            self.prev_pixmap = self.heatmap_pixmap
        else:
            self.timer.stop()
        
    def add_colors(self):
        self.class_colors = {
            1: QColor(1, 165, 141, 180),    # emerald
            2: QColor(126, 183, 213, 180),  # dusk blue
            3: QColor(152, 204, 182, 180),  # grayed jade
            4: QColor(170, 170, 255, 180),  # lavander
            5: QColor(254, 223, 94, 180),   # lemon zest
            6: QColor(185, 149, 197, 180),  # african violet
            7: QColor(249, 224, 201, 180),  # linen
            8: QColor(21, 69, 118, 180),    # monaco blue
            9: QColor(231, 50, 43, 180),    # poppy red
            10: QColor(246, 142, 81, 180)   # nectarine
        }
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatmapViewerWindow()
    window.show()
    sys.exit(app.exec())