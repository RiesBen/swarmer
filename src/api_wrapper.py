import json
import requests
import time
import multiprocessing as mp
import src.PathSolving.path_solver as ps
import logging

logging.getLogger("requests").setLevel(logging.WARNING)

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
        att_list = ["duration", "relative", "target_x", "target_y", "target_z", "target_yaw", "battery_percentage"]
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
                r = requests.get(url=adress + "/" + command, )
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
    drones:list =[]
    swarm_thread_pool:mp.Pool = None
    processes = []

    def __init__(self, swarm_id:str, server_id:str = "http://10.4.14.248:5000/api", swarm_drones=[34,35,36], arena:int=2):
        super().__init__(server_id=server_id)
        self.id = swarm_id
        self.swarm_adress = server_id+"/"+self.id
        self.droneIDs = swarm_drones
        self.drone_jobs = {x:"FREE" for x in self.droneIDs}
        #self.swarm_thread_pool = mp.Pool(processes=len(self.droneIDs))

        try:
            self.register(arena=arena)
        except Exception as err:
            print("Was already Registered")


    def init_drones(self):
        print("connect drones")
        for ind,x in enumerate(self.droneIDs):
            print("Drone: "+str(x))
            tmp_drone = Drone(droneID=x, swarm=self)
            self.drones.append(tmp_drone)
            tmp_drone.connect()

    def shutdown(self):
        for drone in self.drones:
            try:
                drone.land()
                time.sleep(1)
                drone.disconnect()
            except:
                continue

    def schedule_jobs(self,job):
        print("new JOB")
        print(job)
        print(self.drone_jobs)
        assigned = False
        for ind,droneID in enumerate(self.droneIDs):
            if(self.drone_jobs[droneID] == "FREE" or not droneID in self.drone_jobs):
                self.drone_jobs.update({droneID:"BUSY"})
                p=mp.Process(target=self.drones[ind].assign_job, args=job)
                self.processes.append(p)
                print(self.drone_jobs)
                return p

        if not(assigned):
            time.sleep(7) #parameter!
            return self.schedule_jobs(job)

    def run_processes(self):
        print(self.processes)
        for p in self.processes:
            print("START")
            p.start()
            time.sleep(1)

        self.wait_for_jobs()


    def swarm_assign_job(self, drone_ID, job):
        self.drones[self.droneIDs.index(drone_ID)].assign_job(job)

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['swarm_thread_pool']
        return self_dict

    def wait_for_jobs(self):
        for p in self.processes:
            p.join()
            print("Wait")
        """
        while True:
            print("JOBS:",[x for x in self.drone_jobs.values()])
            if(all([x == "FREE" for x in self.drone_jobs.values()])):
                print("ALL Free!")
                return True
            else:
                print("waiting for jobs")
                time.sleep(5)
        """
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
    swarm: Swarm = None
    swarm_adress:str = None
    capacity:float = None
    action:Action = None
    status:str = None
    sleep_update: float = 0.5
    accepting_ration:float = 0.75
    accepted_variance = 0.2
    packages:Package = []
    load = 0
    flight_heigth = 0.3

    def __init__(self, droneID:int, swarm:Swarm, capacity:float=1.0):
        super().__init__(server_id=swarm.server_id)
        self.swarm = swarm
        self.swarm_adress = swarm.swarm_adress
        self.ID = droneID
        self.capacity = capacity

    def load_Package(self, package:Package):
            self._wait_for_task()
            ret=self.pickup(package.id)
            if(ret):
                self.packages.append(package)
                self.load += package.weight
            return ret

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
                    sleep_time = self.accepting_ration*self.action.duration
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
    def assign_job(self, *job):
        print("assign job")
        print(job)

        (delivery_paths, package) = job
        self.swarm.drone_jobs.update({self.ID:"BUSY"})
        time.sleep(5*self.swarm.droneIDs.index(self.ID))

        if(self.z < 0.2):
            self.takeoff()

        if(self.x != delivery_paths[0][0] and self.y != delivery_paths[0][1]):
            self.goto(delivery_paths[0])
        self.lower()

        while True:
            if(self.load_Package(package)):
                print("loaded Package: "+str(package.id))
                break
            time.sleep(self.sleep_update)

        for node in delivery_paths:
            print("go to node: "+str(ps.get_point_or_idx(node)))
            self.goto((float(node[0]), float(node[1])))

        self.do_delivery(self.packages.pop())


        for node in reversed(delivery_paths):
            self.goto((float(node[0]), float(node[1])))

        self.swarm.drone_jobs.update({self.ID:"FREE"})


    def do_delivery(self, package:Package):
        self.lower()
        while True:
            if(self.deliver(package)):
                print("Delivered package to: "+str(ps.get_point_or_idx(package.coordinates[:2])))
                break
            time.sleep(self.sleep_update)

    def lower(self):
        self._wait_for_task()

        # check bugs
        if (self.z == 0):
            raise Exception("I'm not in the air!")

        command = "goto?x=" + str(float(self.x)) + "&y=" + str(float(self.y)) + "&z=" + str(
            float(0.1)) + "&yaw=" + str(0.0) + "&v=" + str(0.3)
        action_dict = self._drone_command(command)
        print("Drone " + str(self.ID) + " Lowering")
        action = Action(action_dict)
        setattr(self, "action", action)
        return action

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

    def _other_drone(self, droneID):
        command =str(self.swarm_adress)+"/"+str(droneID)+"/status"
        status = self._command(command=command)
        return status

    def _check_others(self, pos:(float, float)):
        droneIDs=self.swarm.droneIDs
        found_clash = False
        max_iter=3
        i=0
        while found_clash or (i >= max_iter):
            found_clash = False
            for id in droneIDs:
                od_status = self._other_drone(id)
                if(self.ID > od_status["id"] and pos[0] == od_status["x"] and pos[1] == od_status["y"]):
                    time.sleep(5)
                    found_clash = True
                else:
                    continue
            i += 1

    def goto(self, pos:(float,float)=(1,1), vel:float=0.5, yaw:float = 0.0)->float:
        self._wait_for_task()
        self._check_others(pos)

        #check bugs
        if(self.z == 0):
            raise Exception("I'm not in the air!")

        command="goto?x="+str(float(pos[0]))+"&y="+str(float(pos[1]))+"&z="+str(float(self.flight_heigth))+"&yaw="+str(yaw)+"&v="+str(vel)
        action_dict = self._drone_command(command)
        print("Drone "+str(self.ID)+" is navigating to: "+str(ps.get_point_or_idx(pos)))
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
        self.load -= package.weight
        setattr(self, "action", None)
        return register["success"]

    def calibrate(self)->bool:
        command="calibrate"
        register = self._drone_command(command)
        return register["success"]

    def pickup(self, packageID:str):
        command="pickup?package_id="+packageID
        register = self._drone_command(command=command)
        setattr(self, "action", None)
        return register["success"]