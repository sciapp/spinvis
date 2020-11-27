import atexit
import gr3
import gr
import math
import os
import subprocess
import tempfile
from . import spinVis_coor
import numpy as np
from scipy.spatial.distance import cdist

focus_point = np.array([0, 0, 0])  # Punkt auf den die Kamera und das Licht zeigt
up_vector = [0.0, 0.0, 1.0]  # Up Vektor
spin_size = 1  # Zoom Variable um bei belieben die Pfeile verbrössern
bg_rgb = [0.1, 0.1, 0.4, 1]  # RGB Werte für den Hintergrund im Bereich 0 bis 1 und Deckungswert
spin_rgb = [1.00, 1.00, 1.00]  # RGB Werte für die Pfeile im Bereich 0 bis 1 und Deckungswert
projection_right = 20  # Wert des Orthographischen Quaders in Wuerfel Form
projection_far = 400  # Laenge des Quaders
current_path = ""  # Path Variable um den Momentanen Pfad auch nach der Auswahl zu benutzen
is_orthograpghic = True  # If True -> Orthographic else Perspektive
symbol_of_atom = []
color_of_atom = []
bond_indices = None
bond_positions = None
bond_vectors = None
bond_lengths = None
bond_directions = None
bond_color = [0.5, 0.5, 0.5]  # RGB color of bond cylinders
bond_distance_threshold = None
bond_distance_threshold_callback = None
first_draw = True


def spin_sphere_input(file_path):
    global focus_point, current_path, symbol_of_atom, color_of_atom

    current_path = file_path  # Setzt den momentanen Pfad auf die Eingabe, sodass die Methode für die Ausgaben mit dem selben Pfad spaeter nochmal aufgerufen werden können

    if not (file_path.endswith(".txt")):
        print("False input")
    try:  # Es wird probiert den Pfad zu öffnen um eine Exception, bei nicht vorhandener Datei abzufangen (mit Path-Dialog eeigentlich unnötig)
        with open(file_path, 'r') as f:

            pass
    except FileNotFoundError:
        print("This path does not exist, please try again")
        return
    mid_point_of_atom = []  # Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    mid_point_of_sphere = []
    radius_of_sphere = []
    symbol_of_sphere = []
    is_kugel = False
    with open(file_path,
              'r') as infile:  # Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
        for line in infile.readlines():

            if "spin" in line:
                pass
            elif "kugel" in line and is_kugel == False:
                is_kugel = True
            elif "kugel" not in line and is_kugel == False:
                line = line.strip()
                helf = line.split()  # Leerzeichen als Trennzeichen
                for i in range(8):
                    try:
                        helf[i] = float(helf[i])
                    except ValueError:
                        print("Some values are not compatible, please review them and try again")
                        return
                mid_point_of_atom.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spalten
                direction_of_atom.append(helf[3:6])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
                symbol_of_atom.append(
                    np.array([helf[6], helf[7], helf[8]]))  # Das letzte Element ist das Symbol des Elementes
            else:
                line = line.strip()
                helf = line.split()  # Leerzeichen als Trennzeichen
                for i in range(7):
                    try:
                        helf[i] = float(helf[i])
                    except ValueError:
                        print("Some values are not compatible, please review them and try again")
                        return
                mid_point_of_sphere.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spalten
                radius_of_sphere.append(helf[3])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
                symbol_of_sphere.append(
                    np.array([helf[4], helf[5], helf[6]]))

    mid_point_of_atom = np.array(
        mid_point_of_atom)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    direction_of_atom = np.array(direction_of_atom)
    symbol_of_atom = np.array(symbol_of_atom)
    mid_point_of_sphere = np.array(
        mid_point_of_sphere)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    radius_of_sphere = np.array(radius_of_sphere)
    symbol_of_sphere = np.array(symbol_of_sphere)

    focus_point = mid_point_of_atom.max(axis=0) / 2 + mid_point_of_atom.min(axis=0) / 2
    return mid_point_of_atom, direction_of_atom, symbol_of_atom, mid_point_of_sphere, radius_of_sphere, symbol_of_sphere, focus_point  # Tuple-Packing



def file_input(file_path):
    global focus_point, current_path, symbol_of_atom, color_of_atom, bond_distance_threshold

    current_path = file_path  # Setzt den momentanen Pfad auf die Eingabe, sodass die Methode für die Ausgaben mit dem selben Pfad spaeter nochmal aufgerufen werden können

    if not (file_path.endswith(".txt")):
        print("False input")
    try:  # Es wird probiert den Pfad zu öffnen um eine Exception, bei nicht vorhandener Datei abzufangen (mit Path-Dialog eeigentlich unnötig)
        with open(file_path, 'r') as f:

            pass
    except FileNotFoundError:
        print("This path does not exist, please try again")
        return
    mid_point_of_atom = []  # Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    with open(file_path,
              'r') as infile:  # Fuer den Bereich die Datei oeffnen, fuer jede Zeile das ganze in 3 Tupel schreiben
        for line in infile.readlines():
            line = line.strip()
            helf = line.split()  # Leerzeichen als Trennzeichen
            for i in range(6):
                try:
                    helf[i] = float(helf[i])
                except ValueError:
                    print("Some values are not compatible, please review them and try again")
                    return
            mid_point_of_atom.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spalten
            direction_of_atom.append(helf[3:6])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
            symbol_of_atom.append(np.array([helf[6], helf[7], helf[8]]))  # Das letzte Element ist das Symbol des Elementes
    mid_point_of_atom = np.array(
        mid_point_of_atom)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    direction_of_atom = np.array(direction_of_atom)
    symbol_of_atom = np.array(symbol_of_atom)
    focus_point = mid_point_of_atom.max(axis=0) / 2 + mid_point_of_atom.min(axis=0) / 2
    bond_distance_threshold = None
    return mid_point_of_atom, direction_of_atom, symbol_of_atom, focus_point  # Tuple-Packing


def calculate_bonds(spin_positions, distance_threshold=None):
    global bond_indices, bond_positions, bond_vectors, bond_lengths, bond_directions, bond_distance_threshold

    if len(spin_positions) < 2:
        bond_indices = None
        bond_positions = None
        bond_vectors = None
        bond_lengths = None
        bond_directions = None
    else:
        distances = cdist(spin_positions, spin_positions, "sqeuclidean")
        distances[distances < np.finfo(np.float).eps] = np.inf
        if distance_threshold is None:
            if bond_distance_threshold is None:
                upper_triangle_indices = np.triu_indices(spin_positions.shape[0], k=1)
                min_distance = math.sqrt(np.min(distances[upper_triangle_indices]))
                distance_threshold = 1.5 * min_distance
            else:
                distance_threshold = bond_distance_threshold
        if bond_distance_threshold_callback is not None:
            bond_distance_threshold_callback(distance_threshold)
        squared_distance_threshold = distance_threshold ** 2
        bond_indices = [(i, j) for i, j in zip(*np.where(distances < squared_distance_threshold)) if j > i]
        bond_positions = np.take(spin_positions, [i for i, _ in bond_indices], axis=0)
        bond_vectors = np.take(spin_positions, [j for _, j in bond_indices], axis=0) - bond_positions
        bond_lengths = np.linalg.norm(bond_vectors, axis=1)[:, np.newaxis]
        bond_directions = bond_vectors / bond_lengths


def create_color_atoms():
    global color_of_atom, symbol_of_atom

    color_of_atom = None
    color_of_atom = [None] * len(symbol_of_atom)
    for k in range(len(symbol_of_atom)):
        color_of_atom[k] = [spin_rgb[0], spin_rgb[1], spin_rgb[2]]


def fill_table():
    global symbol_of_atom
    symb_set =  np.unique(symbol_of_atom, axis=0)
    f = open("sumboltest.txt", 'w')
    for e in symb_set:

        print(e, file=f)
    return symb_set


def args_input(string, height, width, ratio):
    global spin_rgb, spin_size, focus_point, current_path, symbol_of_atom

    spinvis_temp_dir = tempfile.TemporaryDirectory()

    current_path = os.path.join(spinvis_temp_dir.name, "pipe_data.txt")
    f = open(current_path, 'w')
    atexit.register(spinvis_temp_dir.cleanup)

    list = str(string).splitlines()

    mid_point_of_atom = []  # Erstellung der lokalen Listen
    direction_of_atom = []
    symbol_of_atom = []
    for line in list:
        line = line.strip()

        helf = line.split()  # Leerzeichen als Trennzeichen
        for i in range(6):

            try:
                helf[i] = float(helf[i])
            except ValueError:
                print("Some values are not compatible, please review them and try again")
                return
        mid_point_of_atom.append(helf[0:3])  # Der Mittelpunkt des Atoms sind die ersten 3 Spaltenaa
        direction_of_atom.append(helf[3:6])  # Die Richtung des Atoms als Punkt mit den 2ten 3 Spalten
        symbol_of_atom.append(helf[6])  # Das letzte Element ist das Symbol des Elementes
    for i in range(len(mid_point_of_atom)):
        midpoints = str(mid_point_of_atom[i][0]) + "\t" + str(mid_point_of_atom[i][1]) + "\t" + str(mid_point_of_atom[i][2])
        dirctions = str(direction_of_atom[i][0]) + "\t" + str(direction_of_atom[i][1]) + "\t" + str(direction_of_atom[i][2])
        symbols = str(symbol_of_atom[i])
        print(str(midpoints) + "\t" + str(dirctions) + "\t" + str(symbols), file=f)
    f.close()
    mid_point_of_atom = np.array(
        mid_point_of_atom)  # Parse die Liste auf numpy Array um Zugriff auf .max(axis=0) zu bekomme
    direction_of_atom = np.array(direction_of_atom)
    calculate_bonds(mid_point_of_atom)
    gr3.clear()
    gr3.drawspins(mid_point_of_atom, direction_of_atom,
                      len(mid_point_of_atom) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1,
                      spin_size * 0.75, spin_size * 2.00)
    if bond_indices is not None:
        gr3.drawcylindermesh(len(bond_indices), bond_positions, bond_directions, len(bond_indices) * bond_color,
                            len(bond_indices) * (0.1 * spin_size, ), bond_lengths)
    gr3.drawimage(0, height, 0, width,
                  height * ratio, width * ratio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)




def set_focus_point(val_list):  # Setter Methode für Focus Point
    global focus_point
    focus_point = list(val_list)


def grSetUp(width, height):
    global up_vector, focus_point, bg_rgb, projection_right, projection_far
    gr3.setbackgroundcolor(bg_rgb[0], bg_rgb[1], bg_rgb[2], bg_rgb[3])  # Hintergrundfarbe wird gesetzt
    gr3.setcameraprojectionparameters(45, 1, 200)
    gr3.setorthographicprojection(-projection_right * width / height, projection_right * width / height,
                                  -projection_right, projection_right, -projection_far,
                                  projection_far)  # Setzt Projectionstyp auf Orthographisch
    gr3.cameralookat(spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1],
                     spinVis_coor.camera_koordinates[2],
                     # Nimmt die Camera Koordinaten aus spinVis_coor.py, fokus_punkt und up_vector wird noch de-globalisiert
                     focus_point[0], focus_point[1], focus_point[2],
                     up_vector[0], up_vector[1], up_vector[2])
    gr.setviewport(0, 1, 0, 1)


def set_projection_type_orthographic():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_ORTHOGRAPHIC)


def set_projection_type_perspective():
    gr3.setprojectiontype(gr3.GR3_ProjectionType.GR3_PROJECTION_PERSPECTIVE)
    gr3.setcameraprojectionparameters(45, 2, 200)


def grLookAt():
    global focus_point
    gr3.cameralookat(spinVis_coor.camera_koordinates[0], spinVis_coor.camera_koordinates[1], spinVis_coor.camera_koordinates[2],
                     focus_point[0], focus_point[1], focus_point[2],
                     up_vector[0], up_vector[1], up_vector[2])

def grCameraArcBallChange(camera_list):
    global focus_point
    gr3.cameralookat(camera_list[0], camera_list[1], camera_list[2],
                     focus_point[0], focus_point[1], focus_point[2],
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

def set_symbol_spin_color(rgb_color, symbol):
    global color_of_atom
    spin_rgb[0] = int(rgb_color[0]) / 255
    spin_rgb[1] = int(rgb_color[1]) / 255
    spin_rgb[2] = int(rgb_color[2]) / 255
    gr3.clear()
    a, b, c, d = file_input(current_path)
    for i in range(len(color_of_atom)):
        if c[i] == symbol:
            color_of_atom[i] = [spin_rgb[0], spin_rgb[1], spin_rgb[2]]
    gr3.drawspins(a, b,
                  color_of_atom, spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)
    if bond_indices is not None:
        gr3.drawcylindermesh(len(bond_indices), bond_positions, bond_directions, len(bond_indices) * bond_color,
                            len(bond_indices) * (0.1 * spin_size, ), bond_lengths)

def set_spin_color(rgb_color, pixelratio):
    spin_rgb[0] = rgb_color[0] / 255
    spin_rgb[1] = rgb_color[1] / 255
    spin_rgb[2] = rgb_color[2] / 255
    gr3.clear()
    a, b, c, d = file_input(current_path)
    gr3.drawspins(a, b,
                  len(a) * [(spin_rgb[0], spin_rgb[1], spin_rgb[2])], spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)
    if bond_indices is not None:
        gr3.drawcylindermesh(len(bond_indices), bond_positions, bond_directions, len(bond_indices) * bond_color,
                            len(bond_indices) * (0.1 * spin_size, ), bond_lengths)


def zoom(int, breite, hoehe):
    global projection_right, focus_point, is_orthograpghic
    if is_orthograpghic:
        projection_right += int
        gr3.setorthographicprojection(-projection_right * breite / hoehe, projection_right * breite / hoehe,
                                      -projection_right, projection_right,
                                      -projection_far, projection_far)

    else:
        camera_to_focus_vector = np.array(focus_point) - np.array(spinVis_coor.camera_koordinates)  # Vektorberechnung von Kamera zu Fokuspunkt
        spinVis_coor.camera_koordinates += camera_to_focus_vector * (
                    int / 20)  # Addition auf Kamerapunkt mit parameter 1/10
        grCameraArcBallChange(spinVis_coor.camera_koordinates)


def grDrawSpin(xmax, ymax, pixelRatio, is_sphere):
    global spin_rgb, spin_size, color_of_atom, first_draw  # Erstellung der Spins mithilfe der Tupel aus der Einlesedatei

    gr3.clear()
    if first_draw:
        first_draw = False
        create_color_atoms()


    #a, b, c, d = file_input(current_path)
    a, b, c, d, e, f, g = spin_sphere_input(current_path)
    calculate_bonds(a)
    spin_rgb_divided = []
    for ele in c:
        t1 = float(ele[0])/255
        t2 = float(ele[1])/255
        t3 = float(ele[2])/255
        spin_rgb_divided.append([t1,t2,t3])
    sphere_rgb_divided = []
    for ele in f:
        t1 = float(ele[0])/255
        t2 = float(ele[1])/255
        t3 = float(ele[2])/255
        sphere_rgb_divided.append([t1,t2,t3])

    if bond_indices is not None:
        gr3.drawcylindermesh(len(bond_indices), bond_positions, bond_directions, len(bond_indices) * bond_color,
                             len(bond_indices) * (0.1 * spin_size,), bond_lengths)


    gr3.drawspins(a, b,
                  spin_rgb_divided, spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)

    if is_sphere:

        gr3.drawspheremesh(len(d),d , sphere_rgb_divided, e*5)
    gr3.drawimage(0, xmax, 0, ymax,
                  xmax * pixelRatio, ymax * pixelRatio, gr3.GR3_Drawable.GR3_DRAWABLE_OPENGL)


def make_screenshot(name, format, width, height):
    if name != "":
        filename = name + "." + format  # Zusammensetzung des Dateinamen aus Name.Format
        gr3.setquality(8)
        gr3.export(filename, width, height)  # Screenshoot Speiche
        return filename

def save_file():
    global current_path
    if current_path != "":
        f = open("spinvis_safv_data.txt", 'w')
        an, bn, cn, dn = file_input(current_path)
        for i in range(len(an)):
            midpoints = str(an[i][0]) + "\t" + str(an[i][1]) + "\t" + str(an[i][2])
            dirctions = str(bn[i][0]) + "\t" + str(bn[i][1]) + "\t" + str(bn[i][2])
            symbols = str(cn[i][0])
            print(str(midpoints) + "\t" + str(dirctions) + "\t" + str(symbols), file=f)
        f.close()

def render_povray(povray_filepath, png_filepath=None, block=True):
    if png_filepath is None:
        png_filepath = os.path.splitext(povray_filepath)[0] + ".png"
    process = subprocess.Popen(
        ["povray", "+W1920", "+H1920", "-D", "+UA", "+A", "+R9", "+Q11", "+O{}".format(png_filepath), povray_filepath]
    )
    if block:
        process.join()


def render_povray(povray_filepath, png_filepath=None, block=True):
    if png_filepath is None:
        png_filepath = os.path.splitext(povray_filepath)[0] + ".png"
    process = subprocess.Popen(
        ["povray", "+W1920", "+H1920", "-D", "+UA", "+A", "+R9", "+Q11", "+O{}".format(png_filepath), povray_filepath]
    )
    if block:
        process.join()

