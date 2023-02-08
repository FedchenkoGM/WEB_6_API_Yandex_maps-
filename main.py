import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import requests
from PyQt5.QtCore import Qt
import  math


coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
coord_to_geo_y = 0.0000428


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

        self.text = QLabel(self)
        self.text.setGeometry(50, 450, 500, 50)
        self.text.setText('')

        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_z = 7
        self.delta = 0.5

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
            "l": self.map_l,
            'z': self.map_z
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
            if self.map_z < 17:
                self.map_z += 1
        elif key == Qt.Key_PageDown:
            if self.map_z > 0:
                self.map_z -= 1

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

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == Qt.RightButton:
            self.add_org(event.pos())

    def add_org(self, pos):
        point = self.screen_to_geo(pos)
        org = self.find_business((point[0], point[1]))
        # print('1====',org)

        if not org:
            self.text.setText('')
            return

        org_point = org["geometry"]["coordinates"]
        # print(org_point)
        org_lon = float(org_point[0])
        org_lat = float(org_point[1])

        self.text.setText(org['properties']['name'])

    def find_business(self, ll):
        lll = f"{ll[0]},{ll[1]}"
        geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={lll}&format=json"
        geocoder_request = geocoder_request_template.format(**locals())
        response = requests.get(geocoder_request)
        json_response = response.json()
        features = json_response["response"]["GeoObjectCollection"]["featureMember"]
        text = (features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text'])


        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        search_params = {
            "apikey": api_key,
            "lang": "ru_RU",
            "ll": f"{ll[0]},{ll[1]}",
            "spn": "0.3,0.3",
            "type": "biz",
            "text": text,
            #"text": f"{ll[0]},{ll[1]}",
        }

        response = requests.get(search_api_server, params=search_params)
        if not response:
            raise RuntimeError(
                """Ошибка выполнения запроса:
                {request}
                Http статус: {status} ({reason})""".format(
                    request=search_api_server, status=response.status_code, reason=response.reason))

        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первую найденную организацию.
        organizations = json_response["features"]
        # print('ау    ', search_params['text'], ll, organizations)
        return organizations[0] if organizations else None


    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        pos = pos.x(), pos.y()
        dy = 200 - pos[1]
        dx = pos[0] - 200
        lx = self.map_ll[0] + dx * coord_to_geo_x * math.pow(2, 15 - self.map_z)
        ly = self.map_ll[1] + dy * coord_to_geo_y * math.cos(math.radians(self.map_ll[1])) * math.pow(2,
                                                                                          15 - self.map_z)
        return lx, ly


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# задача 1 + 2 + 3
if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())