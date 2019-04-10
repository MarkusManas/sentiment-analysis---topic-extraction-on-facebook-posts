import csv
import gensim
from multiprocessing import Process, freeze_support


#tokenize function
def tokenize(msg):
    tokens = []
    for token in gensim.utils.simple_preprocess(msg) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            tokens.append(token)
    return tokens

#preprocessing
def preprocess(msg):
    #tokenize; return list of tokens
    tokens = [tokenize(msg)]
    #create a bag of words
    dictionary = gensim.corpora.Dictionary(tokens)
    bow = [dictionary.doc2bow(doc) for doc in tokens]
    return bow,dictionary

def model_processing():
    with open('2196073673808423-post.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                colnames = ",".join(row)
        #            print(f'Column names are {", ".join(row)}')
        #            print(colnames)
                line_count += 1
            else:
                text = row[3]
                line_count += 1

    bow,dictionary = preprocess(text)
    lda_model =  gensim.models.LdaMulticore(bow, num_topics = 1, id2word = dictionary, passes = 4, workers = 2)

    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")
    return 0

if __name__ == '__main__':
    freeze_support()
    Process(target=model_processing).start()
    
