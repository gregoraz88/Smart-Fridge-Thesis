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
from fuzzywuzzy import fuzz


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
    quantity_list = ['cup', 'Tbsp', 'bunch', 'grams', 'ounce', 'kg', 'ml', 'tsp','tbsp','cups', 'ounces', 'teaspoon','tablespoon','tablespoons','teaspoons', 'can', 'cans','pinch', 'to_taste', 'for brushing', 'grated', 'pound' , 'finely', 'freshly', 'ground', 'thinly', 'sliced', 'slices', 'small', 'large', 'minced']
    full_ingredient = value
    quantity_type = 'Empty'
    quantities = ''
    quantities.join(quantity_list)
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
            for type_list in quantity_list:
                if fuzz.ratio(t_el.lower(),type_list) > 90:
                    if t_el.lower() not in typeToDelete:
                        typeToDelete.append(t_el.lower())
                        continue
                else:
                    continue
                
        ingre =  tuple_el[0].lower()
       
        if OR:#if or is present, it means there are multiple options for one ingredients, we want to eliminate this, so we only choose the first option and not consider everything after the 'or'
            ingre = ingre[0:or_index-1]
            for el in typeToDelete:
                ingre = ingre.replace(el,'')
        else:
            for el in typeToDelete:
                ingre = ingre.replace(el,'')

        #print('THIS IS INGRE ', ingre)
        #print('TYPE TO DELETE ',  typeToDelete)
        quantity =  tuple_el[1]
        #print('quantity ', quantity)
        parsed_ingredient = (ingre,quantity,quantity_type)
        print('before cleaning ingredient', tuple_el)
        print(' ')
        inner_recipes_dict[r_id] = parse_semantic(ingre) ##returns the cleaned version of the ingredient
        print('after cleaning ingredient: cleaned ingredient: ', inner_recipes_dict[r_id], ',  quantity: ', quantity,', quantity_type: ' , typeToDelete)
        print(' ')
        r_id += 1 
    return inner_recipes_dict

def mix_country_with_diet_recipes(fridge,special_diet_name):
    country_recipes_list =  return_country_cuisine(fridge)
    special_recipes_list =  return_all_special_diets(fridge,special_diet_name)
    mixed_recipes  = list(itertools.chain.from_iterable(zip(country_recipe_dict,special_recipes_list)))
    start_notification(mixed_recipes, fridge)


def map_ingredients_to_country_cuisine(fridge,recipe_size):
    recipe_string_list = list()
    country_recipe_dict =  fridge.get_country_cuisine()
    for key , informations in country_recipe_dict.items():
        #print(key)
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
            if int(recipe_id) >= recipe_size:
                start_notification(recipe_string_list,fridge, key)
                break

def return_all_special_diets(fridge,special_diet_name,size):
    all_special_diets = {}
    recipe_list = list()
    counter_size = 0
    for recipe_name,ingredients in fridge.get_diet()[special_diet_name].items():
        if counter_size == size:
            break
        counter_size += 1
        special_diet_ingredients = list()
        for name,quantity in ingredients.items():
            start_indx = name.find('(')
            end_indx = name.find(')')
            ingre_name = name.replace(name[start_indx:end_indx+1],'')
            special_diet_ingredients.append((ingre_name,quantity))
        all_special_diets[recipe_name]= special_diet_ingredients
    print('pre ingredient processing: ' , all_special_diets)
    for r_name,recipe in all_special_diets.items():
        temp_dict = {}
        temp_dict[r_name] =  list(parse_ingredients(recipe).values())
        print('dict after parsing: ', temp_dict)
        recipe_list.append(temp_dict)
        print('list ', recipe_list)
        if len(recipe_list) >= size and size != None:
            return  recipe_list
    return recipe_list
    
def map_ingredients_to_special_diets(fridge,size):
    all_special_diets = {}
    all_fridge_special_diets = {}
    recipe_list = list()
    all_fridge_special_diets =  fridge.get_diet()
    for special_diet_name in all_fridge_special_diets.keys():
        all_special_diets[special_diet_name] = return_all_special_diets(fridge,special_diet_name,size)
    for diet,recipes in all_special_diets.items():
        print('this is diet ', diet)
        print()
        print('this is recipes ', recipes)
        recipe_list =  recipe_list + recipes
        if len(recipe_list) >= size-1 :
            print('recipes before notification ', recipe_list)
            start_notification(recipe_list,fridge,diet)
            recipe_list = list()
            #print('this is step ' , recipe_list,'   ' , fridge.get_diet().keys())
            continue
