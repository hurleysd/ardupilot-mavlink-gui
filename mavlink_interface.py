'''
@file mavlink_interface.py

@author Sean Hurley <seandhurley@live.com>

@brief Class to manage MAVLink connection for sending messages to and receiving messages
       from the target vehicle system component.
'''
import threading
from pymavlink import mavutil

class MAVLinkInterface:
   '''
   @brief Constructor.
   
   @note This will take ownership over the provided connection and become responsible for 
         closing it on shutdown.

   @param connection The MAVLink connection to send/receive on.
   @param system_id The MAVLink system ID of the target vehicle.
   @param component_id The MAVLink component ID of the target vehicle.
   @param state The vehicle state to store received data into.
   @param state_lock The mutex that protects state.
   ''' 
   def __init__(self, connection, system_id, component_id, state, state_lock):
      self.connection = connection
      self.system_id = system_id
      self.component_id = component_id
      
      self.state = state
      self.state_lock = state_lock
      
      self.shutdown_event = threading.Event()
      self.receiver_thread = None
      
   '''
   -------------------------------------------------------------------------------------------
   STATUS RECEIVING
   -------------------------------------------------------------------------------------------
   '''
   
   '''
   @brief Loop until a MAVLink heartbeat message is received for the specified system component.

   @return True if the target heatbeat was received, otherwise False on shutdown.
   '''             
   def wait_for_target_heartbeat(self):
      while not self.shutdown_event.is_set():
         msg = self.connection.recv_match(
            type="HEARTBEAT",
            blocking=True,
            timeout=1.0
         )
         
         if msg is None:
            continue
         
         print(f"Got heartbeat for system {msg.get_srcSystem()} component {msg.get_srcComponent()}")

         if (msg.get_srcSystem() == self.system_id) and (msg.get_srcComponent() == self.component_id):
            return True
      
      return False
   
   '''
   @brief Start the background MAVLink receiver thread.
   '''
   def start_receiver_thread(self):
      if self.receiver_thread is None:
         self.receiver_thread = threading.Thread(
            target=self._recv_loop,
            daemon=True,
         )
         self.receiver_thread.start()
      
   '''
   @brief Receive relevant MAVLink messages for the specified system component on a loop and store them.

   @note To be threaded. 
   ''' 
   def _recv_loop(self):
      while not self.shutdown_event.is_set():
         msg = self.connection.recv_match(
            blocking=True,
            timeout=1.0,
         )

         if msg is None:
            continue
         
         # Ignore messages for the non-target system component
         if (msg.get_srcSystem() != self.system_id) or (msg.get_srcComponent() != self.component_id):
            continue
      
         match msg.get_type():
            case "GLOBAL_POSITION_INT":
               # Acquire mutex and update shared state
               with self.state_lock:
                  self.state.speed_ms = ((msg.vx**2 + msg.vy**2) ** 0.5) / 100.0
                  self.state.heading_deg = msg.hdg / 100.0
                  self.state.latitude_deg = msg.lat / 1e7
                  self.state.longitude_deg = msg.lon / 1e7
            
            case "HEARTBEAT":
               # Acquire mutex and update shared state
               with self.state_lock:
                  self.state.mode = mavutil.mode_string_v10(msg)
                  self.state.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                  
   '''
   @brief Stop the receiver thread and close the MAVLink connection.
   '''
   def shutdown(self):
      self.shutdown_event.set()

      if (self.receiver_thread is not None) and (self.receiver_thread.is_alive()):
         self.receiver_thread.join(timeout=2.0)

      self.connection.close()
      
   '''
   -------------------------------------------------------------------------------------------
   COMMAND SENDING
   -------------------------------------------------------------------------------------------
   '''
   
   '''
   @brief Change the vehicle to GUIDED mode.
   '''
   def set_guided_mode(self):
      self.connection.set_mode("GUIDED")

   '''
   @brief Send an arm command to the vehicle.
   '''
   def send_arm_cmd(self):
      self.connection.mav.command_long_send(
         self.system_id,
         self.component_id,
         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
         0,
         1, # arm
         0,
         0,
         0,
         0,
         0,
         0,
      )

   '''
   @brief Send a global position target to the vehicle.
   
   @param latitude_deg Target latitude in degrees.
   @param longitude_deg Target longitude in degrees.
   '''
   def send_goto_cmd(self, latitude_deg, longitude_deg):
      self.connection.mav.set_position_target_global_int_send(
         0, # time_boot_ms
         self.system_id,
         self.component_id,
         mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
         3580, # position only
         int(latitude_deg * 1e7),
         int(longitude_deg * 1e7),
         0,       # altitude
         0, 0, 0, # velocity x, y, z
         0, 0, 0, # acceleration x, y, z
         0, 0,    # yaw, yaw rate
      )