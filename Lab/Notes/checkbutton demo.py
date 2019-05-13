from tkinter import *

class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        Label(self,text = "Select all that apply:").grid(row = 1, column = 0, sticky = W)
        
        self.checkBoxA = BooleanVar()
        Checkbutton(self,
                    text = "A",
                    variable = self.checkBoxA,
                    command = self.update_text
                    ).grid(row = 2, column = 0, sticky = W)

        self.checkBoxB = BooleanVar()
        Checkbutton(self,
                    text = "B",
                    variable = self.checkBoxB,
                    command = self.update_text
                    ).grid(row = 3, column = 0, sticky = W)

        self.checkBoxC = BooleanVar()
        Checkbutton(self,
                    text = "C",
                    variable = self.checkBoxC,
                    command = self.update_text
                    ).grid(row = 4, column = 0, sticky = W)

        self.results_txt = Text(self, width = 40, height = 5, wrap = WORD)
        self.results_txt.grid(row = 5, column = 0, columnspan = 3)

    def update_text(self):
        likes = ""
        
        if self.checkBoxA.get():
            likes += "A\n"

        if self.checkBoxB.get():
            likes += "B\n"

        if self.checkBoxC.get():
            likes += "C"
      
        self.results_txt.delete(0.0, END)
        self.results_txt.insert(0.0, likes)

root = Tk()
root.title("Movie Chooser")
app = Application(root)
root.mainloop()
