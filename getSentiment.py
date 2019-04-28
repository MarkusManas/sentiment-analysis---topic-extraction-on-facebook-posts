import os
import csv
import random
import sklearn
from topicExtraction import tokenize
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.preprocessing import LabelEncoder


def splitTextBySentiment():
    positive = open("positive.txt", "w", encoding="utf-8", newline="")
    negative = open("negative.txt", "w", encoding="utf-8", newline="")
    inquiry = open("inquiry.txt", "w", encoding="utf-8", newline="")
    neutral = open("neutral.txt", "w", encoding="utf-8", newline="")

    with open("data-set for senti analysis - collated-Comments.csv", encoding="utf-8") as csvfile:
        info = csv.reader(csvfile, delimiter=',')
        for row in info:
            if(row[6] == '1'):
                print("writing")
                positive.write(row[5]+"\n")
            elif(row[6] == '2'):
                print("writing")
                negative.write(row[5]+"\n")
            elif(row[6] == '3'):
                print("writing")
                inquiry.write(row[5]+"\n")
            elif(row[6] == '5'):
                print("writing")
                neutral.write(row[5]+"\n")
    positive.close()
    negative.close()
    inquiry.close()
    neutral.close()
    return 0


# splitTextBySentiment()

# posSet = []
# negSet = []
# corpus = []

def trainModel():
    z = "Hello po sir manny, majority of netizen want to know if your department is doing something to seriously eliminate the midlemen in the agricultural sector para naman yung farmer ay tunay na giginhawa. Dito kasi sa Canada malalaki ang bahay ng mga farmer,it’s very evident na may bunga talaga ang kanilang hardwork.Hindi gaya dyan na ang mnga farmers natin ay nagdidildil ng asin. As far as i know yung middlemen ay laway lang ang effort tapos mas malaki ang kita kisa sa farmer. 😔."

    data = []
    dataLabels = []

    positive = open("positive.txt", "r", encoding="utf-8")
    negative = open("negative.txt", "r", encoding="utf-8")
    neutral = open("neutral.txt", "r", encoding="utf-8")
    for line in positive:
        data.append(line.rstrip())
        dataLabels.append('pos')
    for line in negative:
        data.append(line.rstrip())
        dataLabels.append('neg')
#    for line in neutral:
#        data.append(line.rstrip())
#        dataLabels.append('neu')

    vectorizer = CountVectorizer(analyzer='word',tokenizer=tokenize, lowercase=False)
    encoder = LabelEncoder()
    x = vectorizer.fit_transform(data)
    y = encoder.fit_transform(dataLabels)
    X_train, X_test, y_train, y_test = train_test_split(x, y, train_size=0.80, random_state=84230)

    mnb = MultinomialNB()
    mnb.fit(X_train,y_train)
    y_pred = mnb.predict(X_test)
    y_predicted_labels = encoder.inverse_transform(y_pred)
    y_test_actual = encoder.inverse_transform(y_test)
    x_test_maps = vectorizer.inverse_transform(X_train)

    predictFile = open("predictions.txt", "w", encoding="utf-8")
    for i in range(len(y_predicted_labels)):
        predictFile.write(str(y_predicted_labels[i]) + " - " + str(y_test_actual[i]) + str(x_test_maps[i]) + "\n")
    print(accuracy_score(y_test, y_pred))
    predictFile.close()
    
    return mnb,encoder,vectorizer
# print(posSet)

def getSent(model, encoder, vect, text):
    x = vect.transform([text])
    y = model.predict(x)
    senti = encoder.inverse_transform(y)

    return senti
'''
x, enc, vect = trainModel()
z = "Hello po sir manny, majority of netizen want to know if your department is doing something to seriously eliminate the midlemen in the agricultural sector para naman yung farmer ay tunay na giginhawa. Dito kasi sa Canada malalaki ang bahay ng mga farmer,it’s very evident na may bunga talaga ang kanilang hardwork.Hindi gaya dyan na ang mnga farmers natin ay nagdidildil ng asin. As far as i know yung middlemen ay laway lang ang effort tapos mas malaki ang kita kisa sa farmer. 😔."
getSent(x, enc, vect,z)'''