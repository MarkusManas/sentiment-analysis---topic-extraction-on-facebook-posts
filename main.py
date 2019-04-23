from tkinter import *
import threading
import selenium
import re
from getcomments import get_comments, login
from getSentiment import trainModel, getSent
from topicExtraction import model_processing
def processPost():
    global app, model, encoder, vect

    link = app.link.get()

    #download and save comments and post first
    #downloading post
    print("attempting to get comments")
    postObj, commentsList = get_comments(app.browser,link)

    print("Finished downloading posts and comments")
    generalSenti = ""
    count = 0
    posCount = negCount = neuCount = 0
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
        if sent == "pos":
            posCount += 1
        elif sent == "neu":
            neuCount += 1
        else:
            negCount += 1

    if posCount > negCount:
        generalSenti = "Positive"
    else:
        generalSenti = "Negative"

    print("finished predicting")
    file = open("test.txt", "w", encoding="utf-8")

    for item in textSentiList:
        file.write(str(item["senti"]))
        file.write(" - ")
        file.write(item["text"])
        file.write("\n")  

    file.close()
    print("Genereal sentiment is: ", generalSenti)

    topicModel = model_processing(postObj["text"])    
    #get Topic
    #postTopics = str(topicModel.print_topics(-1)[0])
    topics = topicModel.show_topic(0)
    topics = topics[0][0] + ", " + topics[1][0] + ", " + topics[2][0]
    app.idLabel["text"] = postObj["id"]
    app.authorLabel["text"] = postObj["author"]
    app.commentLabel["text"] = str(len(commentsList))
    app.dateLabel["text"] =  postObj["date"]
    app.topicLabel["text"] = topics
    app.sentimentLabel["text"] = generalSenti

#    print(postTopics)
    app.root.update()


def processBtnThread():
    thr = threading.Thread(target=processPost)
    thr.start()

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
        self.idLabel = None
        self.authorLabel = None
        self.commentLabel = None
        self.dateLabel = None
        self.topicLabel = None
        self.sentimentLabel = None
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
        #self.mainFrame = Frame(self.root)
        self.root.geometry("550x250+400+400")
        self.mainFrame = Frame(self.root,pady=10,bg="gray")
        topFrame = Frame(self.mainFrame,borderwidth=1, relief="raised")
        Label(topFrame, text="Enter link:").pack(side="left")
        self.link = Entry(topFrame,width=80)
        self.link.pack(side="right")
        topFrame.pack(pady=5)
        self.processBtn = Button(self.mainFrame, command=processBtnThread , pady = 2, text="Get summary")
        self.processBtn.pack()
        botFrame = Frame(self.mainFrame,bd=1, relief="raised")
        Label(botFrame, text="General summary:", bd=1, relief="raised").pack()
        gridInFrame = Frame(botFrame,pady=1,padx=3, bd=1, relief='raised')
        Label(gridInFrame, text="Post Id:", font=('Arial', 10,'bold')).grid( row=0, column=0, padx=5)
        Label(gridInFrame, text="Post Author:", font=('Arial', 10,'bold')).grid( row=0, column=1, padx=5)
        Label(gridInFrame, text="Post Date:", font=('Arial', 10,'bold')).grid( row=0, column=2, padx=5)
        Label(gridInFrame, text="Comments:", font=('Arial', 10,'bold')).grid( row=0, column=3, padx=5)
        self.idLabel = Label(gridInFrame, text="lorem")
        self.idLabel.grid( row=1, column=0, padx=5)
        self.authorLabel = Label(gridInFrame, text="ipsum")
        self.authorLabel.grid( row=1, column=1, padx=5)
        self.dateLabel = Label(gridInFrame, text="dolor")
        self.dateLabel.grid( row=1, column=2, padx=5)
        self.commentLabel = Label(gridInFrame, text="lorem")
        self.commentLabel.grid( row=1, column=3, padx=5)
        Label(gridInFrame, text = "Topic", font=('Arial', 10,'bold')).grid(row=2, column=0, padx=5)
        self.topicLabel = Label(gridInFrame, text = "lorem ipsum")
        self.topicLabel.grid(row=3, column=0, padx=5)
        Label(gridInFrame, text = "Sentiment", font=('Arial', 10,'bold')).grid(row=2, column=1, padx=5)
        self.sentimentLabel = Label(gridInFrame, text = "lorem ipsum")
        self.sentimentLabel.grid(row=3, column=1, padx=5)

        gridInFrame.pack(padx=5, pady=5)
        botFrame.pack(pady=10)
        self.mainFrame.pack(fill=BOTH, expand=1)


ROOT = Tk()
ROOT.geometry("300x100+300+300")
app = App(ROOT)
model, encoder, vect = trainModel()
ROOT.mainloop()