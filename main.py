'''
@file main.py

@author Sean Hurley <seandhurley@live.com>

@brief Entry point. Runs the MAVLink message receiver and the GUI.
'''
import threading
from pymavlink import mavutil
import tkinter as tk
from vehicle_state import VehicleState
from gui import GUI

'''
@brief Print information about this tool.
'''
def printInfo():
   pass
      
'''
@brief Receive relevant MAVLink messages on a loop and store them. To be threaded. 

@param connection The MAVLink connection to receive on.
@param state The vehicle state to store received data into.
@param state_lock The mutex that protects state.
@param shutdown_event The threading event that will notify when to shutdown.
''' 
def mavlink_recv_loop(connection, state, state_lock, shutdown_event):
   while not shutdown_event.is_set():
      msg = connection.recv_match(
         type="GLOBAL_POSITION_INT",
         blocking=True,
         timeout=1.0,
      )

      if msg is None:
         continue
   
      # Acquire mutex and update shared state
      with state_lock:
         state.speed_ms = (msg.vx**2 + msg.vy**2) ** 0.5 / 100.0
         state.heading_deg = msg.hdg / 100.0
         state.latitude_deg = msg.lat / 1e7
         state.longitude_deg = msg.lon / 1e7
         
'''
@brief Main - initializes MAVLink connection and GUI.
'''
def main():
   # Shared vehicle state
   state = VehicleState()
   state_lock = threading.Lock()

   # Threading events
   shutdown_event = threading.Event()

   # Initialize MAVLink connection
   connection = mavutil.mavlink_connection("udp:127.0.0.1:14550")

   print("Waiting for heartbeat...")
   connection.wait_heartbeat()

   print(
      f"Connected to system {connection.target_system}, "
      f"component {connection.target_component}"
   )

   receiver_thread = threading.Thread(
      target=mavlink_recv_loop,
      args=(connection, state, state_lock, shutdown_event),
      daemon=True,
   )
   receiver_thread.start()
   
   # Initialize GUI
   root = tk.Tk()
   
   def shutdown():
      print("\nShutting down...")

      shutdown_event.set()
      receiver_thread.join(timeout=2.0)
      connection.close()
      root.destroy()
      
   root.protocol("WM_DELETE_WINDOW", shutdown)
   
   gui = GUI(root, state, state_lock)
   gui.update_loop() # start GUI vehicle state update loop
   
   # Run GUI
   try:
      root.mainloop() # start Tk event loop and show the GUI
   except KeyboardInterrupt:
      shutdown()

'''
@brief Entrypoint.
'''
if __name__ == "__main__":
   main()