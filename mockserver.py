### mock server for testing
import sys
import socket
import random
from base64 import b64encode
from time import sleep
from xpydef import acf_description, cdu_datarefs

blankScreen = cdu_datarefs.copy()

home = blankScreen.copy()
home['laminar/B738/fmc1/Line00_L'] = '<FMC'.ljust(24)
home['laminar/B738/fmc1/Line02_L'] = '<ACARS'.ljust(24)
home['laminar/B738/fmc1/Line_entry'] = 'ENTER IRS POSITION'.ljust(24)

ident = blankScreen.copy()
ident['laminar/B738/fmc1/Line00_L'] = 'IDENT'.center(20) + '1/2 '
ident['laminar/B738/fmc1/Line01_S'] = ' MODEL'.ljust(14) + 'ENG RATING'
ident['laminar/B738/fmc1/Line01_L'] = '737-800WL'.ljust(21) + '26K'
ident['laminar/B738/fmc1/Line02_S'] = ' NAV DATA'.ljust(18) + 'ACTIVE'
ident['laminar/B738/fmc1/Line02_L'] = '1812301901'.ljust(24)
ident['laminar/B738/fmc1/Line04_S'] = ' OP PROGRAM'.ljust(24)
ident['laminar/B738/fmc1/Line04_L'] = '556909-001    (U11.0)'.ljust(24)
ident['laminar/B738/fmc1/Line05_S'] = 'SUPP DATA'.rjust(24)
ident['laminar/B738/fmc1/Line06_L'] = '<INDEX'.ljust(13) + 'POS INIT>'
ident['laminar/B738/fmc1/Line_entry'] = 'ENTER IRS POSITION'.ljust(24)

posInit = blankScreen.copy()
posInit['laminar/B738/fmc1/Line00_L'] = 'POS INIT'.center(20) + '1/3 '
posInit['laminar/B738/fmc1/Line01_S'] = 'LAST POS'.rjust(24)
posInit['laminar/B738/fmc1/Line01_L'] = 'N40 51.5 W073 48.5'.rjust(24)
posInit['laminar/B738/fmc1/Line02_S'] = 'REF AIRPORT'.ljust(24)
posInit['laminar/B738/fmc1/Line02_L'] = '_ _ _ _'.ljust(24)
posInit['laminar/B738/fmc1/Line03_S'] = 'GATE'.ljust(24)
posInit['laminar/B738/fmc1/Line03_L'] = '_ _ _ _ _'.ljust(24)
posInit['laminar/B738/fmc1/Line04_S'] = 'SET IRS POS'.rjust(24)
posInit['laminar/B738/fmc1/Line04_L'] = '___ __._ ____ __._'.rjust(24)
posInit['laminar/B738/fmc1/Line05_S'] = 'GMT-MON/DY'.ljust(24)
posInit['laminar/B738/fmc1/Line05_L'] = '0023.5Z 02/17'.ljust(24)
posInit['laminar/B738/fmc1/Line06_S'] = ''.center(24, '-')
posInit['laminar/B738/fmc1/Line06_L'] = '<INDEX'.ljust(19) + 'ROUTE>'

screens = [ 
    home,
    ident,
    posInit
]

class TcpServer:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 51000))
        self.server.listen(1)
        self.active = True
    
    def listen(self):
        conn, addr = self.server.accept()
        self.server.settimeout(5)
        print >>sys.stderr, 'Connection from ', addr
        conn.send("EXTPLANE\nVERSION 1003\n")
        while self.active:
            try:
                data = conn.recv(1024)
                print >>sys.stderr, 'received ', data
                if (acf_description in data):
                    conn.send('Boeing 737-800')
                else:
                    conn.send(self.getScreen())
            except socket.timeout:
                pass
            except Exception as e:
                print >>sys.stderr, 'Erro ', e
                break

    def getScreen(self):
        result = ''
        for k, v in posInit.items():
            result += 'ub ' + k + ' ' + \
                b64encode(v.decode('ascii')).encode('ascii') + '\n'
        print >>sys.stderr, result
        return result

server = TcpServer()
server.listen()
