import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import requests


# 37.618920 55.756994 0.5
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
        self.map_z = 7

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": f"{self.map_ll[0]},{self.map_ll[1]}",
            "l": self.map_l,
            "z": self.map_z
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)

        with open('map.png', mode='wb') as f:
            f.write(response.content)

        pixmap = QPixmap('map.png')
        self.map.setPixmap(pixmap)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
