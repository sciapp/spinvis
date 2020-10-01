#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gr3
import faulthandler
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import gr
from . import spinVis_camera
from . import spinVis_coor
from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout, QApplication, QPushButton,
                             QLabel, QSlider, QTableWidget, QTableWidgetItem)  # Import der versch. QtWidgets
from PyQt5.QtCore import Qt
import math
from PyQt5.QtGui import QPixmap
import numpy as np

left_turn = 1
up_turn = 1


# Eingabe der Datein aus tet.txt

class MainWindow(QtWidgets.QWidget):  # Klasse MainWindow ist das uebergeordnete Fenster, dass fuer Simulation und Gui unterteilt wird
    def __init__(self,ladestyle , *args, **kwargs):
        super().__init__(**kwargs)  # Uebernahme von uebergebenen Daten
        self._first_paint = True
        self._camera_angle = 0.0
        self.inputstyle = ladestyle
        self.initUI()
        pass

    def initUI(self):
        self.setWindowTitle('SpinVis2 by PGI/JCNS-TA test test')
        self.draw_window = GLWidget()  # Erstellung der Zwei zentralen Fenster: das GLWidget m, mit der 3D Darstellung
        self.gui_window = GUIWindow(
            self.draw_window, self.inputstyle)  # Und das GUIWindow w, dass m uebergeben bekommt um die Kameraperspektive per Regler zu veraendern
        self.draw_window.setMinimumSize(1000, 1000)
        self.gui_window.setFixedSize(700, 1000)
        self.gui_window.setFocusPolicy(Qt.ClickFocus)
        self.complete_window_hbox = QHBoxLayout()  # Horizontales Layout umd beides nebeneinander zulegen
        self.complete_window_hbox.addWidget(self.draw_window)
        self.complete_window_hbox.addWidget(self.gui_window)
        self.complete_window_hbox.setContentsMargins(0, 0, 0, 0)
        self.complete_window_hbox.setSpacing(0)  # Abstand 0 setzen um beides direkt nebeneinander zu haben
        self.setLayout(self.complete_window_hbox)



    def keyPressEvent(self, QKeyEvent):

        self.gui_window.p_win.perspective_check.setFocusPolicy(Qt.NoFocus)
        self.gui_window.p_win.orthographic_check.setFocusPolicy(Qt.NoFocus)
        if QKeyEvent.key() == QtCore.Qt.Key_Right:
            self.draw_window.rotate_right(False)
        if QKeyEvent.key() == QtCore.Qt.Key_Left:
            self.draw_window.rotate_left(False)
        if QKeyEvent.key() == QtCore.Qt.Key_Up:
            self.draw_window.rotate_up(False)
        if QKeyEvent.key() == QtCore.Qt.Key_Down:
            self.draw_window.rotate_down(False)

        if QKeyEvent.key() == QtCore.Qt.Key_A:
            spinVis_camera.zoom(0.1, self.draw_window.width(), self.draw_window.height())
        if QKeyEvent.key() == QtCore.Qt.Key_B:
            spinVis_camera.zoom(- 0.1, self.draw_window.width(), self.draw_window.height())
        self.draw_window.update()


class GUIWindow(
    QtWidgets.QWidget):  # GUI Window setzt sich aus einzelnen Windows die vertikal unteieinander gelegt wurden zusammen
    def __init__(self,glwindow, ladestyle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des GLwindows als lokale private variable
        self.ladestyle = ladestyle
        self.initUI()
        pass

    def initUI(self):
        self.pgroup = QtWidgets.QGroupBox()
        self.p_win = ProjectionWindow(self._glwindow)
        self.slide_win = SliderWindow(self._glwindow)                           #Slider Boxlayout fuer Kamerasteuerung per Slider
        self.screen_win = ScreenWindow(self._glwindow)  # Screen Boxlayout fuer Screenshot steuerung
        self.cs_win = SpinColorWindow(self._glwindow)
        self.l_win = DataLoadWindow(self._glwindow, self.ladestyle, self.cs_win)  # Lade Boxlayout um neuen Datensatz zu laden
        self.c_win = ColorWindow(self._glwindow, self.cs_win)  # Color Boxlayout um Farbe für Hintergrund und Spins zu setzen
        self.v_win = VideoWindow(self._glwindow)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.p_win)
        self.vbox.addWidget(self.slide_win)
        self.vbox.addWidget(self.screen_win)
        self.vbox.addWidget(self.l_win)
        self.vbox.addWidget(self.cs_win)
        self.vbox.addWidget(self.c_win)
        self.vbox.addWidget(self.v_win)
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
        self.projectiongroup = QtWidgets.QGroupBox("Projection Window")
        self.projectiongroup.setTitle("Projection Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.projectiongroup)
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

        self.projectiongroup.setLayout(self.projection_box)
        self.setLayout(self.groupbox)
        pass

    def radio_clicked(self):
        if self.orthographic_check.isChecked():
            spinVis_camera.is_orthograpghic = True
            spinVis_camera.set_projection_type_orthographic()
        else:
            spinVis_camera.is_orthograpghic = False
            spinVis_camera.set_projection_type_perspective()
        self._glwindow.update()

    def is_orthographic_projection(self):
        if self.orthographic_check.isChecked():
            return True
        else:
            return False

class SpinColorWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.spincolorgroup = QtWidgets.QGroupBox("Spin Color Window")
        self.spincolorgroup.setTitle("Spin Color Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.spincolorgroup)
        self.table_box = QtWidgets.QVBoxLayout()
        self.table_label = QtWidgets.QLabel()
        self.table_label.setToolTip("Click on the cell under the symbol of the spins you want to change color.\n"
                                    "If you use the feature further down to change the color of all sppins or \n"
                                    "change the data set that is in use, the selection will be reseted. \n"
                                    "If you want to load a color scheme, it must have the same list of symbols \n"
                                    "like the one you have loaded right now. A saved color scheme can be found \n"
                                    "under spinvis_color_safe.txt")
        self.table_label.setText("Color groups of spins:")
        self.hori_box = QtWidgets.QHBoxLayout()
        self.load_scheme_button = QtWidgets.QPushButton("Load scheme")
        self.load_scheme_button.setFixedSize(130,30)
        self.load_scheme_button.clicked.connect(self.load_color)
        self.safe_scheme_button = QtWidgets.QPushButton("Save scheme")
        self.safe_scheme_button.setFixedSize(130,30)
        self.safe_scheme_button.clicked.connect(self.safe_color)
        self.hori_box.addWidget(self.table_label)
        self.hori_box.addWidget(self.safe_scheme_button)
        self.hori_box.addWidget(self.load_scheme_button)
        self.color_table = QtWidgets.QTableWidget(0, 0)
        self.color_table.setFixedHeight(70)
        self.table_box.addLayout(self.hori_box)
        self.table_box.addWidget(self.color_table)
        self.color_table.clicked.connect(self.on_click)
        self.spincolorgroup.setLayout(self.table_box)
        self.setLayout(self.groupbox)

    def load_color(self):

        options = QtWidgets.QFileDialog.Options()  # File Dialog zum auswählen der Daten-Datei
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        input, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose your data", "",
                                                           "All Files (*);;", options=options)

        list = []

        if (not input):
            pass  # Falls nichts ausgewählt wird, wird kein neuer Datensatz gewählt
        else:
            if not (input.endswith(".txt")):
                print("Please make sure that your file is a '.txt'")
                return
            try:  # Es wird probiert den Pfad zu öffnen um eine Exception, bei nicht vorhandener Datei abzufangen (mit Path-Dialog eeigentlich unnötig)
                with open(input, 'r') as f:
                    pass
            except FileNotFoundError:
                print("This path does not exist, please try again")
                return
            with open(input,
                      'r') as infile:  # Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
                for line in infile.readlines():
                    line = line.strip()
                    list.append(line)
                if len(list) == self.color_table.columnCount():
                    i= 0
                    for line in list:
                        helf = line.split()  # Leerzeichen als Trennzeichen
                        if helf[0] == self.color_table.horizontalHeaderItem(i).text().title():
                            rgb_list = [int(helf[1]), int(helf[2]), int(helf[3])]
                            rgb = QtGui.QColor.fromRgb(rgb_list[0], rgb_list[1], rgb_list[2])
                            self.color_table.item(0, i).setBackground(rgb)
                            spinVis_camera.set_symbol_spin_color([helf[1], helf[2], helf[3]], self.color_table.horizontalHeaderItem(
                            i).text().title())
                        i = i+1

    def safe_color(self):
        f = open("spinvis_color_safe.txt", "w")
        for i in range(self.color_table.columnCount()):
            symbol = self.color_table.horizontalHeaderItem(i).text().title()
            rgbtuple = self.color_table.item(0, i).background().color().getRgb()

            print(symbol + "\t" + str(rgbtuple[0]) + "\t" + str(rgbtuple[1]) + "\t" + str(rgbtuple[2]), file=f)
        f.close()


    def on_click(self):

        spin_rgb = [c * 255 for c in
                    spinVis_camera.spin_rgb]  # Umrechnung der momentanen Farbe als Stndardwert, Multiplikation der Werte von 0-1 auf 0-255
        for currentQTableWidgetItem in self.color_table.selectedItems():
            currentQTableWidgetItem.setSelected(False)
            selectedColor = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgb(*spin_rgb))
            if selectedColor.isValid():
                self.color_table.item(currentQTableWidgetItem.row(), currentQTableWidgetItem.column()).setBackground(selectedColor)
                spinVis_camera.set_symbol_spin_color(selectedColor.getRgb(), self.color_table.horizontalHeaderItem(currentQTableWidgetItem.column()).text().title())
                self._glwindow.update()

    def fillTable(self, list):
        symbol_list = np.array(list)
        self.color_table.setRowCount(1)
        self.color_table.setColumnCount(symbol_list.size)
        i = 0
        symbol_list_int = symbol_list.tolist()
        for e in symbol_list_int:
            self.color_table.setHorizontalHeaderItem(i, QTableWidgetItem(str(e)))
            self.color_table.setItem(0, i, QTableWidgetItem(""))
            self.color_table.item(0, i).setBackground(QtGui.QColor.fromRgb(spinVis_camera.spin_rgb[0] * 255, spinVis_camera.spin_rgb[1] * 255, spinVis_camera.spin_rgb[2] * 255))
            i = i+1

    def color_table(self, rgb):
        for e in range(self.color_table.columnCount().__int__()):
            self.color_table.item(0, e).setBackground(QtGui.QColor.fromRgb(rgb[0], rgb[1], rgb[2]))



class DataLoadWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, ladestyle, spin_colour_win,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.lade_style = ladestyle
        self.spin_colour_win = spin_colour_win
        self.initUI()
        pass

    def initUI(self):
        self.loadgroup = QtWidgets.QGroupBox("Data Load Window")
        self.loadgroup.setTitle("Data Load Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.loadgroup)


        self.load_label = QtWidgets.QLabel()
        self.load_label.setText("Load new set of spins from a txt file:")
        self.load_label.setToolTip("Please choose a '.txt' file to load that has the following structure: \n"
                                   "the position of the center of the spin, the direction of the spin, a symbol. \n"
                                   "For example: -1.819     6.300   -25.500     0.022    -0.075     0.355      54. \n"
                                   "Its important that the individual numbers are seperated by tabs. \n"
                                   "But you can also save a data file. If you do so you can find it under \n"
                                   "spinvis_safe_data.txt.")
        self.load_button = QPushButton('Load set', self)
        self.load_button.setFixedSize(130, 30)
        self.load_button.clicked.connect(self.load_file)
        self.safe_button = QPushButton('Safe set', self)
        self.safe_button.setFixedSize(130, 30)
        self.safe_button.clicked.connect(self.safe_data)
        self.hbox = QHBoxLayout()  # HBox mit einem Label und einem Knopf zum Laden
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.load_label)
        self.hbox.addWidget(self.safe_button)
        self.hbox.addWidget(self.load_button)
        self.loadgroup.setLayout(self.hbox)
        self.setLayout(self.groupbox)

    def safe_data(self):
        spinVis_camera.safe_file()

    def load_file(self):
        options = QtWidgets.QFileDialog.Options()  # File Dialog zum auswählen der Daten-Datei
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        input, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose your data", "",
                                                           "All Files (*);;", options=options)
        if (not input):
            pass  # Falls nichts ausgewählt wird, wird kein neuer Datensatz gewählt
        else:
            self._glwindow.data_path = input  # So wird der Eingabestring verwendet und der neue Datensatz gewählt
            self._glwindow.setDataSet()
            self.spin_colour_win.fillTable(spinVis_camera.fill_table())




class ColorWindow(QtWidgets.QWidget):
    def __init__(self, glwindow,spin_color_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self._spin_color_win = spin_color_window
        self.initUI()
        pass

    def initUI(self):
        self.colorgroup = QtWidgets.QGroupBox("Color Window")
        self.colorgroup.setTitle("Color Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.colorgroup)
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
        self.colorgroup.setLayout(self.color_hbox)
        self.setLayout(self.groupbox)

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
            self._spin_color_win.color_table(selectedColor.getRgb())
            spin_rgb[0] = selectedColor.getRgb()[0] / 255
            spin_rgb[1] = selectedColor.getRgb()[1] / 255
            spin_rgb[2] = selectedColor.getRgb()[2] / 255
            for i in range(len(spinVis_camera.color_of_atom)):
                spinVis_camera.color_of_atom[i] = [spin_rgb[0], spin_rgb[1], spin_rgb[2]]
            self._glwindow.set_spin_color(selectedColor.getRgb())

class VideoWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.vidgroup = QtWidgets.QGroupBox("Video Window")
        self.vidgroup.setTitle("Video Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.vidbox = QHBoxLayout()
        self.vidlabel = QLabel()
        self.vidlabel.setText("Create a video: ")
        self.groupbox.addWidget(self.vidgroup)

        self.namebox = QVBoxLayout()
        self.namelabel = QLabel()
        self.namelabel.setText("Name the video:")
        self.vidname = QtWidgets.QTextEdit()
        self.vidname.setFixedSize(100,25)
        self.namebox.addWidget(self.vidlabel)
        self.namebox.addWidget(self.vidname)

        self.fpsbox = QVBoxLayout()
        self.fpslabel = QLabel()
        self.fpslabel.setText("FPS:")
        self.validator = QtGui.QIntValidator(1, 120, self)
        self.fpscounter = QtWidgets.QLineEdit()
        self.fpscounter.setValidator(self.validator)
        self.fpscounter.setFixedSize(25,25)
        self.fpsbox.addWidget(self.fpslabel)
        self.fpsbox.addWidget(self.fpscounter)

        self.resolution_validator = QtGui.QIntValidator(1, 4000, self)

        self.widthbox = QVBoxLayout()
        self.widthlabel = QLabel()
        self.widthlabel.setText("Width: ")
        self.vidwidth = QtWidgets.QLineEdit()
        self.vidwidth.setValidator(self.resolution_validator)
        self.vidwidth.setFixedSize(50, 25)
        self.widthbox.addWidget(self.widthlabel)
        self.widthbox.addWidget(self.vidwidth)

        self.heighthbox = QVBoxLayout()
        self.heightlabel = QLabel()
        self.heightlabel.setText("Height: ")
        self.vidheight = QtWidgets.QLineEdit()
        self.vidheight.setValidator(self.resolution_validator)
        self.vidheight.setFixedSize(50, 25)
        self.heighthbox.addWidget(self.heightlabel)
        self.heighthbox.addWidget(self.vidheight)

        self.vidbutton = QPushButton("Make a video")
        self.vidbutton.clicked.connect(self.doVideo)
        self.vidbox.addLayout(self.namebox)
        self.vidbox.addLayout(self.fpsbox)
        self.vidbox.addLayout(self.widthbox)
        self.vidbox.addLayout(self.heighthbox)
        self.vidbox.addWidget(self.vidbutton)
        self.vidgroup.setLayout(self.vidbox)
        self.setLayout(self.groupbox)

    def doVideo(self):
        self._glwindow.make_video(self.vidname.toPlainText().title(), self.fpscounter.text().title(),
                                  self.vidwidth.text().title(), self.vidheight.text().title())
        pass

class ScreenWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebernahme des GLWindows zur Slidersteuerung
        self.initUI()
        pass

    def initUI(self):
        self.screengroup = QtWidgets.QGroupBox("Screenshot Window")
        self.screengroup.setTitle("Screenshot Window")
        self.outer_box = QVBoxLayout()  # Position the screengroup on the widget (self)
        self.outer_box.addWidget(self.screengroup)
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
        self.screengroup.setLayout(self.fullbox)
        self.setLayout(self.outer_box)

        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setText("The name must be at least one character long")
        pass

    def doScreenshot(self):
        if self.pngcheck.isChecked() == True:  # Wenn die Png Box an ist dann wird der Dateiname auf Variable gesetzt und das ganze anf das
            dataname = self.fileName.text()  # glwindw uebergeben, da ansonsten zu fehlern kommt
            if dataname != "":
                self._glwindow.export(dataname)
            else:
                self.warning_box.show()
        else:

            spinVis_camera.make_screenshot(self.fileName.text(), "html", self._glwindow.width(),
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
        global sliderval, left_turn  # Globale Variablen sliderval und linksdreh zur steuerung
        self.slidergroup = QtWidgets.QGroupBox("Slider Window")
        self.slidergroup.setTitle("Slider Window")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.slidergroup)
        self.slidbox = QVBoxLayout() #Beinhaltet vbox und ein label
        self.vbox = QHBoxLayout()  # Beinhaltet 2 Slider, 1 fuer links und rechts und 1 fuer oben und unten
        self.boxlbl = QLabel()
        self.boxlbl.setText("Slider for camera adjustment:")
        self.boxlbl.setToolTip("You can use the silder to make slight adjustments to the camera view. \n"
                                             "Just slide it in the direction you want the camera to change. If you are \n"
                                             "at the end of the slider just klick on any space on the slider an you can \n"
                                             "use it again.")

        self.left_right_slider_label = QtWidgets.QLabel()
        self.left_right_slider_label.setText("Horizontal Slider")
        self.leftslid = QtWidgets.QDial()  # Erstellungs des linksrechtssliders
        self.leftslid.setWrapping(True)
        self.leftslid.setValue(50)  # Startwert auf 50
        self.leftslid.setFocusPolicy(Qt.NoFocus)
        self.leftslid.valueChanged[int].connect(self.changeLeftValue)  # Bei aenderung wird changeLeftValue aufgerufen
        self.vertival_slider_box = QVBoxLayout()
        self.vertival_slider_box.addWidget(self.left_right_slider_label)
        self.vertival_slider_box.addWidget(self.leftslid)
        self.vertival_slider_box.addStretch(1)

        self.up_down_slider_label = QtWidgets.QLabel()
        self.up_down_slider_label.setText("Vertical Slider")

        self.upslid = QtWidgets.QDial()  # Erstellung des Hochundruntersliders
        self.upslid.setWrapping(True)
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
        self.slidergroup.setLayout(self.slidbox)
        self._glwindow.register(self.leftslid)
        self._glwindow.register(self.upslid)
        self._glwindow.get_slid_win(self)
        self.setLayout(self.groupbox)



    def changeUpValue(self, value):
        global up_turn # Globale Variable hochdreh wird benutzt und veraendert
        print("turn up")
        if value > up_turn:
            self._glwindow.rotate_up(True)
        else:
            self._glwindow.rotate_down(True)

        up_turn = value  # Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel
        self._glwindow.update()  # Update des Fensters um aenderung anzuszeigen

    def changeLeftValue(self, value):
        global left_turn  # Globale Variable linskdreh wird benutzt und veraendert
        print("turn left")
        if value > left_turn:
            self._glwindow.rotate_left(True)
        else:
            self._glwindow.rotate_right(True)
        left_turn = value  # Setzt den Wert des Sliders auf das Pandan zwischen 0 und 2*pi fuer die Kugelformel
        self._glwindow.update()  # Update des Fensters um aenderung anzuszeigen


class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_paint = True
        self._make_video = False
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
        self._mouseY = 1.0
        self._maus_z = 2.0
        self.first_rot = True

        self.upslidval = 0
        self.sideslidval = 0

        self.vid_timer = QtCore.QTimer()
        self.vid_timer.timeout.connect(self.video_connect)
        self._observers = []
        self._blocker = []



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
        if self._make_video:
            gr.clearws()
            gr3.drawimage(0, 1, 0, 1,
                          self.width(), self.height(),
                          gr3.GR3_Drawable.GR3_DRAWABLE_GKS)
            gr.updatews()
        spinVis_camera.grSetUp(self.width(), self.height())

        pass

    def spinDraw(self):
        spinVis_camera.grDrawSpin(self.width(), self.height(), self.devicePixelRatio())

    def paintGL(self):
        gr3.usecurrentframebuffer()
        if self._make_video:
            gr.clearws()
            gr3.drawimage(0, 1, 0, 1,
                          self.width(), self.height(),
                          gr3.GR3_Drawable.GR3_DRAWABLE_GKS)
            gr.updatews()
        if self._export_screen:  # Screenshot und setzen von export screen auf False fuer neuen Durchlauf
            spinVis_camera.make_screenshot(self.screendateiname, "png", self.height(), self.width())
            self._export_screen = False
        gr3.drawimage(0, self.devicePixelRatio() * self.width(), 0, self.devicePixelRatio() * self.height(),
                      self.devicePixelRatio() * self.width(), self.devicePixelRatio() * self.height(),
                      gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)

    def guiCameraChange(self):
        global left_turn, up_turn
        spinVis_camera.grCameraGuiChange(up_turn, left_turn)
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
        if self._mouseX == e.x() and self._mouseY == self.height() - e.y():  # Wenn nicht rotiert wurde wird es abgebrochen (Berechnung unnötig)
            return
        self._mouseX = e.x()
        self._mouseY = self.height() - e.y()  # Setzt Y 0-Wert auf unten links statt oben links
        self.point_c_vektor[0] = 2 * self._mouseX / self.width() - 1  # Umrechnung der Werte von 0-Fenstergrösse zu 0-1
        self.point_c_vektor[1] = 2 * self._mouseY / self.height() - 1
        self.calculate_koordinates_from_mouseclick(self.point_c_vektor)  # Berechnung des 3D Punktes der Kamerabewegung
        print("Mouse move")
        self.change_camera(self.point_a_vektor, self.point_c_vektor, False)
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
        self._mouseX = e.x()
        self._mouseY = self.height() - e.y()
        self.point_a_vektor[0] = 2 * self._mouseX / self.width() - 1  # Umrechnung der Werte von 0-Fenstergrösse zu 0-1
        self.point_a_vektor[1] = 2 * self._mouseY / self.height() - 1
        self.calculate_koordinates_from_mouseclick(self.point_a_vektor)
        pass

    def recalculate_up_vector(self, forward_vector,
                              up_vector):  # Berechnet den neuen up_vector aus dem neuen forward_vector
        right_vector = np.cross(forward_vector, up_vector)
        up_vector = np.cross(right_vector, forward_vector)
        return up_vector / np.linalg.norm(up_vector)

    def change_camera(self, start_point, end_point, isObserved):
        global left_turn, up_turn
        i = 0
        self.new_up_v = self.recalculate_up_vector(spinVis_coor.camera_koordinates,
                                                   self.new_up_v)  # Update des up Vektors
        old_vektor = spinVis_coor.camera_koordinates
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
            #print("Theta", theta)


            if norm:
                self.new_up_v = np.dot(self.rotation_matrix(u, theta), self.new_up_v)
                spinVis_coor.camera_koordinates = np.dot(self.rotation_matrix(u, theta),
                                                         spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates /= np.linalg.norm(spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates *= self.camera_vektor_length
        differenceX = spinVis_coor.camera_koordinates[0] - old_vektor[0]
        differenceY = spinVis_coor.camera_koordinates[1] - old_vektor[1]
        differenceZ = spinVis_coor.camera_koordinates[2] - old_vektor[2]


        if(not isObserved):
            print("observe")


            for observer in self._observers:
                self._blocker[i].reblock()
                if (i == 0):
                    observer.setValue(self._slidwin.leftslid.value().__int__() + differenceZ)
                    i += 1
                else:
                    observer.setValue(self._slidwin.upslid.value().__int__() + differenceY)
                self._blocker[i].unblock()
        spinVis_camera.setUpVektor(self.new_up_v)
        spinVis_camera.grCameraArcBallChange(spinVis_coor.camera_koordinates)

    def rotate_right(self, alr_observ):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([2.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        print("Muv right")
        self.change_camera(center_point_vektor, rotate_point_vektor, alr_observ)

    def rotate_left(self, alr_observ):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([-2.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        print("Muv left")
        self.change_camera(center_point_vektor, rotate_point_vektor, alr_observ)

    def rotate_up(self, alr_observ):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, 0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        print("Muv up")
        self.change_camera(center_point_vektor, rotate_point_vektor, alr_observ)

    def rotate_down(self, alr_observ):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, -0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        print("Muv down")
        self.change_camera(center_point_vektor, rotate_point_vektor, alr_observ)

    def setDataSet(self):
        gr3.clear()  # Loecht die Drawlist vom GR3
        spinVis_camera.file_input(self.data_path)  # Speichert die Spins aus der Eingabedatei in die Drawlist
        spinVis_camera.grSetUp(self.width(), self.height())
        gr3.usecurrentframebuffer()
        spinVis_camera.spin_rgb = [1.00, 1.00, 1.00]
        spinVis_camera.create_color_atoms()
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

    def make_video(self, name, fps, res_width, res_height):
        if self._make_video == False:
            if fps == '':
                fps = 60
            if res_width == '':
                res_width = 1920
            if res_height == '':
                res_height = 1920
            if name == "":
                name = "spinvis_output"
            vidname = str(name) + ".mp4"
            self._make_video = True
            vidops = str(res_width) + "x" + str(res_height) + "@" + str(fps)
            os.environ['GKS_VIDEO_OPTS'] = vidops
            gr.beginprint(vidname)
            self.vid_timer.start(fps/1000)
            self.paintGL()
        else:
            gr.endprint()
            self._make_video = False
            self.vid_timer.stop()
        pass

    def video_connect(self):
        gr.updatews()
        pass

    def register(self, observer):
        self._blocker.append(QtCore.QSignalBlocker(observer))
        self._observers.append(observer)
        for block in self._blocker:
            block.unblock()

    def get_slid_win(self, slidwin):
        self._slidwin = slidwin

def main():
    app = QtWidgets.QApplication(sys.argv)
    os.environ['GKS_WSTYPE'] = "png"

    faulthandler.enable()
    # Enable multisampling for smoother results`
    format = QtGui.QSurfaceFormat()
    format.setSamples(8)
    QtGui.QSurfaceFormat.setDefaultFormat(format)
    mein = MainWindow(sys.stdin.isatty())  # Initialisierung von mein als Maindwindow, wo sich alles drin abspielt
    mein.show()
    if sys.stdin.isatty() == True:
        spinVis_camera.args_input(sys.stdin.read(), mein.draw_window.height(), mein.draw_window.width(),
                                  mein.draw_window.devicePixelRatio())
        spinVis_camera.create_color_atoms()
        mein.gui_window.cs_win.fillTable(spinVis_camera.fill_table())
    sys.exit(app.exec_())
