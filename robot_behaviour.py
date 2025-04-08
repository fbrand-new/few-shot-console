import yarp
import time
import logging
import sys

class RobotBehaviour(yarp.RFModule):
    def configure(self, rf):
        self.action_port = yarp.BufferedPortBottle()
        self.action_port.open("/action_recognition/action:i")

        self.behaviour_rpc_port = yarp.RpcClient()
        self.behaviour_rpc_port.open("/action_recognition/behaviour:o")

        self.last_action_time = 0.0
        self.cooldown_period = 15.0  # seconds

        print("Finished configuring the module")
        return True
    
    def updateModule(self):

        input_action = self.action_port.read()

        if input_action is not None:

            action = input_action.get(0).asString()

            if action == "":
                return True

            print("Received action:", action)

            now = time.time()

            if now - self.last_action_time < self.cooldown_period:
                print("Cooldown period active. Please wait.")
                return True

            if action == "wave":
                print("wave")
                self.last_action_time = now
                self.behaviour("wave_hand")
                # time.sleep(0.5)
            elif action == "handshake":
                print("handshake")
                self.last_action_time = now
                self.behaviour("handshake")
                # time.sleep(0.5)
            else:
                print("Unknown action")

        return True
    
    def behaviour(self, behaviour_name):

        response = yarp.Bottle()
        response.clear()

        cmd = yarp.Bottle()
        cmd.addString("reset")
        # Reset before starting a new action
        self.behaviour_rpc_port.write(cmd, response)

        print(f"Response: {response.get(0).asString()}")

        if response.get(0).asString() == "ack":
            print(f"Reset executed successfully.")        
        else:
            print(f"Failed to reset.")

        # Reset bottle
        response.clear()
        cmd.clear()

        # Choose action
        print(f"Choosing action: {behaviour_name}")
        cmd.addString("choose_action")
        cmd.addString(f"{behaviour_name}")
        print(f"Command: {cmd.toString()}")
        self.behaviour_rpc_port.write(cmd, response)

        if response.get(0).asString() == "ack":
            print(f"Choose action executed successfully.")
        else:
            print(f"Failed to choose action.")


        response.clear()
        cmd.clear()

        # Start the action
        cmd.addString("start")
        self.behaviour_rpc_port.write(cmd, response)
        if response.get(0).asString() == "ack":
            print(f"Start action executed successfully.")
        else:
            print(f"Failed to start action.")

        return response.toString()

    def interruptModule(self):
        self.action_port.interrupt()
        self.behaviour_rpc_port.interrupt()

        return True
    
    def close(self):
        self.action_port.close()
        self.behaviour_rpc_port.close()
        return True
    
    def getPeriod(self):
        return 0.1

if __name__ == "__main__":
    yarp.Network.init()
    module = RobotBehaviour()
    rf = yarp.ResourceFinder()
    rf.configure(sys.argv)
    
    # Run the module
    try:
        if not module.configure(rf):
            logging.error("Failed to configure the module")
        else:
            module.runModule()
    except KeyboardInterrupt:
        logging.info("Stopping action recognition module.")
    except Exception as e:
        logging.error(f"Error in action recognition module: {e}")
    finally:
        module.close()
        logging.info("Action recognition module closed.")
    yarp.Network.fini()