from tkinter import *
from tkinter import ttk, _tkinter

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
def makeWordCloud(arg1):
    global lock
    while lock:
        time.sleep(1)
    lock = True
    for child in app.wcTab.winfo_children():
        child.destroy()
    print("creating wordcloud...")
    text = ""
    #    comments = getHotTopic(arg1)
    for comment in arg1:
        if "replied sticker" in comment["text"]:
            continue
        else:
            text += comment ["text"] +". "
    text = "Happy Birthday PRRD!  DA COMMISSIONS SIGNAL 5 TYPHOON-RESISTANT DOME  By Manny Piñol  Iguig, Cagayan - The days when government spends hundreds of millions of pesos to repair buildings and warehouses after the devastation by typhoons will soon be over.  The Department of Agriculture (DA) yesterday inaugurated and commissioned the first monolithic dome which will serve as a grains warehouse in the DA Experimental Station in Iguig town Cagayan Province.  Designed by German engineers, the first monolithic dome constructed by a Filipino company with Polish engineers as consultants could withstand Typhoon Signal 5 many of which previously devastated many DA buildings and warehouses in the Cagayan Valley Region.  I flew to Cagayan Province  yesterday shortly after arriving from a 4-day marketing promotions trip to Belarus and Russia over the weekend to commission the first-ever monolithic dome constructed by the DA.  Costing P10-M and constructed in record time, the monolithic dome is impressive indeed.  While the temperature outside when I arrived at 3:30 p.m. was a scorching 36C degrees, it was only 21C  inside the Monolithic Dome.  The Polish engineers told me that the dome has insulators which deflects the heat of the sun and keeps the interior temperature at levels ideal for grains storage.  DA Cagayan Valley Director Narciso Edillo said the Iguig Monolithic Dome is the first of 8 units to be established in the region which is hit by as much as 12 typhoons every year.   Seven other smaller units costing P5-M each are now being constructed for farmers' groups in Cagayan Valley Region.  When the Monolithic Domes are tested and proven to withstand the destructive power of typhoons, similar structures will be built in other areas located on the path of typhoons.  These areas include Eastern and Western Visayas, Bicol, Southern Tagalog including Mindoro, Central Luzon, Ilocos and Cordillera Regions.  Yesterday during the commissioning, I said it was our fitting birthday gift to President Rody Duterte to support his goal of making life better for the people.  This innovation, along with the National Color-Coded Agriculture Guide Map, the Solar-Powered Irrigation and many more, will make Philippine Agriculture Climate Change Resilient.  #NeverStopDreaming! #NeverStopBelieving! #KungGustoMaramingParaan! #BukasMayUmagangDarating!  (Photos by Mayette Tudlas)"
    
    wc = wordcloud.WordCloud(background_color="white",stopwords=set(wordcloud.STOPWORDS)).generate(text)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("wc.png")
    plt.clf()
    lock = False
        
    app.wcImg = ImageTk.PhotoImage(Image.open("wc.png"))
    app.wcLabel = Label(app.wcTab, image=app.wcImg)
    app.wcLabel.pack(fill=BOTH, expand=1)
    print("finishedcreating wordCloud")
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
    #for comment in discussionList:
    #    print(comment)
    topics = multi_process(discussionList)
    return topics


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
            count+=1
            continue
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    textWidget.pack( fill=BOTH, expand=1)
    textWidget.config(state=DISABLED)
    print("asdadasdasdasdadsADSADSADADSADSADA")
    return


def processPost():
    global app, model, encoder, vect

    link = app.link.get()

    #download and save comments and post first
    #downloading post
    print("attempting to get comments")
    postObj, commentsL = get_comments(app.browser,link)
    commentsList = cleanComments(commentsL)
    #print(commentsList)
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
    topLevelCommentTopics(commentsList)
    threading.Thread(target=showPiechart, args=(posCount, negCount), daemon=True).start()
    threading.Thread(target=makeSentiTable, args=([textSentiList]) ,daemon=True).start()

    for item in commentsList:
        print(item)

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
        self.sentTab = None
        self.pcImg = None
        self.pcLabel = None
        self.wcImg = None
        self.wcLabel = None
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
        self.idLabel = Label(gridInFrame, text="-")
        self.idLabel.grid( row=1, column=0, padx=5)
        self.authorLabel = Label(gridInFrame, text="-")
        self.authorLabel.grid( row=1, column=1, padx=5)
        self.dateLabel = Label(gridInFrame, text="dolor")
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
        self.nb.add(self.pieTab, text="Sentiment Pie chart")
        self.wcTab = ttk.Frame(self.nb)
        self.wcTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.wcTab, text="Post topic wordcloud")
        self.sentTab = ttk.Frame(self.nb)
        self.sentTab.pack(fill=BOTH, expand=1)
        self.nb.add(self.sentTab, text="Sentiment Table")
        self.nb.pack(fill=BOTH, expand=1)
        

ROOT = Tk()
ROOT.title("sp")
app = App(ROOT)
model, encoder, vect = trainModel()
ROOT.mainloop()