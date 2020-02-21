import gr3
import gr
import math
helf = None
mittelAtom = []
richtungAtom = []
symbolAtom = []
dreiCameraWerte = [50.0, 2.0, 2.0]
upVector = [0.0, 0.0, 1.0]
zoomVar = 1

def eingabe(pfad):
    global mittelAtom, richtungAtom, symbolAtom
    clearAtoms()
    print(mittelAtom)
    try:
        with open(pfad,'r') as f:
            pass
    except FileNotFoundError:
        print("This path does not exist, please try again")
        return

    with open(pfad, 'r') as infile:                           #Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
        for line in infile.readlines():
            line = line.strip()
            helf = line.split()                                  #Leerzeichen als Trennzeichen
            for i in range(6):
               try:
                   helf[i] = float(helf[i])
               except ValueError:
                   print("Bitte ueberpruefen Sie Ihre Eingabe")
            mittelAtom.append(helf[0:3])                            #Der Mittelpunkt des Atoms sind die ersten 3 Spalten
            richtungAtom.append(helf[3:6])                          #Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
            symbolAtom.append(helf[6])                              #Das letzte Element ist das Symbol des Elementes

def clearAtoms():
    global mittelAtom, richtungAtom, symbolAtom
    mittelAtom.clear()
    richtungAtom.clear()
    symbolAtom.clear()
    gr3.clear()

def grSetUp():
    global upVector, dreiCameraWerte
    gr3.setbackgroundcolor(0, 1, 1, 1)                              #Hintergrundfarbe
    gr3.setcameraprojectionparameters(45, 1, 100)
    gr3.cameralookat(dreiCameraWerte[0], dreiCameraWerte[1], dreiCameraWerte[2],
                     0.0, 0.0, 0.0,
                     upVector[0], upVector[1], upVector[2])
    gr.setviewport(0, 1, 0, 1)

def grCameraGuiChange(azimuth, tilt):
    global upVector, dreiCameraWerte, zoomVar
    r = math.sqrt(
    dreiCameraWerte[0]* dreiCameraWerte[0] + dreiCameraWerte[1] * dreiCameraWerte[1] + dreiCameraWerte[2] * dreiCameraWerte[2])  # Laenge des Kameravektors mit Laengenformel

    dreiCameraWerte[0] = r * math.sin(azimuth) * math.cos(tilt)  # Kugleformel mit Winkeln zur Kamerasteuerung
    dreiCameraWerte[1] = r * math.sin(azimuth) * math.sin(tilt)
    dreiCameraWerte[2] = r * math.cos(azimuth)
    gr3.cameralookat(dreiCameraWerte[0], dreiCameraWerte[1], dreiCameraWerte[2],
                     0, 0, 0,
                     upVector[0], upVector[1], upVector[2])





def grCameraArcBallChange(camera_list):
    global dreiCameraWerte
    print("eingabe 1 = " + str(camera_list[0]))
    print("eingabe 2 = " + str(camera_list[1]))
    print("eingabe 3 = " + str(camera_list[2]))
    gr3.cameralookat(camera_list[0], camera_list[1], camera_list[2],
                     0, 0, 0,
                     upVector[0], upVector[1], upVector[2])                                                                                               #Muss noch veraendert werden um sich mit zu kippen
    dreiCameraWerte = list(camera_list)

def getCameraWerte(i):
    hilfs = dreiCameraWerte[i]
    return hilfs


def setUpVektor(up_vekt):
    global upVector
    upVector = list(up_vekt)

def getUpVektor():
    global upVector
    return upVector

def grDrawSpin(xmax, ymax, pixelRatio):
    global mittelAtom, richtungAtom                                                                 #Erstellung der Spins mithilfe der Tupel aus der Einlesedatei
    gr3.drawspins(mittelAtom, richtungAtom,
                          len(mittelAtom)*[(50.00, 100.00, 0.00)], 0.3, 0.1, 0.75, 2.00)
    gr3.drawimage(0, xmax, 0, ymax,
              1000 * pixelRatio, 1000 * pixelRatio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)

def ScreenShoot(name, format, width, height):
    filename = name + "." + format                                  #Zusammensetzung des Dateinamen aus Name.Format
    gr3.export(filename, width, height)
    print(filename, width, height)
