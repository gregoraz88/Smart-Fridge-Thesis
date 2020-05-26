import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
import en_core_web_sm
import spacy
from spacy.tokens import Doc,Span,Token
from spacy.matcher import Matcher
from numpy import dot
from numpy.linalg import norm
import numpy as np
import random
from nltk.corpus import stopwords
from functools import reduce 



nlp = spacy.load('en_core_web_md')

def cosine(v1, v2):
    if norm(v1) > 0 and norm(v2) > 0:
        return dot(v1, v2) / (norm(v1) * norm(v2))
    else:
        return 0.0

def spacy_closest(token_list, vec_to_check, n):
    return sorted(token_list,
                  key=lambda x: cosine(vec_to_check, vec(x)),
                  reverse=True)[:n]

def vec(s):
    return nlp.vocab[s].vector

def meanv(coords):
    sumv = [0] * len(coords[0])
    for item in coords:
        for i in range(len(item)):
            sumv[i] += item[i]
    mean = [0] * len(sumv)
    for i in range(len(sumv)):
        mean[i] = float(sumv[i]) / len(coords)
    return mean

def sentvec(s):
    sent = nlp(s)
    return meanv([w.vector for w in sent])

counter =  0
def parse_semantic(not_doc):
    doc = nlp(not_doc)
    entity = False
    ROOT = False
    NOUN = False
    PROPN = False
    ADJ = False
    VERB = False
    nsubj = False
    compound = False
    token_dep = list()
    token_pos = list()
    print(' ')
    print('this is entire doc',doc)
    # print('this is entyty: ', doc.ents, 'of doc ', doc)
    token_dep = list([[t.dep_,t.text] for t in doc])
    token_pos =list([[t.pos_, t.text]for t in doc])
    tokens = list()
    print(token_dep)
    print(token_pos)
    replacement = ''
    root_text = list()
    noun_text = list()
    adj_text = list()
    propn_text = list()
    verb_text  =list()
    nsubj_text = list()
    compound_text = list()
    if doc.ents: ## check entity exsitance
        entity = True
        entity_text = str((doc.ents)[0])
    else:
        entity =  False
    for pos in token_pos: ## set semantic position for doc
    # print('this is pos', pos)
        if 'NOUN' in pos:
            NOUN = True
            noun_text.append(pos[1])
            tokens.append(pos[1])
            continue

        if 'PROPN' in pos:
            PROPN = True
            propn_text.append(pos[1])
            tokens.append(pos[1])
            continue

        if 'ADJ' in pos:
            ADJ =  True
            adj_text.append(pos[1]) 
            tokens.append(pos[1])
            continue
        if 'VERB' in pos:
            VERB = True
            verb_text.append(pos[1])
            continue
    for el in token_dep: #set semantic depth for doc
        if 'ROOT' in el:
            ROOT = True
            print('ROOOOOOOOOOOOOOOOOT')
            #if el[1] in verb_text and el[1] != 'paste': ##check if root is like a conjuction or and ADP or SPACE
            #    print('ROOT IS A VERB')
            #    ROOT = False
            doc = nlp(el[1])
            for t in doc:
                if t.pos_ == 'ADP' or t.pos_ == 'CONJ':
                    print('bad root')
                    ROOT = False
                    break
            if ROOT:
                root_text.append(el[1])
        if 'nsubj' in el:
            nsubj = True
            nsubj_text.append(el[1])
        if 'compound' in el:
            compound = True
            compound_text.append(el[1])
        if 'amod' in el:
            compound = True
            compound_text.append(el[1])
        if 'xcomp' in el:
            compound = True
            compound_text.append(el[1])
        if 'pobj' in el:
            compound = True
            compound_text.append(el[1])
        if 'dep' in el:
            compound = True
            compound_text.append(el[1])

    print('this is root', ROOT, '== ', root_text , 'and compound', compound, 'and nsujb',nsubj )

    if ROOT and entity: ##if root and entity similar return only entity, there is no neeed to return semantic
        for r in root_text:
            if r in entity_text and r != entity_text:
                print('GOODDDD ROOT AND ENTITY')
                replacement = entity_text
                print('this replacement', replacement)
                return replacement
            else:
                continue
    
    if ROOT and nsubj and compound:
        print('root and  nsubjjjjjjjjjjjjjjjjjjjjjjjj')
        nsubj_sorted  = spacy_closest(nsubj_text,vec(root_text[0]), len(nsubj_text))
        compound_sorted = spacy_closest(compound_text, vec(root_text[0]), len(compound_text))
        print('sorted subj', nsubj_sorted, 'for root' , root_text[0])
        print('sorted compound', compound_sorted, 'for root' , root_text[0])
        sorted_compound_all = spacy_closest(compound_sorted, sentvec(nsubj_sorted[0]+' '+root_text[0]), len(compound_sorted))
        print('compound sorted ' , sorted_compound_all , 'on nsbuj', nsubj_sorted[0], 'on root', root_text[0])
        if sorted_compound_all:
            print('also compounddd')
            return root_text[0]+' '+nsubj_sorted[0]+' '+sorted_compound_all[0]
        else:
            return root_text[0]+' '+nsubj_sorted[0]
        #sorted_all = spacy_closet(nsubj_sorted+compound_sorted)

    if ROOT and compound:
        print('root and compounddddddddddddddddddddddddddddddddddd')
        counter_elimation = 0
        if len(tokens) > 3:
            counter_elimation = int(len(compound_text)/2) 
            print('elimination number', counter_elimation)

        list_compound = spacy_closest(compound_text, vec(root_text[0]), len(compound_text))
        print('full compound list'  ,list_compound)
        print('filtered list' , ' '.join(list_compound[0:(len(list_compound)-counter_elimation)]))
        return root_text[0]+' '+' '.join(list_compound[0:(len(list_compound)-counter_elimation)])
   
    if nsubj and compound:
        list_compound = spacy_closest(compound_text, vec(nsubj_text[0]), len(compound_text))
        print('only nsubj plus compound', nsubj_text)
        counter_elimation = 0
        if len(compound_text) > 3:
            counter_elimation = int(len(compound_text)/2) 
            print('elimination number', counter_elimation)
        return nsubj_text[0]+' '.join(list_compound[0:(len(list_compound)-counter_elimation)])
    
    if nsubj or ROOT or compound:
        if ROOT and nsubj:
            print('rooT AND nsubj')
            return root_text[0]+' '+nsubj_text[0]
        if nsubj:
            print('nusbjjjjjjjjjjjjjjjjjjjj')
            return nsubj_text[0]
        if compound:
            return compound_text[0]+' '+compound_text[1]
        else:
            return root_text[0]
    
    print('WAS NOT ENOUGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
    return None
  
    #return ' '.join( return_semantic(NOUN,PROPN,ADJ,ROOT,noun_text,propn_text,adj_text,root_text)) #return semantic

def return_semantic(NOUN,PROPN,ADJ,ROOT,noun_text,propn_text,adj_text,root_text):
##check for the root, if root is a verb do not take into consideration
    counter += 1
    print('this is counter' ,counter)

    print('semanticccccccccccccccccccccccccccccccccccccccccc')
    counter_elimation = 0
    options = list()
    if NOUN and ROOT:
        sorted_noun  = spacy_closest(noun_text, vec(root_text[0]), len(noun_text))
        sorted_adj  = spacy_closest(adj_text, vec(root_text[0]) , len(adj_text))
        if len(sorted_noun) > 3:
            counter_elimation = int(len(sorted_noun)/2) 
            print('elimination number for noun and root', counter_elimation)
        print('this is sorted noun', sorted_noun)
        temp_sorted_noun = sorted_noun[0:(len(sorted_noun)-counter_elimation)]

        if sorted_adj:
            noun_adj = spacy_closest( sorted_adj,sentvec(''.join(sorted_noun[0:(len(sorted_noun)-counter_elimation)])),len(sorted_adj) )
            temp_sorted_noun.append(noun_adj[0])
            print('this is sorted adj for root and noun', temp_sorted_noun)
        if root_text[0] in sorted_noun:
            return temp_sorted_noun
        else:
            temp_sorted_noun.append(root_text[0])
            return temp_sorted_noun
        
    if PROPN and ROOT:
        sorted_propn  = spacy_closest(propn_text, vec(root_text[0]), len(propn_text))
        sorted_adj  = spacy_closest(adj_text, vec(root_text[0]),len(adj_text))
        print('this is sorted propn', sorted_propn)
        print('this is sorted adj', sorted_adj)
        if len(sorted_propn) > 3:
            counter_elimation = int(len(sorted_propn)/2) 
            print('elimination number for noun and root', counter_elimation)
        temp_propn = sorted_propn[0:(len(sorted_propn)-counter_elimation)] 
        if sorted_adj:
            propn_adj = spacy_closest(sorted_adj,sentvec(''.join(sorted_propn[0:(len(sorted_propn)-counter_elimation)])), len(sorted_adj))
            print('this is sorted adj for root and propn', propn_adj)
            temp_propn.append(propn_adj[0])

        if root_text[0] in sorted_propn:
            return temp_propn
        else:
            temp_propn.append(root_text[0])
            return temp_propn
            
    if NOUN and ADJ == False :
        print('going double noun')
        n1 = ''
        n2  =''
        n1_aCosine=  0
        for n in noun_text:
            for n1 in noun_text:
                print('this is cosine between nouns',cosine(vec(n),vec(n1)) , 'n ', n , 'n1 ', n1)
                if cosine(vec(n),vec(n1)) > n1_aCosine and n != n1:
                    n1 = n
                    n2 = n1
                    n1_aCosine = cosine(vec(n),vec(n1))
                else:
                    continue
        if n1 and n2:
            options.append(n1+' '+n2)
            print('this is options ', options)
            return options
        else:
            options.append(n1)
            print('bad noumsss')
            return options

        
    if NOUN and ADJ:
        adj = ''
        noun = ''
        print('noun , adj')
        for n in noun_text:
            sorted_adj = spacy_closest(adj_text,vec(n), len(adj_text))
            print('this is sorted', sorted_adj, 'for noun', n)
        exit()
        n_aCosine = 0
        for n in noun_text:
            for a in adj_text:
                if cosine(vec(n),vec(a)) > n_aCosine and cosine(vec(n),vec(a)) < 0.95:
                    noun = n
                    adj = a
                    n_aCosine = cosine(vec(n),vec(a))
                else:
                    continue
        if noun and adj:
            options.append(adj+' '+noun)
            print('this is options ', options)
            return options
        else:
            print('going double noun')
            n1 = ''
            n2  =''
            n1_aCosine=  0
            for n in noun_text:
                for n1 in noun_text:
                    if cosine(vec(n),vec(n1)) > n1_aCosine and cosine(vec(n),vec(n1)) < 0.95:
                        n1 = n
                        n2 = n1
                        n1_aCosine = cosine(vec(n),vec(n1))
                    else:
                        continue
            if n1 and n2:
                options.append(n1+' '+n2)
                print('this is options ', options)
                return options
            else:
                print('bad noumsss')
                return None
    if PROPN:
        print('only propnsssssss')
        print('need to chcek this')
        options.append(propn_text[0])
        return options
    if ROOT:
        print('rooting only')
        options.append(root_text[0])
        return options

    print('this is a bad items')
    options.append('None')
    return options