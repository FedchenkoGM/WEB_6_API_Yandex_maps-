import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import requests
from PyQt5.QtCore import Qt


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(700, 100, 700, 550)
        self.setWindowTitle('Работа с картой')

        self.map = QLabel(self)
        self.map.move(50, 30)
        self.map.resize(400, 400)
        pixmap = QPixmap('tmp.png')
        pixmap = pixmap.scaled(400, 400)
        self.map.setPixmap(pixmap)

        self.map_ll = [87.3, 55.7]
        self.map_l = 'map'
        self.map_zoom = 7
        self.delta = 0.5

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
            "l": self.map_l,
            'z': self.map_zoom
        }

        response = requests.get('https://static-maps.yandex.ru/1.x/',
                                params=map_params)
        with open('map.png', mode='wb') as f:
            f.write(response.content)

        pixmap = QPixmap()
        pixmap.load('map.png')
        self.map.setPixmap(pixmap)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_PageUp:
            if self.map_zoom < 17:
                self.map_zoom += 1
        elif key == Qt.Key_PageDown:
            if self.map_zoom > 0:
                self.map_zoom -= 1

        elif key == Qt.Key_Right:
            self.map_ll[0] += self.delta
            if self.map_ll[0] > 180:
                self.map_ll[0] = self.map_ll[0] - 360
        elif key == Qt.Key_Left:
            self.map_ll[0] -= self.delta
            if self.map_ll[0] < 0:
                self.map_ll[0] = self.map_ll[0] + 360
        elif key == Qt.Key_Up:
            if self.map_ll[1] + self.delta < 90:
                self.map_ll[1] += self.delta
        elif key == Qt.Key_Down:
            if self.map_ll[1] - self.delta > -90:
                self.map_ll[1] -= self.delta
        else:
            return

        self.refresh_map()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# задача 1 + 2 + 3
if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())