from Tkinter import *
from ttk import *


class MainFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.parent.title("Simple")
        self.style = Style()
        self.style.theme_use("default")
        self.pack()

        # Center the window on the screen
        self.center()

        # Setup the leds in the grid layout
        self.led_columns = self.setup_leds()

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

        led_columns = {}
        x_pos = 10
        y_pos = 10
        for i in range(5):
            led_columns[i] = []

            for j in range(5):
                if j == 4:
                    if i == 2:
                        led = Text(self.parent, background="green", foreground="red", height="7", width="14",
                                   state=DISABLED)
                    else:
                        led = Text(self.parent, background="black", foreground="red", height="7", width="14",
                                   state=DISABLED)
                else:
                    led = Text(self.parent, background="gray", foreground="red", height="7", width="14", state=DISABLED)
                led.place(x=x_pos, y=y_pos)
                led_columns[i].append(led)
                y_pos += 120

            y_pos = 10
            x_pos += 120

        return led_columns

    def display_game_over(self):
        label = Label(self.parent, background="white", foreground="red", text="GAME OVER!", font="Times 60 bold")
        size_x = int(self.parent.geometry().split('+')[0].split('x')[0])
        size_y = int(self.parent.geometry().split('+')[0].split('x')[1])
        label.place(x=(size_x/2)-260, y=(size_y/2)-50)

def main():
    root = Tk()
    root.geometry("620x620+300+300")
    app = MainFrame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
