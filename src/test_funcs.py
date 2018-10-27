from src import api_wrapper as api
import time

execute_it=True

swarm = api.Swarm(swarm_id="Swarmer", server_id="http://10.4.14.28:5000/api")
#248, 28, 37

arena = swarm.get_arena()
#print("ARENA:\n",arena)

#print(swarm.buildings )
buildingOne = swarm.buildings[0]
buildingOne = arena["buildings"][0]
#print("BUILDING: ",buildingOne)

drone_ids = swarm.droneIDs
#print(drone_ids)

droneOne = api.Drone(droneID=drone_ids[1], swarm=swarm)

#Do
try:
    registered= swarm.register()
except Exception as err:
    print("Was already Registered")

#generate packages
#packages = [swarm.get_package() for x in range(10)]
#print([x.weight for x in packages])

if execute_it:
    try:
        register_drone = droneOne.connect()
        droneOne.takeoff(height=0.3, vel=1)

        droneOne.goto(pos=(1.0, 1.6), vel=0.2)
        droneOne.do_delivery()
        #droneOne.goto(pos=(2.2,1.6,0.0))

        droneOne.land(height=0, vel=1)
        droneOne.disconnect()

    except Exception as err:
        droneOne.land()
        droneOne.disconnect()
        print("error: "+str(err.args))