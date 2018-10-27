import json
import requests
import enum
import time

class Package:
    coordinates: (float, float, float)=None
    weight: float = None
    id :str = None

    def __init__(self, coordinates:(float, float, float), weight:float, id:str):
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
    waited_dur: bool = False

    def __init__(self, action: dict):
        att_list = ["duration", "relative", "target_x", "target_y", "target_z", "target_yaw"]
        for x in action:
            if(x in att_list):
                setattr(self, x, action[x])

            else:
                raise Exception("Action got an unexpected attribute: "+x+"\n val: "+str(action[x]))
        self.waited_dur = False


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
    drone_jobs:dict = {}

    def __init__(self, swarm_id:str, server_id:str = "http://10.4.14.248:5000/api", swarm_drones=[34,35,36]):
        super().__init__(server_id=server_id)
        self.id = swarm_id
        self.swarm_adress = server_id+"/"+self.id
        self.droneIDs = swarm_drones
        self.drone_jobs = {x:[] for x in self.droneIDs}

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
    sleep_update: int = 2
    accepted_variance = 0.1
    packages:Package = []
    load = 0
    flight_heigth = 0.3

    def __init__(self, droneID:int, swarm:Swarm, capacity:float=1.0):
        super().__init__(server_id=swarm.server_id)
        self.swarm_adress = swarm.swarm_adress
        self.ID = droneID
        self.capacity = capacity

    def load_Package(self, package:Package):
        self.package.append(package)
        self.load += package.weight

    def _reached_target(self):
        targets = {x:getattr(self.action, x)  for x in vars(self.action) if "target" in x and not "yaw" in x}
        actual_pos = {"x":self.x, "y":self.y, "z":self.z, "yaw":self.yaw}
        var_pos = [self.var_x, self.var_y, self.var_z]
        print("Target params: "+str(targets))
        print("actual_vars: "+str(actual_pos))
        accepted_var=self.accepted_variance

        #check if pos is reached
        for target in targets:
            if(targets[target] >= actual_pos[target.replace("target_", "")]-accepted_var and targets[target]  <= actual_pos[target.replace("target_", "")]+accepted_var ):
                continue
            else:
                return False
        print("Reached Targets")
        return True

    def _wait_for_task(self):

        if(self.action == None):
            print("DID not find previous Action")
            return True

        while True:
            if(not self._reached_target()):
                if(self.action.waited_dur):
                    sleep_time = self.sleep_update
                else:
                    sleep_time = 0.95*self.action.duration
                    setattr(self.action, "waited_dur", True)
                print("Waiting for " + str(sleep_time) + "s with status: " + self.status)
                time.sleep(sleep_time)
                self._update_status()
                time.sleep(1)
                continue
            elif any([self.status == x for x in  ["OFFLINE"]]):
                raise Exception("DRONE - ACTION FAILED drone is : "+self.status)
            else:
                print("next")
                break


    def _update_status(self)->dict:
        command="status"
        status = self._drone_command(command=command)

        #update class attributes
        try:
            for x in status:
                if x in ["id", "var_x", "var_y", "var_z", "x", "y", "z", "yaw", "status", "battery_voltage", "battery_percentage"]:
                    setattr(self, x, status[x])
        except Exception as err:
            raise Exception("Could not update. got: "+str(status))
        return status

    def _drone_command(self, command:str)->dict or bool:
        return self._command(adress=self.swarm_adress+"/"+str(self.ID), command=command)

    #funcs
    def assign_job(self, delivery_path:list):
        for x in delivery_path:
            self.goto(float(x[0]), float(x[1]), float(x[2]))

        self.do_delivery()

        for x in reversed(delivery_path):
            self.goto(float(x[0]), float(x[1]), float(x[2]))

    def do_delivery(self, package:Package):
        self.land(height=0.15, vel=0.3)
        self.do_delivery(package)
        self.takeoff()

    #API
    def connect(self, radio:int=0):
        command="connect?r="+str(radio)+"&c=98&a=E7E7E7E7"+str(self.ID)+"&dr=2M"
        self._drone_command(command=command)
        self._update_status()

    def disconnect(self)->bool:
        self._wait_for_task()
        command="disconnect"
        register = self._drone_command(command=command)
        return register["success"]

    def takeoff(self, height:float=flight_heigth, vel:float=1)->dict:
        self._wait_for_task()
        command="takeoff?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        setattr(self, "action", Action(register))
        return register

    def land(self, height:float=0, vel:float=1)->dict:
        self._wait_for_task()
        command="land?z="+str(height)+"&v="+str(vel)
        register = self._drone_command(command)
        setattr(self, "action", Action(register))
        print("Drone: "+str(self.ID)+"\t Landing")
        return register

    def goto(self, pos:(float,float)=(1,1), vel:float=0.5, yaw:float = 0.0)->float:
        print("Goto waiting")
        self._wait_for_task()

        #check bugs
        if(self.z == 0):
            raise Exception("I'm not in the air!")

        command="goto?x="+str(float(pos[0]))+"&y="+str(float(pos[1]))+"&z="+str(float(self.flight_heigth))+"&yaw="+str(yaw)+"&v="+str(vel)
        action_dict = self._drone_command(command)
        print("Drone "+str(self.ID)+" is navigating to: "+str(pos))
        action = Action(action_dict)
        setattr(self, "action", action)
        return action

    def stop(self)->dict:
        command="stop"
        register = self._drone_command(command=command)
        setattr(self, "action", Action(register))
        return register

    def status(self)->dict:
        status = self._update_status()
        return status

    def deliver(self, package:Package)->dict:
        self._wait_for_task()
        command="deliver?package_id="+str(package.id)
        register = self._drone_command(command=command)
        action = Action(register)
        self.load -= package.weight
        setattr(self.action, action)
        return register["success"]

    def calibrate(self)->bool:
        command="calibrate"
        register = self._drone_command(command)
        return register["success"]
