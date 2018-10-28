from src import api_wrapper as api
from src.PathSolving import path_solver as ps
from src.PathSolving import split_optimization as so

execute_it=True

swarm = api.Swarm(swarm_id="Swarmer", server_id="http://10.4.14.248:5000/api", swarm_drones=[36])
#248, 28, 37

#arena = swarm.get_arena()
#print("ARENA:\n",arena)

#print(swarm.buildings )
#buildingOne = swarm.buildings[0]
#buildingOne = arena["buildings"][0]
#print("BUILDING: ",buildingOne)

#Do
#generate packages
source_node=[2.2, 1.6]
packages = [swarm.get_package() for x in range(10)]
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
"""
packages_divided = so.assign_package_wrapper(packages,graph=graph)
my_work, optimal_path = so.get_my_work(len(drone_ids), packages_divided)
"""

edges = [(graph[x-1],graph[x]) for x in range(1, len(graph))]
paths = ps.do([(source_node, package.coordinates[:2]) for package in packages])

print(paths)
print(packages)

for pack in packages:
    print("Deliver package to : "+str(ps.get_point_or_idx(pack.coordinates[:2])))

if execute_it:
    try:
        swarm.init_drones()
        swarm.schedule_jobs(delivery_path=[paths], packages=[packages[0]])

        #while True:
        #    if(swarm.check_jobs_done):
        #        swarm.shutdown()

        swarm.shutdown()

        """
        droneOne.connect()
        droneOne.calibrate()
        for ind, path in enumerate(paths):
            droneOne.assign_job(job=([path], [packages[ind]]))
        droneOne.land(vel=0.2)
        droneOne.disconnect()
        """
        print(swarm.print_deliveries())

    except Exception as err:
        #droneOne.land()
        #droneOne.disconnect()
        swarm.shutdown()
        print("error: "+str(err.with_traceback(err)))