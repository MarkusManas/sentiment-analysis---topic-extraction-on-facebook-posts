from tkinter import *
from tkinter import ttk
import threading
import selenium
import re
import wordcloud
from getcomments import get_comments, login
from getSentiment import trainModel, getSent
from topicExtraction import model_processing, multi_process
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.patches
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

lock = False

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

#creates a pie chart - worker thread
def showPiechart(pos,neg):
    global app, lock
    while lock:
        time.sleep(0.1)
    lock = True
    pieLabels = 'Positive', 'Negative'
    sizes = [pos, neg]
    colors = ['lightskyblue', 'lightcoral']
    # explode = (0.1, 0, 0, 0)  # explode 1st slice
    
    # Plot
    plt.pie(sizes, autopct=make_autopct(sizes), startangle=90, labels=pieLabels, colors=colors, shadow=True)

    plt.axis('equal')
    plt.savefig("pc.png")
    plt.clf()
    lock = False
    for child in app.pieTab.winfo_children():
        child.destroy()
    pc = ImageTk.PhotoImage(Image.open("pc.png"))
    panel = Label(app.pieTab, image=pc)
    panel.pack(fill=BOTH, expand=1)
    return

#creates a wordcloud - worker thread
def makeWordCloud(arg1):
    global lock
    while lock:
        time.sleep(0.1)
    lock = True
    text = ""
    #    comments = getHotTopic(arg1)
    for comment in arg1:
        if "replied sticker" in comment["text"]:
            continue
        else:
            text += comment ["text"] +". "
    wc = wordcloud.WordCloud(background_color="white",stopwords=set(wordcloud.STOPWORDS)).generate(text)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("wc.png")
    plt.clf()
    lock = False
    for child in app.wcTab.winfo_children():
        child.destroy()
    wc = ImageTk.PhotoImage(Image.open("wc.png"))
    panel1 = Label(app.wcTab, image=wc)
    panel1.pack(fill=BOTH, expand=1)
    return

#gets the topic using LDA of the comment that 
#generated the most discussion
def getHotTopic(comments):
    global app
    largestID = 0
    largestCount = 0 
    count = 0
    #search comment list for most count of replies
    for comment in comments:
        if count == 0:
            largestID = comment["id"]
            largestCount = comment["no_of_replies"]
            count += 1
            continue

        if comment["no_of_replies"] > largestCount:
            largestCount = comment["no_of_replies"]
            largestID = comment["id"]
        count += 1
    #done getting id of most talked reply
    # get all comments in said discussion
    discussionList = []
    for comment in comments:
        if comment["id"] == largestID:
            discussionList.append(comment["text"])
        if comment["parent_comment_id"] == largestID:
            discussionList.append(comment["text"])
    # done getting whole discussion
    # call topic extraction
    topics = multi_process(discussionList)
    return topics


def topLevelCommentTopics(comments):
    
    # get all comments in said discussion
    discussionList = []
    for comment in comments:
        if comment["parent_comment_id"] == 0:
            discussionList.append(comment["text"])
    # done getting whole discussion
    # call topic extraction
    for comment in discussionList:
        print(comment)
    topics = multi_process(discussionList)
    return topics


def cleanComments(comments):
    for comment in comments:
        if "replied sticker" in comment["text"]:
            comments.remove(comment)

    return comments


def processPost():
    global app, model, encoder, vect

    link = app.link.get()

    #download and save comments and post first
    #downloading post
    print("attempting to get comments")
    postObj, commentsList = get_comments(app.browser,link)
    commentsList = cleanComments(commentsList)
    asd = [commentsList]
    threading.Thread(target=makeWordCloud, args=(asd), daemon=True).start()
    print("Finished downloading posts and comments")
    generalSenti = ""
    count = 0
    posCount = negCount = neuCount = 0
    textSentiList = []

    for comm in commentsList:
        textSenti = {"text":"", "senti": None}
        textSenti["text"] = comm["text"]
        sent = getSent(model, encoder, vect, textSenti["text"])
        sent = sent[0]
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
    
    #getHotTopic(commentsList)
    topLevelCommentTopics(commentsList)
    threading.Thread(target=showPiechart, args=(posCount, negCount), daemon=True).start()

    app.root.update()


def processBtnThread():
    thr = threading.Thread(target=processPost, daemon=True)
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
        self.hotTopicLabel = None
        self.nb = None
        self.pieTab = None
        self.wcTab = None
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
        topFrame = Frame(self.loginFrame)
        Label(topFrame, text='Username:').grid(row=0, column=0)
        Label(topFrame, text='Password:').grid(row=1, column=0)
        self.uname = Entry(topFrame)
        self.uname.grid(row=0, column=1)
        self.passw = Entry(topFrame,show="*")
        self.passw.grid(row=1, column=1)
        topFrame.pack()
        self.loginBtn = Button(self.loginFrame, text="Login", command=loginBtn)
        self.loginBtn.pack(pady=5)
        self.errorLabel = Label(self.loginFrame, text="Login Failed", fg="red", pady=10)
        self.loginFrame.pack(pady=5)

    def mainAppUI(self):
        #self.mainFrame = Frame(self.root)
        #self.root.geometry("550x550+400+400")
        self.nb = ttk.Notebook(self.root)
        self.mainFrame = ttk.Frame(self.nb)
        topFrame = Frame(self.mainFrame,borderwidth=1, relief="raised")
        Label(topFrame, text="Enter link:").pack(side="left")
        self.link = Entry(topFrame,width=80)
        self.link.pack(side="right")
        topFrame.pack(pady=5)
        self.processBtn = Button(self.mainFrame, command=processBtnThread , pady = 2, text="Retrieve Post")
        self.processBtn.pack()
        botFrame = Frame(self.mainFrame,bd=1, relief="raised")
        Label(botFrame, text="General summary:", bd=1, relief="raised").pack()
        gridInFrame = Frame(botFrame,pady=1,padx=3)
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
        Label(gridInFrame, text = "Hot topic", font=('Arial', 10,'bold')).grid(row=2, column=2, padx=5)
        self.hotTopicLabel = Label(gridInFrame, text = "lorem ipsum")
        self.hotTopicLabel.grid(row=3, column=2, padx=5)

        gridInFrame.pack(padx=5, pady=5)
        botFrame.pack(pady=10,fill=BOTH, expand=1)
        self.mainFrame.pack(fill=BOTH, expand=1)
        self.pieTab = ttk.Frame(self.nb)
        self.pieTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.mainFrame, text="Retrieve Post")
        self.nb.add(self.pieTab, text="Sentiment Pie chart")
        self.wcTab = ttk.Frame(self.nb)
        self.wcTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.wcTab, text="Hot topic wordcloud")
        self.nb.pack(fill=BOTH, expand=1)
        

ROOT = Tk()
app = App(ROOT)
model, encoder, vect = trainModel()
ROOT.mainloop()