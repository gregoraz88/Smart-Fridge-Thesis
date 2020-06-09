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
    quantity_list = ['cup', 'Tbsp', 'bunch', 'grams', 'ounce', 'kg', 'ml', 'tsp','tbsp','cups', 'ounces', 'teaspoon','tablespoon','tablespoons','teaspoons', 'can', 'pinch', 'to_taste', 'for brushing'  ]
    #print(raw_ingredients)
    #print(recipe_name)
    #print(type(value))
    full_ingredient = value
    quantity_type = 'Empty'
    r_id = 0
    delete_type = False
    for tuple_index,tuple_el in enumerate(full_ingredient):
        OR = False
        quantity = ''
        quantity_type = ''
        print(tuple_el)
        delete_type  = False
        typeToDelete = list()
        for t_el in tuple_el[0].split(' '):
            if t_el == 'or':
                or_index  =tuple_el[0].find('or')
                OR = True
                break
            for type_list in quantity_list:
                if t_el.lower().find(type_list) != -1:
                    print('this is type_list found ', type_list)
                    if delete_type:
                        print('second appending' , t_el)
                        if t_el not in typeToDelete:
                            typeToDelete.append(t_el.lower())
                            continue
                    else:
                        quantity_type = type_list
                        if t_el not in typeToDelete:
                            print('appendinggg ' , t_el)
                            typeToDelete.append(t_el.lower())
                            delete_type = True
                            continue
                else:
                    continue
        print('this is quantity_type ', quantity_type)
        print('this is what to delete', typeToDelete)
        ingre =  tuple_el[0].lower()
        if OR:
            ingre = ingre[0:or_index-1]
            for el in typeToDelete:
                print('pre or  deleting ', ingre)
                ingre = ingre.replace(el,'')
                print('ingre at  or deleting ', ingre)
            print('this is or ingre', ingre)
            print('this is OR  quantity_type ', quantity_type)
        else:
            print('not orrrrr')
            for el in typeToDelete:
                print('pre deleting ', ingre)
                ingre = ingre.replace(el,'')
                print('ingre at deleting ', ingre)
        quantity =  tuple_el[1]
        parsed_ingredient = ((ingre,quantity,quantity_type))
        print('this is important temp tupleeeeeeeeeeeeeeee  ',  parsed_ingredient)
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
                parse_barcodes(recipe_list,fridge)
                exit()
            ## this returns the parsed ingredients of recipes - after this compare it to the fridge el 