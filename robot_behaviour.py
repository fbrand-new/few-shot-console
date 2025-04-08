import yarp
import time

class RobotBehaviour(yarp.RFModule):
    def configure(self, rf):
        self.action_port = yarp.Port()
        self.action_port.open("/action_recognition/action:i")

        self.behaviour_rpc_port = yarp.RpcClient()
        self.behaviour_rpc_port.open("/action_recognition/behaviour:o")

        self.last_action_time = None
        self.cooldown_period = 10.0  # seconds

        return super().configure(rf)
    
    def updateModule(self):
        input_action = self.action_port.read()

        if input_action is not None:

            now = time.time()

            if now - self.last_action_time < self.cooldown_period:
                print("Cooldown period active. Please wait.")
                return True

            action = input_action.get(0).asString()
            if action == "wave":
                print("wave")
                self.behaviour("wave")
            elif action == "handshake":
                print("handshake")
                self.behaviour("handshake")
            else:
                print("Unknown action")

        return True
    
    def behaviour(self, behaviour_name):
        response = yarp.Bottle()
        response.clear()

        cmd = yarp.Bottle()
        cmd.addString(behaviour_name)

        # Implement behaviour action
        self.behaviour_rpc_port.write(cmd, response)
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
    module.runModule()
    yarp.Network.fini()