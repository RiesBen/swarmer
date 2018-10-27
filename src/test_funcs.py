from src import api_wrapper as api
import time

execute_it=False

swarm = api.Swarm(swarm_id="Swarmer", server_id="http://10.4.14.28:5000/api")

arena = swarm.get_arena()
print("ARENA:\n",arena)

print(swarm.buildings )
buildingOne = swarm.buildings[0]
buildingOne = arena["buildings"][0]
print("BUILDING: ",buildingOne)


packages = [swarm.get_package() for x in range(10)]

print([x.weight for x in packages])

drone_ids = swarm.droneIDs
print(drone_ids)

droneOne = api.Drone(droneID=drone_ids[0], swarm=swarm)

#Do
if execute_it:
    try:
        registered= swarm.register()
    except Exception as err:
        print("Was already Registered")
    print(registered)

    register_drone = droneOne.connect()
    take_off = droneOne.takeoff(height=1, vel=0.1)
    print(take_off)
    time.sleep(5)
    landing = droneOne.land(height=0, vel=0.1)
    print(landing)
    time.sleep(5)
    disconnect = droneOne.disconnect()
