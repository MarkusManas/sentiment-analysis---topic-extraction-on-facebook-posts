import csv
import gensim
import re
from multiprocessing import Process, freeze_support
from gensim.test.utils import common_corpus, common_dictionary

#tokenize function
def tokenize(msg):
    tokens = []
    for token in gensim.utils.simple_preprocess(msg) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            tokens.append(token)
    for token in tokens:
        if len(token) <= 3:
            tokens.remove(token)
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
    
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")   

    return lda_model
def model_processing(text):
    freeze_support()
    
    bow,dictionary = preprocess(text)
    lda_model =  gensim.models.ldamodel.LdaModel(bow, num_topics = 3, id2word = dictionary, passes = 4, random_state=1)
    
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")         
   
    return lda_model

if __name__ == '__main__':
    freeze_support()
    #x = "Happy Birthday PRRD!  DA COMMISSIONS SIGNAL 5 TYPHOON-RESISTANT DOME  By Manny Piñol  Iguig, Cagayan - The days when government spends hundreds of millions of pesos to repair buildings and warehouses after the devastation by typhoons will soon be over.  The Department of Agriculture (DA) yesterday inaugurated and commissioned the first monolithic dome which will serve as a grains warehouse in the DA Experimental Station in Iguig town Cagayan Province.  Designed by German engineers, the first monolithic dome constructed by a Filipino company with Polish engineers as consultants could withstand Typhoon Signal 5 many of which previously devastated many DA buildings and warehouses in the Cagayan Valley Region.  I flew to Cagayan Province  yesterday shortly after arriving from a 4-day marketing promotions trip to Belarus and Russia over the weekend to commission the first-ever monolithic dome constructed by the DA.  Costing P10-M and constructed in record time, the monolithic dome is impressive indeed.  While the temperature outside when I arrived at 3:30 p.m. was a scorching 36C degrees, it was only 21C  inside the Monolithic Dome.  The Polish engineers told me that the dome has insulators which deflects the heat of the sun and keeps the interior temperature at levels ideal for grains storage.  DA Cagayan Valley Director Narciso Edillo said the Iguig Monolithic Dome is the first of 8 units to be established in the region which is hit by as much as 12 typhoons every year.   Seven other smaller units costing P5-M each are now being constructed for farmers' groups in Cagayan Valley Region.  When the Monolithic Domes are tested and proven to withstand the destructive power of typhoons, similar structures will be built in other areas located on the path of typhoons.  These areas include Eastern and Western Visayas, Bicol, Southern Tagalog including Mindoro, Central Luzon, Ilocos and Cordillera Regions.  Yesterday during the commissioning, I said it was our fitting birthday gift to President Rody Duterte to support his goal of making life better for the people.  This innovation, along with the National Color-Coded Agriculture Guide Map, the Solar-Powered Irrigation and many more, will make Philippine Agriculture Climate Change Resilient.  #NeverStopDreaming! #NeverStopBelieving! #KungGustoMaramingParaan! #BukasMayUmagangDarating!  (Photos by Mayette Tudlas)"
    #res = model_processing(x)