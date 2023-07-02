import sys
import threading
import mss
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QSizePolicy, QStatusBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage, QCursor

class ScreenCaptureThread(threading.Thread):
    def __init__(self, window, roi, max_diameter, min_diameter, mag, width):
        threading.Thread.__init__(self)
        self.window = window
        self.roi = roi # an array with four parameters defining top-left corner coordinates, height and width of the Region of Interest (ROI)
        self.max_diameter = max_diameter
        self.min_diameter = min_diameter
        self.mag = mag
        self.width = width
        self.counter = 0
        self.sum = 0
        self.average = 0
        self.detected_circles = []
        self.stopped = threading.Event()
        

    def run(self):
        with mss.mss() as sct:
            while not self.stopped.wait(0.01):
                sct_img = sct.grab(self.roi)
                img = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2RGB)

                # Apply Hough Circle detection
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

                # 1) so, we will measure the width of StreamMotion Live Screen using the Status Bar.
                # 2) This width equals to the 7031.2 microns / magnification of lens
                # 3) 7031.2/4 = 1757.8 micron, for example.
                # 4) So, the user will enter desired Radius in microns
                # 5) Since we detect 7031.2/mag [um] = width [px] our formulation should be:
                # 6) int(self.min_radius * self.width * self.mag / 7031.2)

                scale = self.width * self.mag / 7031.2
                
                circles = cv2.HoughCircles(gray_blur, cv2.HOUGH_GRADIENT, dp=1, 
                                           minDist=int(self.max_diameter * scale),
                                           param1=80, param2=40, 
                                           minRadius=int(self.min_diameter/2 * scale), 
                                           maxRadius=int(self.max_diameter/2 * scale))
                
                if circles is not None:
                    circles = np.round(circles[0,:]).astype("int")
                    for(x, y, r) in circles:
                        cv2.circle(img, (x, y), r, (255, 0, 0), 1)
                        diameter = round(r * 2 / scale, 3)
                        self.detected_circles.append(diameter)
                        if self.counter > 10000 or self.sum > 1000000:
                            self.counter = 0
                            self.sum = 0
                            self.average = 0
                        self.counter += 1
                        self.sum = self.sum + diameter
                        self.average = self.sum / self.counter
                        cv2.putText(img, f"Diameter: {diameter}", (x, y + r + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                
                cv2.putText(img, f"Counter {self.counter}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(img, f"Average {round(self.average,3)}", (100,150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(img, f"numpy.mean: {round(np.mean(self.detected_circles),3)}", (300,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(img, f"st dev: {round(np.std(self.detected_circles),3)}", (300,150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                
                
                
                #cv2.putText(img, f"Average: {diameter}", (self.roi[0]+20, self.roi[3]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)        
                
                

                    
                        
                h, w, ch = img.shape
                bytes_per_line = ch * w
                qt_img = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                self.window.update_image(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Onel Lab | Live Image Droplet Detector v2 ")
        self.setGeometry(1200,50,720,930)

        
        self.central_widget = QWidget(self)
        self.central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel(self)
        self.layout.addWidget(self.label)

        self.roi_labels = []
        self.roi_lineedits = []
        self.roi_values = []
        
        
        layoutLineTexts = QHBoxLayout(self)
        for i in range(8):
            
            lineedit = QLineEdit(self)
            if i == 0:
                label = QLabel(f"ROI {i+1}: y-coordinate of top-left corner ", self)
                lineedit.setText("50")  
            elif i == 1:
                label = QLabel(f"ROI {i+1}: x-coordinate of top-left corner", self)
                lineedit.setText("100")
            elif i == 2:
                label = QLabel(f"ROI {i+1}: x-coordinate of bottom-right corner", self)
                lineedit.setText("800")
            elif i == 3:
                label = QLabel(f"ROI {i+1}: y-coordinate of bottom-right corner", self)
                lineedit.setText("600")
            elif i == 4:
                label = QLabel(f"maxDiameter: ", self)
                lineedit.setText("80")
            elif i == 5:
                label = QLabel(f"minDiameter: ", self)
                lineedit.setText("70")
            elif i == 6:
                label = QLabel(f"magnification")
                lineedit.setText("4")
            elif i == 7:
                label = QLabel(f"Width length in pixels")
                lineedit.setText("1000")
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            lineedit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.roi_labels.append(label)
            self.roi_lineedits.append(lineedit)
            self.layout.addWidget(label)
            self.layout.addWidget(lineedit)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        # Start a QTimer to update the status bar message periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status_bar)
        self.update_interval = 500  # Set the desired update interval in milliseconds
        self.update_timer.start(self.update_interval)

        self.button = QPushButton("Start", self)
        self.button.clicked.connect(self.toggle_capture)
        self.layout.addWidget(self.button)

        self.setCentralWidget(self.central_widget)

        self.capture_thread = None
        self.is_capturing = False

    def toggle_capture(self):
        if self.is_capturing:
            self.stop_capture()
        else:
            roi_values = []
            for lineedit in self.roi_lineedits:
                value = int(lineedit.text())
                roi_values.append(value)
            max_diameter = int(self.roi_lineedits[4].text())
            min_diameter = int(self.roi_lineedits[5].text())
            mag = int(self.roi_lineedits[6].text())
            width = int(self.roi_lineedits[7].text())
            self.start_capture(roi_values, max_diameter, min_diameter, mag, width)

    def start_capture(self, roi_values, max_diameter, min_diameter, mag, width):
        self.button.setText("Stop")
        self.is_capturing = True
        roi = {"top": roi_values[0], "left": roi_values[1], "width": roi_values[2]-roi_values[1], "height": roi_values[3]-roi_values[0]}
        self.capture_thread = ScreenCaptureThread(self, roi, max_diameter, min_diameter, mag, width)
        self.capture_thread.start()

    def stop_capture(self):
        self.button.setText("Start")
        self.is_capturing = False
        self.capture_thread.stopped.set()
        self.capture_thread.join()
        self.capture_thread = None

    def update_image(self, pixmap):
        pixmap = pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Resize pixmap with smooth transformation
        self.label.setPixmap(pixmap)

    def update_status_bar(self):
        # Get the cursor position
        cursor_pos = QCursor.pos()
        x = cursor_pos.x()
        y = cursor_pos.y()

        # Show the cursor position in the status bar
        message = f"Cursor Position: x: {x}, y: {y} pixels. Avg diameter:  "
        self.statusBar.showMessage(message)

    def reset(self):
        self.reset_flag = True
        self.circle_count = 0
        self.circle_sum = 0
        self.circle_avg= 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
