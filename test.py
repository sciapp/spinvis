import gr3
import gr
import math
import koor
import spintest
import numpy as np




fokus_punkt = [0,0,0]                                                                                                   #Punkt auf den die Kamera und das Licht zeigt
up_vector = [0.0, 0.0, 1.0]                                                                                              #Up Vektor
spin_size = 1                                                                                                             #Zoom Variable um bei belieben die Pfeile verbrössern
bg_rgb = [0.1, 0.1, 0.4, 1]                                                                                             #RGB Werte für den Hintergrund im Bereich 0 bis 1 und Deckungswert
spin_rgb = [1.00, 1.00, 1.00]                                                                                           #RGB Werte für die Pfeile im Bereich 0 bis 1 und Deckungswert
projection_right = 20                                                                                                   #Wert des Orthographischen Quaders in Wuerfel Form
projection_far = 400                                                                                                    #Laenge des Quaders
current_path = ""                                                                                                       #Path Variable um den Momentanen Pfad auch nach der Auswahl zu benutzen
is_projection = True                                                                                                       #If True -> Orthographic else Perspektive

def eingabe(pfad):
    global fokus_punkt, current_path

    current_path = pfad                                                                                                 #Setzt den momentanen Pfad auf die Eingabe, sodass die Methode für die Ausgaben mit dem selben Pfad spaeter nochmal aufgerufen werden können

    try:                                                                                                                #Es wird probiert den Pfad zu öffnen um eine Exception, bei nicht vorhandener Datei abzufangen (mit Path-Dialog eeigentlich unnötig)
        with open(pfad,'r') as f:
            pass
    except FileNotFoundError:
        print("This path does not exist, please try again")
        return
    mid_point_of_atom = []                                                                                                     #Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    with open(pfad, 'r') as infile:                                                                                     #Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
        for line in infile.readlines():
            line = line.strip()
            helf = line.split()                                                                                         #Leerzeichen als Trennzeichen
            for i in range(6):
               try:
                   helf[i] = float(helf[i])
               except ValueError:
                   print("Bitte ueberpruefen Sie Ihre Eingabe")
            mid_point_of_atom.append(helf[0:3])                                                                                #Der Mittelpunkt des Atoms sind die ersten 3 Spalten
            direction_of_atom.append(helf[3:6])                                                                              #Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
            symbol_of_atom.append(helf[6])                                                                                  #Das letzte Element ist das Symbol des Elementes
    print("mid_point_of_atom", mid_point_of_atom)
    mid_point_of_atom = np.array(mid_point_of_atom)                                                                                   #Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    fokus_punkt = mid_point_of_atom.max(axis=0) / 2 + mid_point_of_atom.min(axis=0) / 2
    return mid_point_of_atom, direction_of_atom, symbol_of_atom, fokus_punkt                                                            #Tuple-Packing



def set_focus_point(val_list):                                                                                          #Setter Methode für Focus Point
    global fokus_punkt
    fokus_punkt = list(val_list)


def grSetUp():
    global up_vector,  fokus_punkt, bg_rgb, projection_right, projection_far
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])                                                  #Hintergrundfarbe wird gesetzt
    gr3.setcameraprojectionparameters(45, 1, 100)
    gr3.setorthographicprojection(-projection_right, projection_right, -projection_right, projection_right, -projection_far, projection_far )       #Setzt Projectionstyp auf Orthographisch
    gr3.cameralookat(koor.camera_koordinates[0], koor.camera_koordinates[1], koor.camera_koordinates[2],  #Nimmt die Camera Koordinaten aus koor.py, fokus_punkt und up_vector wird noch de-globalisiert
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])
    gr.setviewport(0, 1, 0, 1)

def grCameraGuiChange(azimuth, tilt):                                                                                   #Camera Veränderung durch Slider und Euler Winkel
    global up_vector,  fokus_punkt
    print(koor.camera_koordinates)
    r = math.sqrt(
    koor.camera_koordinates[0]* koor.camera_koordinates[0] + koor.camera_koordinates[1] * koor.camera_koordinates[1] + koor.camera_koordinates[2] * koor.camera_koordinates[2])  # Laenge des Kameravektors mit Laengenformel

    koor.euler_angles_to_koordinates(azimuth, tilt, r)
    gr3.cameralookat(koor.camera_koordinates[0], koor.camera_koordinates[1], koor.camera_koordinates[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])
    print(koor.camera_koordinates)

def set_projection_type_orthographic():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_ORTHOGRAPHIC)

def set_projection_type_perspective():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_PERSPECTIVE)
    gr3.setcameraprojectionparameters(45, 2, 100)


def grCameraArcBallChange(camera_list):
    global  fokus_punkt
    gr3.cameralookat(camera_list[0], camera_list[1], camera_list[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])
    koor.camera_koordinates = list(camera_list)                                                                         #Übergabe der Kameraposition an koor.py


def setUpVektor(up_vekt):                                                                                               #Setter Methode für den UpVektor
    global up_vector
    up_vector = list(up_vekt)

def set_background_color(rgb_color):
    global bg_rgb
    bg_rgb = list(rgb_color)
    bg_rgb = [c/255 for c in rgb_color]                                                                                 #Umrechnung der Werte von 0 bis 255 zu werten im Bereich von 0 bis 1
    print(bg_rgb, "von test her")
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])                                                  #Hintergrundfarbe in neuen Werten setzen

def set_spin_color(rgb_color, pixelratio):
    spin_rgb[0] = rgb_color[0]/255
    spin_rgb[1] = rgb_color[1]/255
    spin_rgb[2] = rgb_color[2]/255
    gr3.clear()
    a, b, c, d = eingabe(current_path)
    gr3.drawspins(a, b,
                  len(a) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1, spin_size * 0.75, spin_size * 2.00)
    print(bg_rgb, "von test her")


def getUpVektor():
    global up_vector
    return up_vector


def zoom(int):
    global projection_right, fokus_punkt, is_projection
    print()

    if is_projection:
        print("Projection_Right: ", projection_right)
        projection_right += int
        gr3.setorthographicprojection(-projection_right, projection_right, -projection_right, projection_right,
                                      -projection_far, projection_far)
        print("Projection_Right: ", projection_right)
    else:
        print("Vor zoom ", "Fokuspunkt ", fokus_punkt, "Kamerekoordinaten ", koor.camera_koordinates)
        camera_to_focus_vector = fokus_punkt - koor.camera_koordinates  # Vektorberechnung von Kamera zu Fokuspunkt
        koor.camera_koordinates += camera_to_focus_vector * (int / 20)  # Addition auf Kamerapunkt mit parameter 1/10
        grCameraArcBallChange(koor.camera_koordinates)
        print("Nach Zoom ", "Fokuspunkt ", fokus_punkt, "Kamerekoordinaten ",koor.camera_koordinates)
    print()

def grDrawSpin(xmax, ymax, pixelRatio):
    global spin_rgb, spin_size                                                                                            #Erstellung der Spins mithilfe der Tupel aus der Einlesedatei
    gr3.clear()
    a, b, c, d = eingabe(current_path)
    gr3.drawspins(a, b,
                  len(a) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1, spin_size * 0.75, spin_size * 2.00)
    print("pixel ratio", pixelRatio)
    gr3.drawimage(0, xmax, 0, ymax,
              xmax * pixelRatio, ymax * pixelRatio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)
    print("xmax", xmax, "ymax", ymax)

def ScreenShoot(name, format, width, height):
    filename = name + "." + format                                                                                      #Zusammensetzung des Dateinamen aus Name.Format
    gr3.export(filename, width, height)                                                                                 #Screenshoot Speicher
    print(filename, width, height)
