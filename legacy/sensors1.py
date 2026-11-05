import psutil
sensorList = psutil.sensors_temperatures()
p0 = sensorList['coretemp']
print(type(p0))
print(p0[0])
print(p0[0][1])

