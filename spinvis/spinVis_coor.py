import math
import numpy as np
camera_koordinates = np.array([50.0, 2.0, 2.0])

def euler_angles_to_koordinates(azimuth, tilt, r ):
    camera_koordinates[0] = r * math.sin(azimuth) * math.cos(tilt)  # Kugleformel mit Winkeln zur Kamerasteuerung
    camera_koordinates[1] = r * math.sin(azimuth) * math.sin(tilt)
    camera_koordinates[2] = r * math.cos(azimuth)