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





def testUmgebung(x,y,z):
    d1Vektor = np.array([50., 10., 5.])
    d2Vektor = np.array([0., 10., 5.])


    d1Norm = np.linalg.norm(d1Vektor)
    d1Vektor[0] /= d1Norm
    d1Vektor[1] /= d1Norm
    d1Vektor[2] /= d1Norm

    d2Norm = np.linalg.norm(d2Vektor)
    d2Vektor[0] /= d2Norm
    d2Vektor[1] /= d2Norm
    d2Vektor[2] /= d2Norm

    newUpV = np.array([-1., 1., 0.])

    fowardVektor = np.array([0., 0., 1.])

    negativfVektor = fowardVektor * -1

    upNorm = np.linalg.norm(newUpV)
    newUpV[0] /= upNorm
    newUpV[1] /= upNorm
    newUpV[2] /= upNorm


    rightVektor = [1.,1.,0.]
    uVektor = np.cross((rightVektor/np.linalg.norm(rightVektor)), fowardVektor)
    matrix = np.array([rightVektor, uVektor, negativfVektor])

    print(matrix)
    d1Vektor = np.matmul(matrix.T, d1Vektor)

    d2Vektor = np.matmul(matrix.T, d2Vektor)

    d1Norm = np.linalg.norm(d1Vektor)
    d1Vektor[0] /= d1Norm
    d1Vektor[1] /= d1Norm
    d1Vektor[2] /= d1Norm

    d2Norm = np.linalg.norm(d2Vektor)
    d2Vektor[0] /= d2Norm
    d2Vektor[1] /= d2Norm
    d2Vektor[2] /= d2Norm

    print("d1", d1Vektor, "d2", d2Vektor)

    n = np.cross(d1Vektor, d2Vektor)
    dot = np.dot(d1Vektor, d2Vektor)
    print("dot", dot)
    """if dot >= 1 - 1e-3:
        print("bug")
        exit(1)"""

    winkel = np.arccos(dot)

    print("Neuer UpVektor" , np.dot(rotation_matrix(n, winkel), newUpV))
    print("Neue Kamera Position" , np.dot(rotation_matrix(n, winkel), np.array([x, y, z])))


testUmgebung(30, 30, 30)
