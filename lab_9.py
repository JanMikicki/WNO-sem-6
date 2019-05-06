from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QPixmap)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton)
from xml.dom.minidom import *
import json
import time
import random
import threading

class Character(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)
        self.HP = 100.0


class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.mouse_pos = QPointF(0, 0)
        self.przycisk = 0  # 1 - lewy, 2 - prawy
        self.inside_bool = False

        scene = QGraphicsScene(self)

        self.worf = Character(QPixmap("Worf.png"))
        self.sword = Character(QPixmap("Sword.png"))
        self.q = Character(QPixmap("Mariachi_Q.png"))
        self.trombone = Character(QPixmap("trombone.png"))
        self.q.setPos(600, 25)
        self.worf.setPos(40, 20)
        self.sword.setPos(80, 100)
        self.trombone.setPos(530, 60)

        scene.setBackgroundBrush(QColor(24, 23, 28))
        scene.addItem(self.trombone)
        scene.addItem(self.worf)
        scene.addItem(self.sword)
        scene.addItem(self.q)

        scene.setSceneRect(0, 0, 800, 600)
        self.setScene(scene)
        self.setWindowTitle("Deja Q")

    def keyPressEvent(self, event):
        if event.key() == 83:
            save = { "worfposx": self.worf.x(), "worfposy": self.worf.y()}
            print(json.dumps(save))

            with open('data.txt', 'w') as outfile:
                json.dump(save, outfile)

        elif event.key() == 76:
            with open('data.txt') as json_file:
                data = json.load(json_file)
                self.worf.setX(data["worfposx"])
                self.worf.setY(data["worfposy"])

        elif event.key() == 82:

            dor = parse("myxml.xml")
            clicks = dor.getElementsByTagName("klik")

            start_time = time.time()
            interval = 1

            for i in range(len(clicks)):
                time.sleep(start_time + i * interval - time.time())

                pos = clicks[i].getElementsByTagName("Worfpos")[0]
                xpos = pos.getElementsByTagName("x")[0]
                ypos = pos.getElementsByTagName("y")[0]
                x_worf, y_worf = float(xpos.firstChild.data), float(ypos.firstChild.data)

                swordpos = clicks[i].getElementsByTagName("Swordpos")[0]
                sw_xpos = swordpos.getElementsByTagName("x_sword")[0]
                sw_ypos = swordpos.getElementsByTagName("y_sword")[0]
                x_sword, y_sword = float(sw_xpos.firstChild.data), float(sw_ypos.firstChild.data)

                self.worf.setPos(x_worf, y_worf)
                self.sword.setPos(x_sword, y_sword)
                app.processEvents()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.przycisk = 1
            if event.pos() in self.worf.sceneBoundingRect():
                self.worf.setPos(event.x() - 140, event.y() - 190)
        if event.button() == Qt.RightButton:
            self.przycisk = 2

    def mouseMoveEvent(self, event):
        if self.q.collidesWithItem(self.sword):
            self.hit(event)
            self.inside_bool = True
        else:
            self.inside_bool = False

        if self.przycisk == 1 and event.pos() in self.worf.sceneBoundingRect():
            self.worf.setPos(event.x() - 140, event.y() - 190)
            self.sword.setPos(self.worf.scenePos().x() + 40, self.worf.scenePos().y() + 80)

        elif self.przycisk == 2 and event.pos() in self.sword.sceneBoundingRect() and event.pos().x() < self.q.sceneBoundingRect().x():
            self.sword.setPos(event.x() - 80, event.y() - 40)  # przesuwanie miecza
            if (self.sword.scenePos() - self.worf.scenePos()).x() > 200.0:  # przesuwanie Worfa za mieczem
                self.worf.setPos(self.worf.x() + 10.0, self.worf.y())
            if (self.sword.scenePos() - self.worf.scenePos()).x() < -80.0:
                self.worf.setPos(self.worf.x() - 10.0, self.worf.y())

    def mouseReleaseEvent(self, event):

        self.q.setPos(self.q.scenePos().x() + time.time() % 20 - random.randint(1, 21), self.q.scenePos().y())
        self.trombone.setPos(self.q.x() - 70, self.trombone.y())

        dom = parse("myxml.xml")
        klik = dom.createElement("klik")
        worfpos_elem = dom.createElement("Worfpos")
        swordpos_elem = dom.createElement("Swordpos")

        x_elem = dom.createElement("x")
        x = dom.createTextNode(str(self.worf.x()))

        y_elem = dom.createElement("y")
        y = dom.createTextNode(str(self.worf.y()))

        x_elem.appendChild(x)
        y_elem.appendChild(y)

        worfpos_elem.appendChild(x_elem)
        worfpos_elem.appendChild(y_elem)

        #############################################

        x_sword_elem = dom.createElement("x_sword")
        x_sword_elem.appendChild(dom.createTextNode(str(self.sword.x())))

        y_sword_elem = dom.createElement("y_sword")
        y_sword_elem.appendChild(dom.createTextNode(str(self.sword.y())))

        swordpos_elem.appendChild(x_sword_elem)
        swordpos_elem.appendChild(y_sword_elem)

        #############################################

        klik.appendChild(worfpos_elem)
        klik.appendChild(swordpos_elem)
        dom.childNodes[1].appendChild(klik)

        with open("myxml.xml", "w") as f:
            dom.writexml(f)

        print(dom.toxml())

    def hit(self, event):
        if self.inside_bool is False:
            if event.y() > self.q.scenePos().y() + 285:
                print("nogi")
            elif event.y() > self.q.scenePos().y() + 120.:
                print("tulow")
            elif event.y() > self.q.scenePos().y():
                print("glowa (crit)")
                self.q.HP -= int(time.time() % 9) + 1

            self.q.HP -= 10.0
            print("Q HP = ", self.q.HP)
            if self.q.HP < 1.0:
                print("game over")
                sys.exit()


if __name__ == '__main__':
    import sys

    doc = Document();
    doc.appendChild(doc.createComment("My game xml"))
    node = doc.createElement('root')
    doc.appendChild(node)

    file_handle = open("myxml.xml", "w")
    doc.writexml(file_handle, newl='\n')
    file_handle.close()

    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    sys.exit(app.exec_())