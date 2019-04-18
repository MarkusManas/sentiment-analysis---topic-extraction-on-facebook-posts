from tkinter import *

class UI(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.root = master
        self.loginFrame = Frame(self.root)
        self.uname = None
        self.passw = None
        self.loginBtn = None
        self.errorLabel = None
        self.link = None
        self.processBtn = None
        self.mainFrame = None

    def loginMenu(self):
        def login():
            flag = 1 #log in result
            if flag:
                #proceed to next ui
                self.loginFrame.pack_forget()
                self.mainAppUI()
                return
            else:
                self.uname.delete(0, END)
                self.passw.delete(0, END)
                self.errorLabel.pack()
            

        userFrame = Frame(self.loginFrame)
        passFrame = Frame(self.loginFrame)
        Label(userFrame, text='Username:').pack(side="left") 
        Label(passFrame, text='Password:').pack(side="left")
        self.uname = Entry(userFrame)
        self.uname.pack(side="right") 
        self.passw = Entry(passFrame,show="*")
        self.passw.pack(side="right")
        userFrame.pack()
        passFrame.pack()
        self.loginBtn = Button(self.loginFrame, text="Login", command=login)
        self.loginBtn.pack()
        self.errorLabel = Label(self.loginFrame, text="Login Failed", fg="red", pady=10)
        self.loginFrame.pack()
        
        
    def mainAppUI(self):
        self.mainFrame = Frame(self.root)
        topFrame = Frame(self.mainFrame)
        Label(topFrame, text="Enter link:").pack(side="left")
        self.link = Entry(topFrame)
        self.link.pack(side="right")
        topFrame.pack()
        self.processBtn = Button(self.mainFrame, text="Go")
        self.processBtn.pack()
        botFrame = Frame(self.mainFrame)
        Label(botFrame, text="Results here").pack()
        botFrame.pack()
        self.mainFrame.pack()

    

#        Label(loginUI,text="Failed").pack()
        return
root = Tk()
root.geometry("300x100+300+300")
windowUI = UI(root)
windowUI.loginMenu()

root.mainloop()