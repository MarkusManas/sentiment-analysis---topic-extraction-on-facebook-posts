import csv
import gensim
import re
from multiprocessing import Process, freeze_support
from gensim.test.utils import common_corpus, common_dictionary

tagalogStopwords = [
    "dito", "bawal", "lang", "diyan", "hindi", "yang", "naman", "paano", "paanu", "para", "bakit",
    "niyo", "niya", "nila", "mong", "tayo", "sila", "kayo", "kami", "kapa", "paki"
]
#tokenize function
def topicTok(msg):
    global tagalogStopwords
    msg= msg.lower()

    tokens = []
    for token in gensim.utils.simple_preprocess(msg) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            tokens.append(token)
    toBeDeleted = []
    for token in tokens:
        if len(token) <= 3:
            toBeDeleted.append(token)
    for dels in toBeDeleted:
        tokens.remove(dels)
    toBeDeleted = []
    for token in tokens:
        if token in tagalogStopwords:
            toBeDeleted.append(token)
    for dels in toBeDeleted:
        tokens.remove(dels)
    return tokens

def tokenize(msg):
    msg= msg.lower()
    tokens = []
    for token in gensim.utils.simple_preprocess(msg) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            tokens.append(token)
    toBeDeleted = []
    for token in tokens:
        if len(token) <= 3:
            toBeDeleted.append(token)
    for dels in toBeDeleted:
        tokens.remove(dels)
    return tokens

#preprocessing
def preprocess(msg):
    #tokenize; return list of tokens
    tokens = [tokenize(msg)]
    #create a bag of words
    dictionary = gensim.corpora.Dictionary(tokens)
    bow = [dictionary.doc2bow(doc) for doc in tokens]
    return bow,dictionary

def multi_process(docs):
    freeze_support()
    tokens = []
    for doc in docs:
        tokens.append(tokenize(doc))
    dictionary = gensim.corpora.Dictionary(tokens)
    bow = [dictionary.doc2bow(doc) for doc in tokens]
    lda_model =  gensim.models.ldamodel.LdaModel(bow, num_topics = 3, id2word = dictionary, passes = 4, random_state=1)
    '''
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")   
    '''
    return lda_model
def model_processing(text):
    freeze_support()
    
    bow,dictionary = preprocess(text)
    lda_model =  gensim.models.ldamodel.LdaModel(bow, num_topics = 3, id2word = dictionary, passes = 4, random_state=1)
    '''
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")         
   '''
    return lda_model

if __name__ == '__main__':
    freeze_support()
    #x = "Tale of two rich Tugades!  THE CABSEC IS A BILLIONAIRE; FARMER HAS HEART OF GOLD  On Friday, in a remote village in Kabacan town, North Cotabato, I met a farmer with a heart of gold named Rolando Tugade.  Farmer Tugade has a 40-hectare property with a small lake which he turned into a small water impounding system to irrigate 50 hectares of his neighbours rice farms.  He has also allowed 30 families belonging to the Blaan tribe displaced by the conflict to stay and farm in his area without getting any share from the crops.  When I told him that he could be related to my friend, Transportation Secretary Arthur Tugade, he bowed his head apparently humbled.  \"Mayaman man yon Sir. Mahiya man tayo magsabi na kamag-anak natin yon,\" Rolly Tugade said.  Indeed, Sec. Tugade is rich. In fact, he is among the richest members of the Cabinet including Public Works Secretary Mark Villar and Finance Secretary Carlos G. Dominguez.  But I told farmer Tugade that he could actually be richer than the Transportation Secretary because he has a heart of gold.  I told Rolly Tugade that I will inform the Transportation Secretary that he has relatives in my province he could truly be proud of.  @ArtTugade. Boss, ang bait ng kamaganak mo.  (File photo of Sec. Tugade downloaded from public website while Rolly Tugade's photo was taken by DA AFID)"
    #res = model_processing(x)