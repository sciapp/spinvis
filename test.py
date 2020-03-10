import gr3
import gr
import math
helf = None
mittelAtom = []
richtungAtom = []
symbolAtom = []
dreiCameraWerte = [50.0, 2.0, 2.0]
fokus_punkt = [0,0,0]
upVector = [0.0, 0.0, 1.0]
zoomVar = 1
bg_rgb = [0.1, 0.1, 0.4, 1]
spin_rgb = [1.00, 1.00, 1.00]

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

def set_focus_point(val_list):
    global fokus_punkt
    fokus_punkt = list(val_list)

def clearAtoms():
    global mittelAtom, richtungAtom, symbolAtom
    mittelAtom.clear()
    richtungAtom.clear()
    symbolAtom.clear()
    gr3.clear()

def grSetUp():
    global upVector, dreiCameraWerte, fokus_punkt, bg_rgb
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])                              #Hintergrundfarbe
    gr3.setcameraprojectionparameters(45, 1, 100)
    gr3.cameralookat(dreiCameraWerte[0], dreiCameraWerte[1], dreiCameraWerte[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     upVector[0], upVector[1], upVector[2])
    gr.setviewport(0, 1, 0, 1)

def grCameraGuiChange(azimuth, tilt):
    global upVector, dreiCameraWerte, fokus_punkt
    r = math.sqrt(
    dreiCameraWerte[0]* dreiCameraWerte[0] + dreiCameraWerte[1] * dreiCameraWerte[1] + dreiCameraWerte[2] * dreiCameraWerte[2])  # Laenge des Kameravektors mit Laengenformel

    dreiCameraWerte[0] = r * math.sin(azimuth) * math.cos(tilt)  # Kugleformel mit Winkeln zur Kamerasteuerung
    dreiCameraWerte[1] = r * math.sin(azimuth) * math.sin(tilt)
    dreiCameraWerte[2] = r * math.cos(azimuth)
    gr3.cameralookat(dreiCameraWerte[0], dreiCameraWerte[1], dreiCameraWerte[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     upVector[0], upVector[1], upVector[2])


def grCameraArcBallChange(camera_list):
    global dreiCameraWerte, fokus_punkt
    print("eingabe 1 = " + str(camera_list[0]))
    print("eingabe 2 = " + str(camera_list[1]))
    print("eingabe 3 = " + str(camera_list[2]))
    gr3.cameralookat(camera_list[0], camera_list[1], camera_list[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     upVector[0], upVector[1], upVector[2])                                                                                               #Muss noch veraendert werden um sich mit zu kippen
    dreiCameraWerte = list(camera_list)

def getCameraWerte(i):
    hilfs = dreiCameraWerte[i]
    return hilfs


def setUpVektor(up_vekt):
    global upVector
    upVector = list(up_vekt)

def set_background_color(rgb_color):
    global bg_rgb
    bg_rgb = list(rgb_color)
    bg_rgb = [c/255 for c in rgb_color]
    print(bg_rgb, "von test her")
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])

def set_spin_color(rgb_color, pixelratio):
    global spin_rgb, mittelAtom, richtungAtom
    spin_rgb[0] = rgb_color[0]/255
    spin_rgb[1] = rgb_color[1]/255
    spin_rgb[2] = rgb_color[2]/255
    gr3.clear()
    gr3.drawspins(mittelAtom, richtungAtom,
                  len(mittelAtom) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], 0.3, 0.1, 0.75, 2.00)
    print(bg_rgb, "von test her")


def getUpVektor():
    global upVector
    return upVector

def grDrawSpin(xmax, ymax, pixelRatio):
    global mittelAtom, richtungAtom, spin_rgb                                                                 #Erstellung der Spins mithilfe der Tupel aus der Einlesedatei
    gr3.drawspins(mittelAtom, richtungAtom,
                          len(mittelAtom)*[(spin_rgb[0], spin_rgb[1], spin_rgb[2])], 0.3, 0.1, 0.75, 2.00)
    gr3.drawimage(0, xmax, 0, ymax,
              1000 * pixelRatio, 1000 * pixelRatio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)

def ScreenShoot(name, format, width, height):
    filename = name + "." + format                                  #Zusammensetzung des Dateinamen aus Name.Format
    gr3.export(filename, width, height)
    print(filename, width, height)
