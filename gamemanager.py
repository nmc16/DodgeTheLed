import sys
from time import *


class GameManager(object):

    highscore = 0
    commands = ["start", "stop", "reset", "highscore", "help", "quit"]

    def __init__(self, playername):
        # Reset the score and player name
        self.highscore = 0
        self.playername = playername

    def init_game(self):
        # Print the menu
        print "Welcome to Dodge The LED! Player",
        if not self.playername:
            print "Default"
        else:
            print self.playername

        self.print_menu()

    def print_menu(self):
        print "> Game Commands:"
        print ">     start : start the game with a countdown from 3"
        print ">     stop : stops the current game in progress"
        print ">     reset [playername] : resets the highscore and playername"
        print ">     highscore : displays player's high score"
        print ">     help : prints available commands"
        print ">     quit : quits the game"
        print ""

    def run_gamemanager(self):
        while(True):
            command = raw_input("> ")
            if command in self.commands:
                print "> ", command, " registered"
            else:
                print "> Command does not exist. Type help to see all available commands!"


def main():
    gm = GameManager(sys.argv[1])
    gm.init_game()
    gm.run_gamemanager()

if __name__ == "__main__":
    main()

