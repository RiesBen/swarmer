from src import api_wrapper as api
from src.PathSolving import path_solver as ps
import time

execute_it=True

swarm = api.Swarm(swarm_id="Swarmer", server_id="http://10.4.14.248:5000/api")
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
    registered= swarm.register(arena=2)
except Exception as err:
    print("Was already Registered")

#generate packages
source_node=[2.2, 1.6]
packages = [swarm.get_package() for x in range(2)]
print([x.weight for x in packages])

#generate_paths:
graph= [[2.2, 1.6], #[2.3,1.6],
            [2.6, 0.6], #[2.7,0.5],
            [3.4, 1.4], #[3.7,1.5],
            [2.4, 3.4], #[2.5,3.4],
            [0.6, 2.2], #[0.5,2.1],
            [1.4, 3.2], #[1.4,3.2],
            [1.0, 1.6], #[0.8,1.6],
            [3.6, 0.6], #[3.7,0.5],
            [3.2, 3.2]] #[3.3,3.1],
edges = [(graph[x-1],graph[x]) for x in range(1, len(graph))]
paths = ps.do([(source_node, package.coordinates[:2]) for package in packages])
paths = ps.do(edges)
print(paths)
print(packages)

exit()
if execute_it:
    try:
        """
            droneOne.connect()
            droneOne.calibrate()
            droneOne.load_Package(packages[0])
            droneOne.takeoff(height=0.3, vel=1)
            print("GOTO!")
            droneOne.goto(pos=(1.0, 1.6), vel=0.6)
            droneOne.do_delivery(droneOne.packages[0])
            droneOne.goto(pos=(2.2,1.6), vel=0.6)
            print("LAAAND")
            droneOne.land(height=0, vel=0.3)
            droneOne.disconnect()
        """

        """
        droneOne.takeoff()
        for path in paths:
            print("Do path:"+str(path))
            for node in path:
                print(node)
                droneOne.goto((float(node[0]), float(node[1])))

        droneOne.land()
        droneOne.disconnect()
        """
        droneOne.connect()
        droneOne.calibrate()
        droneOne.assign_job(delivery_paths=paths , packages=[packages[0]])
        droneOne.land()
        droneOne.disconnect()
        print(swarm.print_deliveries())

    except Exception as err:
        droneOne.land()
        droneOne.disconnect()
        print("error: "+str(err.with_traceback(err)))