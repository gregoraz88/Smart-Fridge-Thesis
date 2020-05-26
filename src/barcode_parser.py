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
from process_syntax import parse_semantic
import itertools
nlp = spacy.load('en_core_web_md')



def meanv(coords):
    sumv = [0] * len(coords[0]) ##check for error here - there is no index zero so no element is passsed, it s an indexerrro
    for item in coords:
        for i in range(len(item)):
            sumv[i] += item[i]
    mean = [0] * len(sumv)
    for i in range(len(sumv)):
        mean[i] = float(sumv[i]) / len(coords)
    return mean

def CountVectorizer_special_recipe(chunck):
    cv2=CountVectorizer(analyzer = 'word' ,stop_words = 'english', lowercase = True , ngram_range=(1,2))
    for x in chunck:
        if  x not in stopwords.words('english'):
                word_count_vector2=cv2.fit_transform(chunck)
                v2 = cv2.get_feature_names()
                return v2
        else:
            continue
    return None

def generate_ngrams(words_list, n):
    ngrams_list = []
    for num in range(0, len(words_list)):
        ngram = ' '.join(words_list[num:num + n])
        ngrams_list.append(ngram)

    return ngrams_list

def cosine(v1, v2):
    if norm(v1) > 0 and norm(v2) > 0:
        return dot(v1, v2) / (norm(v1) * norm(v2))
    else:
        return 0.0

def spacy_closest(token_list, vec_to_check, n):
    print('vec to cechk', vec_to_check)
    return sorted(token_list,
                  key=lambda x: cosine(vec_to_check, vec(x)),
                  reverse=True)[:n]

def vec(s):
    return nlp.vocab[s].vector

def sentvec(s): ##raise error: IndexError in meanv function call c
    sent = nlp(s)
    return meanv([w.vector for w in sent])



def spacy_closest_sent(space, input_str, n=10):
    print('input string', input_str)
    input_vec = sentvec(input_str)
    return sorted(space,
                  key=lambda x: cosine(np.mean([w.vector for w in x], axis=0), input_vec),
                  reverse=True)[:n]

def sample_n_barcode(n):
    path = 'C:/Users/gregh/Desktop/thesis/Smart-Fridge-Thesis/barcode_data'
    barcode_file_path = 'translated_barcode.json'
    with open(path + '/' + barcode_file_path) as json_file:
        barcode_data = json.load(json_file)
    dictionary = random.sample(barcode_data.items(),n)
    # dictionary = dict(zip(barcodes, ingredients)) ##
    fridge_list = list()
    fridge_list_vec = list()
    for barcode, ingredient in dict(dictionary).items():#ingredient - list(ingredient,quantity)
        cleaned_fridge_ingredients = re.sub(r"[^A-Za-z()]", " ", ingredient[0])
        try:
            vector = CountVectorizer_special_recipe(cleaned_fridge_ingredients.split(' '))
        except ValueError:
                    print('empty vocabulary')
                    continue
        if not vector:
            print('this is empty vector',vector)
            continue
        temp_fridge = ' '.join(vector)
        ##delete some redundant and useless info from barcode 
        temp_fridge = temp_fridge.replace('albert','')
        temp_fridge = temp_fridge.replace('heijn','')
        temp_fridge = temp_fridge.replace('ah','')
        temp_fridge = temp_fridge.replace('jumbo','')
        temp_fridge = temp_fridge.replace('ekoplaza','')
        temp_fridge = temp_fridge.replace('hellmann','')
        temp_fridge =  temp_fridge.replace('hema','')
        if temp_fridge and temp_fridge != ' ':
            #doc = nlp(temp_fridge)
            temp_fridge  = parse_semantic(temp_fridge)
            print('this is temp fridge', temp_fridge)
            fridge_list.append(temp_fridge.strip())
            fridge_list_vec.append(temp_fridge.split(' '))
            continue
        else:
            print('empty element')
            continue

    print( ' ')
    print('list',fridge_list)
    print('veccc',fridge_list_vec)
    return fridge_list, fridge_list_vec

fridge_list,fridge_list_vec = sample_n_barcode(3)


def Matcher_func(ingre,recipe_doc):
    print('fridge ingrer to compare', ingre)
    matcher = Matcher(nlp.vocab)
    pattern = [{'TEXT': str(ingre)}]
    matcher.add('rule_1', None, pattern)
    matches = matcher(recipe_doc)
    print(matches)

def check_extension(fride_doc, recipe_doc):
    print('this is recipe', recipe_doc)
    for f in fride_doc:
        print('this is fridge',f )
        if f == '':
            continue
        else:
            has_similar_to_fridge = lambda r_obj : any([cosine(sentvec(f),sentvec(r.text))> 0.7 for r in r_obj])
            Doc.set_extension('has_similar_element', getter = has_similar_to_fridge, force = True)
            if recipe_doc._.has_similar_element:
                return True, f , recipe_doc
            else:
                continue
    return False, None , None


#############################
    # #print(sentvec(r))
    #
    # for r in recipe_list:
    #     print(r)
    # for  f in fridge:
    #     print(f)
    # for i in range(0,len(fridge)):
    #     for j in range(0,len(recipe_list)):
    #         print('this is cosine for fridge el',fridge[i], 'and recipe ingredient' , recipe_list[j], cosine(vec(fridge[i]), vec(recipe_list[j])))
    # exit()
    # print(recipe_doc)
    # recipe_sent = list(recipe_doc.sents)
        ####print(temp_fridge)
    #fridge_list,fridge_list_vec = sample_n_barcode(10)
# ##############################
# for x in doc:
#     #print(sentvec(x))
#     exit()
# sentences = doc.sents
# print(list(sentences))
# exit()
# for x in sentences:
#     print(x)
# temp_x = list()
# sents = list()
# # for x in sentences:
# #     if flag == True and str(x).endswith('.') :
# #         print('this is the constructed sent')
# #         t =''
# #         for y in temp_x:
# #             t = t + str(y)
# #         print(t+str(x))
# #         sents.append(t+str(x))
# #         temp_x = list()
# #         flag = False
# #         continue
# #     if not str(x).endswith('.'):
# #         flag = True
# #         temp_x.append(str(x))
# #         continue
# #     if str(x).endswith('.') and flag == False:
# #         print('this is a good sent:' ,x)
# #         sents.append(x)
# #         print(' ')
# #         continue
# sentences  = list(sents)
# for sent in spacy_closest_sent(sentences, fridge_list[i]):
#     print (sent.text)
#     print ("---")
# exit()
######################################################
###
def parse_barcodes(dict_of_recipe):
    list_of_recipe = list()
    for recipe_dict in dict_of_recipe:
        list_of_recipe.append((  ( list( itertools.chain.from_iterable( (list(recipe_dict.values())) ) ) ) , str(recipe_dict.keys()) ))
    similar_ingredient = False
    similar_ingredient_ind =list()
    possible_options = list()
    #print(type(recipe_ingredients))
    #print(recipe_ingredients[0])
    #r = ' '.join(recipe_ingredients)
    # doc = nlp(r)
    # for x in recipe_ingredients:
    #     x_doc = nlp(x)
    #     #print('this is doc',x_doc)
    #     break
    #print('this is doc',doc)
    #tokens = list(set([w.text for w in doc if w.is_alpha]))
    #recipe_list = recipe_ingredients.split(' ')
    #print(r[0])
####################################
    # #print(sentvec(r))
    #
    # for r in recipe_list:
    #     print(r)
    # for  f in fridge:
    #     print(f)
    # for i in range(0,len(fridge)):
    #     for j in range(0,len(recipe_list)):
    #         print('this is cosine for fridge el',fridge[i], 'and recipe ingredient' , recipe_list[j], cosine(vec(fridge[i]), vec(recipe_list[j])))
    # exit()
    # print(recipe_doc)
    # recipe_sent = list(recipe_doc.sents)
        ####print(temp_fridge)
    #fridge_list,fridge_list_vec = sample_n_barcode(10)
    fridge_sent = ''.join(fridge_list)
#    print('this is recipe', r)
    flag = False
    if len(fridge_list) > 2:
        for recipe in list_of_recipe: ## recipe contains - [0] -- recipe ingredients [1] -- recipe_id
            recipe_doc = nlp(' '.join(recipe[0]))
            print('doc', recipe_doc)
            if check_extension(fridge_list,recipe_doc)[0]:
                print('EXTENSION TRUE WITH RECIPE', recipe[0])
                recipe_string_list = recipe[0]
                r_id = recipe[1]
                for i in range(0,len(fridge_list)):
                   # print(Matcher_func('pepper',recipe_doc))
                    #continue
                    #reipce_doc_to_check = ' '.join(list_of_recipe)
                    print('fridge el', fridge_list[i])
                    #print(spacy_closest(tokens, vec('milk'),len(tokens)))
                    #exit()
                    #Matcher_func(fridge_list[i],doc)
                    #exit()
                    print(' ')
                    #print('this is cosine between all fridge ingre and all recipe ingre',cosine(sentvec(fridge_sent),sentvec(r)))
                    #print(' ')
                    #print('this is the cosine: ',cosine(sentvec(r), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i])
                    #print(' ')
                    if cosine(sentvec(' '.join(recipe_string_list )), sentvec(fridge_list[i])) > 0.3:
                        print('this is the cosine: ',cosine(sentvec(' '.join(recipe_string_list )), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i],'and recipe ingredient sent ', ' '.join(recipe_string_list ) )
                        for j in range(0,len(fridge_list_vec[i])):
                            if not fridge_list_vec[i][j] or fridge_list_vec[i][j] == '':
                                print('contnueeeeee for fridge', fridge_list_vec[i][j])
                                continue
                            for g in range(0,(len(recipe_string_list))):
                                #print('all listttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt' , recipe_string_list)
                                #print('this is recipe sting list ' , recipe_string_list[g], 'at g ', g)
                                #print('this is cosine for fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_string_list[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])))
                                if cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])) > 0.75: ## when two strings matches we need to work with n-gram model to extract more meaning
                                    similar_ingredient = True
                                    print( ' ')
                                    possible_options.append((i,j,g,r_id))
                                    print('this is cosine n-gram', cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])), 'between fridge' , fridge_list[i], 'and', recipe_string_list[g] )

                                    if cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])) > 0.90:
                                    #before appending need to work with n gram to extracts real meaning -
                                    #
                                        similar_ingredient_ind.append((i,j,g,r_id)) ## here append the indexes of sent_vec similr fridge el, where i - is the list index , j - the string index - r_id - recipe_id
                                        print(' ')
                                        print('this is cosine for inner fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_string_list[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])))
                                        print(' ')
                                else:
                                    continue
                    else:
                        print('value too low for ingre', fridge_list[i])
                        continue

            else:
                print('NO EXTENSION')
                continue

        print(similar_ingredient_ind)
        print(possible_options)
        for output in similar_ingredient_ind:
            i = int(output[0])
            j = int(output[1])
            ingre = int(output[2])
            name = str(output[3])
            print('u have ',fridge_list_vec[i][j], '--full ingredient: ', fridge_list[i] , ' that goes well with recipe ingredient' ,  'at recipe', name)

        for output in possible_options:
            i = int(output[0])
            j = int(output[1])
            ingre = int(output[2])
            name = str(output[3])
            print('there is similarity between fridge ',fridge_list_vec[i][j],'--full ingredient: ', fridge_list[i] , ' that goes well with recipe ingredient' , 'at recipe', name)

        return similar_ingredient,similar_ingredient_ind,fridge_list_vec
    else:
        print('too few ingredients')
        return 0,0,0
    #     for i in range(0,len(fridge_list)):
    #         reipce_doc_to_check = ' '.join(list_of_recipe)
    #         print('fridge el', fridge_list[i])
    #         #print(spacy_closest(tokens, vec('milk'),len(tokens)))
    #         #exit()
    #         #Matcher_func(fridge_list[i],doc)
    #         #exit()
    #         print(' ')
    #         print('this is the cosine: ',cosine(sentvec(r), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i])
    #         print(' ')
    #         if cosine(sentvec(r), sentvec(fridge_list[i])) > 0.8:
    #                 for j in range(0,len(fridge_list_vec[i])):
    #                     for g in range(0,len(recipe_ingredients)):
    #                         print('this is cosine for fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_ingredients[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_ingredients[g])))
    #                         if cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_ingredients[g])) > 0.8:
    #                             similar_ingredient = True
    #                             similar_ingredient_ind.append((i,j))
    #                             print(' ')
    #                             print('this is cosine for inner fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_ingredients[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_ingredients[g])))
    #                             print(' ')
    #     return similar_ingredient,similar_ingredient_ind,fridge_list_vec
    # else:
    #     print('too few ingredients')
