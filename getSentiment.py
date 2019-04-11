import os
import csv
import random
import sklearn
from topicExtraction import tokenize
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


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

data = []
dataLabels = []

positive = open("postest1.txt", "r", encoding="utf-8")
negative = open("negative.txt", "r", encoding="utf-8")
for line in positive:
    data.append(line.rstrip())
    dataLabels.append('pos')
for line in negative:
    data.append(line.rstrip())
    dataLabels.append('neg')

vectorizer = CountVectorizer(analyzer='word', lowercase=False)
features = vectorizer.fit_transform(data)
features_nd = features.toarray()  # for easy usage

X_train, X_test, y_train, y_test = train_test_split(
        features_nd,
        dataLabels,
        train_size=0.80,
        random_state=1234)

log_model = LogisticRegression()
log_model = log_model.fit(X=X_train, y=y_train)
y_pred = log_model.predict(X_test)

j = random.randint(0, len(X_test)-7)
for i in range(j, j+7):
    print(y_pred[0])
    ind = features_nd.tolist().index(X_test[i].tolist())
    print(data[ind].strip())

print(accuracy_score(y_test, y_pred))

# print(posSet)
