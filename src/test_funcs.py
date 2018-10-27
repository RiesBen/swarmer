from src import api_wrapper as api

swarm = api.Swarm("Swarmer")
arena = swarm.get_arena()
print("ARENA:\n",arena)

buildingOne = arena["buildings"][0]
print("BUILDING: ",buildingOne)

packages = [swarm.get_package() for x in range(10)]
print(packages)

drone_ids = swarm.swarm_drones
print(drone_ids)

droneOne = api.Drone(droneID=drone_ids[0], swarm=swarm)

#Do
registered= api.swarm_register()
print(registered)


register_drone = droneOne.connect()
take_off = droneOne.takeoff(height=20, vel=100)
landing = droneOne.land(height=0, vel=100)
disconnect = droneOne.disconnect()

