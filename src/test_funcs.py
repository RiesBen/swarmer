from src import api_wrapper as api

swarm = api.Swarm("Swarmer")
arena = swarm.get_arena()
drone_ids = swarm.swarm_drones

print(drone_ids)

arena = api.get_arena()
print(arena)

buildingOne = arena["buildings"][0]

print(buildingOne)

registered= api.swarm_register()
print(registered)

drones = [34,35,36]

#register_drone = api.connect_drone(droneID=drones[1])

#unregister = api.disconnect_drone(drones[1])
packages = [api.get_package() for x in range(10)]
print(packages)