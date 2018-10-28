from src import api_wrapper as api
from src.PathSolving import path_solver as ps
from src.PathSolving import split_optimization as so

execute_it=True

swarm = api.Swarm(swarm_id="Swarmer", server_id="http://10.4.14.248:5000/api", swarm_drones=[ 34,35, 36])

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
for pack in packages:
    setattr(pack, "coordinates", pack.coordinates[:2])

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

packages_divided = so.assign_package_wrapper(packages,graph=graph)
print("Divided",str(packages_divided))
jobs = []
for ind,drone in enumerate(swarm.droneIDs):
    package_chunk, path_chunk = so.get_my_work(ind, packages_divided)
    jobs.append((path_chunk, package_chunk))

print(jobs)


edges = [(ps.get_point_or_idx(graph[x-1]),ps.get_point_or_idx(graph[x])) for x in range(1, len(graph))]

paths = ps.do([(source_node, package.coordinates[:2]) for package in packages])
jobs = list(zip(paths,packages))

#paths = ps.do(edges)



print(paths)
print(packages)
print(jobs)


for pack in packages:
    print("Deliver package to : "+str(ps.get_point_or_idx(pack.coordinates[:2])))

if execute_it:
    try:
        import time
        swarm.init_drones()
        for job in jobs[:4]:
            for drone in swarm.droneIDs:
                swarm.schedule_jobs(job)
            swarm.run_processes()

        while True:
            if(swarm.wait_for_jobs):
                swarm.shutdown()
                break

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