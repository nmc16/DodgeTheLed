import RPi.GPIO as G
import time
import socket

class Controller_Gb(object):
    
    def __init__(self):
        # Setup the port to send UDP info to game
        self.UDP_IP = '10.0.0.10'
        self.UDP_PORT = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Setup the gertboard ports to read button presses
        G.setmode(G.BCM)
        G.setup(25, G.IN, pull_up_down=G.PUD_UP)
        G.setup(23, G.IN, pull_up_down=G.PUD_UP)

        self.previous_status = ''

    def run_controller(self):

        while True:
            status_list = [G.input(25), G.input(23)]
            if status_list[0] == 0:
                self.sock.sendto('-1', (self.UDP_IP, self.UDP_PORT)) 
                while G.input(25) == 0:
                    pass
            if status_list[1] == 0:
                self.sock.sendto('1', (self.UDP_IP, self.UDP_PORT))
                while G.input(23) == 0:
                    pass

if __name__ == "__main__":
    try:
        controller = Controller_Gb()
        controller.run_controller()
    except KeyboardInterrupt:
        pass
    finally:
        G.cleanup()
