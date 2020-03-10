import numpy as np
import math

def rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])





def testUmgebung(maus1X, maus1Y, maus2X, maus2Y):
    radius = 2
    height = 500
    width = 500
    momentanerKameraVektor = np.array([1, 1, 2])
    oldUpV = np.array([0, 0, 1])

    PaVektor = [0,0,0]
    PcVektor = [0,0,0]

    PaVektor[0] = (maus1X / (width / 2)) - 1
    PaVektor[1] = (maus1Y / (height / 2)) - 1

    if (PaVektor[0] ** 2 + PaVektor[1] ** 2 <= 2):
        PaVektor[2] = math.sqrt(radius ** 2 - PaVektor[0] ** 2 - PaVektor[1] ** 2)
    else:
        PaVektor[2] = 0
        koeff = (radius / 2) / (math.sqrt(PaVektor[0] ** 2 + PaVektor[1] ** 2))
        PaVektor[0] /= koeff
        PaVektor[1] /= koeff

    PcVektor[0] = (maus2X / (width / 2)) - 1
    PcVektor[1] = (maus2Y / (height / 2)) - 1

    if (PcVektor[0] ** 2 + PcVektor[1] ** 2 <= 2):
        PcVektor[2] = math.sqrt(radius ** 2 - PcVektor[0] ** 2 - PcVektor[1] ** 2)
    else:
        PcVektor[2] = 0
        koeff = (radius / 2) / (math.sqrt(PcVektor[0] ** 2 + PcVektor[1] ** 2))
        PcVektor[0] /= koeff
        PcVektor[1] /= koeff





    u = np.cross(PaVektor, PcVektor)
    skalar = np.dot(PaVektor, PcVektor)
    norm = np.linalg.norm(u)
    theta = 1 / (np.arctan(skalar / norm))

    if (math.sqrt(np.dot(u, u) != 0)):
        newUpV = np.dot(rotation_matrix(u, theta), oldUpV)
        momentanerKameraVektor = np.dot(rotation_matrix(u, theta), momentanerKameraVektor)


    print("Pa", PaVektor, "Pc", PcVektor)

    print("Neuer UpVektor" , np.dot(rotation_matrix(u, theta), newUpV))
    print("Neue Kamera Position" , momentanerKameraVektor[0], momentanerKameraVektor[1],momentanerKameraVektor[2])


testUmgebung(250.0,250.0, 251.0, 250.0 )
