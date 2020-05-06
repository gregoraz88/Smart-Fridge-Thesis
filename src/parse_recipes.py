from os import getcwd,chdir,path
import json
import nltk
import numpy as np
from nltk.util import ngrams
import string
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
import pandas as pd
import re
from num2words import num2words
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from numpy import array
from keras.utils import to_categorical


def save_recipes(filename, recipe_dict):
    with open(filename, 'w') as f:
        json.dump(recipe_dict, f)


def clean_recipes(raw_ingredients):
    #print(raw_ingredients)
    special_character_list = ['-', '–']
    for list_index,list in enumerate(raw_ingredients):
        #print(list)
        print(list)
        list = list.split(' ')
        #list = re.sub("[^0-9a-zA-Z]"," ",list)
        temp_index = 0
        bracket= False
        for index,el in enumerate(list):
            if '(' in el and not bracket:
                if '(' and ')' in el:
                    list.remove(list[index])
                bracket = True
                temp_index = index
                continue
            if ')' in el and bracket:
                    list.remove(list[index])
                    list.remove(list[temp_index])
                    temp_index = 0
                    bracket= False
                    continue
            temp_punct = re.findall(r'[^\w\s]',el)
            if len(temp_punct) > 0:
                if temp_punct[0] in special_character_list:
                    break
                else:
                    list[index] = re.sub(r'[^\w\s]','',el)
        raw_ingredients[list_index] = list
            # if el.isdigit():
            #     temp_digit =  num2words(el)
            #     #temp_list  = list.replace(el, temp_digit)
            #     #raw_ingredients[list_index] = temp_list
            #
            # else:
            #     continue
    return raw_ingredients



def TF_IDF(raw_ingredients):
    print('this is rawwwwwwww')
    cv=CountVectorizer()
    word_count_vector=cv.fit_transform(raw_ingredients)
    vectorizer = TfidfTransformer(use_idf=True, norm=None)
    vectorizer.fit(word_count_vector)
    count_vector=cv.transform(raw_ingredients)
    tf_idf_vector=vectorizer.transform(count_vector)
    feature_names = cv.get_feature_names()
    print('these are the featuresssss:', feature_names)
    return feature_names


    # recipe_df= pd.DataFrame()
    # for i in range(len(raw_ingredients)):
    #     first_document_vector=tf_idf_vector[i]
    #     df = pd.DataFrame(first_document_vector.T.todense(), index=feature_names, columns=["tfidf"])
    #     df = df.sort_values(by=["tfidf"],ascending=False)
    #     recipe_df[i] = df.iloc[:,0]
    # print(recipe_df)



def return_ingredients(value):
    inner_recipes_dict = {}
    plus = False
    to = False
    ## handle where that are multiple quantity
    ##handle where quantity frequency is of multiple digits
    #handle the 'to' and 'or' statement
    quantity_list = ['cup', 'Tbsp', 'gr', 'bunch', 'grams', 'ounce', 'kg', 'ml', 'l', 'cl', 'tsp','tbsp','cups','oz', 'ounces','lb', 'teaspoon','tablespoon', 'can']
    #solve problems or quarter and half
    raw_ingredients = value['ingredients']
    raw_ingredients = clean_recipes(raw_ingredients)
    #print(raw_ingredients)
    recipe_name = value['title']
    #print(recipe_name)
    for full_ingredient in raw_ingredients:
        #full_ingredient = full_ingredient.split(' ')
        for str_index,str in enumerate(full_ingredient):
            quantity = ''
            if not str.isalpha():
                #print(str)
                #print('Do i know it' , full_ingredient[str_index+1])
                if str_index > (len(full_ingredient)-3):
                    break
                else:
                    if full_ingredient[str_index+1] in quantity_list:
                        if plus:
                            plus = False
                            quantity = temp_quantity+ ' plus ' + full_ingredient[str_index] + ' ' + full_ingredient[str_index+1]
                            quantity_ingredient_tuple = ( (full_ingredient[str_index+2:len(full_ingredient)]) ,quantity)
                            inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])]= quantity_ingredient_tuple[1]
                            #print('plus qunatity',quantity_ingredient_tuple)
                            break
                        else:
                            quantity = full_ingredient[str_index] + ' ' + full_ingredient[str_index+1]
                            if full_ingredient[str_index+2] != 'plus' and full_ingredient[str_index+2] != 'to':
                                quantity_ingredient_tuple = ((full_ingredient[str_index+2:len(full_ingredient)]),quantity)
                                inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                                #print('no plus' , quantity_ingredient_tuple)
                    else:
                        if plus == False and full_ingredient[str_index+1] != 'to':
                            quantity_ingredient_tuple = ((full_ingredient[str_index+1:len(full_ingredient)]),str)
                            inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                        if full_ingredient[str_index+1] ==  'to':
                            quantity = full_ingredient[str_index]
                        if to == True:
                            to= False
                            quantity = temp_quantity +  ' to ' + full_ingredient[str_index]
                            quantity_ingredient_tuple = ((full_ingredient[str_index+1:len(full_ingredient)]),quantity)
                            inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                            #print(quantity_ingredient_tuple)
                            #print('no quantity fund')
                        break
            else:
                if full_ingredient[str_index] == 'plus':
                    plus = True
                    temp_quantity = quantity
                    continue
                if  full_ingredient[str_index] == 'to':
                    to = True
                    temp_quantity = quantity
                    continue
    return inner_recipes_dict


recipes_dict = {}
chdir('..')
chdir('data')
path1 = getcwd()
print(path1)
recipes_path = '/recipes_raw_epi.json'
with open(path1 + recipes_path) as json_file:
    recipes_data = json.load(json_file)

counter = 0
temp_labels = list()
temp_x_train = list()
temp_list = list()
new_recipe_path = path.join( path1, 'cleaned_recipes.json')
for key,value in recipes_data.items():
    counter += 1
    if counter > 30:
        save_recipes(new_recipe_path,recipes_dict)
        #print(counter , 'recipeeeeeeeeeeeeeeeeeee')
    #TF_IDF(value['ingredients'])
    if value != None and len(value) >= 1:
        recipes_dict[value['title']] = return_ingredients(value)
        #print(value['title'])
        #print(recipes_dict)
