from Tkinter import *
from ttk import *
from socket import socket, AF_INET, SOCK_DGRAM, error
from copy import copy
from random import randint
from threading import Event
import fcntl, os, errno, logging


class MainFrame(Frame):
    """
       Main GUI class to run the LED game from.

       Uses RPi PiFace input sent from the controller to update the player position
       and creates falling LEDs for the player to dodge.
    """

    _flag = False
    _stop_event = Event()
    collision_row = []
    PLAYER_ROW = 4
    UDP_PORT = 5005
    UDP_IP = "10.0.0.10"
    RPI_COUNTER_ADDR = "10.0.0.3"
    RPI_CONTROLLER_ADDR = "10.0.0.5"
    BUFFER_SIZE = 1024

    def __init__(self, parent):
        Frame.__init__(self, parent)

        # Setup logger
        self.logger = logging.getLogger('MainFrame')
        fh = logging.FileHandler('../logs/mainframe.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Store the root tk
        self.parent = parent

        # Set the player position back to the default index
        self.player_pos = 2

        # Initialize the frame style
        self.parent.title("Dodge The LED!")

        try:
            img = PhotoImage(file='doge_icon.gif')
        except TclError:
            img = PhotoImage(file='../gui/doge_icon.gif')

        self.parent.tk.call('wm', 'iconphoto', self.parent._w, img)
        self.style = Style()
        self.style.theme_use("default")
        self.pack()

        # Center the window on the screen
        self.center()

        # Setup the LEDs in the grid layout
        self.led_rows = self.setup_leds()

        # Create the UDP socket to receive messages
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))

        # Make socket non-blocking
        fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)

        # Create the UDP socket to send messages
        self.sock_outbound = socket(AF_INET, SOCK_DGRAM)

        # Reset program counters
        self.rows_passed = 0
        self.open_index = 0
        self.last_shift = 0
        self.remaining = 3

        # Create the countdown label and center it
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
            Sets up the grid of the LEDs to their default colours.

            :return: Returns the dictionary of led column lists
        """

        # Create a dictionary to hold the rows and store the current pixel positions
        led_rows = {}
        x_pos = 10
        y_pos = 10

        # Create 5 rows
        for i in range(5):
            led_rows[i] = []

            # Create 5 LEDs in each row
            for j in range(5):
                if i == self.PLAYER_ROW:
                    if j == self.player_pos:
                        led = Text(self.parent, background="green", height="7", width="14", state=DISABLED)
                    else:
                        led = Text(self.parent, background="gray", height="7", width="14", state=DISABLED)
                else:
                    led = Text(self.parent, background="gray", height="7", width="14", state=DISABLED)

                # Place them on the screen and increase the counters
                led.place(x=x_pos, y=y_pos)
                led_rows[i].append(led)
                x_pos += 120

            x_pos = 10
            y_pos += 120

        return led_rows

    def display_game_over(self):
        """
           Creates a label at the center of the screen that displays the Game Over text.
        """

        label = Label(self.parent, background="black", foreground="red", text="GAME OVER!", font="Times 60 bold")
        size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        label.place(x=(size_x/2)-260, y=(size_y/2)-50)
        self.sock_outbound.sendto("stop", (self.RPI_COUNTER_ADDR, self.UDP_PORT))

    def read_piface_input(self):
        """
            Reads the socket buffer for data and an address. Attempts to convert the data
            to an integer as the controller passes 1 or -1.

           :return: Tuple consisting of the data collected and the address it was collected from
        """
        data = ""
        address = ""

        # Read data from socket buffer
        try:
            data, address = self.sock.recvfrom(self.BUFFER_SIZE)
        except error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                # Data was empty, no input was sent
                self.logger.debug("Received no data from piface: %s", e)
            else:
                # Real error occurred
                self.logger.error("Error occurred reading data from buffer: %s", e)

        # Attempt to convert the data into an integer
        if data != "":
            try:
                data = int(data)
            except ValueError, e:
                self.logger.error("Message received was not correct format: %s, %s", data, e)
                data = None

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
        if p_row[self.player_pos].config("background")[4] == "red":
            self._flag = True
            self.display_game_over()
        p_row[self.player_pos].configure(background="green")

    def create_led_row(self):
        """
           Creates a new row of LEDs for the player to dodge and shifts all rows
           below it down one index.

           Stores the rows passed and adds one for each new row created in the game.
           Delegates the creation of the first row to :func:`MainFrame.init_first_row`
        """

        # No need to shift the rows down when the it is the first row in the game
        if self.rows_passed != 0:
            # Make a copy of the row above the player to detect for collision
            self.collision_row = copy(self.led_rows[3])

            # Shift all the rows down one index
            rows = copy(self.led_rows)
            for i in range(0, 4):
                self.shift_rows(rows[3 - i], self.led_rows[4 - i])

            # Create a new open space either to the left or right of the open_index
            if self.open_index == 4:
                shift = randint(-1, 0)
            elif self.open_index == 0:
                shift = randint(0, 1)
            else:
                # Don't allow the game to choose the inverse direction, stops game from going back and forth
                # that doesn't create any new spots
                if self.last_shift == -1:
                    shift = randint(-1, 0)
                elif self.last_shift == 1:
                    shift = randint(0, 1)
                else:
                    shift = randint(-1, 1)

            # Store the new shift
            self.last_shift = shift

            # Change the colour of the LEDs to red or gray
            for led in self.led_rows[0]:
                led.configure(background="red")
            self.led_rows[0][self.open_index].configure(background="gray")

            # Create another opening above the old one so the player has room to move to the new opening
            if shift != 0:
                self.open_index = self.open_index + shift
                self.led_rows[0][self.open_index].configure(background="gray")

        else:
            self.init_first_row()

        # Increase the rows passed
        self.rows_passed += 1

        # Re-update the player position to green after the rows have shifted down
        self.led_rows[self.PLAYER_ROW][self.player_pos].configure(background="green")

    def init_first_row(self):
        """
           Initializes the first row of LEDs by selecting four unique random indexes
           and changing their colours to red.
        """

        # If the first row, randomize 4 indexes to change to red LEDs
        indexes_to_change = []
        while len(indexes_to_change) < 4:
            indexes_to_change.append(randint(0, 4))

            # Remove duplicates so all 4 indexes are unique
            indexes_to_change = list(set(indexes_to_change))

        # Change new LEDs to red
        for i in indexes_to_change:
            self.led_rows[0][i].configure(background="red")

        # Store the open index for use later
        for led in self.led_rows[0]:
            if led.config()["background"][4] == "gray":
                self.open_index = self.led_rows[0].index(led)

    def shift_rows(self, row1, row2):
        """
           Shifts all LEDs in row1 into row2 at the same indexes.

           :param row1 Row to copy all LEDs from
           :param row2 Row to shift all copied LEDs to
        """

        # Store all the LED colours from the first row
        colours = []
        for led in row1:
            colours.append(led.config()["background"][4])

        # Change the colours in the second row
        for i in range(len(row2)):
            row2[i].config(background=colours[i])

    def detect_collision(self):
        """
           Checks if the player position shares the same index as a red LED and will set
           the end game flag and display the game over text if it is.
        """

        # If the collision row hasn't been initialized there isn't a collision yet
        if not self.collision_row:
            return

        if self.collision_row[self.player_pos].config()["background"][4] == "red":
            self._flag = True
            self.display_game_over()

    def run_countdown(self):
        """
           Displays a countdown at the center of the screen before the game starts.

           After three seconds the label is destroyed and the controller input
           is added to the event queue to be read.
        """
        self.remaining -= 1

        if self.remaining == -1:
            self.countdown.destroy()
            self.after(10, self.run_controller)
        elif self.remaining == 0:
            self.countdown.configure(text="GO!")
        else:
            self.countdown.configure(text=self.remaining)

        self.pack_propagate()

    def run_controller(self):
        """
           Reads the data given from the piface controller and if the address is the expected one
           updates the player position with the input.
        """

        # Don't move the player if the game is over
        if not self._flag:
            data, address = self.read_piface_input()

            # Only attempt if the address is the same and the data is not NULL
            if address != "" and address[0] == self.RPI_CONTROLLER_ADDR and data is not None:
                self.update_player(data)

            # Add to the even queue again
            self.after(100, self.run_controller)

    def run_ui(self):
        """
           Main loop to run.

           Runs the countdown until the game is ready to be played. Checks for collision with
           the row above the player, then creates a new LED row.

           If the threading event is set, destroys the root frame which closes the GUI.

           Calculates a cool down between each newly created row that decreases linearly
           until it hits one row per 75 milliseconds which is the cap.

           Adds itself back to the event queue after the cool down has expired.
        """

        # Run the countdown for the first 3 seconds of the game
        if self.remaining > -1:
            self.run_countdown()
        else:
            # If the game has not ended check collision and add a new row
            if not self._flag:
                self.detect_collision()
                self.create_led_row()
                self.pack()

        if not self._flag:
            # Add itself back to the event queue after calculating the cool down
            cooldown = int((-7 * self.rows_passed) + 1000)
            if cooldown < 75:
                self.after(75, self.run_ui)
            else:
                self.after(cooldown, self.run_ui)
        else:
            # If the game has ended check for the threading event every second
            self.led_rows[self.PLAYER_ROW][self.player_pos].configure(background="black")
            self.after(1000, self.run_ui)

        if self._stop_event.isSet():
            self.parent.destroy()

    def stop_ui(self):
        """
           Sets the threading event to close the GUI.
        """
        self._stop_event.set()


def main():
    root = Tk()
    root.geometry("620x620+300+300")
    app = MainFrame(root)
    root.after(1000, app.run_ui)
    root.mainloop()

if __name__ == "__main__":
    main()
