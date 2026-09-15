'''
@file gui.py

@author Sean Hurley <seandhurley@live.com>

@brief Class to hold GUI window/widgets and update methods.
'''
import tkinter as tk
from tkinter import ttk
from vehicle_state import VehicleState

gui_update_rate_ms = 1000

class GUI:
   '''
   @brief Init.
   
   @param root Tk root.
   @param state The vehicle state to display.
   @param state_lock The mutex that protects state.
   ''' 
   def __init__(self, root, state, state_lock):
      self.root = root
      self.state = state
      self.state_lock = state_lock

      self.root.title("MAVLink Vehicle Controller")
      self.root.geometry("500x300")

      self._build_widgets()

   '''
   @brief Initialize this' widgets.
   ''' 
   def _build_widgets(self):
      frame = ttk.Frame(self.root, padding=20)
      frame.pack(fill="both", expand=True)

      ttk.Label(
         frame,
         text="Vehicle State",
         font=("TkDefaultFont", 16, "bold"),
      ).pack(pady=(0, 20))

      self.speed_label = ttk.Label(frame, text="Speed: 0.0 m/s")
      self.speed_label.pack(anchor="w")

      self.heading_label = ttk.Label(frame, text="Heading: 0.0°")
      self.heading_label.pack(anchor="w")

      self.position_label = ttk.Label(
         frame,
         text="Position: 0.000000°, 0.000000°",
      )
      self.position_label.pack(anchor="w")

   '''
   @brief Update the displayed information from this' stored members, then queue another update.
   ''' 
   def update_loop(self):
      # Acquire mutex and get latest state info
      with self.state_lock:
         state = VehicleState(
            speed_ms=self.state.speed_ms,
            heading_deg=self.state.heading_deg,
            latitude_deg=self.state.latitude_deg,
            longitude_deg=self.state.longitude_deg,
         )

      # Update widgets
      self.speed_label.config(
         text=f"Speed: {state.speed_ms:.1f} m/s"
      )

      self.heading_label.config(
         text=f"Heading: {state.heading_deg:.1f}°"
      )

      self.position_label.config(
         text=f"Position: {state.latitude_deg:.6f}°, "
            f"{state.longitude_deg:.6f}°"
      )

      # Queue next update
      self.root.after(gui_update_rate_ms, self.update)