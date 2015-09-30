import socket
import pifacedigitalio as p

class detector_OO(object):
	
	def play(self):	
		UDP_IP = '10.0.0.10'
		UDP_PORT=5005	
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		working = True
		p.init()
		while working: 

			
			S1= p.digital_read(0)
			S2= p.digital_read(3)
			if S1 ==1:
				msg = '-1'
				sock.sendto(msg, (UDP_IP,UDP_PORT))
				p.digital_write(0,1)
				p.digital_write(0,0)
				while p.digital_read(0)  == 1:
					pass 
			
			if S2 == 1:
				msg='1'
				sock.sendto(msg, (UDP_IP,UDP_PORT))
				p.digital_write(3,1)
				p.digital_write(3,0)
				while p.digital_read(3)  == 1:
					pass
					
testing=detector_OO()
while True:
	testing.play()
			


