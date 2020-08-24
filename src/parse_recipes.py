from os import getcwd,chdir,path
import json
import nltk
import numpy as np
from nltk.util import ngrams
import string
import spacy
from spacy.tokens import Doc,Span,Token
from process_syntax import parse_semantic
from barcode_parser import parse_barcodes,start_notification
import itertools
import re


def save_recipes(filename, recipe_dict):
    with open(filename, 'w') as f:
        json.dump(recipe_dict, f)
   
def parse_ingredients(value):#given a recipes with multiple ingredients in which the quantity, quantity type and ingredient are not separated. this function divides the three elements in a tuple so that they can be easily accesible 
    print('returning ingre')
    inner_recipes_dict = {}
    plus = False
    to = False
    #handle where that are multiple quantity
    #handle where quantity frequency is of multiple digits
    #handle the 'or' statement
    quantity_list = ['cup', 'Tbsp', 'bunch', 'grams', 'ounce', 'kg', 'ml', 'tsp','tbsp','cups', 'ounces', 'teaspoon','tablespoon','tablespoons','teaspoons', 'can', 'pinch', 'to_taste', 'for brushing'  ]
    full_ingredient = value
    quantity_type = 'Empty'
    r_id = 0
    delete_type = False
    for tuple_index,tuple_el in enumerate(full_ingredient):#loop through all ingredients
        OR = False
        quantity = ''
        quantity_type = ''
        delete_type  = False
        typeToDelete = list()
        for t_el in tuple_el[0].split(' '):
            if t_el == 'or':
                or_index  =tuple_el[0].find('or')
                OR = True
                break
            else:
                continue
            for type_list in quantity_list:
                if t_el.lower().find(type_list) != -1:
                    if delete_type:
                        if t_el not in typeToDelete:
                            typeToDelete.append(t_el.lower())
                            continue
                    else:
                        quantity_type = type_list
                        if t_el not in typeToDelete:
                            typeToDelete.append(t_el.lower())
                            delete_type = True
                            continue
                else:
                    continue
        print('this is quantity_type ', quantity_type)
        print('this is what to delete', typeToDelete)
        ingre =  tuple_el[0].lower()
        if OR:#if or is present, it means there are multiple options for one ingredients, we want to eliminate this, so we only choose the first option and not consider everything after the 'or'
            ingre = ingre[0:or_index-1]
            for el in typeToDelete:
                ingre = ingre.replace(el,'')
        else:
            for el in typeToDelete:
                ingre = ingre.replace(el,'')
        quantity =  tuple_el[1]
        parsed_ingredient = ((ingre,quantity,quantity_type))
        inner_recipes_dict[r_id] = parse_semantic(ingre) ##returns the cleaned version of the ingredient
        r_id += 1 
    return inner_recipes_dict

def mix_country_with_diet_recipes(fridge,special_diet_name):
    country_recipes_list =  return_country_cuisine(fridge)
    special_recipes_list =  return_all_special_diets(fridge,special_diet_name)
    mixed_recipes  = list(itertools.chain.from_iterable(zip(country_recipe_dict,special_recipes_list)))
    start_notification(mixed_recipes, fridge)


def return_country_cuisine(fridge):
    recipe_string_list = list()
    country_recipe_dict =  fridge.get_country_cuisine()
    for key , informations in country_recipe_dict.items():
        print(key)
        # recipes key are : id, recipeName, rating,totalTimeInSeconds, course, cuisine,ingredients
        for recipe_id,value in informations['ingredients'].items():
            print('this is recie',recipe_id)
            print('this name of recipes', informations['recipeName'][recipe_id])
            raw1 = list()
            raw = value.split(',')
            for el in raw:
                el = re.sub(r'[^\w\s]','',el)
                el = re.sub(r"\s+", ' ', el.lstrip())
                raw1.append(el)
            temp_dict = {}
            temp_dict [recipe_id+'-'+key] = raw1 ##the key of the dictionary - recipe_id which is a digit that maps the recipe and key is the country key in dictionary fridge.get_coutnry_cuisine()
            recipe_string_list.append(temp_dict)
            if int(recipe_id) > 10:
                return recipe_string_list
    return recipe_string_list

def return_all_special_diets(fridge,special_diet_name,size):
    all_special_diets = {}
    recipe_list = list()
    for recipe_name,ingredients in fridge.get_diet()[special_diet_name].items():
        special_diet_ingredients = list()
        for name,quantity in ingredients.items():
            start_indx = name.find('(')
            end_indx = name.find(')')
            ingre_name = name.replace(name[start_indx:end_indx+1],'')
            special_diet_ingredients.append((ingre_name,quantity))
        all_special_diets[recipe_name]= special_diet_ingredients
    for r_name,recipe in all_special_diets.items():
        temp_dict = {}
        temp_dict[r_name] =  list(parse_ingredients(recipe).values())
        print(temp_dict)
        exit()
        recipe_list.append(temp_dict)
        if len(recipe_list) >= size and size != None:
            return  recipe_list
    return recipe_list
    
def map_ingredients_to_special_diets(fridge):
    all_special_diets = {}
    all_fridge_special_diets = {}
    recipe_list = list()
    all_fridge_special_diets =  fridge.get_diet()
    for special_diet_name in all_fridge_special_diets.keys():
        all_special_diets[special_diet_name] = return_all_special_diets(fridge,special_diet_name,1)
    for diet,recipes in all_special_diets.items():
        recipe_list =  recipe_list + recipes
    if len(recipe_list) >= 1 :
        start_notification(recipe_list,fridge)
