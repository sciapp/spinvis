#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pVektor ist der Kameravektor bestehend aus kameraX,Y,Z
# d1Vekor ist der erste gezogene, d2Vektor ist der End Punkt des Zuges
from PyQt5 import QtCore, QtGui, QtWidgets
import gr3
# import gr
import sys
import math
import numpy as np
import os

os.environ['GKS_WSTYPE'] = '381'


helf = None
mittelAtom = []
richtungAtom = []
symbolAtom = []

class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drawSpin = True
        self.initUI()
        self.ersteMalGedrueckt = True

        self.momentanerKameraVektor = np.array([20.0, 5.0, 5.0])
        self.fokusPunkt = np.array([0.0 ,0.0 , 0.0])
        self.newUpV = np.array([0.0,0.0,1.0])
        self._mausX = 0.0
        self._mausY = 0.0
        self._radius = math.sqrt(2.0)
        self.PaVektor = np.array([0.0, 0.0, 0.0])
        self.PcVektor = np.array([0.0, 0.0, 0.0])
    pass

    def initUI(self):
        x = 0
        y = 0
        pass

    def eingabe(self):
        with open('data1.txt',
                  'r') as infile:
            for line in infile.readlines():
                line = line.strip()
                helf = line.split()
                for i in range(6):
                    try:
                        helf[i] = float(helf[i])
                    except ValueError:
                        print("Bitte ueberpruefen Sie Ihre Eingabe")
                mittelAtom.append(helf[0:3])
                richtungAtom.append(helf[3:6])
                symbolAtom.append(helf[6])


    def initializeGL(self):
        self.eingabe()
        gr3.usecurrentframebuffer()

        gr3.setbackgroundcolor(0, 1, 1, 1)

        gr3.setcameraprojectionparameters(45, 1, 100)
        gr3.setlightdirection(0, 50, 60)

        gr3.cameralookat(self.momentanerKameraVektor[0] , self.momentanerKameraVektor[1],  self.momentanerKameraVektor[2],
                         self.fokusPunkt[0], self.fokusPunkt[1], self.fokusPunkt[2],
                         self.newUpV[0], self.newUpV[1], self.newUpV[2])

        if self._drawSpin:
            self.grDrawSpin(self.width(), self.height())
            self._drawSpin = False


    def grDrawSpin(self, xmax, ymax):
        gr3.clear()
        gr3.drawspins(mittelAtom, richtungAtom,
              len(mittelAtom) * [(50.00, 100.00, 0.00)], 0.3, 0.1, 0.75, 2.00)
        gr3.drawimage(0, self.width()*self.devicePixelRatio(), 0, self.height()*self.devicePixelRatio(),
              self.width() * self.devicePixelRatio(), self.height() * self.devicePixelRatio(), gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)
        self.update()
    def paintGL(self):
        gr3.usecurrentframebuffer()

        self.grCameraChange()
        gr3.drawimage(0, self.width() * self.devicePixelRatio(), 0, self.height() * self.devicePixelRatio(),
                          self.width() * self.devicePixelRatio(), self.height() * self.devicePixelRatio(), gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)

    def grCameraChange(self):

        gr3.cameralookat(self.momentanerKameraVektor[0], self.momentanerKameraVektor[1], self.momentanerKameraVektor[2],
                         self.fokusPunkt[0], self.fokusPunkt[1], self.fokusPunkt[2],
                         self.newUpV[0], self.newUpV[1], self.newUpV[2])


    def mousePressEvent(self, e):

        self._mausX = e.x()
        self._mausY = self.height() - e.y()

        self.PaVektor[0] = ((self._mausX / (self.width() / 2)) - 1)
        self.PaVektor[1] = (self._mausY / (self.height() / 2)) - 1


        if(self.PaVektor[0]**2 + self.PaVektor[1]**2 <= 2):
            self.PaVektor[2] = math.sqrt(self._radius ** 2 - self.PaVektor[0] ** 2 - self.PaVektor[1] ** 2)
        else:
            self.PaVektor[2] = 0
            koeff =(math.sqrt(self.PaVektor[0] ** 2 + self.PaVektor[1] ** 2))
            self.PaVektor[0] *= 2/koeff
            self.PaVektor[1] *= 2/koeff
        print(self.PaVektor[0], self.PaVektor[1], self.PaVektor[2], self.width(), self.height())

        print(self.PaVektor[0], self.PaVektor[1], self.PaVektor[2], self.width(), self.height())





    def mouseMoveEvent(self, e):

        self.dreheKamera()

        self._mausX = e.x()
        self._mausY = self.height() - e.y()
        self.PaVektor[0] = ((self._mausX / (self.width() / 2)) - 1)
        self.PaVektor[1] = (self._mausY / (self.height() / 2)) - 1
        if self.PaVektor[0] ** 2 + self.PaVektor[1] ** 2 < 2:
            self.PaVektor[2] = math.sqrt(self._radius ** 2 - self.PaVektor[0] ** 2 - self.PaVektor[1] ** 2)
        else:
            self.PaVektor[2] = 0
            koeffi = (math.sqrt(self.PaVektor[0] ** 2 + self.PaVektor[1] ** 2))
            self.PaVektor[0] *= 2 / koeffi
            self.PaVektor[1] *= 2 / koeffi
        self.update()

        print(self.PaVektor[0], self.PaVektor[1], self.PaVektor[2], self.width(), self.height())


    def recalculate_up_vector(self, forward_vector, up_vector):
        right_vector = np.cross(forward_vector, up_vector)
        up_vector = np.cross(right_vector, forward_vector)
        return up_vector / np.linalg.norm(up_vector)



    def dreheKamera(self):

        self.newUpV = self.recalculate_up_vector(self.momentanerKameraVektor, self.newUpV)


        skalar = np.dot(self.PaVektor, self.PcVektor)
        if skalar:
            u = np.cross(self.PaVektor, self.PcVektor)
            norm = np.linalg.norm(u)
            theta = np.arctan(norm / skalar)

            if norm:
                print("Somethings happenin")
                self.newUpV = np.dot(self.rotation_matrix(u, theta), self.newUpV)
                self.momentanerKameraVektor = np.dot(self.rotation_matrix(u, theta), self.momentanerKameraVektor)
        self.update()


    def rotation_matrix(self, axis, theta):
        axis = np.asarray(axis)
        if(math.sqrt(np.dot(axis, axis)) !=0):
            axis = axis / math.sqrt(np.dot(axis, axis))
            a = math.cos(theta / 2.0)
            b, c, d = -axis * math.sin(theta / 2.0)
            aa, bb, cc, dd = a * a, b * b, c * c, d * d
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Enable multisampling for smoother results`
    #format = QtGui.QSurfaceFormat()
    #format.setSamples(8)
    #QtGui.QSurfaceFormat.setDefaultFormat(format)
    mein = GLWidget()
    mein.setFixedSize(500, 500)
    mein.show()


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()