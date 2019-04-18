from tkinter import *
import threading
import selenium
from getcomments import get_comments, login
from getSentiment import trainModel, getSent
def processPost():
    global app, model, encoder, vect

    app.link = app.link.get()

    #download and save comments and post first
    #downloading post

    postObj, commentsList = get_comments(app.browser,app.link)

    print("Finished downloading posts and comments")

    count = 0

    textSentiList = []

    for comm in commentsList:
        print(count)
        textSenti = {"text":"", "senti": None}
        textSenti["text"] = comm["text"]
        sent = getSent(model, encoder, vect, textSenti["text"])
        print("print predicted - ", count)
        sent = sent[0]
        print("encoded - ", count)
        textSenti["senti"] = sent
        textSentiList.append(textSenti)

    print("finished predicting")
    file = open("test.txt", "w", encoding="utf-8")

    for item in textSentiList:
        file.write(str(item["senti"]))
        file.write(" - ")
        file.write(item["text"])
        file.write("\n")
    
    file.close()
    
    return

class App(threading.Thread):

    def __init__(self, tk_root):
        self.root = tk_root
        self.loginFrame = Frame(self.root)
        self.uname = None
        self.passw = None
        self.loginBtn = None
        self.errorLabel = None
        self.link = None
        self.processBtn = None
        self.mainFrame = None
        self.browser = None
        self.successfulLogin = None
        self.loginUI()

    def loginUI(self):
        
        def loginBtn():
            print("clicked")
            print(self.uname.get())
            self.browser, self.successfulLogin = login(self.uname.get(), self.passw.get())
            
            if self.successfulLogin:
                #proceed to next ui
                self.loginFrame.pack_forget()
                self.mainAppUI()
                return

            else:
                self.uname.delete(0, END)
                self.passw.delete(0, END)
                self.errorLabel.pack()
                return
                
        self.successfulLogin = False
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
        self.loginBtn = Button(self.loginFrame, text="Login", command=loginBtn)
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
        self.processBtn = Button(self.mainFrame, text="Go", command=processPost)
        self.processBtn.pack()
        botFrame = Frame(self.mainFrame)
        Label(botFrame, text="Results here").pack()
        botFrame.pack()
        self.mainFrame.pack()

ROOT = Tk()
ROOT.geometry("300x100+300+300")
app = App(ROOT)
model, encoder, vect = trainModel()
ROOT.mainloop()