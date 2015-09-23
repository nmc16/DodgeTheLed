from Tkinter import *
from ttk import *
from time import sleep


class MainFrame(Frame):

    PLAYER_ROW = 4

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.player_pos = 2
        self.parent.title("Simple")
        self.style = Style()
        self.style.theme_use("default")
        self.pack()

        # Center the window on the screen
        self.center()

        # Setup the leds in the grid layout
        self.led_rows = self.setup_leds()

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
                        led = Text(self.parent, background="green", foreground="red", height="7", width="14",
                                   state=DISABLED)
                    else:
                        led = Text(self.parent, background="black", foreground="red", height="7", width="14",
                                   state=DISABLED)
                else:
                    led = Text(self.parent, background="gray", foreground="red", height="7", width="14", state=DISABLED)
                led.place(x=x_pos, y=y_pos)
                led_rows[i].append(led)
                x_pos += 120

            x_pos = 10
            y_pos += 120

        return led_rows

    def display_game_over(self):
        label = Label(self.parent, background="white", foreground="red", text="GAME OVER!", font="Times 60 bold")
        size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        label.place(x=(size_x/2)-260, y=(size_y/2)-50)

    def update_player(self, x_shift):
        """
            Shifts the player left or right given the input from the piface as a -1 for left and 1 for right
        """

        p_row = self.led_rows[self.PLAYER_ROW]
        p_row[self.player_pos].configure(background="black")
        self.player_pos += x_shift
        p_row[self.player_pos].configure(background="green")


def main():
    root = Tk()
    root.geometry("620x620+300+300")
    app = MainFrame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
