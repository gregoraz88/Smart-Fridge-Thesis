from os import getcwd,chdir,path
import json
import nltk
import numpy as np
from nltk.util import ngrams
import string
import spacy
from spacy.tokens import Doc,Span,Token
from process_syntax import parse_semantic
from barcode_parser import parse_barcodes
# from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
# import pandas as pd
# import re
# from num2words import num2words
# from sklearn.preprocessing import LabelEncoder,OneHotEncoder
# from numpy import array
# from keras.utils import to_categorical


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

    
  
def parse_ingredients(value):
    print('returning ingre')
    inner_recipes_dict = {}
    plus = False
    to = False
    ## handle where that are multiple quantity
    ##handle where quantity frequency is of multiple digits
    #handle the 'to' and 'or' statement
    quantity_list = ['cup', 'Tbsp', 'gr', 'bunch', 'grams', 'ounce', 'kg', 'ml', 'l', 'cl', 'tsp','tbsp','cups','oz', 'ounces','lb', 'teaspoon','tablespoon','tablespoons','teaspoons', 'can', 'Pinch']
    #print(raw_ingredients)
    #print(recipe_name)
    print(type(value))
    full_ingredient = value
    quantity_type = 'Empty'
    r_id = 0
    for tuple_index,tuple_el in enumerate(full_ingredient):
        quantity = ''
        print(tuple_el)
        for t_el in tuple_el[0].split(' '):
            if t_el in quantity_list:
                print('ITS IN')
                print(t_el)
                quantity_type = t_el
        print('this is quantity_type ', quantity_type)
        ingre = tuple_el[0].replace(quantity_type,'')
        quantity =  tuple_el[1]
        temp_tuple = ((ingre,quantity,quantity_type))
        #print('temp with quantity'  ,temp_tuple)
        inner_recipes_dict[r_id] = parse_semantic(ingre)
        print('this is options', inner_recipes_dict[r_id])
        r_id += 1
        #print('this is optionsssss' , parse_semantic(nlp(ingre)))##parsing ingredients from special recipes 
          
    return inner_recipes_dict


def map_ingredients_to_special_diets(fridge):#object fridge passed
    print('mapping special diets')
    all_fridge_special_diets = {}
    all_special_diets = {}
    recipe_list = list()
    all_fridge_special_diets =  fridge.get_diet()
    for special_diet_name in all_fridge_special_diets.keys():
        print(special_diet_name)
        #print(all_fridge_special_diets[special_diet])
        for recipe_name,ingredients in all_fridge_special_diets[special_diet_name].items():
            special_diet_ingredients = list()
            for name,quantity in ingredients.items():
                start_indx = name.find('(')
                end_indx = name.find(')')
                ingre_name = name.replace(name[start_indx:end_indx+1],'')
                special_diet_ingredients.append((ingre_name,quantity))
            all_special_diets[recipe_name]= special_diet_ingredients
        #print('this is list of  speceial recipes '  ,all_special_diets)
        for r_name,recipe in all_special_diets.items():
            #print(r_name)
            #print(all_fridge_special_diets[special_diet_name][r_name])
            #print(recipe)
            temp_dict = {}
            temp_dict[r_name] =  list(parse_ingredients(recipe).values())
            recipe_list.append(temp_dict)
            if len(recipe_list) > 1:
                print('this is recipe list' ,recipe_list)
                parse_barcodes(recipe_list)
                exit()
            ## this returns the parsed ingredients of recipes - after this compare it to the fridge el



# recipes_dict = {}
# chdir('..')
# chdir('data')
# path1 = getcwd()
# print(path1)
# recipes_path = '/recipes_raw_epi.json'
# with open(path1 + recipes_path) as json_file:
#     recipes_data = json.load(json_file)
#
# counter = 0
# temp_labels = list()
# temp_x_train = list()
# temp_list = list()
# new_recipe_path = path.join( path1, 'cleaned_recipes.json')
# for key,value in recipes_data.items():
#     counter += 1
#     if counter > 30:
#         save_recipes(new_recipe_path,recipes_dict)
#         #print(counter , 'recipeeeeeeeeeeeeeeeeeee')
#     #TF_IDF(value['ingredients'])
#     if value != None and len(value) >= 1:
#         recipes_dict[value['title']] = return_ingredients(value)
#         #print(value['title'])
#         #print(recipes_dict)
