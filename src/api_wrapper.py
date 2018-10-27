import json
import requests
import enum
import time

class drone_state(enum.Enum):
    IDLE = "IDLE"
    OFFLINE = "OFFLINE"
    HOVERING = "HOVERING"
    STARTING = "STARTING"
    LANDING = "LANDING"
    NAVIGATING = "NAVIGATING"

class Package:
    coordinates: (int, int, int)=None
    weight: float = None
    id :str = None

    def __init__(self, coordinates:(int, int, int), weight:float, id:str):
        self.coordinates = coordinates
        self.weight = weight
        self.id = id


class Action:
    duration: float = None
    relative: bool = None
    target_x: float = None
    target_y: float = None
    target_yaw: float = None
    target_z: float = None
    waited_dur: bool = None

    def __init__(self, action: dict):
        att_list = ["duration", "relative", "target_x", "target_y", "target_z", "target_yaw"]
        for x in action:
            if(x in att_list):
                setattr(self, x, action[x])

            else:
                raise Exception("Action got an unexpected attribute: "+x+"\n val: "+str(action[x]))
        waited_dur = False


class Api:
    server_id:str = None
    def __init__(self, server_id:str="http://10.4.14.248:5000/api"):
        self.server_id=server_id
        arena = self.get_arena()
        self.min_x = arena["min_x"]
        self.min_y = arena["min_y"]
        self.min_z = arena["min_z"]
        self.max_x = arena["max_x"]
        self.max_y = arena["max_y"]
        self.max_z = arena["max_z"]
        self.buildings = arena["buildings"]



    def _command(self, adress: str, command: str) -> dict or bool:
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

    def _api_command(self, command: str) -> dict or bool:
        return self._command(adress=self.server_id, command=command)

    def get_arena(self) -> dict:
        command="arena"
        return self._api_command(command=command)




class Swarm(Api):

    id:str = None
    swarm_adress:str = None
    droneIDs:list = []
    packages: list = []

    def __init__(self, swarm_id:str, server_id:str = "http://10.4.14.248:5000/api", swarm_drones=[34,35,36]):
        super().__init__(server_id=server_id)
        self.id = swarm_id
        self.swarm_adress = server_id+"/"+self.id
        self.droneIDs = swarm_drones

    def _swarm_command(self, command:str)->dict  or bool:
        return self._command(adress=self.swarm_adress, command=command)

    #SWARM FUNCS
    def get_package(self) -> Package:
        command = "package"
        packages = self._swarm_command(command=command)

        return Package(coordinates=packages["coordinates"], weight=packages["weight"], id=packages["id"])

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

class Drone(Api):
    ID:int = None
    swarm_adress:str = None
    capacity:float = None
    action:Action = None
    status:str = None
    def __init__(self, droneID:int, swarm:Swarm, capacity:float=1.0):
        super().__init__(server_id=swarm.server_id)
        self.swarm_adress = swarm.swarm_adress
        self.ID = droneID
        self.capacity = capacity

    def _wait_for_task(self):
        while True:
            if(any([self.status == x for x in [drone_state.LANDING, drone_state.STARTING, drone_state.NAVIGATING]])):
                if(self.action.waited_dur):
                    time.sleep(3)
                else:
                    time.sleep(0.95*self.action.duration)
                continue

            elif any([self.status == x for x in  [drone_state.OFFLINE]]):
                raise Exception("DRONE - ACTION FAILED drone is : "+self.status)
            else:
                self._update_status()
                break

    def _update_status(self, status:dict):
        for x in status:
            if x in ["id", "var_x", "var_y", "var_z", "x", "y", "z", "yaw", "status", "battery_voltage", "battery_percentage"]:
                setattr(self, x, status[x])



    def _drone_command(self, command:str)->dict or bool:
        return self._command(adress=self.swarm_adress+"/"+str(self.ID), command=command)

    def connect(self, radio:int=0):
        command="connect?r="+str(radio)+"&c=98&a=E7E7E7E7"+str(self.ID)+"&dr=2M"
        status = self._drone_command(command=command)
        self._update_status(status)

    def disconnect(self)->bool:
        self._wait_for_task()
        command="disconnect"
        register = self._drone_command(command=command)
        self._update_status()
        return register["success"]

    def takeoff(self, height:float=1, vel:float=100)->dict:
        self._wait_for_task()
        command="takeoff?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        self._update_status()
        return register

    def land(self, height:float=0, vel:float=10)->dict:
        self._wait_for_task()
        command="land?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        self._update_status()
        return register

    def goto(self, pos:(0,0,0)=(0,0,0), vel:float=10, yaw:float = 0.0)->float:
        self._wait_for_task()
        command="goto?x="+str(pos.x)+"&y="+str(pos.y)+"&z="+str(pos.z)+"&yaw="+str(yaw)+"&v="+str(vel)
        action_dict = self._drone_command(command)
        print("Drone "+self.ID+" is navigating to: "+str(pos))
        action = Action(action_dict)
        setattr(self, "action",action)
        self._update_status()
        return action

    def stop(self)->dict:
        command="stop"
        register = self._drone_command(command=command)
        self._update_status()
        return register

    def status(self)->dict:
        command="status"
        status = self._drone_command(command=command)
        self._update_status(status)
        return status

    def deliver(self, packageID:int)->dict:
        self._wait_for_task()
        command="deliver?package_id="+str(packageID)
        register = self._drone_command(command=command)
        self._update_status()
        return register

    def calibrate(self)->bool:
        command="calibrate"
        register = self._drone_command(command)
        return register["success"]


