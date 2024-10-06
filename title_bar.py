from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)

        self.title_label = QLabel("Matrizen Multiplikator", self)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))

        self.minimize_button = QPushButton("-", self)
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.setStyleSheet("background-color: #1ABC9C; color: white; border: none;")

        self.close_button = QPushButton("x", self)
        self.close_button.setFixedSize(40, 40)
        self.close_button.setStyleSheet("background-color: #E74C3C; color: white; border: none;")

        # Connect buttons to actions
        self.minimize_button.clicked.connect(self.parent().showMinimized)
        self.close_button.clicked.connect(self.parent().close)

        layout = QHBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.parent().move(self.parent().x() + delta.x(), self.parent().y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
