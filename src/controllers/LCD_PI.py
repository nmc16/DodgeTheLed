#import
import RPi.GPIO as GPIO
import time
import socket
import fcntl, os, errno


class LCD_PI(object):
	def lcd_run(self):
		#import
		import RPi.GPIO as GPIO
		import time

		# Define GPIO to LCD mapping
		LCD_RS = 7
		LCD_E  = 8
		LCD_D4 = 25
		LCD_D5 = 24
		LCD_D6 = 23
		LCD_D7 = 18


		# Define some device constants
		LCD_WIDTH = 16    # Maximum characters per line
		LCD_CHR = True
		LCD_CMD = False

		LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
		LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

		# Timing constants
		E_PULSE = 0.0005
		E_DELAY = 0.0005

	def main():
		  # Main program block

		  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
		  GPIO.setup(LCD_E, GPIO.OUT)  # E
		  GPIO.setup(LCD_RS, GPIO.OUT) # RS
		  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
		  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
		  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
		  GPIO.setup(LCD_D7, GPIO.OUT) # DB7


		  # Initialise display
		 # lcd_init()

		  #while True:

			# Send some test
		#	lcd_string("Charlie is still",LCD_LINE_1)
		#	lcd_string("Awesome",LCD_LINE_2)


	def lcd_init():
		  # Initialise display
		  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
		  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
		  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
		  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
		  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
		  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
		  time.sleep(E_DELAY)

	def lcd_byte(bits, mode):
		  # Send byte to data pins
		  # bits = data
		  # mode = True  for character
		  #        False for command

		  GPIO.output(LCD_RS, mode) # RS

		  # High bits
		  GPIO.output(LCD_D4, False)
		  GPIO.output(LCD_D5, False)
		  GPIO.output(LCD_D6, False)
		  GPIO.output(LCD_D7, False)
		  if bits&0x10==0x10:
			GPIO.output(LCD_D4, True)
		  if bits&0x20==0x20:
			GPIO.output(LCD_D5, True)
		  if bits&0x40==0x40:
			GPIO.output(LCD_D6, True)
		  if bits&0x80==0x80:
			GPIO.output(LCD_D7, True)

		  # Toggle 'Enable' pin
		  lcd_toggle_enable()

		  # Low bits
		  GPIO.output(LCD_D4, False)
		  GPIO.output(LCD_D5, False)
		  GPIO.output(LCD_D6, False)
		  GPIO.output(LCD_D7, False)
		  if bits&0x01==0x01:
			GPIO.output(LCD_D4, True)
		  if bits&0x02==0x02:
			GPIO.output(LCD_D5, True)
		  if bits&0x04==0x04:
			GPIO.output(LCD_D6, True)
		  if bits&0x08==0x08:
			GPIO.output(LCD_D7, True)

		  # Toggle 'Enable' pin
		  lcd_toggle_enable()

	def lcd_toggle_enable():
		  # Toggle enable
		  time.sleep(E_DELAY)
		  GPIO.output(LCD_E, True)
		  time.sleep(E_PULSE)
		  GPIO.output(LCD_E, False)
		  time.sleep(E_DELAY)

	def lcd_string(message,line):
		  # Send string to display




		  message = message.ljust(LCD_WIDTH," ")

		  lcd_byte(line, LCD_CMD)

		  for i in range(LCD_WIDTH):
			lcd_byte(ord(message[i]),LCD_CHR)

	if __name__ == '__main__':

		  try:
			main()
		  except KeyboardInterrupt:
			pass
		  finally:
			lcd_byte(0x01, LCD_CMD)
			lcd_string("Goodbye!",LCD_LINE_1)
			GPIO.cleanup()
			
class UDP_ADD(LCD_PI):
	def run_udp(self):
	
		#Define the UDP information 
		UDP_IP ='10.0.0.3'
		UDP_PORT = 5005
		TIMER_TRUE = True

		#Initialize socket internet and udp
		sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		#Init the recieve of information from port
		sock.bind((UDP_IP,UDP_PORT))
		# Make the socket non-blocking
		fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)

		sock_out=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		
		
		def data_recv():
		  while True:
			
			data = recv_from_sock() #buffer size is 1024 bytes 
			if data == 'start':
				super(LCD_PI, self).lcd_init()
				
				score = str(start_timer())
				
				sock_out.sendto(score, ('10.0.0.10',5004))
				lcd_byte(0x01, LCD_CMD)
				lcd_string("GAME OVER!",LCD_LINE_1,2)
				lcd_string("Score is: " + score ,LCD_LINE_2,2) 
			

		def start_timer():
		  time_r = 0
		  TIMER_TRUE = True	
		  while TIMER_TRUE:
			time_r = time_r + 1 
			time_out= str(time_r)
			lcd_string(time_out,LCD_LINE_1,2)
			
			data = recv_from_sock()
			if data == 'stop':
				TIMER_TRUE=False
				time.sleep(1)
				
		  return time_r
			
		def recv_from_sock():
		  try:
			data, address = sock.recvfrom(1024)
			return data
		  except socket.error, e:
			err = e.args[0]
			if err == errno.EAGAIN or err == EWOULDBLOCK:
			  pass
			else:
			  print e
			return None
		while True:
			data_recv()
			
	
testing = UDP_ADD()
testing.lcd_run()
testing.run_udp()

