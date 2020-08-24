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
    flag = True
    token_dep = list()
    token_pos = list()
    print(' ')
    print('this is entire doc',doc)
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

    for el in token_dep: #set semantic depth for doc
        if 'ROOT' in el and flag:
            ROOT = True
            #print('ROOOOOOOOOOOOOOOOOT')
            doc = nlp(el[1])
            for t in doc:
                print(t.pos_)
                if t.pos_ == 'ADP' or t.pos_ == 'CONJ' or t.pos_ == 'ADJ' or t.pos_ == 'VERB': ##keep in mind that as adj can be good ????!!!!!
                    #print('bad root')
                    print('root position', t.pos_)
                    ROOT = False
                    break
            if ROOT:
                root_text.append(el[1])
                flag = False
        if 'nsubj' in el:
            nsubj = True
            doc = nlp(el[1])
            for t in doc:
                if t.pos_ == 'ADP' or t.pos_ == 'CONJ' or t.pos_ == 'ADJ' :
                    print('bad nsubj')
                    nsubj = False   
                    break
            if nsubj:
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
        if 'dobj' in el:
            compound = True
            compound_text.append(el[1])
        if 'nmod' in el:
            compound = True
            compound_text.append(el[1])

    for pos in token_pos: ## set semantic position for doc
        if 'NOUN' in pos:
            if pos[1] not in root_text and pos[1] not in noun_text:
                noun_text.append(pos[1])
                NOUN = True
                tokens.append(pos[1])
            continue

        if 'PROPN' in pos:
            if pos[1] not in root_text and pos[1] not in propn_text:
                propn_text.append(pos[1])
                tokens.append(pos[1])
                PROPN = True
               
            continue

        if 'ADJ' in pos:
            if pos[1] not in root_text and pos[1] not in propn_text:
                adj_text.append(pos[1]) 
                ADJ =  True
                tokens.append(pos[1])
            continue
        if 'VERB' in pos:
            VERB = True
            verb_text.append(pos[1])
            continue
    

    print('this is root', ROOT, '== ', root_text , 'and compound', compound, 'and nsujb',nsubj )

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

    if ROOT and compound:
        print('root and compounddddddddddddddddddddddddddddddddddd')
        if NOUN and ROOT:
            print('noun and root and compound')
            counter_elimation = 0
            sorted_noun  = spacy_closest(noun_text, vec(root_text[0]), len(noun_text))
            sorted_adj  = spacy_closest(adj_text, vec(root_text[0]) , len(adj_text))
            sorted_propn = spacy_closest(propn_text, sentvec(root_text[0]+' '+sorted_noun[0]), len(propn_text))
            if len(noun_text) >= 2:
                counter_elimation = int(len(noun_text)/2) 
                print('elimination number for noun and root', counter_elimation)
            temp_sorted_noun = sorted_noun[0:(len(sorted_noun)-counter_elimation)]
            print('this is sorted noun', temp_sorted_noun)
            if root_text[0] in sorted_noun:
                print('noun root solo', temp_sorted_noun)
            else:
                temp_sorted_noun.append(root_text[0])
                print('noun root solutions' ,temp_sorted_noun)
            if sorted_propn:
                temp_sorted_noun.append(sorted_propn[0])
                print('root noun propn options', temp_sorted_noun)
                return ' '.join(temp_sorted_noun)
            return ' '.join(temp_sorted_noun)

            
        if PROPN and ROOT:
            print('propn and root and compound')
            counter_elimation = 0
            sorted_propn  = spacy_closest(propn_text, vec(root_text[0]), len(propn_text))
            sorted_adj  = spacy_closest(adj_text, vec(root_text[0]),len(adj_text))
            print('this is sorted propn', sorted_propn)
            print('this is sorted adj', sorted_adj)
            if len(propn_text) >= 2:
                counter_elimation = int(len(propn_text)/2) 
                print('elimination number for noun and root', counter_elimation)
            temp_propn = sorted_propn[0:(len(sorted_propn)-counter_elimation)] 
            #if sorted_adj:
                #propn_adj = spacy_closest(sorted_adj,sentvec(''.join(sorted_propn[0:(len(sorted_propn)-counter_elimation)])), len(sorted_adj))
                #print('this is sorted adj for root and propn', propn_adj)
                #temp_propn.append(propn_adj[0])

            if root_text[0] in sorted_propn:
                print('propn root solution' ,temp_propn)
                return ' '.join(temp_propn)
            else:
                temp_propn.append(root_text[0])
                print('proprn root soltuion with root ' ,temp_propn)
                return ' '.join(temp_propn)
        else:
             return root_text[0]+' '+compound_text[0]   
    if nsubj and compound:
        list_compound = spacy_closest(compound_text, vec(nsubj_text[0]), len(compound_text))
        print('only nsubj plus compound', nsubj_text)
        counter_elimation = 0
        if len(tokens) >= 3:
            counter_elimation = int(len(tokens)/2) 
            print('elimination number', counter_elimation)
        if nsubj_text[0] in list_compound[0:(len(list_compound)-counter_elimation)]:
            print('nsubj in compound ')
            return ' '.join(list_compound[0:(len(list_compound)-counter_elimation)])
        else:
            print( 'using tokensssss and nsubjsss' , nsubj_text[0]+' '+' '.join(list_compound[0:(len(list_compound)-counter_elimation)]))
            return  nsubj_text[0]+' '+' '.join(list_compound[0:(len(list_compound)-counter_elimation)])

        
    
    if nsubj or ROOT or compound:
        if ROOT and nsubj:
            print('rooT AND nsubj')
            if bool(tokens):
                sort_tokens = spacy_closest(tokens, sentvec(root_text[0]+' '+nsubj_text[0]), len(tokens))
                if sort_tokens[0] != root_text[0] and sort_tokens[0] != nsubj_text[0]:
                    return root_text[0]+' '+nsubj_text[0]+' '+sort_tokens[0]
            return root_text[0]+' '+nsubj_text[0]
        if nsubj:
            print('nusbjjjjjjjjjjjjjjjjjjjj')
            sort_tokens = spacy_closest(tokens, vec(nsubj_text[0]), len(tokens)) 
            if sort_tokens:
                if sort_tokens[0] != nsubj_text[0]:
                    return nsubj_text[0]+' '+sort_tokens[0]
                else:
                    return nsubj_text[0]
            else:
                return nsubj_text[0]
        if compound:       
            print('only compounddd')
            if len(compound_text) > 3:
                counter_elimation = int(len(compound_text)/2) 
                print('elimination number', counter_elimation)
            print('tokens', tokens)
            if bool(tokens):
                temp = spacy_closest(compound_text, sentvec(' '.join(tokens)), len(compound_text))
            else:
                return compound_text[0]
            print('compound temp', temp)
            if len(temp) > 1:
                return temp[0]+' '+temp[1]
            else:
                return temp[0]
        else:
            return root_text[0]
    
    print('WAS NOT ENOUGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
    return 'None'