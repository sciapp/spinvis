import atexit
import gr3
import gr
import math
import os
import subprocess
import tempfile
from . import spinVis_coor
import numpy as np
from collections.abc import Sequence
from io import TextIOBase
from scipy.spatial.distance import cdist


IS_SPHERE_DEFAULT = True

focus_point = np.array([0, 0, 0])  # Punkt auf den die Kamera und das Licht zeigt
up_vector = [0.0, 0.0, 1.0]  # Up Vektor
spin_size = 1  # Zoom Variable um bei belieben die Pfeile verbrössern
bg_rgb = [0.1, 0.1, 0.4, 1]  # RGB Werte für den Hintergrund im Bereich 0 bis 1 und Deckungswert
spin_rgb = [1.00, 1.00, 1.00]  # RGB Werte für die Pfeile im Bereich 0 bis 1
sphere_rgb = [1.00, 1.00, 1.00]  # RGB Werte für die Kugeln im Bereich 0 bis 1
projection_right = 20  # Wert des Orthographischen Quaders in Wuerfel Form
projection_far = 400  # Laenge des Quaders
current_path = ""  # Path Variable um den Momentanen Pfad auch nach der Auswahl zu benutzen
is_orthograpghic = True  # If True -> Orthographic else Perspektive
symbol_of_atom = []
color_of_atom = []
symbol_of_sphere = []
color_of_sphere = []
bond_indices = None
bond_positions = None
bond_vectors = None
bond_lengths = None
bond_directions = None
bond_color = [0.5, 0.5, 0.5]  # RGB color of bond cylinders
bond_is_activated = False
bond_distance_threshold = None
bond_distance_threshold_callback = None
first_draw = True
draw_spheres = IS_SPHERE_DEFAULT


class ParseError(Exception):
    pass


def spin_sphere_input(file_path_or_object=None, skip_colors=False):
    global focus_point, current_path, symbol_of_atom, color_of_atom, symbol_of_sphere, color_of_sphere

    if file_path_or_object is None:
        file_path = current_path
    else:
        if isinstance(file_path_or_object, str):
            file_path = file_path_or_object
        elif isinstance(file_path_or_object, TextIOBase):
            file_object = file_path_or_object
            spinvis_temp_dir = tempfile.TemporaryDirectory()
            atexit.register(spinvis_temp_dir.cleanup)
            # Create a temporary copy of the input file object,
            # so it can be read multple times (needed for piped input)
            file_path = os.path.join(spinvis_temp_dir.name, "pipe_data.txt")
            with open(file_path, 'w') as f:
                f.write(file_object.read())
        # Save the path for repeated calls of `spin_sphere_input` without arguments
        current_path = file_path

    mid_point_of_atom = []
    direction_of_atom = []
    symbol_of_atom = []
    if not skip_colors:
        color_of_atom = []
    mid_point_of_sphere = []
    radius_of_sphere = []
    symbol_of_sphere = []
    if not skip_colors:
        color_of_sphere = []
    in_spin_block = True
    # Open the selected file and parse every line as three tuples
    with open(file_path, "r") as infile:
        for line in infile:
            # Ensure there is no leading or trailing whitespace in `line` and ignore case
            line = line.strip().lower()
            if line.startswith("spin"):
                in_spin_block = True
                continue
            elif line.startswith("kugel") or line.startswith("sphere"):
                in_spin_block = False
                continue
            fields = line.split()  # Arbitrary amount of whitespace as separator
            field_count = len(fields)
            if in_spin_block:
                if field_count != 7 and field_count < 9:
                    raise ParseError("Cannot parse spin because of missing values.")
                for i in range(6 if field_count == 7 else 9):
                    try:
                        fields[i] = float(fields[i])
                    except ValueError as e:
                        raise ParseError('The value "{}" is not a valid float.'.format(fields[i])) from e
                mid_point_of_atom.append(fields[0:3])  # position of the spin (first three columns)
                direction_of_atom.append(fields[3:6])  # direction of the spin (second three columns)
                if field_count == 7:
                    symbol_of_atom.append(fields[6])  # spin symbol / element / ... (references a color triple)
                    if not skip_colors:
                        color_of_atom.append(None)
                else:
                    symbol_of_atom.append([fields[6], fields[7], fields[8]])  # RGB color of the spin (0-255)
                    if not skip_colors:
                        color_of_atom.append([c / 255.0 for c in symbol_of_atom[-1]])
            else:
                if field_count != 5 and field_count < 7:
                    raise ParseError("Cannot parse sphere because of missing values.")
                for i in range(4 if field_count == 5 else 7):
                    try:
                        fields[i] = float(fields[i])
                    except ValueError as e:
                        raise ParseError('The value "{}" is not a valid float.'.format(fields[i])) from e
                mid_point_of_sphere.append(fields[0:3])  # position of the sphere (first three columns)
                radius_of_sphere.append(fields[3])  # radius of the spin (fourth column)
                if field_count == 5:
                    symbol_of_sphere.append(fields[4])  # sphere symbol / element / ... (references a color triple)
                    if not skip_colors:
                        color_of_sphere.append(None)
                else:
                    symbol_of_sphere.append([fields[4], fields[5], fields[6]])  # RGB color of the sphere (0-255)
                    if not skip_colors:
                        color_of_sphere.append([c / 255.0 for c in symbol_of_sphere[-1]])

    create_color_atoms()

    mid_point_of_atom = np.array(
        mid_point_of_atom)  # Convert to a NumPy array for axis-wise operations
    direction_of_atom = np.array(direction_of_atom)
    mid_point_of_sphere = np.array(
        mid_point_of_sphere)  # Convert to a NumPy array for axis-wise operations
    radius_of_sphere = np.array(radius_of_sphere)

    focus_point = mid_point_of_atom.max(axis=0) / 2 + mid_point_of_atom.min(axis=0) / 2
    return mid_point_of_atom, direction_of_atom, symbol_of_atom, mid_point_of_sphere, radius_of_sphere, symbol_of_sphere, focus_point  # Tuple-Packing


def calculate_bonds(spin_positions, distance_threshold=None):
    global bond_indices, bond_positions, bond_vectors, bond_lengths, bond_directions, bond_distance_threshold

    if len(spin_positions) < 2 or not bond_is_activated:
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
    global color_of_atom, color_of_sphere

    for k in range(len(color_of_atom)):
        if color_of_atom[k] is None:
            color_of_atom[k] = [spin_rgb[0], spin_rgb[1], spin_rgb[2]]
    for k in range(len(color_of_sphere)):
        if color_of_sphere[k] is None:
            color_of_sphere[k] = [sphere_rgb[0], sphere_rgb[1], sphere_rgb[2]]


def fill_table():
    global symbol_of_atom
    symb_set =  np.unique(symbol_of_atom, axis=0)
    return symb_set


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


def get_symbol_color(symbol):
    if not isinstance(symbol, str) and isinstance(symbol, Sequence) and len(symbol) == 3:
        return symbol
    for i in range(len(color_of_atom)):
        if str(symbol_of_atom[i]) == str(symbol):
            return [255*c for c in color_of_atom[i]]


def set_symbol_spin_color(rgb_color, symbol=None):
    global color_of_atom
    spin_rgb[0] = int(rgb_color[0]) / 255
    spin_rgb[1] = int(rgb_color[1]) / 255
    spin_rgb[2] = int(rgb_color[2]) / 255
    gr3.clear()
    a, b, c, d, e, f, g = spin_sphere_input(skip_colors=True)
    for i in range(len(color_of_atom)):
        if str(c[i]) == str(symbol) or symbol is None:
            color_of_atom[i] = [spin_rgb[0], spin_rgb[1], spin_rgb[2]]
    gr3.drawspins(a, b,
                  color_of_atom, spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)
    if draw_spheres:
        gr3.drawspheremesh(len(d), d, color_of_sphere, e * 5)
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


def grDrawSpin(file_path_or_object=None, is_sphere=IS_SPHERE_DEFAULT, skip_colors=False):
    # Erstellung der Spins mithilfe der Tupel aus der Einlesedatei
    global spin_rgb, spin_size, color_of_atom, first_draw, draw_spheres

    gr3.clear()
    a, b, c, d, e, f, g = spin_sphere_input(file_path_or_object, skip_colors=skip_colors)
    if first_draw:
        first_draw = False
        create_color_atoms()
    calculate_bonds(a)
    gr3.drawspins(a, b,
                  color_of_atom, spin_size * 0.3, spin_size * 0.1,
                  spin_size * 0.75, spin_size * 2.00)
    draw_spheres = is_sphere
    if draw_spheres:
        gr3.drawspheremesh(len(d), d, color_of_sphere, e * 5)
    if bond_indices is not None:
        gr3.drawcylindermesh(len(bond_indices), bond_positions, bond_directions, len(bond_indices) * bond_color,
                             len(bond_indices) * (0.1 * spin_size,), bond_lengths)




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
        an, bn, cn, dn, en, fn, gn = spin_sphere_input()
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
