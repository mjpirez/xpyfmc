import sys
import socket
import struct
from time import sleep
from base64 import b64decode

EXTPLANE_PORT = 51000

class Beacon:

   def __init__(self, extport, tuple):
      self.name = tuple[0]
      self.majorVersion = tuple[1]
      self.minorVersion = tuple[2]
      self.hostId = tuple[3]
      self.xplaneVersion = tuple[4]
      self.role = tuple[5]
      self.port = extport
      self.hostname = tuple[7]
      self.remotePort = tuple[6]
      self.ipAddress = None

   def __str__(self):
      return self.name + " " + str(self.majorVersion) + "." + str(self.minorVersion) + "v " + \
         self.hostname + ":" + str(self.port) + " X-Plane version " + str(self.xplaneVersion)

class MulticastListener:

   def __init__(self, mc_group, server_port):
      self.multicast_group = mc_group         # default '239.255.1.1'
      self.server_address = ('', server_port) # default 49707
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.sock.settimeout(5)
      self.sock.bind(self.server_address)
      group = socket.inet_aton(self.multicast_group)
      mreq = struct.pack('4sL', group, socket.INADDR_ANY)
      self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

   def waitForBeacon(self):
      beacon = None
      print >>sys.stderr, 'Discovering X-Plane...'
      while not beacon:
         try:
             data, address = self.sock.recvfrom(1024)
             print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
             beacon = Beacon(EXTPLANE_PORT, struct.unpack('<4sxBBIIiH' + str(len(data)-24) +'sxH', data))
             print >>sys.stderr, beacon
             print >>sys.stderr, 'sending acknowledgement to', address
             self.sock.sendto('ack', address)
             beacon.ipAddress = str(address[0])
         except socket.timeout:
            print >>sys.stderr, 'Timed out waiting for X-Plane, trying again...'
            pass
         except Exception as e:
            print >>sys.stderr, e
            break
      self.sock.close()
      return beacon

class XPlaneTcpClient:

   def __init__(self, server_ip, server_port):
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.client.settimeout(5)
      self.client.connect((server_ip, server_port))
      self.update = True

   def sendMsg(self, msg):
      return self.client.send(msg + b'\n')

   def waitForMsg(self):
      data = None
      while not data:
         try:
            data = self.client.recv(1024)
         except socket.timeout:
            pass
         except Exception as e:
            print >>sys.stderr, e
            break
      return data

   def subscribeForCDUDisplay(self, cdu_refs):
      for k, v in cdu_refs.items():
         print >>sys.stderr, 'subscribing to ', k
         self.client.send('sub ' + k + b'\n')
         sleep(.150)

   def updateCDUDataRefs(self, cdu_refs):
      while self.update:
         try:
            data = self.client.recv(1024)
            tokens = data.split('\n')
            if len(tokens) > 1:
               for token in tokens:
                  update = token.split()
                  if 'ub' == update[0]:
                     cdu_refs[update[1]] = self.decode(update[2])
            else:
               update = tokens[0].split()
               if "ub" == update[0]:
                  cdu_refs[update[1]] = self.decode(update[2])
            #print >>sys.stderr, tokens
         except IndexError:
            pass
         except socket.timeout:
            pass

   def decode(self, msg):
      return b64decode(msg.encode('ascii')).decode('ascii')