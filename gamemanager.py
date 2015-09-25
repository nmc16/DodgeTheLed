from Tkinter import *
from ui import MainFrame
from threading import Thread


class GameManager(object):

    def __init__(self, playername="no-one"):
        # Reset the score and player name
        self.high_score = 0
        self.playername = playername
        self.commands = ["start", "stop", "reset", "highscore", "help", "quit"]
        self.gr = None

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
        print ">"

    def run_gamemanager(self):
        while True:
            command = raw_input("> ")
            if command in self.commands:
                getattr(self, command)()
            else:
                print "> Command does not exist. Type help to see all available commands!"

    def start(self):
        self.gr = GameRunner()
        self.gr.start()

    def stop(self):
        # Destroy the window
        self.gr.set_stop()
        self.gr = None

    def reset(self, playername=None):
        self.high_score = 0

        if playername is not None:
            self.playername = playername

    def highscore(self):
        print "> Player %s has a high score of %d" % (self.playername, self.high_score)

    def help(self):
        self.print_menu()

    def quit(self):
        if self.gr is not None:
            self.gr.set_stop()
        exit(0)


class GameRunner(Thread):

    def __init__(self):
        super(GameRunner, self).__init__()
        self.root = None
        self.frame = None

    def run(self):
        # Create new UI instance
        self.root = Tk()
        self.root.geometry("620x620+300+300")
        self.frame = MainFrame(self.root)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.frame.center()
        self.root.after(1000, self.frame.run_ui)
        self.root.mainloop()

    def set_stop(self):
        self.frame.stop_ui()


def main():
    gm = GameManager()
    gm.init_game()
    gm.run_gamemanager()

if __name__ == "__main__":
    main()

