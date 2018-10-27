import json
import requests
import src.coordinates.coord as coord

class Api:
    server_id:str = None
    def __init__(self, server_id:str="http://10.4.14.248:5000/api"):
        self.server_id=server_id

    def _command(self, adress: str, command: str) -> dict:
            try:
                print(self.server_id + "/" + command)
                r = requests.get(url=adress + "/" + command)
                print(r.text)
            except Exception as err:
                raise Exception(
                    "Could not execute:\n " + adress + "/" + command + "\n got a problem from server: \n" + str(
                        err.args))
            try:
                if ("404 Not Found" in r.text):
                    result = False
                elif ("500 Internal Server Error" in r.text):
                    raise Exception("got 505 error from server!:\n" + r.text)
                else:
                    result = json.loads(r.text)
            except Exception as err:
                raise Exception(
                    "Could not convert json:\n " + adress + "/" + command + "\n got a following text: \n" + r.text)
            return result

    def _api_command(self, command: str) -> dict:
        return self._command(adress=self.server_id, command=command)

    def get_arena(self) -> dict:
        command="arena"
        return self._api_command(command=command)

class Swarm(Api):
    id:str = None
    swarm_adress:str = None
    swarm_drones:list = []

    def __init__(self, swarm_id:str, server_id:str = "http://10.4.14.248:5000/api", swarm_drones=[34,35,36]):
        super().__init__(server_id=server_id)
        self.id = swarm_id
        self.swarm_adress = server_id+"/"+self.id
        self.swarm_drones = swarm_drones

    def _swarm_command(self, command:str)->dict:
        return self._command(adress=self.swarm_adress, command=command)

    #SWARM FUNCS
    def get_package(self) -> dict:
        command = "package"
        return self._swarm_command(command=command)

    def print_deliveries(self) -> dict:
        command="print_deliveries"
        return self._swarm_command(command=command)

    def reset_packageList(self, seed:int=1)->bool:
        command="reset_package_generator?seed="+str(seed)
        return self._swarm_command(command=command)["success"]

    def register(self, arena:int = 2)->bool:
        command="register_swarm?arena_id="+str(arena)
        register = self._swarm_command(command=command)
        return register["success"]

    def status(self)->dict:
        command="status"
        return self._swarm_command(command=command)

    #DRONE FUNC
    def drone_connect(self, droneID:int, radio:int=0):
        command=str(droneID)+"/connect?r="+str(radio)+"&c=98&a=E7E7E7E7"+str(droneID)+"&dr=2M"
        drone = self._swarm_command(command=command)
        return drone

    def drone_disconnect(self, droneID:int)->bool:
        command=str(droneID)+"/disconnect"
        register = self._swarm_command(command=command)
        return register["success"]

    def drone_takeoff(self, droneID:int, height:float=10, vel:float=100)->bool:
        command=str(droneID)+"/takeoff?z="+str(height)+"&v="+str(vel)
        register = self._swarm_command(command)
        return register["success"]

    def drone_land(self, droneID:int, height:float=0, vel:float=100)->bool:
        command=str(droneID)+"/land?z="+str(height)+"&v="+str(vel)
        register = self._swarm_command(command)
        return register["success"]

    def drone_goto(self, droneID:int, pos:coord.Node=coord.Node(0,0,0), vel:float=100, yaw:float = 0.0)->dict:
        command=str(droneID)+"/goto?x="+str(pos.x)+"&y="+str(pos.y)+"&z="+str(pos.z)+"&yaw="+str(yaw)+"&v="+str(vel)
        register = self._swarm_command(command)
        return register

    def drone_stop(self, droneID:int)->dict:
        command=str(droneID)+"/stop"
        register = self._swarm_command(command=command)
        return register

    def drone_status(self, droneID:int)->dict:
        command=str(droneID)+"/status"
        register = self._swarm_command(command=command)
        return register

    def drone_deliver(self, droneID:int, packageID:int):
        command=str(droneID)+"/deliver?package_id="+str(packageID)
        register = self._swarm_command(command=command)
        return register

    def drone_calibrate(self, droneID:int,):
        command=str(droneID)+"/calibrate"
        register = self._swarm_command(command)
        return register["success"]


class Drone(Api):
    ID:int = None
    swarm_adress:str = None
    capacity:float = None

    def __init__(self, droneID:int, swarm:Swarm, capacity:float=1.0):
        super().__init__(server_id=swarm.server_id)
        self.swarm_adress = swarm.swarm_adress
        self.ID = droneID
        self.capacity = capacity

    def _drone_command(self, command:str)->dict:
        return self._command(adress=self.swarm_adress+"/"+str(self.ID), command=command)

    def connect(self, radio:int=0):
        command="connect?r="+str(radio)+"&c=98&a=E7E7E7E7"+str(self.ID)+"&dr=2M"
        drone = self._drone_command(command=command)
        return drone

    def disconnect(self)->bool:
        command="disconnect"
        register = self._drone_command(command=command)
        return register["success"]

    def takeoff(self, droneID:int, height:float=10, vel:float=100)->bool:
        command="takeoff?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        return register["success"]

    def land(self, height:float=0, vel:float=100)->bool:
        command="land?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        return register["success"]

    def goto(self, pos:coord.Node=coord.Node(0,0,0), vel:float=100, yaw:float = 0.0)->dict:
        command="goto?x="+str(pos.x)+"&y="+str(pos.y)+"&z="+str(pos.z)+"&yaw="+str(yaw)+"&v="+str(vel)
        register = self._drone_command(command)
        return register

    def stop(self)->dict:
        command="stop"
        register = self._drone_command(command=command)
        return register

    def status(self)->dict:
        command="status"
        register = self._drone_command(command=command)
        return register

    def deliver(self, packageID:int):
        command="deliver?package_id="+str(packageID)
        register = self._drone_command(command=command)
        return register

    def calibrate(self):
        command="calibrate"
        register = self._drone_command(command)
        return register["success"]
