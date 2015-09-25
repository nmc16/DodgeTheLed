from Tkinter import *
from ttk import *
from socket import socket, AF_INET, SOCK_DGRAM, error
from copy import copy
from random import randint
from threading import Event
import fcntl, os, errno


class MainFrame(Frame):

    _flag = False
    _stop_event = Event()
    collision_row = []
    PLAYER_ROW = 4
    UDP_PORT = 5005
    UDP_IP = "10.0.0.10"
    RPI_CONTROLLER_ADDR = "10.0.0.3"
    BUFFER_SIZE = 1024

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.player_pos = 2
        self.parent.title("Dodge The LED!")
        #self.parent.iconbitmap('doge_icon.ico')
        self.style = Style()
        self.style.theme_use("default")
        self.pack()

        # Center the window on the screen
        self.center()

        # Setup the leds in the grid layout
        self.led_rows = self.setup_leds()

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
	
	# Make socket non-blocking
	fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)

        self.rows_passed = 0

        self.remaining = 3
        self.countdown = Label(self.parent, background="black", foreground="green", text="3", font="Times 60 bold",
                               width=5, anchor=CENTER)
        self.size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        self.size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        self.countdown.place(x=(self.size_x/2) - 100, y=(self.size_y/2) - 100)

    def center(self):
        """
            Centers the window on the screen
        """

        self.parent.update_idletasks()
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        x = screen_width/2 - size_x/2
        y = screen_height/2 - size_y/2

        self.parent.geometry('%dx%d+%d+%d' % (size_x, size_y, x, y))

    def setup_leds(self):
        """
            Sets up the grid of the LEDs
            :return: Returns the dictionary of led column lists
        """

        led_rows = {}
        x_pos = 10
        y_pos = 10
        for i in range(5):
            led_rows[i] = []

            for j in range(5):
                if i == 4:
                    if j == 2:
                        led = Text(self.parent, background="green", height="7", width="14", state=DISABLED)
                    else:
                        led = Text(self.parent, background="gray", height="7", width="14", state=DISABLED)
                else:
                    led = Text(self.parent, background="gray", height="7", width="14", state=DISABLED)
                led.place(x=x_pos, y=y_pos)
                led_rows[i].append(led)
                x_pos += 120

            x_pos = 10
            y_pos += 120

        return led_rows

    def display_game_over(self):
        label = Label(self.parent, background="black", foreground="red", text="GAME OVER!", font="Times 60 bold")
        size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        label.place(x=(size_x/2)-260, y=(size_y/2)-50)

    def read_piface_input(self):
	data = ""
	address = ""
	try:
            data, address = self.sock.recvfrom(self.BUFFER_SIZE)
	except error, e:
     	    err = e.args[0]
    	    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
		# Data was empty, can skip
		pass
	    else:
		# Real error occured
		print e
        print "received data ", data, " from add ", address
        if data != "":
	    data = int(data)
        return data, address

    def update_player(self, x_shift):
        """
            Shifts the player left or right given the input from the piface as a -1 for left and 1 for right
        """
	if (self.player_pos + x_shift) < 0 or (self.player_pos + x_shift) > 4:
	    return

        p_row = self.led_rows[self.PLAYER_ROW]
        p_row[self.player_pos].configure(background="gray")
        self.player_pos += x_shift
        p_row[self.player_pos].configure(background="green")

    def create_led_row(self):
        # No need to shift the rows down when the it is the first row in the game
        self.collision_row = copy(self.led_rows[3])

        if self.rows_passed != 0:
            rows = copy(self.led_rows)

            for i in range(0, 4):
                self.shift_rows(rows[3 - i], self.led_rows[4 - i])

            open_index = 0
            for led in self.led_rows[0]:
                if led.config()["background"][4] == "gray":
                    open_index = self.led_rows[0].index(led)

            if open_index == 4:
                shift = randint(-1, 0)
            elif open_index == 0:
                shift = randint(0, 1)
            else:
                shift = randint(-1, 1)

            for led in self.led_rows[0]:
                led.configure(background="red")

            open_index += shift
            self.led_rows[0][open_index].configure(background="gray")

        else:
            indexes_to_change = []
            while len(indexes_to_change) < randint(2, 4):
                indexes_to_change.append(randint(0, 4))

                # Remove duplicates so all 4 indexes are unique
                indexes_to_change = list(set(indexes_to_change))

            # Reset all the LEDs in the first row to gray that are left over
            # TODO find more efficient way other than just resetting all
            for led in self.led_rows[0]:
                led.configure(background="gray")

            # Change new LEDs to RED
            for i in indexes_to_change:
                self.led_rows[0][i].configure(background="red")

        self.rows_passed += 1
        self.led_rows[self.PLAYER_ROW][self.player_pos].configure(background="green")

    def shift_rows(self, row1, row2):
        colours = []
        for led in row1:
            colours.append(led.config()["background"][4])

        i = 0
        for led in row2:
            led.config(background=colours[i])
            i += 1

    def detect_collision(self):
        if not self.collision_row:
            return

        if self.collision_row[self.player_pos].config()["background"][4] == "red":
            self._flag = True
            self.display_game_over()

    def run_countdown(self):
        self.remaining -= 1

        if self.remaining == -1:
            self.countdown.destroy()
        elif self.remaining == 0:
            self.countdown.configure(text="GO!")
        else:
            self.countdown.configure(text=self.remaining)

        self.pack_propagate()

    def run_ui(self):
        """
        
        """
        if self.remaining > -1:
            self.run_countdown()
        else:
            if not self._flag:
		data, address = self.read_piface_input()
        	if address != "" and address[0] == self.RPI_CONTROLLER_ADDR:
            	    self.update_player(data)
                self.detect_collision()
                self.create_led_row()
                self.pack()

        if self._stop_event.isSet():
            self.parent.destroy()

        if not self._flag:
            #cooldown = int((-3 * self.rows_passed) + 1000)
	    cooldown = 1000
            if cooldown < 50:
                self.after(50, self.run_ui)
            else:
                self.after(cooldown, self.run_ui)
        else:
            self.led_rows[self.PLAYER_ROW][self.player_pos].configure(background="black")
            self.after(1000, self.run_ui)

    def stop_ui(self):
        self._stop_event.set()

def main():
    root = Tk()
    root.geometry("620x620+300+300")
    app = MainFrame(root)
    root.after(1000, app.run_ui)
    root.mainloop()

if __name__ == "__main__":
    main()
