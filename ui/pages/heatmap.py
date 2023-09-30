import cv2
import numpy as np
import csv
from math import ceil
from ultralytics import YOLO
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QSizePolicy, QDialog, QVBoxLayout, QProgressBar
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6 import uic
import sys
import os
import pickle 
from run_draft_logic.utils import load_theme
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import TitleBar

# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

script_dir = os.path.dirname(os.path.abspath(__file__))

class PredictionThread(QThread):
    update_frame = pyqtSignal(QImage)
    update_progress = pyqtSignal(float)

    def __init__(self, parent, video_path, temp_pickle):
        super(PredictionThread, self).__init__(parent)
        self.parent = parent
        self.video_path = video_path
        self.temp_pickle = temp_pickle

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        frame_skip_factor = 1
        results = None

        # Create an empty list to hold detection data
        data_to_save = []

        while cap.isOpened() and self.parent.is_running:
            success, frame = cap.read()

            if success:
                frame_count += 1

                if frame_count % frame_skip_factor != 0:
                    continue

                results = self.parent.model.predict(frame, conf=0.5)

                # Process detection results and append data to the list
                if results:
                    for r in results:
                        for box in r.boxes:
                            class_id = box.cls
                            pred = box.xyxy[0]
                            x_min = pred[0].item()
                            y_min = pred[1].item()
                            x_max = pred[2].item()
                            y_max = pred[3].item()

                            # Format the data as a tuple and append it to the list
                            detection_data = (
                                frame_count,
                                self.parent.model.names[int(class_id)],
                                int(class_id),
                                round((x_min + x_max) / 2, 4),  
                                round((y_min + y_max) / 2, 4)
                            )

                            data_to_save.append(detection_data)

                annotated_frame = results[0].plot()
                q_image = QImage(annotated_frame.data, annotated_frame.shape[1], annotated_frame.shape[0],
                                 annotated_frame.strides[0], QImage.Format.Format_BGR888)

                self.update_frame.emit(q_image)

                progress_percentage = (frame_count / (total_frames - (total_frames % frame_skip_factor))) * 100
                self.update_progress.emit(progress_percentage)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if self.parent.is_stopping:
                    break

            else:
                break

        cap.release()
        self.parent.is_running = False
        self.parent.prediction_thread = None

        # Save the list of detection data to a pickle file
        with open(self.temp_pickle, 'wb') as pickle_file:
            pickle.dump(data_to_save, pickle_file)

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
        self.stop_btn.clicked.connect(self.stop_prediction)
        self.save_btn.clicked.connect(self.save_as_csv)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lock = QThread()

        self.cap = None
        self.video_path = ""
        self.temp_pickle = "outputs/temp.pickle"  # Replace with the desired pickle file path
        self.frame_count = 0

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
        self.progress_bar.setValue(int(percentage))

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def closeEvent(self, event):
        # Stop the prediction thread and remove the pickle file when the window is closed
        if self.is_running:
            self.stop_prediction()
            self.prediction_thread.wait()  # Wait for the thread to finish gracefully

        if os.path.exists(self.temp_pickle):
            os.remove(self.temp_pickle)  # Remove the pickle file if it exists
        event.accept()

    def load_ai_model(self):
        self.model = YOLO('model/yolov8_custom.pt')

    def update_file_name_label(self):
        file_name = os.path.basename(self.video_path)
        self.file_name_label.setText(f"{file_name}")
        self.file_name_label.setFixedWidth(120)

    def resize_video(self, event):
        if self.original_frame is not None and self.is_running == False:
            self.display_frame(self.frame_to_disp)

    def open_video_file(self):
        if self.is_running == True:
            return
        else:
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

                self.update_file_name_label()
                self.progress_bar.setValue(0)
                return True
            else:
                return False

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

            self.is_running = True
            self.is_stopping = False  # Reset the stopping flag

            # Disable UI elements during prediction
            self.open_btn.setDisabled(True)
            self.play_btn.setDisabled(True)

            # Load the AI model asynchronously
            self.prediction_thread = PredictionThread(self, self.video_path, self.temp_pickle)
            self.prediction_thread.update_frame.connect(self.display_frame)
            self.prediction_thread.update_progress.connect(self.update_progress_bar)
            self.prediction_thread.finished.connect(self.prediction_finished)
            self.prediction_thread.start()
        else:
            return
    
    def save_as_csv(self):
        if not self.is_running:
            try:
                with open(self.temp_pickle, 'rb') as pickle_file:
                    data = pickle.load(pickle_file)

                # Use QFileDialog to choose the CSV file save location
                options = QFileDialog.Option.ReadOnly  # Ensure the user can select a save location
                csv_filename, _ = QFileDialog.getSaveFileName(self, "Save as CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)

                if csv_filename:
                    # Open the selected CSV file for writing
                    with open(csv_filename, 'w', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(['Frame', 'Class', 'Class_ID', 'X', 'Y'])

                        # Iterate through the data and write each entry to the CSV file
                        for entry in data:
                            frame_count, class_name, class_id, x_center, y_center = entry
                            csv_writer.writerow([frame_count, class_name, class_id, x_center, y_center])

                    if os.path.exists(self.temp_pickle):
                        os.remove(self.temp_pickle)
                else:
                    return

            except FileNotFoundError:
                print(f"Error: File '{self.temp_pickle}' not found.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")


    def enable_buttons(self):
        self.open_btn.setEnabled(True)
        self.play_btn.setEnabled(True)

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
