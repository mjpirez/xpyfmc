import sys
import threading
import xpynetwork
import curses
from xpydef import acf_description, cdu_datarefs
from time import sleep
from os import system, name 

beacon = xpynetwork.Beacon(0, ('', '', '', '', '', '', '', ''))
client = None

def discover():
   global beacon
   if (len(sys.argv) == 3):
      beacon.ipAddress = sys.argv[1]
      beacon.port = int(sys.argv[2])
   else:
      ### discover x-plane ip via multicast
      multicast = xpynetwork.MulticastListener('239.255.1.1', 49707)
      beacon = multicast.waitForBeacon()
   print 'ExtPlane IP:', beacon.ipAddress
   print 'ExtPlane port:', beacon.port


def initialize():
   ### connect and wait for extplane version
   global client
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
   threading.Thread(target=client.updateCDUDataRefs, args=('thread-1', )).start()

   ### subscribe to CDU display datarefs 
   print 'subscribing to datarefs...'
   #client.subscribeForCDUDisplay()
   client.sendMsg('a')

def main(screen):
   sleep(.300)
   while True:
      curses.start_color()
      screen.addstr(0, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line00_S'])
      screen.addstr(1, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line00_L'])
      screen.addstr(2, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line01_S'])
      screen.addstr(3, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line01_L'])
      screen.addstr(4, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line02_S'])
      screen.addstr(5, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line02_L'])
      screen.addstr(6, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line03_S'])
      screen.addstr(7, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line03_L'])
      screen.addstr(8, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line04_S'])
      screen.addstr(9, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line04_L'])
      screen.addstr(10, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line05_S'])
      screen.addstr(11, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line05_L'])
      screen.addstr(12, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line06_S'])
      screen.addstr(13, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line06_L'])
      screen.addstr(14, 0, xpynetwork.cduRefs['laminar/B738/fmc1/Line_entry'])
      screen.refresh()
      client.sendMsg('a')
      sleep(5)
      screen.clear()
   
discover()
initialize()
curses.wrapper(main)
client.update = False
client.client.close()
print 'system power off...'
sys.exit()

