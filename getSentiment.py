import os
import csv 

def splitTextBySentiment():
    positive = open("positive.txt","w",encoding="utf-8",newline="")
    negative = open("negative.txt","w",encoding="utf-8",newline="")
    inquiry = open("inquiry.txt","w",encoding="utf-8",newline="")
    neutral = open("neutral.txt","w",encoding="utf-8",newline="")

    with open("data-set for senti analysis - collated-Comments.csv", encoding="utf-8") as csvfile:
        info = csv.reader(csvfile, delimiter=',')
        for row in info:
            if(row[6]=='1'):
                print("writing")
                positive.write(row[5]+"\n")
            elif(row[6]=='2'):
                print("writing")
                negative.write(row[5]+"\n")
            elif(row[6]=='3'):
                print("writing")
                inquiry.write(row[5]+"\n")
            elif(row[6]=='5'):
                print("writing")
                neutral.write(row[5]+"\n")
    positive.close()
    negative.close()
    inquiry.close()
    neutral.close()
    return 0

splitTextBySentiment()