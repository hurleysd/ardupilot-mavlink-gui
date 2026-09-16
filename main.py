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
from mavlink_interface import MAVLinkInterface
from gui import GUI

'''
@brief Main - initializes MAVLink interface and GUI.

@param args Command line arguments.
'''
def main(args):
   # Shared vehicle state
   state = VehicleState()
   state_lock = threading.Lock()

   # Initialize MAVLink connection & interface
   connection = mavutil.mavlink_connection(args.address)
   interface = MAVLinkInterface(connection, args.system_id, args.component_id, state, state_lock)
   
   print(f"Waiting for heartbeat from {args.address} for system {args.system_id} component {args.component_id}...")
   try:
      interface.wait_for_target_heartbeat()
   except KeyboardInterrupt:
      print("\nShutting down...")
      interface.shutdown()
      return

   interface.start_receiver_thread()
   
   # Initialize GUI
   root = tk.Tk()
   
   def shutdown():
      print("\nShutting down...")
      interface.shutdown()
      root.destroy()
      
   root.protocol("WM_DELETE_WINDOW", shutdown)
   
   gui = GUI(root, args.system_id, args.component_id, state, state_lock,
             interface.set_guided_mode, interface.send_arm_cmd, interface.send_goto_cmd)
   gui.update_loop()
   
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