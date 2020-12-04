#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gr3
import faulthandler
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import gr
import signal
from . import spinVis_camera
from . import spinVis_coor
from PyQt5.QtWidgets import (QHBoxLayout, QCheckBox, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout,  QPushButton,
                             QLabel, QTableWidgetItem)  # Import der versch. QtWidgets
from PyQt5.QtCore import Qt
import math
import numpy as np



class MainWindow(QtWidgets.QWidget):  #Class MainWindow is the overall window, consisting of a GUI and a canvas part
    def __init__(self,ladestyle , *args, **kwargs):
        super().__init__(**kwargs)  #Takes data from parent
        self.inputstyle = ladestyle #Shows if data comes from pipe or file selection
        self.initUI() #Initialize User Interfaces
        pass

    def initUI(self):
        self.setWindowTitle('SpinVis2 by PGI/JCNS-TA')
        self.draw_window = GLWidget()  #Initialisation of the canvas window
        self.gui_window = GUIWindow(
            self.draw_window, self.inputstyle)  #Initialisation of the GUI with the GLWindow as an parameter
        self.draw_window.setMinimumSize(700, 700) #Size 700x700 is the biggest window possible for the laptop display of a MacBook Pro
        self.gui_window.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.gui_window.setFocusPolicy(Qt.ClickFocus)
        self.complete_window_hbox = QHBoxLayout()  # Horizontales Layout umd beides nebeneinander zulegen
        self.complete_window_hbox.addWidget(self.draw_window)
        self.complete_window_hbox.addWidget(self.gui_window)
        self.complete_window_hbox.setContentsMargins(0, 0, 0, 0)
        self.complete_window_hbox.setSpacing(0)  # Abstand 0 setzen um beides direkt nebeneinander zu haben
        self.setLayout(self.complete_window_hbox)



    def keyPressEvent(self, QKeyEvent):

        #self.gui_window.p_win.perspective_check.setFocusPolicy(Qt.NoFocus)
        #self.gui_window.p_win.orthographic_check.setFocusPolicy(Qt.NoFocus)
        if QKeyEvent.key() == QtCore.Qt.Key_Right:
            self.draw_window.rotate_right()
        if QKeyEvent.key() == QtCore.Qt.Key_Left:
            self.draw_window.rotate_left()
        if QKeyEvent.key() == QtCore.Qt.Key_Up:
            self.draw_window.rotate_up()
        if QKeyEvent.key() == QtCore.Qt.Key_Down:
            self.draw_window.rotate_down()

        if QKeyEvent.key() == QtCore.Qt.Key_A:
            self.draw_window.move_left()
        if QKeyEvent.key() == QtCore.Qt.Key_D:
            self.draw_window.move_right()
        if QKeyEvent.key() == QtCore.Qt.Key_W:
            self.draw_window.move_up()
        if QKeyEvent.key() == QtCore.Qt.Key_S:
            self.draw_window.move_down()

        if QKeyEvent.key() == QtCore.Qt.Key_Z:
            spinVis_camera.zoom(0.1, self.draw_window.width(), self.draw_window.height())
        if QKeyEvent.key() == QtCore.Qt.Key_X:
            spinVis_camera.zoom(- 0.1, self.draw_window.width(), self.draw_window.height())
        self.draw_window.update()


class GUIWindow(
    QtWidgets.QScrollArea):  # GUI Window setzt sich aus einzelnen Windows die vertikal unteieinander gelegt wurden zusammen
    def __init__(self,glwindow, ladestyle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des GLwindows als lokale private variable
        self.ladestyle = ladestyle
        self.initUI()
        pass

    def initUI(self):
        self.parent_widget = QtWidgets.QWidget()
        self.pgroup = QtWidgets.QGroupBox()
        self.p_win = ProjectionWindow(self._glwindow)
        self.slide_win = AngleWindow(self._glwindow)                           #Slider Boxlayout fuer Kamerasteuerung per Slider
        self.t_win = TranslationWindow(self._glwindow)
        self.bond_win = BondWindow(self._glwindow)
        self.screen_win = ScreenWindow(self._glwindow)  # Screen Boxlayout fuer Screenshot steuerung
        self.cs_win = SpinColorWindow(self._glwindow)
        self.l_win = DataLoadWindow(self._glwindow, self.ladestyle, self.cs_win)  # Lade Boxlayout um neuen Datensatz zu laden
        self.c_win = ColorWindow(self._glwindow, self.cs_win)  # Color Boxlayout um Farbe für Hintergrund und Spins zu setzen
        self.v_win = VideoWindow(self._glwindow)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.p_win)
        self.vbox.addWidget(self.slide_win)
        self.vbox.addWidget(self.t_win)
        self.vbox.addWidget(self.bond_win)
        self.vbox.addWidget(self.screen_win)
        self.vbox.addWidget(self.l_win)
        self.vbox.addWidget(self.cs_win)
        self.vbox.addWidget(self.c_win)
        self.vbox.addWidget(self.v_win)
        self.vbox.addStretch(1)
        self.parent_widget.setLayout(self.vbox)
        self.setWidget(self.parent_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


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
        self.projectiongroup.setToolTip("The projectiontype  defines how a 3D object is pictured on a 2D screen. \n"
                                         "The perspektive projection is simulating the effects of the real world. Objects \n"
                                         "farther away appear smaller. The orthographic projection depicts every object \n"
                                         "with the same size. It may reveal patterns in the data, that would else remain hidden")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.projectiongroup)
        self.projection_box = QHBoxLayout()  # Eine grosse HBox die ein Label und eine weite HBox beinhaltet. In der sind 2 VBoxLayouts mit jeweils einem HLabel und einem RadioButton
        # self.projection_box.addStretch(1)
        self.projection_label = QtWidgets.QLabel()
        self.projection_label.setText("Choose a perspective type:")  # Pop-Up das Hilftext anzeigt

        self.checkboxbox = QHBoxLayout()  # Checkboxbox beinhaltet 2 HBoxen, die je ein Label und ein Radiobutton haben

        self.perspective_box = QHBoxLayout()

        self.perspective_check = QRadioButton()
        self.perspective_check.setFocusPolicy(Qt.NoFocus)

        self.perspective_label = QLabel()
        self.perspective_label.setText("Perspektive")
        # self.perspective_check.toggle()

        self.perspective_box.addWidget(self.perspective_label)
        self.perspective_box.addWidget(self.perspective_check)

        self.checkboxmanagment = QButtonGroup()  # Mit der Buttongroup werden die Radiobuttons auf exklusiv gestellt

        self.orthographic_box = QHBoxLayout()

        self.orthographic_check = QRadioButton()
        self.orthographic_check.setChecked(True)
        self.orthographic_check.setFocusPolicy(Qt.NoFocus)
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
        self.groupbox.setContentsMargins(0, 0, 0, 0)
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
        self.spincolorgroup.setToolTip("Click on the cell under the symbol of the spins you want to change color.\n"
                                    "If you use the feature further down to change the color of all spins or \n"
                                    "change the data set that is in use, the selection will be reseted. \n"
                                    "If you want to load a color scheme, it must have the same list of symbols \n"
                                    "like the one you have loaded right now. A saved color scheme can be found \n"
                                    "under spinvis_color_save.txt")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.spincolorgroup)
        self.table_box = QtWidgets.QHBoxLayout()
        self.button_box = QtWidgets.QVBoxLayout()
        self.load_scheme_button = QtWidgets.QPushButton("Load scheme")
        self.load_scheme_button.setFixedSize(130,30)
        self.load_scheme_button.clicked.connect(self.load_color)
        self.save_scheme_button = QtWidgets.QPushButton("Save scheme")
        self.save_scheme_button.setFixedSize(130,30)
        self.save_scheme_button.clicked.connect(self.save_color)

        self.button_box.addWidget(self.save_scheme_button)
        self.button_box.addWidget(self.load_scheme_button)
        self.color_table = QtWidgets.QTableWidget(0, 0)
        self.color_table.setFixedHeight(70)
        self.color_table.setFocusPolicy(Qt.ClickFocus)
        self.table_box.addWidget(self.color_table)
        self.table_box.addLayout(self.button_box)
        self.color_table.clicked.connect(self.on_click)
        self.spincolorgroup.setLayout(self.table_box)
        self.groupbox.setContentsMargins(0, 0, 0, 0)
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

    def save_color(self):
        f = open("spinvis_color_save.txt", "w")
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
        f = open("listtest.txt", 'w')
        for e in symbol_list:
            print(e, file=f)
        self.color_table.setColumnCount(len(symbol_list))

        i = 0
        symbol_list_int = symbol_list.tolist()
        for e in symbol_list_int:
            self.color_table.setHorizontalHeaderItem(i, QTableWidgetItem(str(e)))
            self.color_table.setItem(0, i, QTableWidgetItem(""))
            c = spinVis_camera.get_symbol_color(e)
            self.color_table.item(0, i).setBackground(QtGui.QColor.fromRgb(int(c[0]), int(c[1]), int(c[2])))
            i = i+1

    def color_all_spins(self, rgb):
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
        self.loadgroup.setToolTip("Please choose a '.txt' file to load that has the following structure: \n"
                                   "the position of the center of the spin, the direction of the spin, a symbol. \n"
                                   "For example: -1.819     6.300   -25.500     0.022    -0.075     0.355      54. \n"
                                   "Its important that the individual numbers are seperated by tabs. \n"
                                   "But you can also save a data file. If you do so you can find it under \n"
                                   "spinvis_save_data.txt.")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.loadgroup)
        self.load_label = QtWidgets.QLabel()
        self.load_label.setText("Load new set of spins from a txt file:")
        self.load_button = QPushButton('Load set', self)
        self.load_button.setFixedSize(130, 30)
        self.load_button.clicked.connect(self.load_file)
        self.save_button = QPushButton('Save set', self)
        self.save_button.setFixedSize(130, 30)
        self.save_button.clicked.connect(self.save_data)
        self.hbox = QHBoxLayout()  # HBox mit einem Label und einem Knopf zum Laden
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.load_label)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.loadgroup.setLayout(self.hbox)
        self.groupbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.groupbox)

    def save_data(self):
        spinVis_camera.save_file()

    def load_file(self):
        options = QtWidgets.QFileDialog.Options()  # File Dialog zum auswählen der Daten-Datei
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        input, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose your data", "",
                                                           "All Files (*);;", options=options)
        if (not input):
            pass  # Falls nichts ausgewählt wird, wird kein neuer Datensatz gewählt
        else:
            self._glwindow.data_path = input  # So wird der Eingabestring verwendet und der neue Datensatz gewählt
            #try:
            self._glwindow.setDataSet()
            ''' except TypeError:
                typ_err_box = QtWidgets.QMessageBox()
                typ_err_box.setIcon(2)  # Gives warning Icon
                typ_err_box.setText("Error ocurred while trying to load a data set!")
                typ_err_box.setInformativeText(
                    "Something went wrong trying to open the data file. Please make sure that the the selected file is a '.txt'-file with the schematic"
                    " described in the tooltip.")
                typ_err_box.exec_()'''

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
        self.colorgroup.setToolTip("Click on either button to open a window where you can choose a color \n"
                                    "for either the background or the spins. This color will be saved for \n"
                                    "how long the app is running. However it will be reset if you restart \n"
                                    "the app.")
        self.groupbox = QtWidgets.QVBoxLayout()
        self.groupbox.addWidget(self.colorgroup)
        self.color_hbox = QHBoxLayout()  # Hbox mt 2 Knöpfen und einem Label
        self.color_label = QLabel()
        self.color_label.setText("Choose a color:")
        self.sphere_switch = QtWidgets.QPushButton()
        self.sphere_switch.setText("Switch spheres")
        self.sphere_switch.clicked.connect(self.switch_sphere)
        self.bg_color_button = QPushButton('Background', self)
        self.bg_color_button.setFixedSize(100, 30)
        self.bg_color_button.clicked.connect(self.get_bg_color)
        self.spin_color_button = QPushButton('Spins', self)
        self.spin_color_button.setFixedSize(100, 30)
        self.spin_color_button.clicked.connect(self.get_spin_color)
        self.color_dialog = QtWidgets.QColorDialog()  # Dialog Picker zum Farben auswählen
        self.color_hbox.addWidget(self.color_label)
        self.color_hbox.addWidget(self.sphere_switch)
        self.color_hbox.addWidget(self.bg_color_button)
        self.color_hbox.addWidget(self.spin_color_button)
        self.colorgroup.setLayout(self.color_hbox)
        self.groupbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.groupbox)

    def switch_sphere(self):

        if self._glwindow._issphere:
            self._glwindow._issphere = False
        else:
            self._glwindow._issphere = True

        self._glwindow.spinDraw()
        self._glwindow.update()


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
            self._spin_color_win.color_all_spins(selectedColor.getRgb())
            spin_rgb[0] = selectedColor.getRgb()[0] / 255
            spin_rgb[1] = selectedColor.getRgb()[1] / 255
            spin_rgb[2] = selectedColor.getRgb()[2] / 255
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
        self.vidgroup.setToolTip("Create a video by clicking once on the 'Make a video' button. Pressing a second time\n"
                                 "will finish the video. The default parameters are 1920*1920 pixels and 60 fps.\n"
                                 "But if you enter valid value, they will be used instead. The default name is spinvis_output.mp4")
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
        self.groupbox.setContentsMargins(0, 0, 0, 0)
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
        self.screengroup.setToolTip("Click the button to generate a screenshot. This screenshot contains only the\n"
                            "coloured part of the window, not the gui. Currently length is the fixed size \n"
                            "of 1000 * 1000px, but we are working on a setting for that. The screenshot can \n"
                            "either be in the PNG or the HTML-format. Latter can be opend with your browser")
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

        self.povbox = QVBoxLayout()

        self.povcheck = QRadioButton()
        self.povcheck.setChecked(False)
        self.povlabel = QLabel()
        self.povlabel.setText("POV")

        self.htmlbox = QVBoxLayout()

        self.htmlcheck = QRadioButton()
        self.htmlcheck.setChecked(False)
        self.htmllabel = QLabel()
        self.htmllabel.setText("HTML")

        # self.pngcheck..connect(self.pngChange)
        # self.htmlcheck.stateChanged.connect(self.htmlChange)

        self.checkboxmanagment.addButton(
            self.pngcheck)  # Hinzufuegen der Radiobuttons und dann das setzen der Gruppe auf exklusiv
        self.checkboxmanagment.addButton(self.povcheck)
        self.checkboxmanagment.addButton(self.htmlcheck)
        self.checkboxmanagment.setExclusive(True)  # Exklusiv, sodass immer nur genau ein Knopf an sein kann

        self.povbox.addWidget(self.povlabel)
        self.povbox.addWidget(self.povcheck)

        self.htmlbox.addWidget(self.htmllabel)
        self.htmlbox.addWidget(self.htmlcheck)

        self.checkboxbox.addLayout(self.pngbox)
        self.checkboxbox.addLayout(self.povbox)
        self.checkboxbox.addLayout(self.htmlbox)

        self.fullbox.addLayout(self.screenbox)  # Hinzufuegen der einzelnen Boxen zu der Gesamtbox
        self.fullbox.addLayout(self.checkboxbox)
        self.fullbox.addLayout(self.fileVBox)
        self.screengroup.setLayout(self.fullbox)
        self.outer_box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.outer_box)

        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setText("The name must be at least one character long")
        pass

    def doScreenshot(self):
        if self.pngcheck.isChecked():  # Wenn die Png Box an ist dann wird der Dateiname auf Variable gesetzt und das ganze anf das
            dataname = self.fileName.text()  # glwindw uebergeben, da ansonsten zu fehlern kommt
            if dataname != "":
                self._glwindow.export(dataname)
            else:
                self.warning_box.show()
        else:
            if self.htmlcheck.isChecked():
                format = "html"
            else:
                format = "pov"
            filename = spinVis_camera.make_screenshot(self.fileName.text(), format, 1920,
                                           1920)  # Test.screenshot ruft gr3.export mit html/pov auf
            spinVis_camera.render_povray(filename, block=False)
            self._glwindow.update()
        self.update()
        pass


class AngleWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des glwindow
        self.initUI()
        pass

    def initUI(self):
        self.anglegroup = QtWidgets.QGroupBox("Angle Window")

        self.anglegroup.setTitle("Angle Window")
        self.anglegroup.setToolTip("These 3 angles allow you to set a specific camera position. While phi and thete\n"
                                   "depict your camera position, is alpha used to show the rotation of the upvector.\n"
                                   "Any tripel you enter gives a unique view. ")
        self.groupbox = QtWidgets.QHBoxLayout()
        self.groupbox.addWidget(self.anglegroup)
        self.anglebox = QHBoxLayout()

        self.theta_box = QHBoxLayout()
        self.theta_lbl = QLabel()
        self.theta_lbl.setText("Theta: ")
        self.theta_input = QtWidgets.QLineEdit()
        self.theta_input.setFocusPolicy(Qt.ClickFocus)
        self.theta_input.setFixedSize(70,25)
        self.theta_box.addWidget(self.theta_lbl)
        self.theta_box.addWidget(self.theta_input)
        #self.theta_validator = QtGui.QDoubleValidator(-1/2 * math.pi, math.pi/2,5, self)
        #self.theta_input.setValidator(self.theta_validator)

        self.phi_box = QHBoxLayout()
        self.phi_lbl = QLabel()
        self.phi_lbl.setText("Phi: ")
        self.phi_input = QtWidgets.QLineEdit()
        self.phi_input.setFocusPolicy(Qt.ClickFocus)
        self.phi_input.setFixedSize(75,25)
        self.phi_box.addWidget(self.phi_lbl)
        self.phi_box.addWidget(self.phi_input)
        #self.phi_validator = QtGui.QDoubleValidator(-1* math.pi, math.pi,5, self)
        #self.phi_input.setValidator(self.phi_validator)

        self.up_box = QHBoxLayout()
        self.up_lbl = QLabel()
        self.up_lbl.setText("Alpha: ")
        self.up_input = QtWidgets.QLineEdit()
        self.up_input.setFocusPolicy(Qt.ClickFocus)
        self.up_input.setFixedSize(75, 25)
        self.up_box.addWidget(self.up_lbl)
        self.up_box.addWidget(self.up_input)

        self.angle_button = QPushButton("Set camera")
        self.angle_button.setMaximumSize(150, 25)
        self.angle_button.clicked.connect(self.camera_change_from_angle)


        euler_norm = np.linalg.norm(spinVis_coor.camera_koordinates)

        euler_theta = math.acos(spinVis_coor.camera_koordinates[2] / euler_norm)
        euler_phi = np.arctan2(spinVis_coor.camera_koordinates[1], spinVis_coor.camera_koordinates[0])
        self.theta_input.setText(str(round(euler_theta, 5)))
        self.phi_input.setText(str(round(euler_phi, 5)))

        r = np.array([-math.sin(euler_phi), math.cos(euler_phi), 0])
        v = np.array([-math.cos(euler_phi) * math.cos(euler_theta), -math.sin(euler_phi) * math.cos(euler_theta),
                      math.sin(euler_theta)])
        alpha = math.atan2(-1 * np.dot(spinVis_camera.up_vector, r), np.dot(spinVis_camera.up_vector, v))
        self.up_input.setText(str(round(alpha, 5)))
        self.anglebox.addLayout(self.theta_box)
        self.anglebox.addLayout(self.phi_box)
        self.anglebox.addLayout(self.up_box)
        self.anglebox.addWidget(self.angle_button)
        self.anglegroup.setLayout(self.anglebox)
        self._glwindow.register(self.theta_input)
        self._glwindow.register(self.phi_input)
        self._glwindow.register(self.up_input)
        self.groupbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.groupbox)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return or QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.camera_change_from_angle()


    def camera_change_from_angle(self):
        try:
            theta = float(self.theta_input.text().__str__())
            phi = float(self.phi_input.text().__str__())
            input_up = float(self.up_input.text().__str__())
            r = np.array([-math.sin(phi), math.cos(phi), 0])
            v = np.array([-math.cos(phi) * math.cos(theta), -math.sin(phi) * math.cos(theta), math.sin(theta)])
            self._glwindow.new_up_v = v * math.cos(input_up) - r * math.sin(input_up)
            spinVis_coor.euler_angles_to_koordinates(theta, phi, np.linalg.norm(spinVis_coor.camera_koordinates),
                                                     input_up)

            self._glwindow.update()
        except ValueError:
            val_err_box = QtWidgets.QMessageBox()
            val_err_box.setIcon(2)  # Gives warning Icon
            val_err_box.setText("Error ocurred while trying to recalculate the camera position!")
            val_err_box.setInformativeText("Your entred value was not a floating number. Please make sure that your input is right, before trying to change the camera.")
            val_err_box.exec_()


class BondWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._distance_threshold = 0.0
        self._glwindow = glwindow  # Uebergabe des glwindow
        self.initUI()
        spinVis_camera.bond_distance_threshold_callback = lambda value: self.threshold_input.setText(str(round(value, 5)))

    def initUI(self):
        self.bondgroup = QtWidgets.QGroupBox("Bond Window")

        self.bondgroup.setTitle("Bond Window")
        self.bondgroup.setToolTip("Set a distance threshold for bond calculation. The default value is 150 per cent\n"
                                  "of the minimum distance between the centers of two spins.")
        self.groupbox = QtWidgets.QHBoxLayout()
        self.groupbox.addWidget(self.bondgroup)
        self.bondbox = QHBoxLayout()

        self.threshold_box = QHBoxLayout()
        self.threshold_checkbox = QCheckBox("Show bonds")
        self.threshold_checkbox.stateChanged.connect(self.update_bond_distance_threshold)
        self.threshold_lbl = QLabel()
        self.threshold_lbl.setText("Distance threshold: ")
        self.threshold_input = QtWidgets.QLineEdit()
        self.threshold_input.setFocusPolicy(Qt.ClickFocus)
        self.threshold_input.setFixedSize(70, 25)
        self.threshold_input.returnPressed.connect(self.update_bond_distance_threshold)
        self.threshold_box.addWidget(self.threshold_checkbox)
        self.threshold_box.addWidget(self.threshold_lbl)
        self.threshold_box.addWidget(self.threshold_input)

        self.bond_button = QPushButton("Set threshold")
        self.bond_button.setMaximumSize(150, 25)
        self.bond_button.clicked.connect(self.update_bond_distance_threshold)

        self.bondbox.addLayout(self.threshold_box)
        self.bondbox.addWidget(self.bond_button)
        self.bondgroup.setLayout(self.bondbox)
        self.groupbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.groupbox)

    def update_bond_distance_threshold(self):
        try:
            if self.threshold_input.text().strip() != "":
                threshold = float(self.threshold_input.text())
                spinVis_camera.bond_distance_threshold = threshold
            else:
                spinVis_camera.bond_distance_threshold = None
            spinVis_camera.bond_is_activated = self.threshold_checkbox.isChecked()
            self._glwindow.spinDraw()
            self._glwindow.update()
        except ValueError:
            val_err_box = QtWidgets.QMessageBox()
            val_err_box.setIcon(2)  # Gives warning Icon
            val_err_box.setText("Error ocurred while trying to recalculate the bonds!")
            val_err_box.setInformativeText("Your entred value was not a floating number. Please make sure that your input is right, before trying to change the bond distance threshold.")
            val_err_box.exec_()



class TranslationWindow(QtWidgets.QWidget):
    def __init__(self, glwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_angle = 0.0
        self._glwindow = glwindow  # Uebergabe des glwindow
        self.initUI()
        pass

    def initUI(self):
        self.translationgroup = QtWidgets.QGroupBox("Angle Window")

        self.translationgroup.setTitle("Translation Window")
        self.translationgroup.setToolTip("These 3 angles allow you to set a specific camera position. While phi and thete\n"
                                   "depict your camera position, is alpha used to show the rotation of the upvector.\n"
                                   "Any tripel you enter gives a unique view. ")
        self.groupbox = QtWidgets.QHBoxLayout()
        self.groupbox.addWidget(self.translationgroup)
        self.translationbox = QHBoxLayout()

        self.x_box = QHBoxLayout()
        self.x_lbl = QLabel()
        self.x_lbl.setText("X: ")
        self.x_input = QtWidgets.QLineEdit()
        self.x_input.setFocusPolicy(Qt.ClickFocus)
        self.x_input.setFixedSize(70,25)
        self.x_box.addWidget(self.x_lbl)
        self.x_box.addWidget(self.x_input)
        #self.theta_validator = QtGui.QDoubleValidator(-1/2 * math.pi, math.pi/2,5, self)
        #self.theta_input.setValidator(self.theta_validator)
        self._glwindow._focus_observer.append(self.x_input.setText)

        self.y_box = QHBoxLayout()
        self.y_lbl = QLabel()
        self.y_lbl.setText("Y: ")
        self.y_input = QtWidgets.QLineEdit()
        self.y_input.setFocusPolicy(Qt.ClickFocus)
        self.y_input.setFixedSize(75,25)
        self.y_box.addWidget(self.y_lbl)
        self.y_box.addWidget(self.y_input)
        self._glwindow._focus_observer.append(self.y_input.setText)
        #self.phi_validator = QtGui.QDoubleValidator(-1* math.pi, math.pi,5, self)
        #self.phi_input.setValidator(self.phi_validator)

        self.z_box = QHBoxLayout()
        self.z_lbl = QLabel()
        self.z_lbl.setText("Z: ")
        self.z_input = QtWidgets.QLineEdit()
        self.z_input.setFocusPolicy(Qt.ClickFocus)
        self.z_input.setFixedSize(75, 25)
        self.z_box.addWidget(self.z_lbl)
        self.z_box.addWidget(self.z_input)
        self._glwindow._focus_observer.append(self.z_input.setText)

        self.translation_button = QPushButton("Translate focus")
        self.translation_button.setMaximumSize(150, 25)
        self.translation_button.clicked.connect(self.change_focus_point)

        self.x_input.setText(str(0))
        self.y_input.setText(str(0))
        self.z_input.setText(str(0))
        self.translationbox.addLayout(self.x_box)
        self.translationbox.addLayout(self.y_box)
        self.translationbox.addLayout(self.z_box)
        self.translationbox.addWidget(self.translation_button)
        self.translationgroup.setLayout(self.translationbox)
        self.groupbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.groupbox)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Return or QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.change_focus_point()

    def change_focus_point(self):
        spinVis_camera.focus_point = np.array([float(self.x_input.text()), float(self.y_input.text()), float(self.z_input.text())])
        spinVis_camera.grLookAt()
        self._glwindow.update()


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
        self._angle_observers = []
        self._angle_blocker = []

        self._focus_observer = []

        self._issphere = spinVis_camera.IS_SPHERE_DEFAULT

        self.data_path = ""
        self.setAcceptDrops(True)
        self.initUI()
        pass

    def export(self, stringname):  # Export Funktion im GLWindow um Freeze zu vermeiden
        self._export_screen = True
        self.screendateiname = stringname  # Benutzt den uebergebenen dateinamen
        self.update()

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == "file":
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == "file":
            filepath = str(urls[0].path())
            self.data_path = filepath
            self.setDataSet()

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
        spinVis_camera.grSetUp(self.width(), self.height())

    def spinDraw(self):
        spinVis_camera.grDrawSpin(None, self._issphere, skip_colors=True)

    def paintGL(self):
        gr3.usecurrentframebuffer()
        if self._make_video:
            gr.clearws()
            gr3.drawimage(0, 1, 0, 1,
                          self.width(), self.height(),
                          gr3.GR3_Drawable.GR3_DRAWABLE_GKS)
            gr.updatews()
        if self._export_screen:  # Screenshot und setzen von export screen auf False fuer neuen Durchlauf
            spinVis_camera.grSetUp(1920, 1920)
            spinVis_camera.make_screenshot(self.screendateiname, "png", 1920, 1920)
            spinVis_camera.grSetUp(self.width(), self.height())
            self._export_screen = False
        gr3.drawimage(0, self.devicePixelRatio() * self.width(), 0, self.devicePixelRatio() * self.height(),
                      self.devicePixelRatio() * self.width(), self.devicePixelRatio() * self.height(),
                      gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)



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

        self.change_camera(self.point_a_vektor, self.point_c_vektor)
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

    def change_camera(self, start_point, end_point):
        i = 0
        self.new_up_v = self.recalculate_up_vector(spinVis_coor.camera_koordinates,
                                                   self.new_up_v)  # Update des up Vektors
        skalar = np.dot(start_point, end_point)  # Skalarprodukt der Endpunkte der Kamerabewegung
        if skalar:  # Falls das Skalar 0 ist also die Ortsvektoren orthogonal sind dann wird nicht berechnet
            u = np.cross(start_point, end_point)

            up_vector = self.new_up_v  # lokale Instanz des Up Vektors
            forward_vector = spinVis_coor.camera_koordinates - spinVis_camera.focus_point
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
                camera_vector = spinVis_coor.camera_koordinates - spinVis_camera.focus_point
                spinVis_coor.camera_koordinates = np.dot(self.rotation_matrix(u, theta),
                                                         spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates /= np.linalg.norm(spinVis_coor.camera_koordinates)
                spinVis_coor.camera_koordinates *= self.camera_vektor_length

                spinVis_coor.camera_koordinates = np.dot(self.rotation_matrix(u, theta),
                                                         spinVis_coor.camera_koordinates - spinVis_camera.focus_point) + spinVis_camera.focus_point

        euler_norm = np.linalg.norm(spinVis_coor.camera_koordinates - spinVis_camera.focus_point)
        euler_theta = math.acos((spinVis_coor.camera_koordinates[2] - spinVis_camera.focus_point[2]) / euler_norm)
        euler_phi = np.arctan2(spinVis_coor.camera_koordinates[1] - spinVis_camera.focus_point[1], spinVis_coor.camera_koordinates[0] - spinVis_camera.focus_point[0])

        for observer in self._angle_observers:

            if (i == 0):
                observer.setText(str(round(euler_theta, 5)))
                i += 1
            elif i == 1:
                observer.setText(str(round(euler_phi, 5)))
                i += 1
            else:
                r = np.array([-math.sin(euler_phi), math.cos(euler_phi), 0])

                v = np.array([-math.cos(euler_phi)*math.cos(euler_theta), -math.sin(euler_phi)*math.cos(euler_theta), math.sin(euler_theta)])
                alpha = math.atan2(-1 * np.dot(up_vector, r), np.dot(up_vector, v))
                observer.setText(str(round(alpha, 5)))

        spinVis_camera.setUpVektor(self.new_up_v)
        spinVis_camera.grCameraArcBallChange(spinVis_coor.camera_koordinates)

    def rotate_right(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.02, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.change_camera(center_point_vektor, rotate_point_vektor)

    def rotate_left(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([-0.02, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.change_camera(center_point_vektor, rotate_point_vektor)

    def rotate_up(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, 0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.change_camera(center_point_vektor, rotate_point_vektor)

    def rotate_down(self):
        center_point_vektor = np.array([0.0, 0.0, 0.0])
        self.calculate_koordinates_from_mouseclick(center_point_vektor)
        rotate_point_vektor = np.array([0.0, -0.02, 0.0])
        self.calculate_koordinates_from_mouseclick(rotate_point_vektor)
        self.change_camera(center_point_vektor, rotate_point_vektor)

    def move_right(self):
        forward_vector = spinVis_coor.camera_koordinates - spinVis_camera.focus_point
        right_vector = np.cross(forward_vector, self.new_up_v)
        right_vector /= np.linalg.norm(right_vector)
        spinVis_camera.focus_point -= right_vector
        spinVis_coor.camera_koordinates -= right_vector
        spinVis_camera.grLookAt()
        self.update_translation_win()
        self.update()

    def move_left(self):
        forward_vector = spinVis_coor.camera_koordinates - spinVis_camera.focus_point
        right_vector = np.cross(forward_vector, self.new_up_v)
        right_vector /= np.linalg.norm(right_vector)
        spinVis_camera.focus_point += right_vector
        spinVis_coor.camera_koordinates += right_vector
        spinVis_camera.grLookAt()
        self.update_translation_win()
        self.update()

    def move_up(self):
        spinVis_camera.focus_point += self.new_up_v
        spinVis_coor.camera_koordinates += self.new_up_v
        spinVis_camera.grLookAt()
        self.update_translation_win()
        self.update()

    def move_down(self):
        spinVis_camera.focus_point -= self.new_up_v
        spinVis_coor.camera_koordinates -= self.new_up_v
        spinVis_camera.grLookAt()
        self.update_translation_win()
        self.update()

    def update_translation_win(self):
        self._focus_observer[0](str(round(spinVis_camera.focus_point[0], 4)))
        self._focus_observer[1](str(round(spinVis_camera.focus_point[1], 4)))
        self._focus_observer[2](str(round(spinVis_camera.focus_point[2],4)))

    def setDataSet(self):
        gr3.clear()  # Loecht die Drawlist vom GR3
        spinVis_camera.spin_sphere_input(self.data_path)
        spinVis_camera.grSetUp(self.width(), self.height())
        gr3.usecurrentframebuffer()
        spinVis_camera.spin_rgb = [1.00, 1.00, 1.00]
        spinVis_camera.create_color_atoms()
        spinVis_camera.grDrawSpin(None, self._issphere)
        self.repaint()  # Zeichnet die Spins neu

    def set_bg_color(self, rgb_color):
        spinVis_camera.set_background_color(rgb_color)
        self.update()
        pass

    def set_spin_color(self, rgb_color):
        try:
            spinVis_camera.set_symbol_spin_color(rgb_color)
        except TypeError:
            val_err_box = QtWidgets.QMessageBox()
            val_err_box.setIcon(2) #Gives warning Icon
            val_err_box.setText("Error ocurred while changing the spin color!")
            val_err_box.setInformativeText(
                "To change the color of the spins, you need to load them first. Try this by either clicking on the 'load set'-button or "
                "by pipeing your data throug a terminal, when you start SpinVis2.")
            val_err_box.exec_()
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
            try:
                fps_as_int = int(fps)
            except ValueError:
                fps_as_int = 60
            self.vid_timer.start(fps_as_int/1000)
            self.update()
        else:
            gr.endprint()
            self._make_video = False
            self.vid_timer.stop()
        pass

    def video_connect(self):
        gr.updatews()
        pass

    def register(self, observer):
        self._angle_observers.append(observer)


    def get_slid_win(self, slidwin):
        self._slidwin = slidwin


def main():
    app = QtWidgets.QApplication(sys.argv)
    os.environ['GKS_WSTYPE'] = "nul"

    faulthandler.enable()
    # Enable multisampling for smoother results`
    format = QtGui.QSurfaceFormat()
    format.setSamples(8)
    QtGui.QSurfaceFormat.setDefaultFormat(format)
    mein = MainWindow(sys.stdin.isatty())  # Initialisierung von mein als Maindwindow, wo sich alles drin abspielt
    mein.show()
    read_data = False
    if len(sys.argv) > 1:
        spinVis_camera.grDrawSpin(sys.argv[1])
        read_data = True
    elif not sys.stdin.isatty():
        spinVis_camera.grDrawSpin(sys.stdin)
        read_data = True
    if read_data:
        mein.gui_window.cs_win.fillTable(spinVis_camera.fill_table())
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow <Ctrl-C> to quit the program
    sys.exit(app.exec_())


# 1 fuer spin; 0 fuer kreis
