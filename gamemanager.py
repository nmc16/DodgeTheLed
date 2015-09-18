import sys
import pifacedigitalio as pfio
from time import *
from threading import * 

class GameManager(object):

    highscore = 0
    commands = ["start", "stop", "reset", "highscore", "help", "quit"]

    def __init__(self, playername):
        # Reset the score and player name
        self.highscore = 0
        self.playername = playername
        self.pfd = pfio.PiFaceDigital()

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
        t1_stop = Event()
        t1 = Thread(target=self.run_leds, args=(1, t1_stop))
        while(True):
            command = raw_input("> ")
            if command in self.commands:
                if command == "start":
                   t1_stop = Event()
                   t1 = Thread(target=self.run_leds, args=(1, t1_stop))
                   t1.start()
                if command == "stop":
                    t1_stop.set()
            else:
                print "> Command does not exist. Type help to see all available commands!"
    
    def run_leds(self, arg1, stop_event):
        i = 0  
        while(not stop_event.is_set()):
            sleep(1)
            self.pfd.leds[i].turn_on()
            if i > 0:
                self.pfd.leds[i-1].turn_off()
            else:
                self.pfd.leds[7].turn_off()
            if i < 7:
                i = i + 1
            else:
                i = 0 

def main():
    gm = GameManager(sys.argv[1])
    gm.init_game()
    gm.run_gamemanager()

if __name__ == "__main__":
    main()

