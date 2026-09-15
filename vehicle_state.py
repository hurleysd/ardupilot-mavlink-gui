'''
@file vehicle_state.py

@author Sean Hurley <seandhurley@live.com>

@brief Class to hold the state of a vehicle.
'''
from dataclasses import dataclass

@dataclass
class VehicleState:
   speed_ms: float = 0.0         # speed in meters per second
   heading_deg: float = 0.0      # heading in degrees
   latitude_deg: float = 0.0     # latitude in degrees
   longitude_deg: float = 0.0    # longitude in degrees