from tkinter import *
from tkinter import ttk, _tkinter, font

import threading
import selenium
import re
import pickle
import wordcloud
from getcomments import get_comments, login
from getSentiment import getVE, getSent
from topicExtraction import model_processing, multi_process, topicTok
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.patches
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from sklearn.externals import joblib
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
        time.sleep(1)
    lock = True
    print("creating piechart...")
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
    app.pcImg = ImageTk.PhotoImage(Image.open("pc.png"))
    app.pcLabel = Label(app.pieTab, image=app.pcImg)
    app.pcLabel.pack(fill=BOTH, expand=1)
    print("finished creating piechart")
    return

#creates a wordcloud - worker thread
def makeWordCloud(arg1, tab, imgTk, labelTk):
    global lock
    while lock:
        time.sleep(1)
    lock = True
    for child in tab.winfo_children():
        child.destroy()
    print("creating wordcloud...")
    text = ""
    #    comments = getHotTopic(arg1)
    for i in range (0, len(arg1)):
        text += arg1[i]["text"]
        text += ". "
    text = topicTok(text)
    text = '. '.join(text)
    wc = wordcloud.WordCloud(background_color="white",stopwords=set(wordcloud.STOPWORDS)).generate(text)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("wc.png")
    plt.clf()
        
    imgTk = ImageTk.PhotoImage(Image.open("wc.png"))
    labelTk = Label(tab, image=imgTk)
    labelTk.pack(fill=BOTH, expand=1)
    print("finishedcreating wordCloud")
    lock = False
    return

def makeWordCloudTop(arg1):
    global lock, app
    while lock:
        time.sleep(1)
    lock = True
    for child in app.wcTabTop.winfo_children():
        child.destroy()
    print("creating wordcloud...")
    text = ""
    #    comments = getHotTopic(arg1)
    for i in range (0, len(arg1)):
        text += arg1[i]["text"]
        text += ". "
    text = topicTok(text)
    text = '. '.join(text)
    wcTop = wordcloud.WordCloud(background_color="white",stopwords=set(wordcloud.STOPWORDS)).generate(text)
    plt.imshow(wcTop, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("wcTop.png")
    plt.clf()
        
    app.wcImgTop = ImageTk.PhotoImage(Image.open("wcTop.png"))
    app.wcLabelTop = Label(app.wcTabTop, image=app.wcImgTop)
    app.wcLabelTop.pack(fill=BOTH, expand=1)
    print("finishedcreating wordCloud")
    lock = False
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
            discussionList.append(comment)
        if comment["parent_comment_id"] == largestID:
            discussionList.append(comment)
    # done getting whole discussion
    # call topic extraction
    #topics = multi_process(discussionList)
    return discussionList


def topLevelCommentTopics(comments):
    
    # get all comments in said discussion
    discussionList = []
    for comment in comments:
        if comment["parent_comment_id"] == 0:
            discussionList.append(comment)
    # done getting whole discussion
    # call topic extraction
    #for comment in discussionList:
    #    print(comment)
    # topics = multi_process(discussionList)
    return discussionList


def cleanComments(comments):
    toBeDeleted = []
    for comment in comments:
        if "Replied sticker" in comment["text"]:
            toBeDeleted.append(comment)
    for item in toBeDeleted:
        comments.remove(item)
    return comments


def makeSentiTable(textSentiList):
    global app

    
    for child in app.sentTab.winfo_children():
        child.destroy()

    vsb = Scrollbar(app.sentTab, orient=VERTICAL)
    hsb = Scrollbar(app.sentTab, orient=HORIZONTAL)
    textWidget = Text(app.sentTab, wrap=NONE)
    vsb.config(command=textWidget.yview)
    hsb.config(command=textWidget.xview)
    textWidget.config(yscrollcommand=vsb.set)
    textWidget.config(xscrollcommand=hsb.set)
    count = 1
    for textSenti in textSentiList:
        try:
            textWidget.insert(END, str(textSenti["senti"]))
            textWidget.insert(END, " - ")
            textWidget.insert(END, textSenti["text"])
            textWidget.insert(END, "\n")  
            count += 1
        except _tkinter.TclError:
            textWidget.delete('%d.0' % (count), END)
            textWidget.insert(END, "\n") 
            count+=1
            continue
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    textWidget.pack( fill=BOTH, expand=1)
    textWidget.config(state=DISABLED)
    return


def processPost():
    global app, sentModel, enc, vect

    link = app.link.get()

    #download and save comments and post first
    #downloading post
    print("attempting to get comments")
    postObj, commentsL = get_comments(app.browser,link)
    commentsList = cleanComments(commentsL)
    #print(commentsList)
    asd = commentsList
    threading.Thread(target=makeWordCloud, args=([postObj], app.wcTab, app.wcImg, app.wcLabel), daemon=True).start()
    #threading.Thread(target=makeWordCloud, args=(getHotTopic(asd), app.wcTabHot, app.wcImgHot, app.wcLabelHot), daemon=True).start()
    #threading.Thread(target=makeWordCloud, args=(topLevelCommentTopics(asd), app.wcTabTop, app.wcImgTop, app.wcLabelTop), daemon=True).start()
    print("Finished downloading posts and comments")
    generalSenti = ""
    count = 0
    posCount = negCount = neuCount = 0
    textSentiList = []

    for comm in commentsList:
        textSenti = {"text":"", "senti": None}
        textSenti["text"] = comm["text"]
        sent = getSent(sentModel, vect, enc, textSenti["text"])
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
    print("General sentiment is: ", generalSenti)

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
    #topLevelCommentTopics(commentsList)
    threading.Thread(target=showPiechart, args=(posCount, negCount), daemon=True).start()
    threading.Thread(target=makeSentiTable, args=([textSentiList]) ,daemon=True).start()
    #threading.Thread(target=makeWordCloud, args=(getHotTopic(asd), app.wcTabHot, app.wcImgHot, app.wcLabelHot), daemon=True).start()
    #threading.Thread(target=makeWordCloud, args=(topLevelCommentTopics(asd), app.wcTabTop, app.wcImgTop, app.wcLabelTop), daemon=True).start()
    makeWordCloudTop(topLevelCommentTopics(asd))
    #for item in commentsList:
    #    print(item)

    app.root.update()

def tryLogin():
    global app
    app.loginBtn['state']=DISABLED

    app.browser, app.successfulLogin = login(app.uname.get(), app.passw.get())
    app.loginBtn['state']=NORMAL

    if app.successfulLogin:
        #proceed to next ui
        app.loginFrame.pack_forget()
        app.mainAppUI()
        return
    else:
        app.uname.delete(0, END)
        app.passw.delete(0, END)
        app.errorLabel.pack()
        return
    return

def loginThread():
    thr = threading.Thread(target=tryLogin, daemon=True)
    thr.start()


def tryProcessPost():
    global app
    app.processBtn['state'] = DISABLED
    processPost()
    app.processBtn['state'] = NORMAL
    return        

def processBtnThread():
    thr = threading.Thread(target=tryProcessPost, daemon=True)
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
        self.sentTab = None
        self.pcImg = None
        self.pcLabel = None
        self.wcImg = None
        self.wcLabel = None
        #hottopic
        self.wcTabHot = None
        self.wcImgHot = None
        self.wcLabelHot = None
        #toptopic
        self.wcTabTop = None
        self.wcImgTop = None
        self.wcLabelTop = None
        self.loginUI()
        

    def loginUI(self):
        
        self.successfulLogin = False
        topFrame = Frame(self.loginFrame)
        Label(topFrame, text='Username:').grid(row=0, column=0)
        Label(topFrame, text='Password:').grid(row=1, column=0)
        self.uname = Entry(topFrame)
        self.uname.grid(row=0, column=1)
        self.passw = Entry(topFrame,show="*")
        self.passw.grid(row=1, column=1)
        topFrame.pack()
        self.loginBtn = Button(self.loginFrame, text="Login", command=loginThread)
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
        self.idLabel = Label(gridInFrame, text="-")
        self.idLabel.grid( row=1, column=0, padx=5)
        self.authorLabel = Label(gridInFrame, text="-")
        self.authorLabel.grid( row=1, column=1, padx=5)
        self.dateLabel = Label(gridInFrame, text="-")
        self.dateLabel.grid( row=1, column=2, padx=5)
        self.commentLabel = Label(gridInFrame, text="-")
        self.commentLabel.grid( row=1, column=3, padx=5)
        Label(gridInFrame, text = "Topic", font=('Arial', 10,'bold')).grid(row=2, column=0, padx=5)
        self.topicLabel = Label(gridInFrame, text = "-")
        self.topicLabel.grid(row=3, column=0, padx=5)
        Label(gridInFrame, text = "Sentiment", font=('Arial', 10,'bold')).grid(row=2, column=1, padx=5)
        self.sentimentLabel = Label(gridInFrame, text = "-")
        self.sentimentLabel.grid(row=3, column=1, padx=5)
        Label(gridInFrame, text = "Hot topic", font=('Arial', 10,'bold')).grid(row=2, column=2, padx=5)
        self.hotTopicLabel = Label(gridInFrame, text = "-")
        self.hotTopicLabel.grid(row=3, column=2, padx=5)

        gridInFrame.pack(padx=5, pady=5)
        botFrame.pack(pady=10,fill=BOTH, expand=1)
        self.mainFrame.pack(fill=BOTH, expand=1)
        self.pieTab = ttk.Frame(self.nb)
        self.pieTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.mainFrame, text="Retrieve Post")
        self.sentTab = ttk.Frame(self.nb)
        self.sentTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.sentTab, text="Sentiment Table")
        self.nb.pack(fill=BOTH, expand=1)
        self.nb.add(self.pieTab, text="Sentiment Pie chart")
        self.wcTab = ttk.Frame(self.nb)
        self.wcTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.wcTab, text="Post topic wordcloud")
        #hot topic
        '''
        self.wcTabHot = ttk.Frame(self.nb)
        self.wcTabHot.pack(fill=BOTH, expand=1)
        self.nb.add(self.wcTabHot, text="Hot topic wordcloud")
        '''
        #toplevel topic
        self.wcTabTop = ttk.Frame(self.nb)
        self.wcTabTop.pack(fill=BOTH, expand=1)
        self.nb.add(self.wcTabTop, text="Comment topic wordcloud")
        

sentModel = joblib.load('sentiModel.pkl')
vect = pickle.load(open("vector.pkl", "rb"))
enc = pickle.load(open("encoder.pkl", "rb"))
#vect, enc = getVE()
ROOT = Tk()
ROOT.title("sp")
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Futura Lt BT")
default_font.configure(size=12)
ROOT.option_add("*Font", "TkDefaultFont")
app = App(ROOT)
ROOT.mainloop()