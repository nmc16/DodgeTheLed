# imports
import RPi.GPIO as GPIO
import time
import socket
import fcntl, os, errno


class LcdPi(object):

    def __init__(self):
        # Define GPIO to LCD mapping
        self.LCD_RS = 7
        self.LCD_E = 8
        self.LCD_D4 = 25
        self.LCD_D5 = 24
        self.LCD_D6 = 23
        self.LCD_D7 = 18

        # Define some device constants
        self.LCD_WIDTH = 16     # Maximum characters per line
        self.LCD_CHR = True
        self.LCD_CMD = False

        self.LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
        self.LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

        # Timing constants
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005

    def main(self):
        """ Main program block """
        GPIO.setmode(GPIO.BCM)             # Use BCM GPIO numbers
        GPIO.setup(self.LCD_E, GPIO.OUT)   # E
        GPIO.setup(self.LCD_RS, GPIO.OUT)  # RS
        GPIO.setup(self.LCD_D4, GPIO.OUT)  # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT)  # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT)  # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT)  # DB7

        # Initialise display
        self.lcd_init()

    def lcd_init(self):
        """ Initialise display """
        self.lcd_byte(0x33, self.LCD_CMD)  # 110011 Initialise
        self.lcd_byte(0x32, self.LCD_CMD)  # 110010 Initialise
        self.lcd_byte(0x06, self.LCD_CMD)  # 000110 Cursor move direction
        self.lcd_byte(0x0C, self.LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28, self.LCD_CMD)  # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self.LCD_CMD)  # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        """
           Send byte to data pins
           :param bits data to send
           :param mode True for character, False for command
        """

        GPIO.output(self.LCD_RS, mode)  # RS

        # High bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        """ Toggle enable """

        time.sleep(self.E_DELAY)
        GPIO.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line, style):
        """ 
           Send string to display on LCD
     
           :param message Message to print on the LCD
           :param line Line on the LCD to print on
           :param style Text justification: 1 = left justified
                                            2 = centered
                                            3 = right justified
        """

        if style == 1:
            message = message.ljust(self.LCD_WIDTH, " ")
        if style == 2:
            message = message.center(self.LCD_WIDTH, " ")
        if style == 3:
            message = message.rjust(self.LCD_WIDTH, " ")
        else:
            message = message.ljust(self.LCD_WIDTH, " ")

        self.lcd_byte(line, self.LCD_CMD)

        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

class UdpAdd(LcdPi):

    def __init__(self):
        super(UdpAdd, self).__init__()
        self.main()
        self.lcd_init()

        # Define the UDP information
        self.UDP_IP = '10.0.0.3'
        self.UDP_PORT = 5005
        self.UDP_IP_OUT = '10.0.0.10'
        self.UDP_PORT_OUT = 5004
        self.TIMER_TRUE = True

        # Initialize socket internet and udp
        self.sock_in = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        # Init the receive of information from port
        self.sock_in.bind((self.UDP_IP, self.UDP_PORT))

        # Make the socket non-blocking
        fcntl.fcntl(self.sock_in, fcntl.F_SETFL, os.O_NONBLOCK)

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def data_recv(self):
        while True:
            data = self.recv_from_sock()  # buffer size is 1024 bytes
            if data == 'start':
                self.lcd_init()

                score = str(self.start_timer())

                self.sock_out.sendto(score, (self.UDP_IP_OUT, self.UDP_PORT_OUT))
                self.lcd_byte(0x01, self.LCD_CMD)
                self.lcd_string("GAME OVER!", self.LCD_LINE_1, 2)
                self.lcd_string("Score is: " + score, self.LCD_LINE_2, 2)

    def start_timer(self):
        time_r = 0
        self.TIMER_TRUE = True
        while self.TIMER_TRUE:
            time_r += 1
            time_out = str(time_r)
            self.lcd_string(time_out, self.LCD_LINE_1, 2)

            data = self.recv_from_sock()
            if data == 'stop':
                self.TIMER_TRUE = False
            time.sleep(1)
        return time_r

    def recv_from_sock(self):
        try:
            data, address = self.sock_in.recvfrom(1024)
            return data
        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == EWOULDBLOCK:
                pass
            else:
                print e
            return None


if __name__ == '__main__':
    testing = UdpAdd()
    try:
        testing.data_recv()
    except KeyboardInterrupt:
        pass
    finally:
        testing.lcd_byte(0x01, testing.LCD_CMD)
        testing.lcd_string("Goodbye!", testing.LCD_LINE_1, 2)
        GPIO.cleanup()

