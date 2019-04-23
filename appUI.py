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
        self.root.geometry("400x250+400+400")
        self.mainFrame = Frame(self.root,pady=10,bg="gray")
        topFrame = Frame(self.mainFrame,borderwidth=1, relief="raised")
        Label(topFrame, text="Enter link:").pack(side="left")
        self.link = Entry(topFrame,width=80)
        self.link.pack(side="right")
        topFrame.pack(pady=5)
        self.processBtn = Button(self.mainFrame, pady = 2, text="Get summary")
        self.processBtn.pack()
        botFrame = Frame(self.mainFrame,bd=1, relief="raised")
        Label(botFrame, text="General summary:", bd=1, relief="raised").pack()
        gridInFrame = Frame(botFrame,pady=1,padx=3, bd=1, relief='raised')
        Label(gridInFrame, text="Post Id:", font=('Arial', 10,'bold')).grid( row=0, column=0, padx=5)
        Label(gridInFrame, text="Post Author:", font=('Arial', 10,'bold')).grid( row=0, column=1, padx=5)
        Label(gridInFrame, text="Post Date:", font=('Arial', 10,'bold')).grid( row=0, column=2, padx=5)
        Label(gridInFrame, text="Comments:", font=('Arial', 10,'bold')).grid( row=0, column=3, padx=5)
        Label(gridInFrame, text="lorem").grid( row=1, column=0, padx=5)
        Label(gridInFrame, text="ipsum").grid( row=1, column=1, padx=5)
        Label(gridInFrame, text="dolor").grid( row=1, column=2, padx=5)
        Label(gridInFrame, text="lorem").grid( row=1, column=3, padx=5)
        Label(gridInFrame, text = "Sentiment", font=('Arial', 10,'bold')).grid(row=2, column=0, padx=5)
        Label(gridInFrame, text = "lorem ipsum").grid(row=3, column=0, padx=5)
        

        gridInFrame.pack(padx=5, pady=5)
        botFrame.pack(pady=10)
        self.mainFrame.pack(fill=BOTH, expand=1)

    

#        Label(loginUI,text="Failed").pack()
        return
root = Tk()
root.geometry("300x100+400+400")
windowUI = UI(root)
windowUI.loginMenu()

root.mainloop()