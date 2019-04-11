import re
import os
import sys
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog


def get_bow(path):
    # set variables
    bag_of_words = {}
    messagecount = 0
    # open directory and iterate over all files in it
    for fn in os.listdir(path):
        # only open files with numbers in it
        messagecount += 1
        filename = os.path.join(path, fn)
        inputfile = open(filename, mode="r", encoding="ISO-8859-1")
        for line in inputfile:
            # regex for matching the word
            matches = re.findall(r'[a-zA-Z-0-9]\S*', line)
            for match in matches:
                # for case insensitivity
                word = match.lower()
                # replace all characters that are not letters
                word = re.sub(r'[^a-zA-Z0-9]', "", word)
                # add to dictionary
                if word in bag_of_words:
                    bag_of_words[word] += 1
                else:
                    bag_of_words[word] = 1
        inputfile.close()
    # delete all blank words that was collected
    if "" in bag_of_words:
        del bag_of_words[""]
    return bag_of_words, messagecount


def count_bow_words(bow):
    count = 0
    for k in bow:
        count += bow[k]
    return count


def update_top_right_frame():
    global spam_bow, ham_bow, dict_size_text, total_words_text
    dict_size_text.configure(state="normal")
    dict_size_text.delete(1.0, "end")
    dict_size_text.insert("end", len(spam_bow)+len(ham_bow))
    dict_size_text.configure(state="disabled")

    total_words_text.configure(state="normal")
    total_words_text.delete(1.0, "end")
    total_words_text.insert("end", count_bow_words(
        spam_bow) + count_bow_words(ham_bow))
    total_words_text.configure(state="disabled")


def choose_spam_dir():
    global spam_bow, spam_messages, spam_tree, spam_word_text
    dirname = filedialog.askdirectory()
    # if cancelled then exit
    if dirname == '':
        return
    # clear vars
    spam_word_text.configure(state="normal")
    spam_word_text.delete(1.0, "end")
    spam_bow = {}
    spam_messages = 0
    spam_tree.delete(*spam_tree.get_children())
    # update vars
    spam_bow, spam_messages = get_bow(dirname)
    for k in spam_bow:
        spam_tree.insert("", 0, text=k, values=(spam_bow[k]))
    spam_word_text.insert("end", count_bow_words(spam_bow))
    spam_word_text.configure(state="disabled")
    update_top_right_frame()


def choose_ham_dir():
    global ham_bow, ham_messages, ham_tree, ham_word_text
    dirname = filedialog.askdirectory()
    # if cancelled then exit
    if dirname == '':
        return
    # clear vars
    ham_word_text.configure(state="normal")
    ham_word_text.delete(1.0, "end")
    ham_bow = {}
    ham_messages = 0
    ham_tree.delete(*ham_tree.get_children())
    # update vars
    ham_bow, ham_messages = get_bow(dirname)
    for k in ham_bow:
        ham_tree.insert("", 0, text=k, values=(ham_bow[k]))
    ham_word_text.insert("end", count_bow_words(ham_bow))
    ham_word_text.configure(state="disabled")
    update_top_right_frame()


def test_messages(path):
    global output_tree
    output_tree.delete(*output_tree.get_children())
    file = open("classify.out", "w")
    # open directory and iterate over all files in it
    for fn in os.listdir(path):
        bag_of_words = {}
        # only open files with numbers in it
        filename = os.path.join(path, fn)
        inputfile = open(filename, mode="r", encoding="ISO-8859-1")
        for line in inputfile:
            # regex for matching the word
            matches = re.findall(r'[a-zA-Z-0-9]\S*', line)
            for match in matches:
                # for case insensitivity
                word = match.lower()
                # replace all characters that are not letters
                word = re.sub(r'[^a-zA-Z0-9]', "", word)
                # add to dictionary
                if word in bag_of_words:
                    bag_of_words[word] += 1
                else:
                    bag_of_words[word] = 1
        inputfile.close()
        # delete all blank words that was collected
        if "" in bag_of_words:
            del bag_of_words[""]
        # cut the name so it doesnt display the full location of file
        shortname = re.findall(r'(?<=/)[^/]+$', filename)[0]
        prob = prob_of_spam_given_msg(bag_of_words)
        output_tree.insert("", 0, text=shortname, values=(
            "SPAM" if prob >= 0.5 else "HAM", prob))
        file.write(shortname+(" SPAM " if prob >=
                              0.5 else " HAM ")+str(prob)+"\n")
    file.close()
    return


def choose_classify_dir():
    dirname = filedialog.askdirectory(initialdir="")
    # if cancelled then exit
    if dirname == '':
        return
    test_messages(dirname)

# formula for computing spam given message


def prob_of_spam():
    global spam_messages, ham_messages
    return (spam_messages/(spam_messages+ham_messages))


def prob_of_ham():
    return (1-prob_of_spam())


def prob_of_word_given_bow(word, bow):
    return (bow[word]/count_bow_words(bow))


def prob_of_msg_given_bow(msg_bow, bow):
    prob = 1
    for k in msg_bow:
        if k in bow:
            prob = prob * prob_of_word_given_bow(k, bow)
    return prob


def prob_of_msg(msg_bow):
    global spam_bow, ham_bow
    return (prob_of_msg_given_bow(msg_bow, spam_bow)*prob_of_spam())+(prob_of_msg_given_bow(msg_bow, ham_bow)*prob_of_ham())


def prob_of_spam_given_msg(msg_bow):
    global spam_bow
    numerator = prob_of_spam() * prob_of_msg_given_bow(msg_bow, spam_bow)
    denominator = prob_of_msg(msg_bow)
    return (numerator/denominator)


# DRAW
root = tk.Tk()
# this is the left most frame for the spam side
mainFrame = Frame(root)
frame1 = Frame(mainFrame)
spam_folder_button = Button(
    frame1, text="Select Spam Folder", command=choose_spam_dir)
spam_folder_button.pack()
spam_tree = ttk.Treeview(frame1, columns=('ham_count'))
spam_tree.column("#0", width=135)
spam_tree.column("#1", width=95, anchor="c")
spam_tree.heading("#0", text="Word")
spam_tree.heading("#1", text="Count")
spam_tree.pack()
Label(frame1, text="Total words in spam: ").pack()
spam_word_text = Text(frame1, height=1, width=10)
spam_word_text.pack()
spam_word_text.configure(state="disabled")
frame1.pack(side="left")
# middle frame for ham side
frame2 = Frame(mainFrame)
ham_folder_button = Button(
    frame2, text="Select Ham Folder", command=choose_ham_dir)
ham_folder_button.pack()
ham_tree = ttk.Treeview(frame2, columns=('ham_count'))
ham_tree.column("#0", width=135)
ham_tree.column("#1", width=95, anchor="c")
ham_tree.heading("#0", text="Word")
ham_tree.heading("#1", text="Count")
ham_tree.pack()
Label(frame2, text="Total words in ham: ").pack()
ham_word_text = Text(frame2, height=1, width=10)
ham_word_text.pack()
spam_word_text.configure(state="disabled")
frame2.pack(side="left")
# rightmost frame for results
bigRightFrame = Frame(mainFrame)
# dictionary and total words frame
topInsideFrame = Frame(bigRightFrame)
topLeftFrame = Frame(topInsideFrame)
# dictsize
Label(topLeftFrame, text="Dictionary Size: ").pack()
dict_size_text = Text(topLeftFrame, height=1, width=9)
dict_size_text.pack()
dict_size_text.configure(state="disabled")
topLeftFrame.pack(side="left")
topRightFrame = Frame(topInsideFrame)
# totalwords
Label(topRightFrame, text="Total Words: ").pack()
total_words_text = Text(topRightFrame, height=1, width=9)
total_words_text.pack()
total_words_text.configure(state="disabled")
topRightFrame.pack(side="left")
topInsideFrame.pack(side="top")
classify_folder_button = Button(
    bigRightFrame, text="Select Classify Folder", command=choose_classify_dir)
classify_folder_button.pack()
# output tree
output_tree = ttk.Treeview(bigRightFrame, columns=('class', 'result'))
output_tree.column("#0", width=155)
output_tree.column("#1", width=75)
output_tree.column("#2", width=135)
output_tree.heading("#0", text="Filename")
output_tree.heading("#1", text="Class")
output_tree.heading("#2", text="P(S|M)")
output_tree.pack()
Label(bigRightFrame, text="Output").pack()
bigRightFrame.pack(side="left")
mainFrame.pack()
####################################

ham_bow = {}
ham_messages = 0
spam_bow = {}
spam_messages = 0
mainloop()
