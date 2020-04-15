#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import partial
import gr3
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import test
import koor
from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout,QRadioButton ,QButtonGroup,QLineEdit, QVBoxLayout, QApplication, QPushButton, QLabel, QSlider)     #Import der versch. QtWidgets
from PyQt5.QtCore import Qt
import math
from PyQt5.QtGui import QPixmap
import numpy as np
linksdreh = 1
hochdreh = 1



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
        self.draw_window = GLWidget()                                             #Erstellung der Zwei zentralen Fenster: das GLWidget m, mit der 3D Darstellung
        self.gui_window = GUIWindow(self.draw_window)                                      #Und das GUIWindow w, dass m uebergeben bekommt um die Kameraperspektive per Regler zu veraendern
        self.draw_window.setMinimumSize(500, 500)
        self.gui_window.setFixedSize(400,500)
        self.gui_window.setFocusPolicy(Qt.ClickFocus)
        self.complete_window_hbox = QHBoxLayout()                                       #Horizontales Layout umd beides nebeneinander zulegen
        self.complete_window_hbox.addWidget(self.draw_window)
        self.complete_window_hbox.addWidget(self.gui_window)
        self.complete_window_hbox.setContentsMargins(0, 0, 0, 0)
        self.complete_window_hbox.setSpacing(0)                                         #Abstand 0 setzen um beides direkt nebeneinander zu haben
        self.setLayout(self.complete_window_hbox)
        #self.w.l.lade_datei()

    def keyPressEvent(self, QKeyEvent):
        global linksdreh, hochdreh
        print("Knopf gedrueckt")
        print(QKeyEvent.key())
        if QKeyEvent.key() == QtCore.Qt.Key_H:                                                                          #Tastatur-Abfrage, Pfeiltasten für Kamerasteuerung ähnlich zu den Slidern, H und G zum Zoomen in perspektive und A/B zum zoomen in orthograpisch
            self.draw_window.focus_point[0] += 1
            test.set_focus_point(self.draw_window.focus_point)
        if QKeyEvent.key() == QtCore.Qt.Key_G:
            self.draw_window.focus_point[0] -= 1
            test.set_focus_point(self.draw_window.focus_point)
        if QKeyEvent.key() == QtCore.Qt.Key_Right:
            self.draw_window.rotate_right()
        if QKeyEvent.key() == QtCore.Qt.Key_Left:
            self.draw_window.rotate_left()
        if QKeyEvent.key() == QtCore.Qt.Key_Up:
            self.draw_window.rotate_up()
        if QKeyEvent.key() == QtCore.Qt.Key_Down:
            self.draw_window.rotate_down()
        if QKeyEvent.key() == QtCore.Qt.Key_A:
            test.zoom_in_or_out_orthographic(0.1)
        if QKeyEvent.key() == QtCore.Qt.Key_B:
            test.zoom_in_or_out_orthographic(-0.1)
        self.draw_window.update()


class GUIWindow(QtWidgets.QWidget):                                     #GUI Window setzt sich aus einzelnen Windows die vertikal unteieinander gelegt wurden zusammen
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebergabe des GLwindows als lokale private variable
        self.initUI()
        pass

    def initUI(self):
        self.pgroup = QtWidgets.QGroupBox()
        self.p_win = ProjectionWindow(self._glwindow)
        self.slide_win = SliderWindow(self._glwindow)                           #Slider Boxlayout fuer Kamerasteuerung per Slider
        self.screen_win = ScreenWindow(self._glwindow)                           #Screen Boxlayout fuer Screenshot steuerung
        self.l_win = LadeWindow(self._glwindow)                                     #Lade Boxlayout um neuen Datensatz zu laden
        self.c_win = ColorWindow(self._glwindow)                                    #Color Boxlayout um Farbe für Hintergrund und Spins zu setzen
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.p_win)
        self.vbox.addWidget(self.slide_win)
        self.vbox.addWidget(self.screen_win)
        self.vbox.addWidget(self.l_win)
        self.vbox.addWidget(self.c_win)
        self.vbox.addStretch(0.5)
        self.setLayout(self.vbox)
        pass


class ProjectionWindow(QtWidgets.QWidget):                              #
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebergabe des GLwindows als lokale private variable
        self.initUI()
        pass

    def initUI(self):
        self.projection_box = QHBoxLayout()                                                                             #Eine grosse HBox die ein Label und eine weite HBox beinhaltet. In der sind 2 VBoxLayouts mit jeweils einem HLabel und einem RadioButton
        #self.projection_box.addStretch(0.5)
        self.projection_label = QtWidgets.QLabel()
        self.projection_label.setText("Waelen sie eine Perspektive")                                                    #Pop-Up das Hilftext anzeigt
        self.projection_label.setToolTip("The projectiontype  defines how a 3D object is pictured on a 2D screen. \n"
                                         "The parallel projection is simulating the effects of the real world. Objects \n"
                                         "farther away appear smaller. The orthographic projection depicts every object \n"
                                         "with the same size. It may reveal patterns in the data, that would else remain hidden \n")

        self.checkboxbox = QHBoxLayout()  # Checkboxbox beinhaltet 2 HBoxen, die je ein Label und ein Radiobutton haben

        self.perspective_box = QVBoxLayout()

        self.perspective_check = QRadioButton()
        self.perspective_check.setFocusPolicy(Qt.ClickFocus)

        self.perspective_label = QLabel()
        self.perspective_label.setText("Perspective")
        #self.perspective_check.toggle()


        self.perspective_box.addWidget(self.perspective_label)
        self.perspective_box.addWidget(self.perspective_check)

        self.checkboxmanagment = QButtonGroup()  # Mit der Buttongroup werden die Radiobuttons auf exklusiv gestellt

        self.orthographic_box = QVBoxLayout()

        self.orthographic_check = QRadioButton()
        self.orthographic_check.setChecked(True)
        self.orthographic_check.setFocusPolicy(Qt.ClickFocus)
        self.orthographic_label = QLabel()
        self.orthographic_label.setText("Orthographic")

        self.perspective_box.addWidget(self.orthographic_label)
        self.perspective_box.addWidget(self.orthographic_check)

        self.checkboxbox.addLayout(self.perspective_box)
        self.checkboxbox.addLayout(self.orthographic_box)

        self.orthographic_check.clicked.connect(self.radio_clicked)
        self.perspective_check.clicked.connect(self.radio_clicked)

        self.projection_box.addWidget(self.projection_label)
        self.projection_box.addLayout(self.checkboxbox)

        self.setLayout(self.projection_box)
        pass

    def radio_clicked(self):
        if self.orthographic_check.isChecked():
            print("Orthographic")
            test.is_projection = True
            test.set_projection_type_orthographic()
        else:
            print("Perspective")
            test.is_projection = False
            test.set_projection_type_perspective()
        self._glwindow.update()

    def is_orthographic_projection(self):
        if self.orthographic_check.isChecked():
            return True
        else:
            return False


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
        self.hbox = QHBoxLayout()                                                                                       #HBox mit einem Label und einem Knopf zum Laden
        #self.hbox.addStretch(0.5)
        self.hbox.addWidget(self.lade_label)
        self.hbox.addWidget(self.lade_button)
        self.setLayout(self.hbox)

    def lade_datei(self):
        options = QtWidgets.QFileDialog.Options()                                                                       #File Dialog zum auswählen der Daten-Datei
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        eingabe, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;", options=options)
        if (not eingabe):
            pass                                                                                                        #Falls nichts ausgewählt wird, wird kein neuer Datensatz gewählt
        else:
            self._glwindow.data_path = eingabe                                                                          #So wird der Eingabestring verwendet und der neue Datensatz gewählt
            self._glwindow.setDataSet()

class ColorWindow(QtWidgets.QWidget):
    def __init__(self,glwindow,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow                                       #Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.color_hbox = QHBoxLayout()                                                                                   #Hbox mt 2 Knöpfen und einem Label
        self.color_label = QLabel()
        self.color_label.setText("Waehlen sie eine Farbe")
        self.bg_color_button = QPushButton('Fuer den Hintergrund', self)
        self.bg_color_button.setFixedSize(100, 30)
        self.bg_color_button.clicked.connect(self.get_bg_color)
        self.spin_color_button = QPushButton('Fuer die Pfeile', self)
        self.spin_color_button.setFixedSize(100, 30)
        self.spin_color_button.clicked.connect(self.get_spin_color)
        self.color_dialog = QtWidgets.QColorDialog()                                                                    #Dialog Picker zum Farben auswählen
        self.color_hbox.addWidget(self.color_label)
        self.color_hbox.addWidget(self.bg_color_button)
        self.color_hbox.addWidget(self.spin_color_button)
        self.setLayout(self.color_hbox)

    def get_bg_color(self):
        bg_rgb = [c * 255 for c in test.bg_rgb]                                                                         #Umrechnung der momentanen Farbe als Stndardwert, Multiplikation der Werte von 0-1 auf 0-255
        selectedColor = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgb(*bg_rgb))                                  #Speichert die Auswahl des Farbendialogs und setzt Standardwert auf vorher umgewandelte Farben
        if selectedColor.isValid():
            self._glwindow.set_bg_color(selectedColor.getRgb())

    def get_spin_color(self):
        spin_rgb = [c * 255 for c in test.spin_rgb]                                                                     #Umrechnung der momentanen Farbe als Stndardwert, Multiplikation der Werte von 0-1 auf 0-255
        selectedColor = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgb(*spin_rgb))                                #Speichert die Auswahl des Farbendialogs und setzt Standardwert auf vorher umgewandelte Farben
        if selectedColor.isValid():
            self._glwindow.set_spin_color(selectedColor.getRgb())


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
        self.fileName.setFocusPolicy(Qt.ClickFocus)

        self.fileLabel = QLabel()
        self.fileLabel.setText("Dateiname:")

        self.fileVBox.addWidget(self.fileLabel)
        self.fileVBox.addWidget(self.fileName)


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
            if dateiname != "":
                self._glwindow.export(dateiname)
            else:
                print("The name must be at least one character long")
        else:

            test.ScreenShoot(self.fileName.text() , "html", self._glwindow.width(), self._glwindow.heigh()) #Test.screenshot ruft gr3.export mit html auf
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
        global hochdreh, linksdreh                                               #Globale Variable hochdreh wird benutzt und veraendert
        hochdreh = ((value/100)-1)*math.pi                              #Setzt den Wert des Sliders auf das Pandan zwischen 0 und pi fuer die Kugelformel
        test.grCameraGuiChange(hochdreh, linksdreh)
        self._glwindow.update()                                         #Update des Fensters um aenderung anzuszeigen

    def changeLeftValue(self, value):
        global linksdreh, hochdreh                                         #Globale Variable linskdreh wird benutzt und veraendert
        linksdreh = ((value/100)+1)*math.pi*2                           #Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel

        test.grCameraGuiChange(hochdreh, linksdreh)
        self._glwindow.update()                                         #Update des Fensters um aenderung anzuszeigen

class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_paint = True
        self._camera_angle = 0.0
        self._draw_spin = True                                           #Verhindert das bei jeder Kamerabewegung die Spins neu gezeichnet werden
        self._export_screen = False                                      #exportScreen wird beim Knopfdruck auf True gestellt und triggert so export()
        self.point_c_vektor = np.array([koor.camera_koordinates[0], koor.camera_koordinates[1], koor.camera_koordinates[2]])            #Ortsvektor des Punktes andem die Kamerabewegung aufhört
        self.current_camera_vector = np.array([koor.camera_koordinates[0], koor.camera_koordinates[1], koor.camera_koordinates[2]])     #Kameravektor
        self.camera_vektor_length = np.linalg.norm(koor.camera_koordinates)                                                          #Norm des Kameravektors
        self.point_a_vektor = np.array([koor.camera_koordinates[0], koor.camera_koordinates[1], koor.camera_koordinates[2]])            #Ortsvektor des Punktes andem die Kamerabewegung startet
        self._radius = 2                                                                                                                #Radius des Arcballs
        self.focus_point = np.array([0.0, 0.0, 0.0])                                                                                    #Fokuspunkt
        self.new_up_v = np.array([0.0, 0.0, 1.0])                                                                                       #
        self._pressed_first_time = False
        self._maus_y = 1.0
        self._maus_z = 2.0

        self.data_path = ""
        self.initUI()
        pass

    def export(self, stringname):                                       #Export Funktion im GLWindow um Freeze zu vermeiden
        self._export_screen = True
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
        test.grSetUp(self.width(), self.height())                          #GrSetup mit Zoomvariable und den Winkeln fuer die Kugelgleichung




    def resizeGL(self, width, height):
        print(self.width(), self.height())
        gr3.drawimage(0, self.width(), 0, self.height(),
                      self.devicePixelRatio() * self.width(), self.devicePixelRatio() * self.height(),
                      gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)
        test.grSetUp(self.width(), self.height())

        pass

    def spinDraw(self):
        test.grDrawSpin(self.width(), self.height(), self.devicePixelRatio())


    def paintGL(self):

        gr3.usecurrentframebuffer()
        if self._export_screen:                                          #Screenshot und setzen von export screen auf False fuer neuen Durchlauf
            test.ScreenShoot(self.screendateiname, "png", self.height(), self.width())
            self._export_screen = False
        gr3.drawimage(0, self.width(), 0, self.height(),
                      self.devicePixelRatio()*self.width(), self.devicePixelRatio()*self.height(), gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)


    def guiCameraChange(self):
        global linksdreh, hochdreh
        test.grCameraGuiChange(hochdreh,linksdreh)
        self.update()


    def trackballCameraChange(self):
        test.grCameraArcBallChange(self.current_camera_vector)
        self.update()

    def rotation_matrix(self, axis, theta):                                                                             #Berechnet aus Achse und Winkel eine Rotationsmatrix um den der Kamerapunkt rotiert wird
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
        if self._mausX == e.x() and self._maus_y == self.height() - e.y():                                              #Wenn nicht rotiert wurde wird es abgebrochen (Berechnung unnötig)
            return
        self._mausX = e.x()
        self._maus_y = self.height() - e.y()                                                                            #Setzt Y 0-Wert auf unten links statt oben links
        self.calculate_koordinates_from_mouseclick(self.point_c_vektor)                                                 #Berechnung des 3D Punktes der Kamerabewegung
        self.dreheKamera(self.point_a_vektor, self.point_c_vektor)
        self.point_a_vektor = list(self.point_c_vektor)                                                                 #Update Vektor a für nächste Berechnung
        self.update()


    def calculate_koordinates_from_mouseclick(self, list):
        list[0] = 2 * self._mausX / self.width() - 1                                                                    #Umrechnung der Werte von 0-Fenstergrösse zu 0-1
        list[1] = 2 * self._maus_y / self.height() - 1
        if (math.sqrt(list[0] ** 2 + list[1] ** 2) <= self._radius / math.sqrt(2)):                                     #Berechnung des 3D-Punktes durch Arc-Ball Berechnung
            list[2] = math.sqrt(self._radius ** 2 - (list[0] ** 2 + list[1] ** 2))
        else:
            list[2] = self._radius ** 2 / (2 * (list[0] ** 2 + list[1] ** 2))

    def wheelEvent(self, event):
        pixels = event.pixelDelta()
        if not pixels.isNull():
            print("Pixels:", pixels.y())
        test.zoom(pixels.y()/10, self.width(), self.height())
        self.camera_vektor_length = np.linalg.norm(koor.camera_koordinates)
        #self.current_camera_vector = koor.camera_koordinates
        self.update()


    def mousePressEvent(self, e):
        self._mausX = e.x()
        self._maus_y = self.height() - e.y()
        self.calculate_koordinates_from_mouseclick(self.point_a_vektor)
        pass



    def recalculate_up_vector(self, forward_vector, up_vector):                                                         #Berechnet den neuen up_vector aus dem neuen forward_vector
        right_vector = np.cross(forward_vector, up_vector)
        up_vector = np.cross(right_vector, forward_vector)
        return up_vector / np.linalg.norm(up_vector)

    def dreheKamera(self, start_point, end_point):
        self.new_up_v = self.recalculate_up_vector(koor.camera_koordinates, self.new_up_v)                           #Update des up Vektors

        print("Kamera vor Rotation", koor.camera_koordinates)
        print()


        skalar = np.dot(start_point, end_point)                                                       #Skalarprodukt der Endpunkte der Kamerabewegung
        if skalar:                                                                                                      #Falls das Skalar 0 ist also die Ortsvektoren orthogonal sind dann wird nicht berechnet
            u = np.cross(start_point, end_point)

            up_vector = self.new_up_v                                                                                   #lokale Instanz des Up Vektors
            forward_vector = koor.camera_koordinates
            right_vector = np.cross(forward_vector, up_vector)
            up_vector = np.cross(right_vector, forward_vector)
            forward_vector /= np.linalg.norm(forward_vector)
            right_vector /= np.linalg.norm(right_vector)
            up_vector /= np.linalg.norm(up_vector)
            u = u[0] * right_vector - u[1] * up_vector + u[2] * forward_vector

            norm = np.linalg.norm(u)
            theta = np.arctan(norm / skalar)

            if norm:
                self.new_up_v = np.dot(self.rotation_matrix(u, theta), self.new_up_v)
                koor.camera_koordinates = np.dot(self.rotation_matrix(u, theta), koor.camera_koordinates)
                print("Kamera vor Normalisierung", koor.camera_koordinates )
                print()
                koor.camera_koordinates /= np.linalg.norm(koor.camera_koordinates)
                koor.camera_koordinates *= self.camera_vektor_length
                print("Kamera nach Normalisierung", koor.camera_koordinates)
                print()
        print("Kamera nach Rotation", koor.camera_koordinates)
        print()
        print()
        test.setUpVektor(self.new_up_v)
        test.grCameraArcBallChange(koor.camera_koordinates)

    def rotate_right(self):
        print("Drehe rechts")

    def rotate_left(self):
        print("Drehe links")

    def rotate_up(self):
        print("Drehe hoch")
        self.dreheKamera(koor.camera_koordinates, koor.camera_koordinates + self.new_up_v)

    def rotate_down(self):
        print("Drehe runter")

    def setDataSet(self):
        print("Setzte Daten")
        gr3.clear()                                                                                                     #Loecht die Drawlist vom GR3
        test.eingabe(self.data_path)                                                                                    #Speichert die Spins aus der Eingabedatei in die Drawlist
        gr3.usecurrentframebuffer()
        test.grDrawSpin(self.width(),self.height(), self.devicePixelRatio())

        self.repaint()                                                                                                  #Zeichnet die Spins neu

    def set_bg_color(self, rgb_color):
        test.set_background_color(rgb_color)
        self.update()
        pass

    def set_spin_color(self, rgb_color):
        test.set_spin_color(rgb_color, self.devicePixelRatio())
        self.update()
        pass



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
