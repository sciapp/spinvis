#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import partial
import gr3
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import test
from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout,QRadioButton ,QButtonGroup,QLineEdit, QVBoxLayout, QApplication, QPushButton, QLabel, QSlider)     #Import der versch. QtWidgets
from PyQt5.QtCore import Qt
import math
from PyQt5.QtGui import QPixmap
import numpy as np
linksdreh = 1
hochdreh = 1
kamerasteuerung = False


    #Eingabe der Datein aus tet.txt

class MainWindow(QtWidgets.QWidget):                                    #Klasse MainWindow ist das uebergeordnete Fenster, dass fuer Simulation und Gui unterteilt wird
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)                               #Uebernahme von uebergebenen Daten
        self._first_paint = True
        self._camera_angle = 0.0
        self.initUI()
        pass

    def initUI(self):
        self.setWindowTitle('PyQt5/GR3 molecule plot example')
        self.m = GLWidget()                                             #Erstellung der Zwei zentralen Fenster: das GLWidget m, mit der 3D Darstellung
        self.w = GUIWindow(self.m)                                      #Und das GUIWindow w, dass m uebergeben bekommt um die Kameraperspektive per Regler zu veraendern
        self.m.setMinimumSize(1000, 1000)
        self.hbox = QHBoxLayout()                                       #Horizontales Layout umd beides nebeneinander zulegen
        self.hbox.addWidget(self.m)
        self.hbox.addWidget(self.w)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(0)                                         #Abstand 0 setzen um beides direkt nebeneinander zu haben
        self.setLayout(self.hbox)

    def keyPressEvent(self, QKeyEvent):
        global linksdreh, kamerasteuerung
        kamerasteuerung = True
        print("Knopf gedrueckt")
        print(QKeyEvent.key())
        if QKeyEvent.key() == 70:
            linksdreh += 0.1
        
        self.m.update()


class GUIWindow(QtWidgets.QWidget):                                     #GUI Window setzt sich aus einzelnen Windows die vertikal unteieinander gelegt wurden zusammen
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebergabe des GLwindows als lokale private variable
        self.initUI()
        pass

    def initUI(self):
        self.k = SliderWindow(self._glwindow)                           #Slider Window fuer Kamerasteuerung per Slider
        self.t = ScreenWindow(self._glwindow)                           #Screenwindow fuer Screenshot steuerung
        self.l = LadeWindow(self._glwindow)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch(0.5)
        self.vbox.addWidget(self.k)
        self.vbox.addWidget(self.t)
        self.vbox.addWidget(self.l)
        self.vbox.addStretch(0.5)
        self.setLayout(self.vbox)
        pass

    def mousePressEvent(self, QMouseEvent):
        global kamerasteuerung
        kamerasteuerung = True
        print("Auf Gui geklickt")

class LadeWindow(QtWidgets.QWidget):
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.lade_label = QtWidgets.QLabel()
        self.lade_label.setText("Load new set of spins from a txt file:")
        self.lade_button = QPushButton('Laden', self)
        self.lade_button.setFixedSize(100, 30)
        self.lade_button.clicked.connect(self.lade_datei)
        self.hbox = QHBoxLayout()
        #self.hbox.addStretch(0.5)
        self.hbox.addWidget(self.lade_label)
        self.hbox.addWidget(self.lade_button)
        self.setLayout(self.hbox)

    def lade_datei(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        eingabe, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;", options=options)
        if (not eingabe):
            pass
        else:
            self._glwindow.data_path = eingabe
            self._glwindow.setDataSet()

class ScreenWindow(QtWidgets.QWidget):
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.fullbox = QHBoxLayout()                                    #Fullbox beinhaltet Screenshotknopf, Radiobuttons und Eingabe Zeile, jeweils in VBox mit Labeln


        self.screenbox = QVBoxLayout()                                  #Screenbox beinhaltet das Label und den Knopf names Screenshot

        self.lbl = QLabel()
        self.screenbutton = QPushButton('Screenshot', self)
        self.screenbutton.setFixedSize(100, 30)
        self.screenbutton.clicked.connect(self.doScreenshot)
        self.lbl.setText("Screenshot")
        self.lbl.setFixedSize(100, 30)

        self.screenbox.addWidget(self.lbl)
        self.screenbox.addWidget(self.screenbutton)


        self.fileVBox = QVBoxLayout()                                   #Filebox beinhaltet die Eingabezeile und das Label

        self.fileName = QLineEdit()
        self.fileLabel = QLabel()
        self.fileLabel.setText("Dateiname:")

        self.fileVBox.addWidget(self.fileLabel)
       # self.fileVBox.addWidget(self.fileName)


        self.checkboxbox = QHBoxLayout()                                #Checkboxbox beinhaltet 2 HBoxen, die je ein Label und ein Radiobutton haben


        self.pngbox = QVBoxLayout()

        self.pngcheck = QRadioButton()
        self.pngcheck.setChecked(True)
        self.pnglabel = QLabel()
        self.pnglabel.setText("PNG")
        self.pngcheck.toggle()

        self.pngbox.addWidget(self.pnglabel)
        self.pngbox.addWidget(self.pngcheck)

        self.checkboxmanagment = QButtonGroup()                         #Mit der Buttongroup werden die Radiobuttons auf exklusiv gestellt

        self.htmlbox = QVBoxLayout()

        self.htmlcheck = QRadioButton()
        self.htmlcheck.setChecked(False)
        self.htmllabel = QLabel()
        self.htmllabel.setText("HTML")

        #self.pngcheck..connect(self.pngChange)
        #self.htmlcheck.stateChanged.connect(self.htmlChange)

        self.checkboxmanagment.addButton(self.pngcheck)                 #Hinzufuegen der Radiobuttons und dann das setzen der Gruppe auf exklusiv
        self.checkboxmanagment.addButton(self.htmlcheck)
        self.checkboxmanagment.setExclusive(True)                       #Exklusiv, sodass immer nur genau ein Knopf an sein kann

        self.htmlbox.addWidget(self.htmllabel)
        self.htmlbox.addWidget(self.htmlcheck)

        self.checkboxbox.addLayout(self.pngbox)
        self.checkboxbox.addLayout(self.htmlbox)

        self.fullbox.addLayout(self.screenbox)                          #Hinzufuegen der einzelnen Boxen zu der Gesamtbox
        self.fullbox.addLayout(self.checkboxbox)
        self.fullbox.addLayout(self.fileVBox)
        self.setLayout(self.fullbox)
        pass

    def doScreenshot(self):
        if self.pngcheck.isChecked() == True:                           #Wenn die Png Box an ist dann wird der Dateiname auf Variable gesetzt und das ganze anf das
            dateiname = self.fileName.text()                            #glwindw uebergeben, da ansonsten zu fehlern kommt
            self._glwindow.export(dateiname)

        else:

            test.ScreenShoot(self.fileName.text() , "html", 1000, 1000) #Test.screenshot ruft gr3.export mit html auf
        self.update()
        print("Photoshoot")
        pass



class SliderWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebergabe des glwindow
        self.initUI()
        pass

    def initUI(self):
        global sliderval, linksdreh                                     #Globale Variablen sliderval und linksdreh zur steuerung
        self.hbox = QHBoxLayout()                                       #Beinhaltet 3 Slider, 1 zum zoomen, 1 fuer links und rechts und 1 fuer oben und unten

        self.left_right_slider_label = QtWidgets.QLabel()
        self.left_right_slider_label.setText("Horizontal Slider")
        self.leftslid = QSlider(Qt.Horizontal)                          #Erstellungs des linksrechtssliders
        self.leftslid.setValue(50)                                      #Startwert auf 50
        self.leftslid.setFocusPolicy(Qt.NoFocus)
        self.leftslid.valueChanged[int].connect(self.changeLeftValue)   #Bei aenderung wird changeLeftValue aufgerufen
        self.vertival_slider_box = QVBoxLayout()
        self.vertival_slider_box.addWidget(self.left_right_slider_label)
        self.vertival_slider_box.addWidget(self.leftslid)
        self.vertival_slider_box.addStretch(0.5)

        self.up_down_slider_label = QtWidgets.QLabel()
        self.up_down_slider_label.setText("Vertical Slider")
        self.upslid = QSlider(Qt.Vertical)                              #Erstellung des Hochundruntersliders
        self.upslid.setFixedSize(50, 75)                                #Kriegt feste groesse, da er sich sonst ueber ganzes fenster erstreckt
        self.upslid.setValue(50)                                        #Startwert ist 50
        self.upslid.setFocusPolicy(Qt.NoFocus)
        self.upslid.valueChanged[int].connect(self.changeUpValue)       #Bei Aenderung wird changeUpValue aufgerufen
        self.horizontal_slider_box = QVBoxLayout()
        self.horizontal_slider_box.addWidget(self.up_down_slider_label)
        self.horizontal_slider_box.addWidget(self.upslid)
        self.horizontal_slider_box.addStretch(0.5)

        self.hbox.addLayout(self.vertival_slider_box)
        self.hbox.addLayout(self.horizontal_slider_box)
        self.setLayout(self.hbox)

    def changeUpValue(self, value):
        global hochdreh, kamerasteuerung                                                 #Globale Variable hochdreh wird benutzt und veraendert
        kamerasteuerung = True
        hochdreh = ((value/100)+1)*math.pi                              #Setzt den Wert des Sliders auf das Pandan zwischen 0 und pi fuer die Kugelformel
        self._glwindow.update()                                         #Update des Fensters um aenderung anzuszeigen
        #print("Up")


    def changeLeftValue(self, value):
        global linksdreh, kamerasteuerung                                                #Globale Variable linskdreh wird benutzt und veraendert
        kamerasteuerung = True
        linksdreh = ((value/100)+1)*math.pi*2                           #Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel
        self._glwindow.update()                                         #Update des Fensters um aenderung anzuszeigen
        #print("left")


class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_paint = True
        self._camera_angle = 0.0
        self._drawSpin = True
        self._exportScreen = False                                      #exportScreen wird beim Knopfdruck auf True gestellt und triggert so export()
        self.PcVektor = np.array([test.getCameraWerte(0),test.getCameraWerte(1),test.getCameraWerte(2)])
        self.momentanerKameraVektor = np.array([test.getCameraWerte(0),test.getCameraWerte(1),test.getCameraWerte(2)])
        self.camera_vektor_length = np.linalg.norm(self.momentanerKameraVektor)
        self.PaVektor = np.array([test.getCameraWerte(0),test.getCameraWerte(1),test.getCameraWerte(2)])
        self._radius = 2
        self.fokusPunkt = np.array([0.0, 0.0, 0.0])
        self.newUpV = np.array([0.0, 0.0, 1.0])
        self._startPWerte = []
        self._ersteMalGedrueckt = False
        self._mausY = 1.0
        self._mausZ = 2.0
        self.data_path = ""
        self.initUI()
        pass

    def export(self, stringname):                                       #Export Funktion im GLWindow um Freeze zu vermeiden
        self._exportScreen = True
        self.screendateiname = stringname                               #Benutzt den uebergebenen dateinamen
        self.update()

    def initUI(self):
        x = 0
        y = 0
        pass

    def initializeGL(self):
        gr3.init()
       # test.eingabe()
        gr3.usecurrentframebuffer()
        test.grSetUp()                          #GrSetup mit Zoomvariable und den Winkeln fuer die Kugelgleichung
        if self._drawSpin:
            self.spinDraw()
            self._drawSpin = False




    def resizeGL(self, width, height):
        pass

    def spinDraw(self):
        test.grDrawSpin(1000, 1000, self.devicePixelRatio())


    def paintGL(self):
        global linksdreh, hochdreh, kamerasteuerung
        tilt = linksdreh
        azimuth = hochdreh
        gr3.usecurrentframebuffer()
        print(kamerasteuerung)
        if kamerasteuerung:
            test.grCameraGuiChange(azimuth, tilt)                          #GrSetup mit Zoomvariable und den Winkeln fuer die Kugelgleichung
        else:
            test.grCameraArcBallChange(self.momentanerKameraVektor)
        if self._exportScreen:                                          #Screenshot und setzen von export screen auf False fuer neuen Durchlauf
            test.ScreenShoot(self.screendateiname, "png", 500, 500)
            self._exportScreen = False
        gr3.drawimage(0, 1000, 0, 1000,
                      self.devicePixelRatio()*1000, self.devicePixelRatio()*1000, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)


    def rotation_matrix(self, axis, theta):
        axis = np.array(axis)
        if (math.sqrt(np.dot(axis, axis)) != 0):
            axis = axis / math.sqrt(np.dot(axis, axis))
            a = math.cos(theta / 2.0)
            b, c, d = -axis * math.sin(theta / 2.0)
            aa, bb, cc, dd = a * a, b * b, c * c, d * d
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                             [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                             [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    def mouseMoveEvent(self, e):
        if self._mausX == e.x() and self._mausY == self.height() - e.y():
            return
        self._mausX = e.x()
        self._mausY = self.height() - e.y()
        self.calculate_koordinates_from_mouseclick(self.PcVektor)
        self.dreheKamera()
        self.PaVektor = list(self.PcVektor)
        self.update()

    def calculate_koordinates_from_mouseclick(self, list):
        list[0] = 2 * self._mausX / self.width() - 1
        list[1] = 2 * self._mausY / self.height() - 1
        if (math.sqrt(list[0] ** 2 + list[1] ** 2) <= self._radius / math.sqrt(2)):
            list[2] = math.sqrt(self._radius ** 2 - (list[0] ** 2 + list[1] ** 2))
        else:
            list[2] = self._radius ** 2 / (2 * (list[0] ** 2 + list[1] ** 2))

    def mousePressEvent(self, e):
        global kamerasteuerung
        kamerasteuerung = False
        print("Auf gl geklickt")
        self._mausX = e.x()
        self._mausY = self.height() - e.y()
        self.calculate_koordinates_from_mouseclick(self.PaVektor)
        pass

    def set_momentaner_kameraVektor_in_test(self):
        test.dreiCameraWerte = list(self.momentanerKameraVektor)

    def recalculate_up_vector(self, forward_vector, up_vector):
        right_vector = np.cross(forward_vector, up_vector)
        up_vector = np.cross(right_vector, forward_vector)
        return up_vector / np.linalg.norm(up_vector)

    def dreheKamera(self):
        self.newUpV = self.recalculate_up_vector(self.momentanerKameraVektor, self.newUpV)

        skalar = np.dot(self.PaVektor, self.PcVektor)
        if skalar:
            u = np.cross(self.PaVektor, self.PcVektor)

            up_vector = self.newUpV
            forward_vector = self.momentanerKameraVektor
            right_vector = np.cross(forward_vector, up_vector)
            up_vector = np.cross(right_vector, forward_vector)
            forward_vector /= np.linalg.norm(forward_vector)
            right_vector /= np.linalg.norm(right_vector)
            up_vector /= np.linalg.norm(up_vector)
            u = u[0] * right_vector - u[1] * up_vector + u[2] * forward_vector

            norm = np.linalg.norm(u)
            theta = np.arctan(norm / skalar)

            if norm:
                print("Somethings happenin")
                self.newUpV = np.dot(self.rotation_matrix(u, theta), self.newUpV)
                self.momentanerKameraVektor = np.dot(self.rotation_matrix(u, theta), self.momentanerKameraVektor)
                self.momentanerKameraVektor *= self.camera_vektor_length
        self.set_momentaner_kameraVektor_in_test()
        test.setUpVektor(self.newUpV)
        test.grCameraArcBallChange(self.momentanerKameraVektor)
        self.update()

    def setDataSet(self):
        print("Setzte Daten")
        test.eingabe(self.data_path)
        gr3.usecurrentframebuffer()
        self.spinDraw()

        self.repaint()




def main():
    app = QtWidgets.QApplication(sys.argv)
    # Enable multisampling for smoother results`
    format = QtGui.QSurfaceFormat()
    format.setSamples(8)
    QtGui.QSurfaceFormat.setDefaultFormat(format)
    mein = MainWindow()                                                                                                 #Initialisierung von mein als Maindwindow, wo sich alles drin abspielt
    mein.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

