from swipe_speed import *
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent


min_value = get_min_value()
max_value = get_max_value()


class SliderValueSender(QObject):
    slider_value_changed = pyqtSignal(int, int)


class RangeSlider(QWidget):
    def __init__(self, min_value, max_value):
        super().__init__()

        self.init_ui(min_value, max_value)
        self.size = 0
        self.setAcceptDrops(True)
        self.file = ''

    def init_ui(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

        self.center_frame = int((min_value + max_value)*0.5)

        layout = QVBoxLayout()

        status_line_layout = QHBoxLayout()
        self.lb_status = QLabel("Drag the sample file and bring it here")
        status_line_layout.addWidget(self.lb_status)
        layout.addLayout(status_line_layout)

        first_line_layout = QHBoxLayout()

        self.file_in = QLineEdit()
        self.file_in.setText('file name')
        first_line_layout.addWidget(self.file_in)

        self.start_in = QLineEdit()
        self.start_in.setText(str(min_value))
        first_line_layout.addWidget(self.start_in)

        self.end_in = QLineEdit()
        self.end_in.setText(str(max_value))
        first_line_layout.addWidget(self.end_in)

        self.button_save = QPushButton("save")
        # first_line_layout.addWidget(self.button_save)

        layout.addLayout(first_line_layout)
        second_line_layout = QHBoxLayout()

        self.min_label = QLabel(f"{min_value}: {min_value + int(size*0.2)}")
        second_line_layout.addWidget(self.min_label)

        self.min_slider = QSlider()
        self.min_slider.setOrientation(Qt.Horizontal)
        self.min_slider.setMinimum(min_value)
        self.min_slider.setMaximum(self.center_frame)
        self.min_slider.setTickPosition(QSlider.TicksBothSides)
        self.min_slider.setTickInterval(10)
        self.min_slider.setValue(min_value + int(size*0.2))
        self.min_slider.setStyleSheet("""
            QSlider {
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #CCCCCC;
                margin: 2px 0;
            }
            QSlider::sub-page:horizontal {
                background: #66CCFF;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #CCCCCC;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #66CCFF;
                border: 1px solid #999999;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #55AAFF;
            }
        """)

        second_line_layout.addWidget(self.min_slider)

        self.max_slider = QSlider()
        self.max_slider.setOrientation(Qt.Horizontal)
        self.max_slider.setMinimum(self.center_frame)
        self.max_slider.setMaximum(self.max_value)
        self.max_slider.setTickPosition(QSlider.TicksBothSides)
        self.max_slider.setTickInterval(10)
        self.max_slider.setValue(max_value - int(size*0.2))
        self.max_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #CCCCCC;
                margin: 2px 0;
            }
            QSlider::sub-page:horizontal {
                background: #CCCCCC;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #66CCFF;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #66CCFF;
                border: 1px solid #999999;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
        second_line_layout.addWidget(self.max_slider)

        self.max_label = QLabel(f"{max_value - int(size*0.2)}: {max_value}")
        second_line_layout.addWidget(self.max_label)

        self.button = QPushButton("Make")
        second_line_layout.addWidget(self.button)

        # 슬라이더 값 변경 시 호출되는 슬롯 설정
        self.min_slider.valueChanged.connect(self.update_min_label)
        self.max_slider.valueChanged.connect(self.update_max_label)
        layout.addLayout(second_line_layout)
        self.setLayout(layout)

        self.sender = SliderValueSender()
        self.button.clicked.connect(self.send_slider_value)
        self.button_save.clicked.connect(self.save_values)

    def save_values(self):
        set_file_name(self.file)
        set_start_frame(int(self.start_in.text()))
        set_end_frame(int(self.end_in.text()))
        self.min_value = int(self.start_in.text())
        self.max_value = int(self.end_in.text())
        self.update_min_label

        self.size = self.max_value - self.min_value
        size = self.size
        self.center_frame = self.min_value + int((size)*0.5)
        print(size, self.center_frame)
        self.min_slider.setMinimum(self.min_value)
        self.min_slider.setMaximum(self.center_frame)
        self.max_slider.setMinimum(self.center_frame)
        self.max_slider.setMaximum(self.max_value)

    def send_slider_value(self):

        set_front_value(self.min_slider.value())
        set_back_value(self.max_slider.value())
        self.lb_status.setText("making...")
        QApplication.processEvents()
        make()
        self.lb_status.setText("Done")

    def update_min_label(self, value):
        self.min_label.setText(f"{self.min_value}: {value}")

    def update_max_label(self, value):
        self.max_label.setText(f"{value}: {self.max_value}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_urls = [url.toLocalFile() for url in event.mimeData().urls()]
            if file_urls:
                file_path = file_urls[0]
                self.file = file_path
                self.file_str = os.path.basename(file_path)
                self.file_in.setText(self.file_str)
                print("Dropped file:", self.file)

                if self.file_str == 'sireum.mp4':
                    self.min_value = 409
                    self.max_value = 510
                elif self.file_str == 'soccer.mp4':
                    self.min_value = 120
                    self.max_value = 164
                elif self.file_str == 'tennis1.mp4':
                    self.min_value = 68
                    self.max_value = 116
                elif self.file_str == 'tennis2.mp4':
                    self.min_value = 75
                    self.max_value = 122
                self.start_in.setText(str(self.min_value))
                self.end_in.setText(str(self.max_value))

                self.save_values()
                self.lb_status.setText(
                    "1) Move the [slider]  2) click the [Make] button")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    slider_window = RangeSlider(min_value, max_value)
    slider_window.resize(1000, 200)
    slider_window.show()
    sys.exit(app.exec_())
