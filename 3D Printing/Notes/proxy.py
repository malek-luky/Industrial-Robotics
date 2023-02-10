import time
from py_openshowvar import openshowvar #pip3.9 install py_openshowvar
#https://pypi.org/project/py-openshowvar
#every robot is different, this works only for kuka robots
#robot operates on windows and vxwarh which communicates between in other
#the communication is processed on the comptuer memory
#PC is connected via proxy between windows and vxarh
#communication is based on TCP/IP

client = openshowvar('172.31.1.147',7000) #that opens the proxy, which allow to open and write to kuka robot config file
#I.P adress + port 7000
print(client.can_connect)

ov = client.read('$OV_PRO')
print(ov)

#ov = client.write('$OV_PRO','100')
#print ov

ov = client.read('$IN[12]') #read the status in the config file
print(ov)

ov = client.write('$OUT[17]',False)
print(ov)

ov = client.read('XHOME')
print(ov)

ov = client.write('XHOME','{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
print(ov)

#axisRead = client.read('MYAXIS')
#print axisRead

for i in range(10):
     axisWrite = client.write('MYAXIS', '{A1 0,A2 -90,A3 90,A4 0,A5 0,A6 10}')
     print(axisWrite)
     time.sleep(1)
     axisWrite = client.write('MYAXIS', '{A1 10,A2 -90,A3 90,A4 0,A5 0,A6 -10}')
     print(axisWrite)
     time.sleep(1)

client.close()
