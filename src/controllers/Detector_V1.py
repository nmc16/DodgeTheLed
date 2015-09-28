import socket
import pifacedigitalio as p

UDP_IP = '10.0.0.10'
UDP_PORT=5005


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
working = True
p.init()
while working: 

	S1= p.digital_read(0)
	S2= p.digital_read(3)
	if S1 ==1:
		msg = '1'
		sock.sendto(msg, (UDP_IP,UDP_PORT))
                while(p.digital_read(0) == S1):
                    pass
	
	if S2 == 1:
		msg='-1'
		sock.sendto(msg, (UDP_IP,UDP_PORT))
                while(p.digital_read(3) == S2):
                    pass

		





 
