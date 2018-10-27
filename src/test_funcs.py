from src import api_wrapper as api

api = api.Api("swarmer")




arena = api.get_arena()
print(arena)

buildingOne = arena["buildings"][0]

print(buildingOne)

registered= api.register_swarm()
print(registered)

drones = [34,35,36]

register_drone = api.connect_drone(droneID=drones[0])

#packages = [api.get_package() for x in range(10)]
#print(packages)