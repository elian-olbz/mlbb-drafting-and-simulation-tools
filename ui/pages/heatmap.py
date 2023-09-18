import cv2
import csv
import numpy as np
from math import ceil
from ultralytics import YOLO
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QSizePolicy, QDialog, QVBoxLayout, QProgressBar
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6 import uic
import sys
import os
from run_draft_logic.utils import load_theme
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import TitleBar

#os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

script_dir = os.path.dirname(os.path.abspath(__file__))

class PredictionThread(QThread):
    update_frame = pyqtSignal(QImage)
    update_progress = pyqtSignal(float)  # Signal for updating the progress bar
    
    def __init__(self, parent, video_path, csv_filename, csv_file, csv_writer):
        super(PredictionThread, self).__init__(parent)
        self.parent = parent
        self.video_path = video_path
        self.csv_filename = csv_filename
        self.csv_file = csv_file
        self.csv_writer = csv_writer

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Get the total number of frames
        frame_count = 0
        frame_skip_factor = 2 # 2 for normal speed
        results = None

        while cap.isOpened() and self.parent.is_running:
            success, frame = cap.read()

            if success:
                frame_count += 1

                # Apply frame skipping
                if frame_count % frame_skip_factor != 0:
                    continue  # Skip this frame

                if self.parent.is_cropping:
                    frame = frame[self.parent.crop_coordinates[1]:self.parent.crop_coordinates[1] + self.parent.crop_coordinates[3],
                                self.parent.crop_coordinates[0]:self.parent.crop_coordinates[0] + self.parent.crop_coordinates[2]]

                results = self.parent.model.predict(frame, conf=0.5)

                for r in results:
                    for box in r.boxes:
                        class_id = box.cls
                        pred = box.xyxy[0]
                        x_min = pred[0].item()
                        y_min = pred[1].item()
                        x_max = pred[2].item()
                        y_max = pred[3].item()

                        # Check if the CSV file is still open
                        if self.csv_file:
                            self.csv_writer.writerow([frame_count, self.parent.model.names[int(class_id)], ceil((x_min + x_max) / 2), ceil((y_min + y_max) / 2)])

                annotated_frame = results[0].plot()
                q_image = QImage(annotated_frame.data, annotated_frame.shape[1], annotated_frame.shape[0], annotated_frame.strides[0], QImage.Format.Format_BGR888)

                self.update_frame.emit(q_image)

                # Calculate and emit the progress percentage
                progress_percentage = (frame_count / (total_frames - (total_frames % frame_skip_factor))) * 100
                self.update_progress.emit(progress_percentage)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if self.parent.is_stopping:
                    break  # Exit the thread gracefully if stopping flag is set
            else:
                break

        cap.release()
        self.parent.is_running = False
        self.parent.prediction_thread = None

class HeatMapWindow(QMainWindow):
    def __init__(self):
        super(HeatMapWindow, self).__init__()

        self.model = None
        self.WINDOW_MAXED = False
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir, "heatmap.ui")

        uic.loadUi(ui_path, self)
        self.load_ai_model()

        self.open_btn.clicked.connect(self.open_video_file)
        self.play_btn.clicked.connect(self.start_prediction)
        self.crop_btn.clicked.connect(self.crop_video)
        self.stop_btn.clicked.connect(self.stop_prediction)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lock = QThread()

        self.cap = None
        self.video_path = ""
        self.csv_filename = 'outputs/locx.csv'
        self.csv_file = None
        self.csv_writer = None
        self.frame_count = 0

        self.is_cropping = False
        self.crop_coordinates = None
        self.original_frame = None
        self.frame_to_disp = None

        self.is_running = False
        self.is_stopping = False
        self.prediction_thread = None

        self.resizeEvent = self.resize_video

        def moveWindow(event):
            if self.title_bar.returnStatus() == True:
                self.title_bar.maximize_restore(self)

            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

        self.header_container.mouseMoveEvent = moveWindow
        self.title_bar.uiDefinitions(self)

    def update_progress_bar(self, percentage):
        self.progress_bar.setValue(percentage)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()
    
    def closeEvent(self, event):
        # Stop the prediction thread and close the CSV file when the window is closed
        if self.is_running:
            self.stop_prediction()
            self.prediction_thread.wait()  # Wait for the thread to finish gracefully

        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        event.accept()
    
    def load_ai_model(self):
        self.model = YOLO('model/yolov8_custom.pt')


    def update_file_name_label(self):
        file_name = os.path.basename(self.video_path)
        self.file_name_label.setText(f"{file_name}")
    
    def resize_video(self, event):
        if self.original_frame is not None and self.is_running == False:
            self.display_frame(self.frame_to_disp)

    def open_video_file(self):
        if self.is_running == True:
            return
        else:
            self.is_cropping = False
            video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv);;All Files (*)")
            if video_path:
                if self.is_running:
                    self.stop_prediction()  # Stop any ongoing prediction

                if self.cap and self.cap.isOpened():
                    self.cap.release()  # Close the previous video if it's open

                self.video_path = video_path
                self.cap = cv2.VideoCapture(self.video_path)
                success, frame = self.cap.read()
                if success:
                    self.original_frame = frame
                    self.frame_to_disp = frame
                    self.display_frame(frame)

                if self.csv_file:
                    self.csv_file.close()  # Close the previous CSV file if it exists
                    self.csv_file = None
            self.update_file_name_label()
            self.progress_bar.setValue(0)

    def crop_video(self):
        if self.is_running == True or self.original_frame is None:
            return
        else:
            self.is_cropping = True
            self.crop_coordinates = cv2.selectROI("Crop Video", self.original_frame)
            cv2.destroyAllWindows()

            # Crop the original frame using the selected coordinates
            if self.crop_coordinates:
                x, y, w, h = self.crop_coordinates
                cropped_frame = self.original_frame[y:y+h, x:x+w]

                # Convert the cropped frame to a format suitable for QImage
                height, width, channel = cropped_frame.shape
                bytes_per_line = 3 * width
                byte_string = cropped_frame.tobytes()

                # Create the QImage from the byte string
                q_image = QImage(byte_string, width, height, bytes_per_line, QImage.Format.Format_BGR888)

                self.frame_to_disp = q_image

                # Display the cropped frame
                self.display_frame(q_image)

    def display_frame(self, frame):
        if isinstance(frame, QImage):
            q_image = frame
        else:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

        scaled_image = q_image.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setPixmap(QPixmap.fromImage(scaled_image))

    
    def start_prediction(self):
        if self.original_frame is not None:
            print("Starting predictions")
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_path)

            if not self.cap.isOpened():
                return

            if self.prediction_thread is not None:
                # If a prediction thread is already running, stop it gracefully
                self.stop_prediction()

            if not self.csv_file:
                self.csv_file = open(self.csv_filename, 'w', newline='')
                self.csv_writer = csv.writer(self.csv_file)
                self.csv_writer.writerow(['Frame', 'Class', 'X', 'Y'])

            self.is_running = True
            self.is_stopping = False  # Reset the stopping flag

            # Disable UI elements during prediction
            self.open_btn.setDisabled(True)
            self.play_btn.setDisabled(True)
            self.crop_btn.setDisabled(True)

            # Load the AI model asynchronously
            self.prediction_thread = PredictionThread(self, self.video_path, self.csv_filename, self.csv_file, self.csv_writer)
            self.prediction_thread.update_frame.connect(self.display_frame)
            self.prediction_thread.update_progress.connect(self.update_progress_bar)
            self.prediction_thread.finished.connect(self.prediction_finished)
            self.prediction_thread.start()
        else:
            return
        
    def enable_buttons(self):
        self.open_btn.setEnabled(True)
        self.play_btn.setEnabled(True)
        self.crop_btn.setEnabled(True)
    
    def prediction_finished(self):
        self.is_running = False
        self.prediction_thread = None

        # Re-enable the buttons
        self.enable_buttons()

    def stop_prediction(self):
        if self.is_running:
            self.is_stopping = True  # Set the stopping flag
            self.is_running = False  # Set the running flag to False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatMapWindow()
    window.show()
    sys.exit(app.exec())