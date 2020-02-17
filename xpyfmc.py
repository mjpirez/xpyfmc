import sys
import threading
import xpynetwork
from xpydef import acf_description, cdu_datarefs
from time import sleep
from os import system, name 

cduRefs = cdu_datarefs

def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

### discover x-plane ip via multicast
multicast = xpynetwork.MulticastListener('239.255.1.1', 49707)
beacon = multicast.waitForBeacon()
print 'ExtPlane IP:', beacon.ipAddress
print 'ExtPlane port:', beacon.port

### connect and wait for extplane version
client = xpynetwork.XPlaneTcpClient(beacon.ipAddress, beacon.port)
version = client.waitForMsg()
if 'VERSION 1003' not in version:
   print 'error attempting connection to extplane'
   sys.exit()
print version
print 'connected!!'

### wait for zibo aircraft to boot up
print '>>> sending: %s' %acf_description
client.sendMsg('sub ' + acf_description)
print 'start a new flight!'
aircraft_desc = client.waitForMsg()
print 'zibo found!'

### start receive of datarefs in background
threading.Thread(target=client.updateCDUDataRefs, args=(cduRefs, )).start()

### subscribe to CDU display datarefs 
print 'subscribing to datarefs...'
client.subscribeForCDUDisplay(cduRefs)

### print drefs updates
clear()
while True:
   try:
      print cduRefs['laminar/B738/fmc1/Line00_L']
      print cduRefs['laminar/B738/fmc1/Line01_L']
      print cduRefs['laminar/B738/fmc1/Line02_L']
      print cduRefs['laminar/B738/fmc1/Line03_L']
      print cduRefs['laminar/B738/fmc1/Line04_L']
      print cduRefs['laminar/B738/fmc1/Line05_L']
      print cduRefs['laminar/B738/fmc1/Line06_L']
      print cduRefs['laminar/B738/fmc1/Line_entry']
      sleep(1)
      clear()
   except KeyboardInterrupt:
      break

client.update = False
client.client.close()
print 'system power off...'
sys.exit()
