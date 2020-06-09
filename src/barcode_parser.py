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

fridge_list,fridge_list_vec = sample_n_barcode(100)


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


def compareFridge_toRecipeIngre(split_fridge,split_recipe): #return missing element similar element and close element between fridge ingre and recipe ingre
    tempSimilar = list()
    close_temp = list()
    diffFridgeComp = list()
    for r in split_recipe:
        for f in split_fridge:
            print('this is super inner cosine ', cosine(vec(r),vec(f) ),'for recipe ', r , 'for fridge ', f)
            if cosine(vec(r),vec(f)) >= 0.90:
                print('PLUSSSSSSSSSSSSSSSSSSSS for r ', r , 'with f ', f)
                print('thre is a match')
                if f not in tempSimilar:
                    tempSimilar.append(f)
                continue
            #if cosine(vec(r),vec(f) )> 0.80 and cosine(vec(r), vec(f)) < 0.90:
                #print('THERE IS A CLOSE MATCH for r ', r , 'with f ', f)
                #close_temp.append(f)
                #continue
            else:
                print('bad cosine ratio for r ' , r,  ' with f ', f  )
                if f not in diffFridgeComp:
                    print('f not in diff ,  ',  f)
                    diffFridgeComp.append(f)
                continue
    if tempSimilar:
        print('this is diffFridgeComp before intersectioon ' , diffFridgeComp)
        whatisMissing =list(set(split_recipe) - set(tempSimilar))
        diffFridgeComp = list(set(diffFridgeComp) - set(tempSimilar))
        whatisPresent = tempSimilar
        return whatisMissing,whatisPresent,close_temp,diffFridgeComp

    else:
        return split_recipe,None,close_temp,diffFridgeComp

def processComparison(split_fridge,split_recipe):
    if compareFridge_toRecipeIngre(split_fridge,split_recipe)[1] != None:
        missingElements,similarElements,closeElements,differenceInFridge = compareFridge_toRecipeIngre(split_fridge,split_recipe)
        print('this is missing elements ' , missingElements)
        print('this is similar element ', similarElements )
        print('this is almost similar element ', closeElements)
        print('this are the different in fridge el ', differenceInFridge)

        if not missingElements and not differenceInFridge:
            return (True,'No missing',split_fridge,[],split_recipe)
            #similar_ingredient_ind.append((i,j,g,r_id,cosine_val))
            
        if not missingElements:
            print('nothing missing for recipe but some extra ingree, this is what is extra from fridge ',differenceInFridge )
            return (True,'No missing',split_fridge,[],split_recipe)
            #similar_ingredient_ind.append((i,j,g,r_id,cosine_val))
            
        if missingElements and differenceInFridge:
            notToBad = 0
            print('there is something missing and something extra')
            for m in missingElements:
                for f in differenceInFridge:
                    print('not too bad cosine' , cosine(sentvec(m), sentvec(f)), 'between m and s' , m ,' and ' , f)
                    if cosine(sentvec(m), sentvec(f)) >= 0.7:
                        print('not too bad cosine' , cosine(sentvec(m), sentvec(f)), 'between m and s' , m ,' and ' , f)
                        notToBad += 1
                        continue
                    else:
                        continue
            if notToBad >= 1:
                print('adding while something missing')
                return (True,'Incomplete_High',missingElements,differenceInFridge,similarElements)
            else:
                return (True,'Incomplete_Low',missingElements,differenceInFridge,similarElements)
                print('TO BADDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
                                            
        if  differenceInFridge:
            good_extra = list()
            bad_extra = list()
            notToBad = 0
            print('there is something extra in fridge')
            for f in differenceInFridge:
                for s in similarElements:
                    #print('not too bad cosine' , cosine(sentvec(f), sentvec(s)), 'between m and s' , f ,' and ' , s)
                    if cosine(sentvec(f), sentvec(s)) >= 0.80:
                        good_extra.append((f,s))
                        #print('not too bad cosine' , cosine(sentvec(f), sentvec(s)), 'between m and s' , f ,' and ' , s)
                        notToBad += 1
                        continue
                    else:
                        bad_extra.append( (f,s))
                        continue
            if good_extra:
                    print('adding while something extra is in fridge')
                    return (True,'Good_Extra' , [],good_extra,bad_extra,similarElements)
            else:
                return (True, 'Bad_Extra', [],[], bad_extra,similarElements)
                print('TO BADDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
        if missingElements:
            print('only missing ingredientsssssssss')
            return ('True', 'Missing', missingElements,similarElements)
            #similar_ingredient_ind(append((i,j,g,r_id,cosine_val)))
        else:
            print('look more in depthhhhhhhhhhhhhhhhhhhhhh')
        #print('this is cosine for inner fridge el',fridge_list[i],' and recipe ingredient' , recipe_string_list[g], cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])))
    else:
        print('no correlation between fridge ',  split_fridge,' to recipe ' ,split_recipe)
        return (False,'Bad')
        print('this is badddddddddddddddddddddd cosine for inner fridge el',fridge_list[i],' and recipe ingredient' , recipe_string_list[g], cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])))
       
def parse_barcodes(dict_of_recipe,fridge_obj): # list of dictionary - dict - {recipe_name} = [ingredients list]
    print('parsingggggg')
    list_of_recipe = list()
    for recipe_dict in dict_of_recipe:
        list_of_recipe.append((  ( list( itertools.chain.from_iterable( (list(recipe_dict.values())) ) ) ) , list(recipe_dict.keys()) ))
    similar_ingredient = False
    similar_ingredient_ind =list()
    possible_options = list()
    cosine_val  = 0.0
    fridge_sent = ''.join(fridge_list)
    flag = False
    if len(fridge_list) > 2:
        for recipe in list_of_recipe: ## recipe contains - [0] -- recipe ingredients [1] -- recipe_id
            recipe_doc = nlp(' '.join(recipe[0]))
            print('doc', recipe_doc)
            if check_extension(fridge_list,recipe_doc)[0]:
                print('EXTENSION TRUE WITH RECIPE', recipe[0])
                recipe_string_list = recipe[0]
                r_id = ' '.join(recipe[1])
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
                    if cosine(sentvec(' '.join(recipe_string_list )), sentvec(fridge_list[i])) >= 0.6:
                        print('this is the cosine: ',cosine(sentvec(' '.join(recipe_string_list )), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i],'and recipe ingredient sent ', ' '.join(recipe_string_list ) )
                        for j in range(0,len(fridge_list_vec[i])):
                            if not fridge_list_vec[i][j] or fridge_list_vec[i][j] == '':
                                print('contnueeeeee for fridge', fridge_list_vec[i][j])
                                continue
                            for g in range(0,(len(recipe_string_list))):
                                #print('this is cosine for fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_string_list[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])))
                                if cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])) > 0.75: ## when two strings matches we need to work with n-gram model to extract more meaning
                                    similar_ingredient = True
                                    print( ' ')
                                    possible_options.append((i,j,g,r_id))
                                    print('this is cosine n-gram', cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])), 'between fridge' , fridge_list[i], 'and', recipe_string_list[g] )
                                    if cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])) >= 0.80:#90
                                        cosine_val = cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g]))
                                        similarityCounter =  0
                                        similar_ingredient_ind.append((i,j,g,r_id,cosine_val))
                                        split_recipe  = recipe_string_list[g].split(' ')
                                        split_fridge = fridge_list_vec[i]
                                        print('this is spit recipe' , split_recipe)
                                        print('this is split fridge' , split_fridge)
                                else:
                                    continue
                    else:
                        print('value too low for ingre', fridge_list[i])
                        continue

            else:
                print('NO EXTENSION')
                continue

        print(similar_ingredient_ind)
        print(dict_of_recipe)
        #print(possible_options)
        process_notification(fridge_obj,similar_ingredient_ind, fridge_list_vec, fridge_list, dict_of_recipe)
        exit()
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

def return_missing_and_similar_notification(string,fridge, similar_ingredient_ind ,fridge_list_vec , fridge_list, dict_of_recipe):
    country = False
    counter = string
    notification_outputDict =  {}
    for output in similar_ingredient_ind:
        i = int(output[0])
        j = int(output[1])
        ingre = int(output[2])
        cosine_value = output[4]
        if string == 'country_cuisine':
            name = str(output[3])
            country = True
            temp = str(output[3]).split('-')
            r_id = temp[0]
            r_country = temp[1]
        else:
            name = str(output[3])

        if country:
            for dict_r in dict_of_recipe:
                if name in dict_r.keys(): 
                    
                ##check how many ingredients are similar in a recipe, print the similar ingredients and inform the user of the existance of missing ingredients
                ##also if a recipe can be done so lets say we have 80% percent of the ingredients, we propose the recipe if it accepted by the user we delete from our fridge recipe dictionary
                    print(' ')
                    print('u have ',fridge_list_vec[i][j], '--full ingredient: ', fridge_list[i] ,'at cosine value ',cosine_value,' that goes well with recipe ingredient' ,list(dict_r[name])[ingre],  'at recipe', list(dict_r[name]), 'with id' , fridge.get_country_cuisine()[r_country]['recipeName'][r_id] ) 
                
        else:
            for dict_r in dict_of_recipe:
                if name in dict_r.keys():
                    print('U have a correlation with recipe :'  , name )
                    split_recipe  = list(dict_r[name])[ingre].split(' ')
                    split_fridge = fridge_list_vec[i]
                    print('fridge' ,split_fridge)
                    print('recipe',split_recipe)
                    if name not in notification_outputDict.keys():
                        comparison = processComparison(split_fridge,split_recipe)
                        if comparison[0]:
                            ingredient_counter = 0
                            first_temp = list()
                            first_temp.append((fridge_list[i] , list(dict_r[name])[ingre], cosine_value,len(comparison[2])))
                            notification_outputDict[name] = first_temp
                            continue
                        else:
                            print('bad estimation')
                            continue
                    else:    
                        temp_el = notification_outputDict[name]
                        comparison = processComparison(split_fridge,split_recipe)
                        if comparison[0]:
                            if  (fridge_list[i],list(dict_r[name])[ingre],cosine_value, len(comparison[2]) ) not in  temp_el:
                                check = False
                                flag = False
                                better_value = ''
                                for value in notification_outputDict[name]:
                                    #print('this is value ' , value)
                                    # print('this is list ', list(dict_of_recipe[name])[ingre] )
                                    if value[1] == list(dict_r[name])[ingre]:
                                        check =  True
                                        print('there existi already this recipe corellation for recipe ', value[1], 'with cosine ',  value[2], 'against cosine' , cosine_value)
                                        if value[2] > cosine_value:
                                            flag =  True
                                            print('and there is no high enough match')
                                            print(value)
                                            break
                                        else:
                                            print('cosine is higher than ')
                                            to_switch = value
                                            better_value =  (fridge_list[i] , list(dict_r[name])[ingre], cosine_value, len(comparison[2]))
                                            break
                                            print(list(dict_r[name])[ingre])
                                            print('this recipe corellation does not exists')
                                            continue
                                            #temp_el.append((fridge_list[i] , list(dict_r[name])[ingre], cosine_value, len(comparison[2])) )
                                            #notification_outputDict[name] = temp_el
                                            #break      
                                    else:
                                        continue
                                        #temp_el.append((fridge_list[i] , list(dict_r[name])[ingre], cosine_value, len(comparison[2])) )
                                        #notification_outputDict[name] = temp_el
                                if not check:
                                    temp_el.append((fridge_list[i] , list(dict_r[name])[ingre], cosine_value, len(comparison[2])))
                                    notification_outputDict[name] = temp_el
                                    
                                if check and not flag:
                                    if to_switch in temp_el:
                                        temp_el.remove(to_switch)
                                        temp_el.append(better_value)
                                        notification_outputDict[name] = temp_el
                                        continue
                                    
                                    
                                    
                                            
                                #if comparison[0] :
                                    #temp_el.append((fridge_list[i] , list(dict_r[name])[ingre], cosine_value, len(comparison[2])) )
                                    #notification_outputDict[name] = temp_el
                                    #print('second step notification ',  notification_outputDict)
                                    #print('this is number of similar ingreidnets ' ,ingredient_counter)
                                    #continue
                                #if comparison[0] and comparison[1] == 'Good_Extra':
                                   # print('there is some extra element in fridge that are good with recipe ,' , comparison)
                                #if comparison[0] and comparison[1] == 'Bad_Extra':
                                    #print('there is some extra element in fridge that are bad with recipe ,' , comparison)

                                #if comparison[0] and comparison[1] == 'Incomplete_High':
                                    #print('something is missing but its replacement has high rate ', comparison)
                                #if comparison [0] and comparison[1] == 'Incomplete_Low':
                                   # print('something is missing and its replacement has low rate ', comparison)
                                #notification_outputDict[name][0] = ingredient_counter
                            else:
                                print(' ')
                                print('fridge el already present ' , fridge_list[i])
                                print( ' ')
                                continue
                        else:
                            print('bad estimation')
                            continue
                    print( '  ')
                    print('u have ',fridge_list_vec[i][j], '--full ingredient: ', fridge_list[i]  ,'at cosine value ',cosine_value, ' that goes well with recipe ingredient' ,list(dict_r[name])[ingre],  'at recipe', list(dict_r[name]), 'with id' , name)
                else:
                    continue
    for recipe_key, possible_ingredients in notification_outputDict.items():
            
        print('For recipe  ',  recipe_key, 'there are ',  len(possible_ingredients) , 'ingredients that are similar to the actual recipe. This is are the following: ', possible_ingredients)
    #print(notification_outputDict)
    

    
    #print('there is similarity between fridge ',fridge_list_vec[i][j],'--full ingredient: ', fridge_list[i] , ' that goes well with recipe ingredients',list(dict_r[name])[ingre] ,  'at recipe', list(dict_r[name]))
     
 

def process_notification(fridge, similar_ingredient_ind ,  fridge_list_vec , fridge_list, dict_of_recipe):
    if bool(fridge.get_diet()):
        print('we return diet notifications for diet ', fridge.get_diet().keys())
        if not similar_ingredient_ind: 
            print('There are not correlations between yuor ingredients and your current diets: ', fridge.get_diet().keys() )
        else:
            print('U have a correlation between fridge and recipe of diet: ' , fridge.get_diet().keys() )
            return_missing_and_similar_notification('diet',fridge,similar_ingredient_ind , fridge_list_vec , fridge_list , dict_of_recipe)
            
        
    if bool(fridge.get_country_cuisine()):
        print('return country cuisine for country ', fridge.get_country_cuisine().keys())
        if not similar_ingredient_ind:
            print('There are not correlations between yuor ingredients and your current country cusisine selection: ', fridge.get_country_cuisine.keys() )
        else:
            return_missing_and_similar_notification('country_cuisine',fridge,similar_ingredient_ind , fridge_list_vec , fridge_list , dict_of_recipe)

    else:
        return all
    
