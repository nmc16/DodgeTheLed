import socket
import pifacedigitalio as p

class Controller(object):

    def __init__(self):
        self.UDP_IP = '10.0.0.10'
        self.UDP_PORT = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def play(self):
        working = True
        p.init()

        while working:
            S1 = p.digital_read(0)
            S2 = p.digital_read(3)

            if S1 == 1:
                # Send -1 to move player to the left
                msg = '-1'
                self.sock.sendto(msg, (self.UDP_IP, self.UDP_PORT))

                # Turn on the LED while the button is pressed
                p.digital_write(0, 1)

                # Wait until the button is let go before reading a new bit
                while p.digital_read(0) == 1:
                    pass

                # Turn off the LED
                p.digital_write(0, 0)

            if S2 == 1:
                # Send 1 to move player to the right
                msg = '1'
                self.sock.sendto(msg, (self.UDP_IP, self.UDP_PORT))

                # Turn on the LED while the button is pressed
                p.digital_write(3, 1)

                # Wait until the button is let go before reading a new bit
                while p.digital_read(3) == 1:
                    pass

                # Turn off the LED
                p.digital_write(3, 0)


if __name__ == '__main__':
    controller = Controller()
    try:
        controller.play()
    except KeyboardInterrupt:
        pass
    finally:
        print "Controller Exiting!"

