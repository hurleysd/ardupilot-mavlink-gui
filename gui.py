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
   @brief Constructor.
   
   @param root Tk root.
   @param system_id The MAVLink system ID to display.
   @param component_id The MAVLink component ID to display.
   @param state The vehicle state to display.
   @param state_lock The mutex that protects state.
   ''' 
   def __init__(self, root, system_id, component_id, state, state_lock,
                guided_cmd_callback, arm_cmd_callback, goto_cmd_callback):
      self.root = root
      self.system_id = system_id
      self.component_id = component_id
      
      self.state = state
      self.state_lock = state_lock
      
      self.guided_cmd_callback = guided_cmd_callback
      self.arm_cmd_callback = arm_cmd_callback
      self.goto_cmd_callback = goto_cmd_callback

      self.root.title("MAVLink Vehicle Controller")
      self.root.geometry("500x450")

      self._build_widgets()

   '''
   @brief Initialize this' widgets.
   ''' 
   def _build_widgets(self):
      frame = ttk.Frame(self.root, padding=20)
      frame.pack(fill="both", expand=True)

      # Title with IDs
      ttk.Label(
         frame,
         text=f"System {self.system_id} Component {self.component_id}",
         font=("TkDefaultFont", 16, "bold"),
      ).pack(pady=(0, 20))

      # Vehicle status
      self.mode_label = ttk.Label(frame, text="Mode: UNKNOWN")
      self.mode_label.pack(anchor="w")
      
      self.armed_label = ttk.Label(frame, text="Armed: FALSE")
      self.armed_label.pack(anchor="w")
            
      self.speed_label = ttk.Label(frame, text="Speed: 0.0 m/s")
      self.speed_label.pack(anchor="w")

      self.heading_label = ttk.Label(frame, text="Heading: 0.0°")
      self.heading_label.pack(anchor="w")

      self.position_label = ttk.Label(
         frame,
         text="Position: 0.000000°, 0.000000°",
      )
      self.position_label.pack(anchor="w")
      
      # Vehicle commands
      control_frame = ttk.LabelFrame(
         frame,
         text="Vehicle Control",
         padding=10,
      )
      control_frame.pack(
         fill="x",
         pady=(20, 10),
      )

      ttk.Button(
         control_frame,
         text="SET GUIDED",
         command=self.guided_cmd_callback,
      ).pack(side="left", padx=5)

      ttk.Button(
         control_frame,
         text="ARM",
         command=self.arm_cmd_callback,
      ).pack(side="left", padx=5)

      destination_frame = ttk.LabelFrame(
         frame,
         text="Guided Destination",
         padding=10,
      )
      destination_frame.pack(fill="x")

      ttk.Label(
         destination_frame,
         text="Latitude:",
      ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

      self.latitude_entry = ttk.Entry(
         destination_frame,
         width=20,
      )
      self.latitude_entry.grid(
         row=0,
         column=1,
         sticky="ew",
         padx=5,
         pady=5,
      )

      ttk.Label(
         destination_frame,
         text="Longitude:",
      ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

      self.longitude_entry = ttk.Entry(
         destination_frame,
         width=20,
      )
      self.longitude_entry.grid(
         row=1,
         column=1,
         sticky="ew",
         padx=5,
         pady=5,
      )

      ttk.Button(
         destination_frame,
         text="GO TO",
         command=self._goto_button_pressed,
      ).grid(
         row=2,
         column=0,
         columnspan=2,
         pady=(10, 5),
      )

      destination_frame.columnconfigure(1, weight=1)
      
   '''
   @brief
   ''' 
   def _goto_button_pressed(self):
      try:
         latitude = float(self.latitude_entry.get())
         longitude = float(self.longitude_entry.get())
      except ValueError:
         print("Invalid waypoint coordinates")
         return

      self.goto_cmd_callback(latitude, longitude)

   '''
   @brief Update the displayed information from this' stored members, then queue another update.
   ''' 
   def update_loop(self):
      # Acquire mutex and get latest state info
      with self.state_lock:
         state = VehicleState(
            mode=self.state.mode,
            armed=self.state.armed,
            speed_ms=self.state.speed_ms,
            heading_deg=self.state.heading_deg,
            latitude_deg=self.state.latitude_deg,
            longitude_deg=self.state.longitude_deg,
         )

      # Update widgets
      self.mode_label.config(
         text="Mode: " + state.mode
      )
      
      self.armed_label.config(
         text="Armed: " + str(state.armed)
      )
      
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
      self.root.after(gui_update_rate_ms, self.update_loop)