
from nvitop import Device
import os
import time
import psutil
devices = Device.all()  # or Device.cuda.all()
while True:
    devices = Device.all()
    sensorList = psutil.sensors_temperatures()
    p0 = sensorList['coretemp']
    m0 = psutil.virtual_memory()
    vm0 = psutil.swap_memory()
    print(f'  - CPU Load:        {psutil.cpu_percent(interval=None)}')
    print(f'  - Used RAM:        {m0[2]}')
    print(f'  - Used SWAP:       {vm0[3]}')
    print(f'  - CPU Temperature: {p0[0][1]}')
    os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/cpu/temperature -m "{int(p0[0][1])}"')
    os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/cpu/memory_used -m "{int(m0[2])}"')
    os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/cpu/swap_used -m "{int(vm0[3])}"')
    os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/cpu/load -m "{int(psutil.cpu_percent(interval=None))}"')
    for device in devices:
        processes = device.processes()  # type: Dict[int, GpuProcess]
        sorted_pids = sorted(processes)

        print(device)
        print(f'  - Fan speed:       {device.fan_speed()}%')
        print(f'  - Temperature:     {device.temperature()}C')
        print(f'  - GPU utilization: {device.gpu_utilization()}%')
        print(f'  - Used memory:     {device.memory_used()}')
        print(f'  - Power draw:     {int(device.power_draw() / 1000)}')
        print('-' * 120)
        os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/gpu/power -m "{int(device.power_draw() / 1000)}"')
        os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/gpu/auslastung -m "{int(device.gpu_utilization())}"')
        os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/gpu/temperature -m "{int(device.temperature())}"')
        os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/gpu/fan -m "{int(device.fan_speed())}"')
        os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/gpu/memory_used -m "{int(device.memory_used())}"')
    #    os.system(f'mosquitto_pub -h knusperhaus.ddns.net -t /home/data/hba/cpu/temperature -m "{p0[0][1])}"') 
        time.sleep(1)
