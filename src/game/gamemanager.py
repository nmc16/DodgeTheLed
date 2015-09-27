from Tkinter import *
from src.gui.ui import MainFrame
from socket import socket, AF_INET, SOCK_DGRAM, error
import logging


class GameManager(object):
    """
       Main class to run the game from.

       Manges all of the game controller functions like starting the game,
       checking the high scores, and quitting the game.
    """

    def __init__(self, playername="no-one"):
        """ Constructor for GameManager() """

        # Setup logger
        self.logger = logging.getLogger('game')
        fh = logging.FileHandler('../logs/game.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Reset the score and player name
        self.high_scores = {}
        self.player = HighScore(playername)
        self.commands = ["start", "reset", "change_user", "highscore", "help", "quit"]
        self.gr = None

    def init_game(self):
        """ Displays the welcome screen to the user on start up of the game. """

        print "Welcome to Dodge The LED! Player",
        print self.player.user
        self.print_menu()

    def print_menu(self):
        """ Prints the game menu that holds all the available commands and what each one does. """

        print "> Game Commands:"
        print ">     start : start the game with a countdown from 3"
        print ">     reset : resets the high score and playername"
        print ">     change_user [playername] : changes the current user"
        print ">     highscore : displays player's high score"
        print ">     help : prints available commands"
        print ">     quit : quits the game"
        print ">"

    def run_gamemanager(self):
        """
           Game loop method.

           Runs infinite loop to gather user inputted commands and run the appropriate methods
           thereafter.
        """

        while True:
            # Collect the user input
            command = raw_input("> ")
            command = command.split(" ")

            # Only check the command not the options
            if command[0] in self.commands:
                # Change user takes an additional option, so in that case send it to the method
                if command[0] == "change_user" and len(command) > 1:
                    getattr(self, command[0])(command[1])
                else:
                    getattr(self, command[0])()
            else:
                print "> Command does not exist. Type help to see all available commands!"

    def find_user(self, user):
        """
           Attempts to find the user given inside the high scores list.

           :param user: user name to search the list for.
           :return: returns the HighScore object of the matching user name or None if does not exist
                    in the list
        """

        if user in self.high_scores:
            return self.high_scores[user]
        else:
            return None

    def start(self):
        """
           Starts the game from the game runner and after it has finished updates the player's
           high score from the LCD controller.
        """

        self.gr = GameRunner()
        self.gr.run()
        self.player.update_high_score(self.gr.high_score)

    def reset(self):
        """ Resets the player's high score to 0. """

        self.player.high_score = 0

    def change_user(self, playername=None):
        """
           Changes the current user to an existing one or creates a new one if the playername
           does not already exist in the high score list.

           :param playername: playername to change to.
        """

        user = self.find_user(playername)
        if user is not None:
            self.player = user
        else:
            user = HighScore(playername)
            self.high_scores[playername] = user
            self.player = user

    def highscore(self):
        """ Prints the high score of the current user. """

        print "> Player %s has a high score of %d seconds" % (self.player.user, self.player.high_score)

    def help(self):
        """ Prints the in game menu. """

        self.print_menu()

    def quit(self):
        """ Quits the game. """
        exit(0)


class GameRunner(object):
    """
       Class that controls the execution of the GUI and the LCD controller signals.

       Starts the TKinter GUI instance for the game and starts the game loop. Also
       sends the start and stop signals to the LCD controller that counts the time
       survived.
    """

    _RPI_COUNTER_ADDR = "10.0.0.7"
    _RPI_COUNTER_PORT = 5005
    _UDP_PORT = 5004
    _UDP_IP = "10.0.0.10"
    _BUFFER_SIZE = 512

    def __init__(self):
        # Reset the high score
        self.high_score = 0

        self.logger = logging.getLogger('game')

        # Create the UDP socket to send and receive messages
        self.sock_inbound = socket(AF_INET, SOCK_DGRAM)
        self.sock_inbound.bind((self._UDP_IP, self._UDP_PORT))
        self.sock_outbound = socket(AF_INET, SOCK_DGRAM)

    def run(self):
        """
           Starts the GUI instance, centers it and brings it to the front.

           Sends the start and stop signals to the LCD controller.
        """

        # Create new UI instance
        root = Tk()
        root.geometry("620x620+300+300")
        frame = MainFrame(root)

        # Bring it to the front
        root.lift()
        root.attributes("-topmost", True)

        # Center it
        frame.center()

        # Send the request to start counting
        root.after(4000, self.send_start_signal)

        # Add the runner to the event queue and start the mainloop
        root.after(1000, frame.run_ui)
        root.mainloop()

        # Get the high score from the timer
        self.high_score = self.get_highscore()

    def get_highscore(self):
        """
           Sends the outbound signal to the LCD controller to stop counting and reads
           the data sent back.

           :return: Data sent back from LCD controller
        """

        self.sock_outbound.sendto("stop", (self._RPI_COUNTER_ADDR, self._RPI_COUNTER_PORT))

        data = ""
        address = ""

        # Read data from socket buffer
        try:
            data, address = self.sock_inbound.recvfrom(self._BUFFER_SIZE)
        except error, e:
            self.logger.error("Error occurred reading data from lcd controller: %s", e)

        if address == self._RPI_COUNTER_ADDR:
            try:
                data = int(data)
            except ValueError, e:
                self.logger.error("Message received was not correct format: %s, %s", data, e)
                data = 0

        return data

    def send_start_signal(self):
        """ Sends the start signal to the LCD controller """

        self.sock_outbound.sendto("start", (self._RPI_COUNTER_ADDR, self._RPI_COUNTER_PORT))


class HighScore(object):
    """
       Basic object used to store a user with a high score
    """

    def __init__(self, user, high_score=0):
        self.user = user
        self.high_score = high_score

    def update_high_score(self, high_score):
        self.high_score = high_score


def main():
    gm = GameManager()
    gm.init_game()
    gm.run_gamemanager()

if __name__ == "__main__":
    main()

