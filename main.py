'''
@file main.py

@author Sean Hurley <seandhurley@live.com>

@brief Entry point. Runs the MAVLink message receiver and the GUI.
'''
import argparse
import threading
from pymavlink import mavutil
import tkinter as tk
from vehicle_state import VehicleState
from gui import GUI
      
'''
@brief Receive relevant MAVLink messages for the specified system component on a loop and store them.

@note To be threaded. 

@param connection The MAVLink connection to receive on.
@param system_id The MAVLink system ID to accept messages for.
@param component_id The MAVLink component ID to accept messages for.
@param state The vehicle state to store received data into.
@param state_lock The mutex that protects state.
@param shutdown_event The threading event that will notify when to shutdown.
''' 
def mavlink_recv_loop(connection, system_id, component_id, state, state_lock, shutdown_event):
   while not shutdown_event.is_set():
      msg = connection.recv_match(
         blocking=True,
         timeout=1.0,
      )

      if msg is None:
         continue
      
      # Check the message is for the specified system component
      if (msg.get_srcSystem() == system_id) and (msg.get_srcComponent() == component_id):
   
         match msg.get_type():
            case "GLOBAL_POSITION_INT":
               # Acquire mutex and update shared state
               with state_lock:
                  state.speed_ms = ((msg.vx**2 + msg.vy**2) ** 0.5) / 100.0
                  state.heading_deg = msg.hdg / 100.0
                  state.latitude_deg = msg.lat / 1e7
                  state.longitude_deg = msg.lon / 1e7
            
            case "HEARTBEAT":
               # Acquire mutex and update shared state
               with state_lock:
                  state.mode = mavutil.mode_string_v10(msg)
                  state.armed = bool(
                  msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
               )

'''
@brief Loop until a MAVLink heartbeat message is received for the specified system component.

@param connection The MAVLink connection to receive on.
@param system_id The MAVLink system ID to wait for.
@param component_id The MAVLink component ID to wait for.
@param shutdown_event The threading event that will notify when to shutdown.
@return The received heartbeat message.
'''             
def wait_for_target_heartbeat(connection, system_id, component_id, shutdown_event):
   while not shutdown_event.is_set():
      msg = connection.recv_match(
         type="HEARTBEAT",
         blocking=True,
      )
      
      print(f"Got heartbeat for system {msg.get_srcSystem()} component {msg.get_srcComponent()}")

      if (msg.get_srcSystem() == system_id) and (msg.get_srcComponent() == component_id):
         return msg
   
   return None

'''
@brief Main - initializes MAVLink connection and GUI.

@param args Command line arguments.
'''
def main(args):
   # Shared vehicle state
   state = VehicleState()
   state_lock = threading.Lock()

   # Threading events
   shutdown_event = threading.Event()

   # Initialize MAVLink connection
   connection = mavutil.mavlink_connection(args.address)
   
   print(f"Waiting for heartbeat from {args.address} for system {args.system_id} component {args.component_id}...")
   try:
      wait_for_target_heartbeat(connection, args.system_id, args.component_id, shutdown_event)
   except KeyboardInterrupt:
      print("\nShutting down...")
      
      shutdown_event.set()
      return

   receiver_thread = threading.Thread(
      target=mavlink_recv_loop,
      args=(connection, args.system_id, args.component_id, state, state_lock, shutdown_event),
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
   
   gui = GUI(root, args.system_id, args.component_id, state, state_lock)
   gui.update_loop() # start GUI vehicle state update loop
   
   # Run GUI
   try:
      root.mainloop()
   except KeyboardInterrupt:
      shutdown()

'''
@brief Entrypoint - parses command line arguments.
'''
if __name__ == "__main__":
   parser = argparse.ArgumentParser(
      description="MAVLink controller and telemetry GUI for ArduPilot vehicles"
   )

   parser.add_argument(
      "-a",
      "--address",
      default="udp:127.0.0.1:14550",
      help="MAVLink connection string "
           "(default: udp:127.0.0.1:14550)",
   )
   
   parser.add_argument(
      "-s",
      "--system-id",
      type=int,
      default=1,
      help="MAVLink system ID "
           "(default: 1)",
   )
   
   parser.add_argument(
      "-c",
      "--component-id",
      type=int,
      default=1,
      help="MAVLink component ID "
           "(default: 1)",
   )
   
   main(parser.parse_args())