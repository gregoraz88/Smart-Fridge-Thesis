from fuzzywuzzy import fuzz
import json
import gensim
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
import numpy as np
import sys
import nltk
import autocomplete
from parse_recipes import parse_ingredients
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from gensim import corpora, models
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem.porter import *
import pandas as pd
import spacy
nlp = spacy.load('en_core_web_sm')

# in this section I am using CountVectorizer to extracts ingrendients from recipes and fridge content, so I have to make a vector per each of the category(recipe,fridge), but
# the size of the two categories, its always never the same,but we need to fit the same size vectors in order to perform an accurate comparison. So lets take an example in consideration
# if the fridge content is (5) and the recipe size is (11) , we already know that we dont have enough ingredients, but we still want how much correlation there is bt the two.
# So we divide the Fridge in a vector of (5) and the recipe into 3 vectors(because it does not fit in two) , of all size 5 , therefore in the last vector there will be a repetition, which is not important.
#In the case in which recipe size is smaller than fridge content, the opposite process is perfomed.

#here we return the chunk list, of the largest category between the two, and we fit the largest category into the size of the smaller one
def return_raw_ingredients_into_chuncks(raw_ingredients,smaller_size):
    chunck_list = list()
    recipe_size = len(raw_ingredients)
    if (recipe_size%smaller_size)==0:
        chunck_size = recipe_size/smaller_size
        for i in range(0,chunck_size-1):
            chunck_list.append(raw_ingredients[i*smaller_size:smaller_size*i+1])
            return chunck_list ## need to check this
    else:
        counter  = 0
        flag = recipe_size/smaller_size
        flag = int(flag)
        for i in range(0,(recipe_size)):
            if counter == flag:
                n_new_ingredient = recipe_size - i
                n_old_ingredient = smaller_size- n_new_ingredient
                start_index = i - n_old_ingredient
                last_chunck = raw_ingredients[start_index:recipe_size]
                chunck_list.append(last_chunck)
                print(last_chunck, 'at counter',counter+1, 'from',start_index, 'to', recipe_size)
            if ((i+1 )% smaller_size) == 0:
                counter = counter + 1
                print('this is counter',counter,'at ', i)
                chunck=  raw_ingredients[i-(smaller_size-1): i+1]
                chunck_list.append(chunck)
                print(chunck, 'at counter',counter, 'from',i-(smaller_size-1), 'to', i)
                continue
            else:
              print(i)
              if counter < flag:
                    continue
        return chunck_list

#CountVectorizer on a chunck, and it return the feature_name of vector
def CountVectorizer_recipe(chunck):
    cv2=CountVectorizer(analyzer = 'word' , token_pattern = r'.*')
    word_count_vector2=cv2.fit_transform(chunck)
    v2 = cv2.get_feature_names()
    return v2

def CountVectorizer_special_recipe(chunck):

    cv2=CountVectorizer(analyzer = 'word' , stop_words= 'english', lowercase = True , token_pattern='[a-zA-Z0-9]{3,}' )
    word_count_vector2=cv2.fit_transform(chunck)
    v2 = cv2.get_feature_names()
    return v2


def lemmatize_stemming(text):
    lemma = nltk.wordnet.WordNetLemmatizer()
    return lemma.lemmatize(text)


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

                                     
 
def read_user_input(missing_ingredients,recipe_id):
    ingredients_missing = list(missing_ingredients)
    Flag = True
    breaking = False
    print('Type : yes/no/exit')
    for line in sys.stdin:
        if 'exit' == line.rstrip():
            break
        if 'yes' == line.rstrip() and Flag:
            print('Nice,lets try to figure out which you have, when you are done listing, please type Exit to terminate')
            Flag = False
            continue
        elif 'no' == line.rstrip() and Flag:
            Flag = False
            print('Bummer, lets find another recipe for you :)')
        if not Flag:
                print('Keep Guessing!')
                breaking = False
                num = line.rstrip()
                filtered_recipes = filter(lambda x:fuzz.ratio(x,num) > 30, ingredients_missing)
                l = list(filtered_recipes)
                if len(l) >= 1:
                    print('Which one Did you mean:',l,' ?')
                    for x in l:
                        if breaking:
                            break
                        print('Was it ' ,x ,'?')
                        print('Yes or No?')
                        for lines in sys.stdin:
                            if lines.rstrip() != 'Yes':
                                    print('Sorry, Okay lets keep trying')
                                    break
                            if lines.strip('Yes'):
                                ingredients_missing.remove(x)
                                if len(ingredients_missing) == 0:
                                    print('Congratualation, all ingredients have been found!!!, you can now cook recipe', recipe_id)
                                    exit()
                                print('There are only ',len(ingredients_missing), ' ingredients missing!!!')
                                breaking = True
                                break

def return_similar_and_missing_ingredients(v2,smallest,recipe_id):
    print('this is smallest',smallest)
    print('this is fridge', v2)
    recipe_np  = np.array(smallest)
    temp_fridgeobj_in_recipe = list()
    fridgeobj_in_recipe = list()
    missing_ingredients = list()
    for i in range (0,len(v2)): ##smallest is recipe ingredients
        for j in range (0, len(smallest)):
            if fuzz.ratio(smallest[i].lower(),v2[j].lower()) >= 60 and   fuzz.ratio(smallest[i].lower(),v2[j].lower()) < 90:
                print(fuzz.ratio(smallest[i].lower(),v2[j].lower()), 'for', smallest[i], v2[j])
                #v2 is a vector containing the element we have in the fridge and the smallest is recipe food
                if (v2[j].lower(),smallest[i].lower(),fuzz.ratio(smallest[i].lower(),v2[j].lower())) not in temp_fridgeobj_in_recipe:
                    temp_fridgeobj_in_recipe.append((v2[j].lower(),smallest[i].lower(),fuzz.ratio(smallest[i].lower(),v2[j].lower())))
            elif fuzz.ratio(smallest[i].lower(),v2[j].lower()) >= 90 and str(v2[j]) != '':
                print('this fridge element ', v2[j], 'is in recipe id' ,recipe_id )
                if smallest[i] not in fridgeobj_in_recipe:
                    fridgeobj_in_recipe.append(smallest[i])
            # else:
            #     if smallest[i] not in missing_ingredients:
            #         print('adding',smallest[i],'at elese')
            #         missing_ingredients.append(smallest[i])
            #         continue
    np1= np.array(fridgeobj_in_recipe)
    missing_ingredients = np.setdiff1d(recipe_np,np1)
    return fridgeobj_in_recipe,missing_ingredients[1:len(missing_ingredients)]

#This function compares each element of the two category and calculates and returns their similarities
def return_notification(chunck_list,smallest,enough_ingredients,recipe_id,same_size):
    temp_fridgeobj_in_recipe =  list()
    fridgeobj_in_recipe = list()
    if same_size == False:
        for i in range(0,len(chunck_list)):
            v2 = CountVectorizer_recipe(chunck_list[i])
            print('chunks of bigger', v2)
            if enough_ingredients:
                print(len(smallest))
                return print(return_similar_and_missing_ingredients(v2,smallest,recipe_id))
                #parse_not_similar_ingredients(temp_fridgeobj_in_recipe)
            else:
                print(' NOT ENOUGH')
    else:
        notifcation_info = return_similar_and_missing_ingredients(chunck_list,smallest,recipe_id)
        print('   ')
        if len(notifcation_info[1]) == 0:
            print('You have ',len(notifcation_info[0]), 'ingredients in your fridge which are all you need to make recipe',recipe_id,', these are the following ingredients:',notifcation_info[0])
        else:
            print('You have ',len(notifcation_info[0]), 'ingredients in your fridge to make recipe',recipe_id,', these are the following ingredients:',notifcation_info[0], 'but you are missing',len(notifcation_info[1]), 'ingredients to complete the recipes,these are the ingredients:',notifcation_info[1],'check if you anything similar in your pantry')
        #    read_user_input(notifcation_info[1],recipe_id)

        return notifcation_info

def return_recipe_notification(raw_ingredients, content_list,recipe_id):
    recipe_size = len(raw_ingredients)
    f_food = list()
    for element in content_list:
        f_food.append(element)
    fridge_size = len(f_food)
    print('fridge size',fridge_size)
    print('recipe size', recipe_size)
    #fit chunck on fridge_size
    if recipe_size > fridge_size: ## do this or do not??????????????
        print('recipe is bigger')
        chunck_list = return_raw_ingredients_into_chuncks(raw_ingredients,fridge_size)
        temp_vector = CountVectorizer_recipe(f_food)
        print('smallest', temp_vector)
        return_notification(chunck_list, temp_vector,False,recipe_id,False)
    #fit chuncks on recipe_size
    elif fridge_size > recipe_size:
        print('recipe is smaller')
        chunck_list = return_raw_ingredients_into_chuncks(f_food, recipe_size)
        temp_vector = CountVectorizer_recipe(raw_ingredients)
        print('smallest', temp_vector)
        return return_notification(chunck_list,temp_vector,True,recipe_id,False)
    elif fridge_size == recipe_size:
        fridge_vec = CountVectorizer_recipe(f_food)
        recipe_vec= CountVectorizer_recipe(raw_ingredients)
        print(return_ingredients(recipe_vec))
        return_notification(fridge_vec,recipe_vec, True,recipe_id,True)
    #print(chunck_list)
    exit()



def map_ingredients_to_special_diets(fridge,special_diet):
    special_diet_ingredients = list()
    for recipe,ingredients in special_diet.items():
        for name,quantity in ingredients.items():
            start_indx = name.find('(')
            end_indx = name.find(')')
            ingre_name = name.replace(name[start_indx:end_indx+1],'')
            special_diet_ingredients.append(ingre_name)
        break
    ##need to clean special_diet_ingredients -
    print(special_diet_ingredients)
    exit()
