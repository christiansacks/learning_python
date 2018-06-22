def getName(): # define function "getName"
    name = input("What is your name: ") # get input from user and store in var "name"
    return name # return what was just captured

def getLocation(): # define funciton "getLocation"
    location = input("Where are you right now: ") # get input from user and store in var "location"
    return location


name = getName()
print("Hello there, " + name + ".")

location = getLocation()

users = {"name":name, "location":location}

print(users)
print(len(users))
print("What is happening at " + location + "?")
