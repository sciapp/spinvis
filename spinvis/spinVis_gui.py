#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gr3
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from . import spinVis_camera
from . import spinVis_coor
from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout, QApplication, QPushButton,
                             QLabel, QSlider)  # Import der versch. QtWidgets
from PyQt5.QtCore import Qt
import math
from PyQt5.QtGui import QPixmap
import numpy as np

linksdreh = 1
hochdreh = 1


# Eingabe der Datein aus tet.txt

class MainWindow(
    QtWidgets.QWidget):  # Klasse MainWindow ist das uebergeordnete Fenster, dass fuer Simulation und Gui unterteilt wird
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # Uebernahme von uebergebenen Daten
        self._first_paint = True
        self._camera_angle = 0.0
        self.initUI()
        pass

    def initUI(self):
        self.setWindowTitle('SpinVis2 by PGI/JCNS-TA')
        self.draw_window = GLWidget()  # Erstellung der Zwei zentralen Fenster: das GLWidget m, mit der 3D Darstellung
        self.gui_window = GUIWindow(
            self.draw_window)  # Und das GUIWindow w, dass m uebergeben bekommt um die Kameraperspektive per Regler zu veraendern
        self.draw_window.setMinimumSize(500, 500)
        self.gui_window.setFixedSize(400, 500)
        self.gui_window.setFocusPolicy(Qt.ClickFocus)
        self.complete_window_hbox = QHBoxLayout()  # Horizontales Layout umd beides nebeneinander zulegen
        self.complete_window_hbox.addWidget(self.draw_window)
        self.complete_window_hbox.addWidget(self.gui_window)
        self.complete_window_hbox.setContentsMargins(0, 0, 0, 0)
        self.complete_window_hbox.setSpacing(0)  # Abstand 0 setzen um beides direkt nebeneinander zu haben
        self.setLayout(self.complete_window_hbox)
        # self.w.l.lade_datei()

    def keyPressEvent(self, QKeyEvent):

        self.gui_window.p_win.perspective_check.setFocusPolicy(Qt.NoFocus)
        self.gui_window.p_win.orthographic_check.setFocusPolicy(Qt.NoFocus)
        if QKeyEvent.key() == QtCore.Qt.Key_Right:
            self.draw_window.rotate_right()
        if QKeyEvent.key() == QtCore.Qt.Key_Left:
            self.draw_window.rotate_left()
        if QKeyEvent.key() == QtCore.Qt.Key_Up:
            self.draw_window.rotate_up()
        if QKeyEvent.key() == QtCore.Qt.Key_Down:
            self.draw_window.rotate_down()

        if QKeyEvent.key() == QtCore.Qt.Key_A:
            spinVis_camera.zoom(0.1, self.draw_window.width(), self.draw_window.height())
        if QKeyEvent.key() == QtCore.Qt.Key_B:
            spinVis_camera.zoom(- 0.1, self.draw_window.width(), self.draw_window.height())
        self.draw_window.update()


class GUIWindow(
    QtWidgets.QWidget):  # GUI Window setzt sich aus einzelnen Windows die vertikal unteieinander gelegt wurden zusammen
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des GLwindows als lokale private variable
        self.initUI()
        pass

    def initUI(self):
        self.pgroup = QtWidgets.QGroupBox()
        self.p_win = ProjectionWindow(self._glwindow)
        self.slide_win = SliderWindow(self._glwindow)                           #Slider Boxlayout fuer Kamerasteuerung per Slider
        self.screen_win = ScreenWindow(self._glwindow)  # Screen Boxlayout fuer Screenshot steuerung
        self.l_win = LadeWindow(self._glwindow)  # Lade Boxlayout um neuen Datensatz zu laden
        self.c_win = ColorWindow(self._glwindow)  # Color Boxlayout um Farbe für Hintergrund und Spins zu setzen
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.p_win)
        self.vbox.addWidget(self.slide_win)
        self.vbox.addWidget(self.screen_win)
        self.vbox.addWidget(self.l_win)
        self.vbox.addWidget(self.c_win)
        self.vbox.addStretch(1)
        self.setLayout(self.vbox)
        pass


class ProjectionWindow(QtWidgets.QWidget):  #
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des GLwindows als lokale private variable
        self.initUI()
        pass

    def initUI(self):
        self.projection_box = QHBoxLayout()  # Eine grosse HBox die ein Label und eine weite HBox beinhaltet. In der sind 2 VBoxLayouts mit jeweils einem HLabel und einem RadioButton
        # self.projection_box.addStretch(1)
        self.projection_label = QtWidgets.QLabel()
        self.projection_label.setText("Choose a perspective type:")  # Pop-Up das Hilftext anzeigt
        self.projection_label.setToolTip("The projectiontype  defines how a 3D object is pictured on a 2D screen. \n"
                                         "The perspektive projection is simulating the effects of the real world. Objects \n"
                                         "farther away appear smaller. The orthographic projection depicts every object \n"
                                         "with the same size. It may reveal patterns in the data, that would else remain hidden")

        self.checkboxbox = QHBoxLayout()  # Checkboxbox beinhaltet 2 HBoxen, die je ein Label und ein Radiobutton haben

        self.perspective_box = QVBoxLayout()

        self.perspective_check = QRadioButton()
        self.perspective_check.setFocusPolicy(Qt.ClickFocus)

        self.perspective_label = QLabel()
        self.perspective_label.setText("Perspektive")
        # self.perspective_check.toggle()

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
            # print("Orthographic")
            spinVis_camera.is_orthograpghic = True
            spinVis_camera.set_projection_type_orthographic()
        else:
            # print("Perspective")
            spinVis_camera.is_orthograpghic = False
            spinVis_camera.set_projection_type_perspective()
        self._glwindow.update()

    def is_orthographic_projection(self):
        if self.orthographic_check.isChecked():
            return True
        else:
            return False


class LadeWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.lade_label = QtWidgets.QLabel()
        self.lade_label.setText("Load new set of spins from a txt file:")
        self.lade_label.setToolTip("Please choose a '.txt' file that has the following structure: \n"
                                   "the position of the center of the spin, the direction of the spin, a symbol. \n"
                                   "For example: -1.819     6.300   -25.500     0.022    -0.075     0.355      54. \n"
                                   "Its important that the individual numbers are seperated by tabs. ")
        self.lade_button = QPushButton('Load set', self)
        self.lade_button.setFixedSize(100, 30)
        self.lade_button.clicked.connect(self.lade_datei)
        self.hbox = QHBoxLayout()  # HBox mit einem Label und einem Knopf zum Laden
        # self.hbox.addStretch(1)
        self.hbox.addWidget(self.lade_label)
        self.hbox.addWidget(self.lade_button)
        self.setLayout(self.hbox)

    def lade_datei(self):
        options = QtWidgets.QFileDialog.Options()  # File Dialog zum auswählen der Daten-Datei
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        eingabe, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose your data", "",
                                                           "All Files (*);;", options=options)
        if (not eingabe):
            pass  # Falls nichts ausgewählt wird, wird kein neuer Datensatz gewählt
        else:
            self._glwindow.data_path = eingabe  # So wird der Eingabestring verwendet und der neue Datensatz gewählt
            self._glwindow.setDataSet()


class ColorWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.color_hbox = QHBoxLayout()  # Hbox mt 2 Knöpfen und einem Label
        self.color_label = QLabel()
        self.color_label.setText("Choose a color:")
        self.color_label.setToolTip("Click on either button to open a window where you can choose a color \n"
                                    "for either the background or the spins. This color will be saved for \n"
                                    "how long the app is running. However it will be reset if you restart \n"
                                    "the app.")
        self.bg_color_button = QPushButton('Background', self)
        self.bg_color_button.setFixedSize(100, 30)
        self.bg_color_button.clicked.connect(self.get_bg_color)
        self.spin_color_button = QPushButton('Spins', self)
        self.spin_color_button.setFixedSize(100, 30)
        self.spin_color_button.clicked.connect(self.get_spin_color)
        self.color_dialog = QtWidgets.QColorDialog()  # Dialog Picker zum Farben auswählen
        self.color_hbox.addWidget(self.color_label)
        self.color_hbox.addWidget(self.bg_color_button)
        self.color_hbox.addWidget(self.spin_color_button)
        self.setLayout(self.color_hbox)

    def get_bg_color(self):
        bg_rgb = [c * 255 for c in
                  spinVis_camera.bg_rgb]  # Umrechnung der momentanen Farbe als Stndardwert, Multiplikation der Werte von 0-1 auf 0-255
        selectedColor = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgb(
            *bg_rgb))  # Speichert die Auswahl des Farbendialogs und setzt Standardwert auf vorher umgewandelte Farben
        if selectedColor.isValid():
            self._glwindow.set_bg_color(selectedColor.getRgb())

    def get_spin_color(self):
        spin_rgb = [c * 255 for c in
                    spinVis_camera.spin_rgb]  # Umrechnung der momentanen Farbe als Stndardwert, Multiplikation der Werte von 0-1 auf 0-255
        selectedColor = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgb(
            *spin_rgb))  # Speichert die Auswahl des Farbendialogs und setzt Standardwert auf vorher umgewandelte Farben
        if selectedColor.isValid():
            self._glwindow.set_spin_color(selectedColor.getRgb())


class ScreenWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.fullbox = QHBoxLayout()  # Fullbox beinhaltet Screenshotknopf, Radiobuttons und Eingabe Zeile, jeweils in VBox mit Labeln

        self.screenbox = QVBoxLayout()  # Screenbox beinhaltet das Label und den Knopf names Screenshot

        self.lbl = QLabel()
        self.screenbutton = QPushButton('Screenshot', self)
        self.screenbutton.setFixedSize(100, 30)
        self.screenbutton.clicked.connect(self.doScreenshot)
        self.lbl.setText("Screenshot")
        self.lbl.setFixedSize(100, 30)
        self.lbl.setToolTip("Click the button to generate a screenshot. This screenshot contains only the\n"
                            "coloured part of the window, not the gui. Currently length is the fixed size \n"
                            "of 1000 * 1000px, but we are working on a setting for that. The screenshot can \n"
                            "either be in the PNG or the HTML-format. Latter can be opend with your browser")

        self.screenbox.addWidget(self.lbl)
        self.screenbox.addWidget(self.screenbutton)

        self.fileVBox = QVBoxLayout()  # Filebox beinhaltet die Eingabezeile und das Label

        self.fileName = QLineEdit()
        self.fileName.setFocusPolicy(Qt.ClickFocus)

        self.fileLabel = QLabel()
        self.fileLabel.setText("Filename:")

        self.fileVBox.addWidget(self.fileLabel)
        self.fileVBox.addWidget(self.fileName)

        self.checkboxbox = QHBoxLayout()  # Checkboxbox beinhaltet 2 HBoxen, die je ein Label und ein Radiobutton haben

        self.pngbox = QVBoxLayout()

        self.pngcheck = QRadioButton()
        self.pngcheck.setChecked(True)
        self.pnglabel = QLabel()
        self.pnglabel.setText("PNG")
        self.pngcheck.toggle()

        self.pngbox.addWidget(self.pnglabel)
        self.pngbox.addWidget(self.pngcheck)

        self.checkboxmanagment = QButtonGroup()  # Mit der Buttongroup werden die Radiobuttons auf exklusiv gestellt

        self.htmlbox = QVBoxLayout()

        self.htmlcheck = QRadioButton()
        self.htmlcheck.setChecked(False)
        self.htmllabel = QLabel()
        self.htmllabel.setText("HTML")

        # self.pngcheck..connect(self.pngChange)
        # self.htmlcheck.stateChanged.connect(self.htmlChange)

        self.checkboxmanagment.addButton(
            self.pngcheck)  # Hinzufuegen der Radiobuttons und dann das setzen der Gruppe auf exklusiv
        self.checkboxmanagment.addButton(self.htmlcheck)
        self.checkboxmanagment.setExclusive(True)  # Exklusiv, sodass immer nur genau ein Knopf an sein kann

        self.htmlbox.addWidget(self.htmllabel)
        self.htmlbox.addWidget(self.htmlcheck)

        self.checkboxbox.addLayout(self.pngbox)
        self.checkboxbox.addLayout(self.htmlbox)

        self.fullbox.addLayout(self.screenbox)  # Hinzufuegen der einzelnen Boxen zu der Gesamtbox
        self.fullbox.addLayout(self.checkboxbox)
        self.fullbox.addLayout(self.fileVBox)
        self.setLayout(self.fullbox)

        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setText("The name must be at least one character long")
        pass

    def doScreenshot(self):
        if self.pngcheck.isChecked() == True:  # Wenn die Png Box an ist dann wird der Dateiname auf Variable gesetzt und das ganze anf das
            dateiname = self.fileName.text()  # glwindw uebergeben, da ansonsten zu fehlern kommt
            if dateiname != "":
                self._glwindow.export(dateiname)
            else:
                self.warning_box.show()
        else:

            spinVis_camera.ScreenShoot(self.fileName.text(), "html", self._glwindow.width(),
                                       self._glwindow.height())  # Test.screenshot ruft gr3.export mit html auf

            self._glwindow.update()
        self.update()
        pass


class SliderWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des glwindow
        self.initUI()
        pass

    def initUI(self):
        global sliderval, linksdreh  # Globale Variablen sliderval und linksdreh zur steuerung
        self.slidbox = QVBoxLayout() #Beinhaltet vbox und ein label
        self.vbox = QVBoxLayout()  # Beinhaltet 2 Slider, 1 fuer links und rechts und 1 fuer oben und unten
        self.boxlbl = QLabel()
        self.boxlbl.setText("Slider for camera adjustment:")
        self.boxlbl.setToolTip("You can use the silder to make slight adjustments to the camera view. \n"
                                             "Just slide it in the direction you want the camera to change. If you are \n"
                                             "at the end of the slider just klick on any space on the slider an you can \n"
                                             "use it again.")

        self.left_right_slider_label = QtWidgets.QLabel()
        self.left_right_slider_label.setText("Horizontal Slider")
        self.leftslid = QSlider(Qt.Horizontal)  # Erstellungs des linksrechtssliders
        self.leftslid.setValue(50)  # Startwert auf 50
        self.leftslid.setFocusPolicy(Qt.NoFocus)
        self.leftslid.valueChanged[int].connect(self.changeLeftValue)  # Bei aenderung wird changeLeftValue aufgerufen
        self.vertival_slider_box = QVBoxLayout()
        self.vertival_slider_box.addWidget(self.left_right_slider_label)
        self.vertival_slider_box.addWidget(self.leftslid)
        self.vertival_slider_box.addStretch(1)

        self.up_down_slider_label = QtWidgets.QLabel()
        self.up_down_slider_label.setText("Vertical Slider")

        self.upslid = QSlider(Qt.Horizontal)  # Erstellung des Hochundruntersliders
        self.upslid.setValue(50)  # Startwert ist 50
        self.upslid.setFocusPolicy(Qt.NoFocus)
        self.upslid.valueChanged[int].connect(self.changeUpValue)  # Bei Aenderung wird changeUpValue aufgerufen
        self.horizontal_slider_box = QVBoxLayout()
        self.horizontal_slider_box.addWidget(self.up_down_slider_label)
        self.horizontal_slider_box.addWidget(self.upslid)
        self.horizontal_slider_box.addStretch(1)

        self.vbox.addLayout(self.vertival_slider_box)
        self.vbox.addLayout(self.horizontal_slider_box)
        self.slidbox.addWidget(self.boxlbl)
        self.slidbox.addLayout(self.vbox)
        self.setLayout(self.slidbox)

    def changeUpValue(self, value):
        global hochdreh # Globale Variable hochdreh wird benutzt und veraendert
        if value > hochdreh:
            self._glwindow.rotate_up()
        else:
            self._glwindow.rotate_down()
        hochdreh = value  # Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel
        self._glwindow.update()  # Update des Fensters um aenderung anzuszeigen

    def changeLeftValue(self, value):
        global linksdreh  # Globale Variable linskdreh wird benutzt und veraendert
        if value > linksdreh:
            self._glwindow.rotate_left()
        else:
            self._glwindow.rotate_right()
        linksdreh = value  # Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel
        self._glwindow.update()  # Update des Fensters um aenderung anzuszeigen


class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_paint = True
        self._camera_angle = 0.0
        self._draw_spin = True  # Verhindert das bei jeder Kamerabewegung die Spins neu gezeichnet werden
        self._export_screen = False  # exportScreen wird beim Knopfdruck auf True gestellt und triggert so export()
        self.point_c_vektor = np.array([spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                                        spinVis_coor.camera_koordinates[
                                            2]])  # Ortsvektor des Punktes andem die Kamerabewegung aufhört
        self.current_camera_vector = np.array([spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                                               spinVis_coor.camera_koordinates[2]])  # Kameravektor
        self.camera_vektor_length = np.linalg.norm(spinVis_coor.camera_koordinates)  # Norm des Kameravektors
        self.point_a_vektor = np.array([spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                                        spinVis_coor.camera_koordinates[
                                            2]])  # Ortsvektor des Punktes andem die Kamerabewegung startet
        self._radius = 2  # Radius des Arcballs
        self.focus_point = np.array([0.0, 0.0, 0.0])  # Fokuspunkt
        self.new_up_v = np.array([0.0, 0.0, 1.0])  #
        self._pressed_first_time = False
        self._maus_y = 1.0
        self._maus_z = 2.0
        self.first_rot = True

        self.data_path = ""
        self.initUI()
        pass

    def export(self, stringname):  # Export Funktion im GLWindow um Freeze zu vermeiden
        self._export_screen = True
        self.screendateiname = stringname  # Benutzt den uebergebenen dateinamen
        self.update()

    def initUI(self):
        x = 0
        y = 0
        pass

    def initializeGL(self):
        gr3.init()
        # test.eingabe()
        gr3.usecurrentframebuffer()
        spinVis_camera.grSetUp(self.width(),
                               self.height())  # GrSetup mit Zoomvariable und den Winkeln fuer die Kugelgleichung

    def resizeGL(self, width, height):
        gr3.drawimage(0, self.width(), 0, self.height(),
                      self.devicePixelRatio() * self.width(), self.devicePixelRatio() * self.height(),
                      gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)
        spinVis_camera.grSetUp(self.width(), self.height())

        pass

    def spinDraw(self):
        spinVis_camera.grDrawSpin(self.width(), self.height(), self.devicePixelRatio())

    def paintGL(self):

        gr3.usecurrentframebuffer()
        if self._export_screen:  # Screenshot und setzen von export screen auf False fuer neuen Durchlauf
            spinVis_camera.ScreenShoot(self.screendateiname, "png", self.height(), self.width())
            self._export_screen = False
        gr3.drawimage(0, self.devicePixelRatio() * self.width(), 0, self.devicePixelRatio() * self.height(),
                      self.devicePixelRatio() * self.width(), self.devicePixelRatio() * self.height(),
                      gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)

    def guiCameraChange(self):
        global linksdreh, hochdreh
        spinVis_camera.grCameraGuiChange(hochdreh, linksdreh)
        self.update()

    def trackballCameraChange(self):
        spinVis_camera.grCameraArcBallChange(self.current_camera_vector)
        self.update()

    def rotation_matrix(self, axis,
                        theta):  # Berechnet aus Achse und Winkel eine Rotationsmatrix um den der Kamerapunkt rotiert wird
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
        if self._mausX == e.x() and self._maus_y == self.height() - e.y():  # Wenn nicht rotiert wurde wird es abgebrochen (Berechnung unnötig)
            return
        self._mausX = e.x()
        self._maus_y = self.height() - e.y()  # Setzt Y 0-Wert auf unten links statt oben links
        self.point_c_vektor[0] = 2 * self._mausX / self.width() - 1  # Umrechnung der Werte von 0-Fenstergrösse zu 0-1
        self.point_c_vektor[1] = 2 * self._maus_y / self.height() - 1
        self.calculate_koordinates_from_mouseclick(self.point_c_vektor)  # Berechnung des 3D Punktes der Kamerabewegung
        self.dreheKamera(self.point_a_vektor, self.point_c_vektor)
        self.point_a_vektor = list(self.point_c_vektor)  # Update Vektor a für nächste Berechnung
        self.update()

    def calculate_koordinates_from_mouseclick(self, list):
        if (math.sqrt(list[0] ** 2 + list[1] ** 2) <= self._radius / math.sqrt(
                2)):  # Berechnung des 3D-Punktes durch Arc-Ball Berechnung
            list[2] = math.sqrt(self._radius ** 2 - (list[0] ** 2 + list[1] ** 2))
        else:
            list[2] = self._radius ** 2 / (2 * (list[0] ** 2 + list[1] ** 2))

    def wheelEvent(self, event):
        pixels = event.pixelDelta()
        degrees = event.angleDelta() / 8
        if not pixels.isNull():
            zoom = pixels.y() / 10
        else:
            zoom = degrees.y() / 5
        spinVis_camera.zoom(zoom, self.width(), self.height())
        self.camera_vektor_length = np.linalg.norm(spinVis_coor.camera_koordinates)
        # self.current_camera_vector = koor.camera_koordinates
        self.update()

    def mousePressEvent(self, e):
        self._mausX = e.x()
        self._maus_y = self.height() - e.y()
        self.point_a_vektor[0] = 2 * self._mausX / self.width() - 1  # Umrechnung der Werte von 0-Fenstergrösse zu 0-1
        self.point_a_vektor[1] = 2 * self._maus_y / self.height() - 1
        self.calculate_koordinates_from_mouseclick(self.point_a_vektor)
        pass

    def recalculate_up_vector(self, forward_vector,
                              up_vector):  # Berechnet den neuen up_vector aus dem neuen forward_vector
        right_vector = np.cross(forward_vector, up_vector)
        up_vector = np.cross(right_vector, forward_vector)
        return up_vector / np.linalg.norm(up_vector)

    def dreheKamera(self, start_point, end_point):
        self.new_up_v = self.recalculate_up_vector(spinVis_coor.camera_koordinates,
                                                   self.new_up_v)  # Update des up Vektors

        skalar = np.dot(start_point, end_point)  # Skalarprodukt der Endpunkte der Kamerabewegung
        if skalar:  # Falls das Skalar 0 ist also die Ortsvektoren orthogonal sind dann wird nicht berechnet
            u = np.cross(start_point, end_point)

            up_vector = self.new_up_v  # lokale Instanz des Up Vektors
            forward_vector = spinVis_coor.camera_koordinates
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
                spinVis_coor.camera_koordinates = np.dot(self.rotation_matrix(u, theta),
                                                         spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates /= np.linalg.norm(spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates *= self.camera_vektor_length
        spinVis_camera.setUpVektor(self.new_up_v)
        spinVis_camera.grCameraArcBallChange(spinVis_coor.camera_koordinates)

    def rotate_right(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.02, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.dreheKamera(center_point_vektor, rotate_point_vektor)

    def rotate_left(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([-0.02, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.dreheKamera(center_point_vektor, rotate_point_vektor)

    def rotate_up(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, 0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.dreheKamera(center_point_vektor, rotate_point_vektor)

    def rotate_down(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, -0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.dreheKamera(center_point_vektor, rotate_point_vektor)

    def setDataSet(self):
        gr3.clear()  # Loecht die Drawlist vom GR3
        spinVis_camera.eingabe(self.data_path)  # Speichert die Spins aus der Eingabedatei in die Drawlist
        spinVis_camera.grSetUp(self.width(), self.height())
        gr3.usecurrentframebuffer()
        spinVis_camera.grDrawSpin(self.width(), self.height(), self.devicePixelRatio())

        self.repaint()  # Zeichnet die Spins neu

    def set_bg_color(self, rgb_color):
        spinVis_camera.set_background_color(rgb_color)
        self.update()
        pass

    def set_spin_color(self, rgb_color):
        spinVis_camera.set_spin_color(rgb_color, self.devicePixelRatio())
        self.update()
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Enable multisampling for smoother results`
    format = QtGui.QSurfaceFormat()
    format.setSamples(8)
    QtGui.QSurfaceFormat.setDefaultFormat(format)
    mein = MainWindow()  # Initialisierung von mein als Maindwindow, wo sich alles drin abspielt
    mein.show()
    sys.exit(app.exec_())
