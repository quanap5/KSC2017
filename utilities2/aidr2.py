#!/usr/bin/python
#!/usr/bin/env python
from __future__ import absolute_import
from six.moves import cPickle
import gzip
import random
import numpy as np

import glob, os, csv, re
from collections import Counter

########################################
##Quan sua lai cho fan loadAndUsingmodel
########################################
def load_and_numberize_data2(input_, path="../data/", nb_words=None, maxlen=None, seed=113, start_char=1, oov_char=2, index_from=3, init_type="random", embfile=None, validate_train_merge=0, map_labels_to_five_class=0):

    """ numberize the train, validate and test files """

    # Read the vocab from the entire corpus (train + test + validate)
    vocab = Counter() #Counter  tool is used to support convenient and rapid tallies(kiem ke)

    # Quan them vao--------------------
    sentences_newinput  = []
    
    # Quan them vao--------------------

    for filename in glob.glob(os.path.join(path, '*.csv')):
        #print "Reading vocabulary from" + filename
        reader  = csv.reader(open(filename, 'rb'))
	#print (filename)
        for rowid, row in enumerate (reader):
            if rowid == 0: #header
                continue

#            if re.search("newinput.csv", filename.lower()):    
#                sentences_newinput.append(row[1])
#		print "******: " + row[1] + str(type(row[1])) 
                 


            for wrd in row[1].split(): #tallies all word from training, test and validate
                vocab[wrd] += 1 #Counter({'blue': 3, 'red': 2, 'green': 1})
#		#print len(vocab)

    #for rowid, row in enumerate (input_):
    row=input_        
    sentences_newinput.append(row)
    print "******: " + row + str(type(row))
    for wrd in row.split(): #tallies all word from training, test and validate
	     vocab[wrd] += 1 #Counter({'blue': 3, 'red': 2, 'green': 1})

    print "number of Tweet of INPUT: "+ str (len(sentences_newinput)) #Quan them vao--------------------
    print "Total vocabulary size: " + str (len(vocab))

    if nb_words is None: # now take a fraction
        nb_words = len(vocab)
	print "Keep all vocabluray 100 % =" + str (len(vocab)) #Quan sua vao  
    else:
        pr_perc  = nb_words
        nb_words = int ( len(vocab) * (nb_words / 100.0) ) 
	print "Pruned vocabulary size: " + str (pr_perc) + "% =" + str (len(vocab)) #Quan sua vao  

    vocab = dict (vocab.most_common(nb_words)) # most common word in vocab

    #print "Pruned vocabulary size: " + str (pr_perc) + "% =" + str (len(vocab)) #Quan sua sao

    #Create vocab dictionary that maps word to ID
    vocab_list = vocab.keys()                  #key vocabulary
    vocab_idmap = {}                           #vocabulary--> ID using dict
    for i in range(len(vocab_list)):
        vocab_idmap[vocab_list[i]] = i         #{'blue': 0, 'green': 1, 'red': 2}

    # Numberize the sentences

    X_newinput  = numberize_sentences(sentences_newinput,  vocab_idmap, oov_char=oov_char) #Quan them vao--------------------


   #randomly shuffle the training data

    print("Random seed", str(seed))
    np.random.seed(seed)



    X_newinput = adjust_index(X_newinput,  start_char=start_char, index_from=index_from, maxlen=maxlen)

 
    # load the embeddeings
#    if init_type.lower() != "random" and embfile:
#        E = load_emb(embfile, vocab_idmap, index_from)
#    else:
#        E = None

    #print E[0]   #quan them vao
    return X_newinput

def remap_labels(y, merge_labels=None):

    if not merge_labels:
        return y

    y_modified = []
    for alabel in y:
        if merge_labels.has_key(alabel):
            y_modified.append(merge_labels[alabel])
        else:
            y_modified.append(alabel)
    #print y_modified #quan them vao remap label
    return y_modified        


def load_emb(embfile, vocab_idmap, index_from=3, start_char=1, oov_char=2, padding_char=0, vec_size=200):#--quan sua 300-->200
    """ load the word embeddings """

    #print "Loading pre-trained word2vec embeddings......"
    print "LOADING PRE_TRAINING EMBEDDING WORD..."

    if embfile.endswith(".gz"):
        f = gzip.open(embfile, 'rb')
    else:
        f = open(embfile, 'rb')

    vec_size_got = int ( f.readline().strip().split()[1]) # read the header to get vec dim

    if vec_size_got != vec_size:
        print " vector size provided and found in the file don't match!!!"
        raw_input(' ')
        exit(1)

    # load Embedding matrix
    row_nb = index_from+len(vocab_idmap)    
    E      = 0.01 * np.random.uniform( -1.0, 1.0, (row_nb, vec_size) )
    #print E #quan them vao

    wrd_found = {}


    #fo = open("reduced_crisis_emb.txt", "rw+")
    #fo.write("300000 300\n")	
    #test = 0
    for line in f: # read from the emb file
        all_ent   = line.split()
	#print(all_ent)
        word, vec = all_ent[0].lower(), map (float, all_ent[1:]) #map word and id word
	#print word, vec #quan them vao
        if vocab_idmap.has_key(word):
            wrd_found[word] = 1 
            wid    = vocab_idmap[word] + index_from
            #print wid #quan them vao
            #print vec  #quan them vao
            E[wid] = np.array(vec)
	    #test = test + 1
	    #write to tmp file
	    #fo.write(line)
    #print(test)
    #fo.close()
    f.close()
    print "Number of words found in emb matrix: " + str (len (wrd_found)) + " of " + str (len(vocab_idmap))
    print E.shape #quan them vao
    return E        




def adjust_index(X, start_char=1, index_from=3, maxlen=None):

    # by convention, use 2 as OOV word
    # reserve 'index_from' (=3 by default) characters: 0 (padding), 1 (start), 2 (OOV)
    if start_char is not None: # add start of sentence char
        X = [[start_char] + [w + index_from for w in x] for x in X] # shift the ids to index_from; id 3 will be shifted to 3+index_from
    elif index_from:
        X = [[w + index_from for w in x] for x in X]

    if maxlen: # exclude tweets that are larger than maxlen
        new_X = []
       
        for x in zip(X):
            if len(x) < maxlen:
                new_X.append(x)
                

        X      = new_X
       
    #print X    #quan them vao
    #print labels  #quan them vao
    return X    


def numberize_sentences(sentences, vocab_idmap, oov_char=2):  

    sentences_id=[]  

    for sid, sent in enumerate (sentences):
        tmp_list = []
        for wrd in sent.split():
            wrd_id = vocab_idmap[wrd] if vocab_idmap.has_key(wrd) else oov_char 
            tmp_list.append(wrd_id)

        sentences_id.append(tmp_list)
	#print sentences_id #quan them vao

    return sentences_id    


def numberize_labels(all_str_label, label_id_map):

    label_cnt = {}
    labels    = []
    
    for a_label in all_str_label:
        labels.append(label_id_map[a_label])

        if label_cnt.has_key(a_label):
            label_cnt[a_label] += 1
        else:
            label_cnt[a_label] = 1    
    #print labels    #quan them vao
    #print label_cnt  #quan them vao
    return (labels, label_cnt)        



def get_label(str_label):
    if  str_label == "informative":
        return 1
    elif str_label == "not informative":
        return 0
    else:
        print "Error!!! unknown label " + str_label
        exit(1)        


def load_data(path="imdb.pkl", nb_words=None, skip_top=0, maxlen=None, test_split=0.2, seed=113,
              start_char=1, oov_char=2, index_from=3):


    if path.endswith(".gz"):
        f = gzip.open(path, 'rb')
    else:
        f = open(path, 'rb')

    X, labels = cPickle.load(f)
    f.close()


    np.random.seed(seed)
    np.random.shuffle(X)
    np.random.seed(seed)
    np.random.shuffle(labels)

    if start_char is not None:
        X = [[start_char] + [w + index_from for w in x] for x in X]
    elif index_from:
        X = [[w + index_from for w in x] for x in X]

    if maxlen:
        new_X = []
        
        for x in zip(X):
            if len(x) < maxlen:
                new_X.append(x)
                
        X = new_X
        

    if not nb_words:
        nb_words = max([max(x) for x in X])


    # by convention, use 2 as OOV word
    # reserve 'index_from' (=3 by default) characters: 0 (padding), 1 (start), 2 (OOV)
    if oov_char is not None:
        X = [[oov_char if (w >= nb_words or w < skip_top) else w for w in x] for x in X]
    else:
        nX = []
        for x in X:
            nx = []
            for w in x:
                if (w >= nb_words or w < skip_top):
                    nx.append(w)
            nX.append(nx)
        X = nX



    X_newinput = X[int(len(X)*(1-test_split)):]
    return X_newinput
