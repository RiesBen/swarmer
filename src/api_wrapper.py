import os
import json
import requests

class Api:
    swarm_id:str = None
    server_id:str = None
    swarm_adress:str = None

    def __init__(self, swarm_id:str, server_id:str = "http://10.4.14.248:5000/api"):
        self.swarm_id = swarm_id
        self.server_id = server_id
        self.swarm_adress = server_id+"/"+self.swarm_id

    def _command(self, adress:str, command:str)->dict:
        try:
            print(self.server_id+"/"+command)
            r=requests.get(url=adress+"/"+command)
            print(r.text)
        except Exception as err:
            raise Exception("Could not execute:\n "+adress+"/"+command+"\n got a problem from server: \n"+str(err.args))
        try:
            if ("404 Not Found" in r.text):
                result = False
            else:
                result = json.loads(r.text)
        except Exception as err:
            raise Exception("Could not convert json:\n "+adress+"/"+command+"\n got a following text: \n"+r.text)
        return result


    def _api_command(self, command:str)->dict:
        return self._command(adress=self.server_id, command=command)
    def _swarm_command(self, command:str)->dict:
        return self._command(adress=self.swarm_adress, command=command)



    def get_package(self) -> dict:
        command = "package"
        return self._swarm_command(command=command)

    def get_arena(self) -> dict:
        command="arena"
        return self._api_command(command=command)

    def print_deliveries(self) -> dict:
        command="print_deliveries"
        return self._swarm_command(command=command)

    def register_swarm(self, arena:int = 2):
        command="register_swarm?arena_id="+str(arena)
        register = self._swarm_command(command=command)
        return register["success"]

    def connect_drone(self, droneID:int, radio:int=0):
        command=str(droneID)+"/connect?r="+str(radio)+"&c=98&a=E7E7E7E7"+str(droneID)+"&dr=2M"
        register = self._swarm_command(command=command)
        print(register)
        return register["success"]