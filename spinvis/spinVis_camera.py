import gr3
import gr
import math
from . import spinVis_coor
import numpy as np

fokus_punkt = [0, 0, 0]  # Punkt auf den die Kamera und das Licht zeigt
up_vector = [0.0, 0.0, 1.0]  # Up Vektor
spin_size = 1  # Zoom Variable um bei belieben die Pfeile verbrössern
bg_rgb = [0.1, 0.1, 0.4, 1]  # RGB Werte für den Hintergrund im Bereich 0 bis 1 und Deckungswert
spin_rgb = [1.00, 1.00, 1.00]  # RGB Werte für die Pfeile im Bereich 0 bis 1 und Deckungswert
projection_right = 20  # Wert des Orthographischen Quaders in Wuerfel Form
projection_far = 400  # Laenge des Quaders
current_path = ""  # Path Variable um den Momentanen Pfad auch nach der Auswahl zu benutzen
is_orthograpghic = True  # If True -> Orthographic else Perspektive


def eingabe(pfad):
    global fokus_punkt, current_path

    current_path = pfad  # Setzt den momentanen Pfad auf die Eingabe, sodass die Methode für die Ausgaben mit dem selben Pfad spaeter nochmal aufgerufen werden können

    if not (pfad.endswith(".txt")):
        return
    try:  # Es wird probiert den Pfad zu öffnen um eine Exception, bei nicht vorhandener Datei abzufangen (mit Path-Dialog eeigentlich unnötig)
        with open(pfad, 'r') as f:

            pass
    except FileNotFoundError:
        print("This path does not exist, please try again")
        return
    mid_point_of_atom = []  # Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    with open(pfad,
              'r') as infile:  # Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
        for line in infile.readlines():
            line = line.strip()
            helf = line.split()  # Leerzeichen als Trennzeichen
            for i in range(6):
                try:
                    helf[i] = float(helf[i])
                except ValueError:
                    print("Bitte ueberpruefen Sie Ihre Eingabe")
                    return
            mid_point_of_atom.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spalten
            direction_of_atom.append(helf[3:6])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
            symbol_of_atom.append(helf[6])  # Das letzte Element ist das Symbol des Elementes
    mid_point_of_atom = np.array(
        mid_point_of_atom)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    direction_of_atom = np.array(direction_of_atom)
    fokus_punkt = mid_point_of_atom.max(axis=0) / 2 + mid_point_of_atom.min(axis=0) / 2
    return mid_point_of_atom, direction_of_atom, symbol_of_atom, fokus_punkt  # Tuple-Packing

def args_eingabe(string):
    global spin_rgb, spin_size, fokus_punkt
    list = string.split("\n")
    print(list)
    mid_point_of_atom = []  # Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    for line in list:
        line = line.strip()
        print(line)
        helf = line.split()  # Leerzeichen als Trennzeichen
        print(helf)
        for i in range(6):
            try:
                print(helf[i])
                helf[i] = float(helf[i])
            except ValueError:
                print("Bitte ueberpruefen Sie Ihre Eingabe")
                return
        mid_point_of_atom.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spalten
        direction_of_atom.append(helf[3:6])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
        symbol_of_atom.append(helf[6])  # Das letzte Element ist das Symbol des Elementes
    mid_point_of_atom = np.array(mid_point_of_atom)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    direction_of_atom = np.array(direction_of_atom)
    gr3.drawspins(mid_point_of_atom, direction_of_atom,
                      len(mid_point_of_atom) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1,
                      spin_size * 0.75, spin_size * 2.00)



def set_focus_point(val_list):  # Setter Methode für Focus Point
    global fokus_punkt
    fokus_punkt = list(val_list)


def grSetUp(breite, hoehe):
    global up_vector, fokus_punkt, bg_rgb, projection_right, projection_far
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])  # Hintergrundfarbe wird gesetzt
    gr3.setcameraprojectionparameters(45, 1, 200)
    gr3.setorthographicprojection(-projection_right * breite / hoehe, projection_right * breite / hoehe,
                                  -projection_right, projection_right, -projection_far,
                                  projection_far)  # Setzt Projectionstyp auf Orthographisch
    gr3.cameralookat(spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                     spinVis_coor.camera_koordinates[2],
                     # Nimmt die Camera Koordinaten aus spinVis_coor.py, fokus_punkt und up_vector wird noch de-globalisiert
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])
    gr.setviewport(0, 1, 0, 1)


def grCameraGuiChange(azimuth, tilt):  # Camera Veränderung durch Slider und Euler Winkel
    global up_vector, fokus_punkt
    r = math.sqrt(
        spinVis_coor.camera_koordinates[0] * spinVis_coor.camera_koordinates[0] + spinVis_coor.camera_koordinates[1] *
        spinVis_coor.camera_koordinates[1] + spinVis_coor.camera_koordinates[2] * spinVis_coor.camera_koordinates[
            2])  # Laenge des Kameravektors mit Laengenformel

    spinVis_coor.euler_angles_to_koordinates(azimuth, tilt, r)
    gr3.cameralookat(spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                     spinVis_coor.camera_koordinates[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])


def set_projection_type_orthographic():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_ORTHOGRAPHIC)


def set_projection_type_perspective():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_PERSPECTIVE)
    gr3.setcameraprojectionparameters(45, 2, 200)


def grCameraArcBallChange(camera_list):
    global fokus_punkt
    gr3.cameralookat(camera_list[0], camera_list[1], camera_list[2],
                     fokus_punkt[0], fokus_punkt[1], fokus_punkt[2],
                     up_vector[0], up_vector[1], up_vector[2])
    spinVis_coor.camera_koordinates = list(camera_list)  # Übergabe der Kameraposition an spinVis_coor.py


def setUpVektor(up_vekt):  # Setter Methode für den UpVektor
    global up_vector
    up_vector = list(up_vekt)


def set_background_color(rgb_color):
    global bg_rgb
    bg_rgb = list(rgb_color)
    bg_rgb = [c / 255 for c in rgb_color]  # Umrechnung der Werte von 0 bis 255 zu werten im Bereich von 0 bis 1
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])  # Hintergrundfarbe in neuen Werten setzen


def set_spin_color(rgb_color, pixelratio):
    spin_rgb[0] = rgb_color[0] / 255
    spin_rgb[1] = rgb_color[1] / 255
    spin_rgb[2] = rgb_color[2] / 255
    gr3.clear()
    a, b, c, d = eingabe(current_path)
    gr3.drawspins(a, b,
                  len(a) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)


def zoom(int, breite, hoehe):
    global projection_right, fokus_punkt, is_orthograpghic
    if is_orthograpghic:
        projection_right += int
        gr3.setorthographicprojection(-projection_right * breite / hoehe, projection_right * breite / hoehe,
                                      -projection_right, projection_right,
                                      -projection_far, projection_far)
    else:
        camera_to_focus_vector = fokus_punkt - spinVis_coor.camera_koordinates  # Vektorberechnung von Kamera zu Fokuspunkt
        spinVis_coor.camera_koordinates += camera_to_focus_vector * (
                    int / 20)  # Addition auf Kamerapunkt mit parameter 1/10
        grCameraArcBallChange(spinVis_coor.camera_koordinates)


def grDrawSpin(xmax, ymax, pixelRatio):
    global spin_rgb, spin_size  # Erstellung der Spins mithilfe der Tupel aus der Einlesedatei
    gr3.clear()
    a, b, c, d = eingabe(current_path)
    gr3.drawspins(a, b,
                  len(a) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)
    gr3.drawimage(0, xmax, 0, ymax,
                  xmax * pixelRatio, ymax * pixelRatio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)


def ScreenShoot(name, format, width, height):
    if name != "":
        filename = name + "." + format  # Zusammensetzung des Dateinamen aus Name.Format
        gr3.export(filename, width, height)  # Screenshoot Speicher
        print(filename, width, height)
