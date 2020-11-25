import math
import numpy as np
from . import spinVis_camera
camera_koordinates = np.array([50.0, 2.0, 2.0])

def euler_angles_to_koordinates(theta, phi,r, upangle):
    camera_koordinates[0] = (r * math.sin(theta) * math.cos(phi)) + spinVis_camera.focus_point[0]  # Kugleformel mit Winkeln zur Kamerasteuerung
    camera_koordinates[1] = (r * math.sin(theta) * math.sin(phi)) + spinVis_camera.focus_point[1]
    camera_koordinates[2] = (r * math.cos(theta)) + spinVis_camera.focus_point[2]
    r = np.array([-math.sin(phi), math.cos(phi), 0])
    v = np.array([-math.cos(phi) * math.cos(theta), -math.sin(phi)*math.cos(theta), math.sin(theta)])
    spinVis_camera.up_vector = v * math.cos(upangle) - r * math.sin(upangle)
    spinVis_camera.grCameraArcBallChange(camera_koordinates)

