import sys
from PyQt5.QtWidgets import *
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
        self.Input_line = QLineEdit(self)
        self.Input_line.move(0, 450)
        self.Input_line.resize(520, 20)

        self.Button = QPushButton("search", self)
        self.Button.move(520, 450)
        self.Button.resize(80, 20)
        self.Button.clicked.connect(self.search)
        self.NeedPt = False


        self.map_ll = [87.3, 55.7]
        self.map_l = 'map'
        self.map_z = 7
        self.delta = 0.5

        self.refresh_map()

    def search(self):
        toponym_to_find = self.Input_line.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            pass

        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]

        toponym_coodrinates = toponym["Point"]["pos"]

        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

        self.map_ll = [toponym_longitude, toponym_lattitude]
        self.NeedPt = True
        self.refresh_map()

    def refresh_map(self):
        if self.NeedPt:
            map_params = {
                "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
                'l': self.map_l,
                "z": self.map_z,
                "pt": f'{self.map_ll[0]},{self.map_ll[1]}',
            }
        else:
            map_params = {
                "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
                'l': self.map_l,
                "z": self.map_z,
            }

        res = requests.get('https://static-maps.yandex.ru/1.x', params=map_params)

        with open('map.png', 'wb') as file:
            file.write(res.content)

        pixmap = QPixmap('map.png')
        self.map.setPixmap(pixmap)


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_PageUp and self.map_z < 17:
            self.map_z += 1
        elif key == Qt.Key_PageDown and self.map_z > 0:
            self.map_z -= 1
        elif key == Qt.Key_Up and self.map_ll[1] + self.delta < 90:
            self.map_ll[1] += self.delta
        elif key == Qt.Key_Down and self.map_ll[1] + self.delta > -90:
            self.map_ll[1] -= self.delta
        elif key == Qt.Key_Right:
            self.map_ll[0] += self.delta
            if self.map_ll[0] > 180:
                self.map_ll -= 360
        elif key == Qt.Key_Left:
            self.map_ll[0] -= self.delta
            if self.map_ll[0] < 0:
                self.map_ll += 360
        else:
            return
        self.refresh_map()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())