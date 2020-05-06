import pandas as pd
from os import getcwd,chdir,listdir,path
import glob
import json
import requests
from bs4 import BeautifulSoup
import config
import re


def save_data(filename, dict):
    with open(filename, 'w') as f:
        json.dump(dict, f)
#merging nutritional dictionary to 'final_nutritional_dict.json' in special_diets folder
################################################################################
def merge_nutritional_dict():
    path = 'C:/Users/gregh/Desktop/thesis/special_diets'

    nutritional_file_path = 'nutritional_dict.json'
    nutritional_file_path1 = 'nutritional_dict1.json'

    with open(path + '/' + nutritional_file_path) as json_file:
        nutritional_data = json.load(json_file)
    with open(path + '/' + nutritional_file_path1) as json_file:
        nutritional_data1 = json.load(json_file)

    nutritional_data.update(nutritional_data1)
    save_data(path + '/'+ 'final_nutritional_dict.json', nutritional_data)

#save all cuisine recipes, into a nested dictionary, per each country
#################################################################################
def scrape_cuisine_recipes():
    chdir('..')
    chdir('..')
    path1 = getcwd()

    Cuisines_data = pd.DataFrame({'A' : []})
    results = pd.DataFrame({'A' : []})
    path2 = 'thesis\\Recipe-Analysis-master\\CuisineAnalyzer\\cuisinedata'
    final_path = path.join(path1,path2)
    all_file= glob.glob(path.join(final_path,'*.csv'))

    ##all_cuisine_recipes is a nested dictionary, at each index there is a dictionary per each cuisine-
    # in order to access the american cuisine - all_cuisine_recipes['american'] - and each of the nested dictionary -
    #there are multiple dictionary - 'id' - id of the recipes /'recipesName' - name of the recipes related to id / '
    # / 'rating' - mapping the id to rating - course - mapping id to type of course / cuisine' - type of cuisine
    # / ingredients - mapping id recipes to ingredients /
    all_cuisine_recipes = {}
    for file in all_file:
        temp = file.split('\\')
        name = temp[-1]
        name = name.split('.')
        df = pd.read_csv(file)
        dict = df.to_dict()
        all_cuisine_recipes[name[0]] = dict

    print(all_cuisine_recipes['american']['id'])
    print('------------------------------------------')
    print(all_cuisine_recipes['american']['ingredients'])
    save_data('thesis/data/all_cuisine_recipes',all_cuisine_recipes)

#/////////////////////////////////////////////////////////////////////////////////////////////////


page_counter = 1
base_url = 'https://cooking.nytimes.com/search'
recipe_base_url = 'https://cooking.nytimes.com'
# url = 'https://cooking.nytimes.com/search?filters%5Bcuisines%5D%5B%5D=african&q=&page=1'
# url1 = 'https://cooking.nytimes.com/search?filters%5Bcuisines%5D%5B%5D=greek&q=&page=1'
special_recipes_dict = {}
special_diets = []

#return a list of the different special diets we have to scrape from 'https://cooking.nytimes.com/search'
def return_special_diets(url):
    ingredients_dict = {}
    page = requests.get(url)
    web_tree =  BeautifulSoup(page.text, 'html.parser')
    for ultag in web_tree.find_all('ul',{'class':'term-list term-list-special_diets'}):
        for litag in ultag.find_all('li'):
            temp_diet = litag.text.strip()
            special_diets.append(temp_diet)
    return special_diets


def save_diet():
    temp_dict= {}
    special_diets = return_special_diets(base_url)
    print(special_diets)
    page_counter = 1
    counter = 0
    for diet in special_diets:
        page_counter = 1
        print('Doinggggggggggggggg'+diet+'///////////////////////////')
        next_page =  return_next_page(diet,page_counter)
        while next_page != None:
            if next_page == str(2):
                special_recipes_dict[diet] = return_recipe_special_diets(diet,1)
            else:
                special_recipes_dict[diet].update(return_recipe_special_diets(diet,int(next_page)-1))
            page_counter = page_counter + 1
            # print('size is dictionaryyyyyyyyyyyyy of page ',int(next_page)-1 , len(special_recipes_dict[diet]))
            next_page =  return_page_list(diet,page_counter)
        if next_page == None  and page_counter==1:
            print('page', page_counter)
            special_recipes_dict[diet] = return_recipe_special_diets(diet,1)
        #save_data('special_diets_from_raw.json', special_recipes_dict)



def return_next_page(diet,counter):
    special_diet_url =' https://cooking.nytimes.com/search?filters%5Bspecial_diets%5D%5B%5D='+ diet + '&q=&page='+str(counter)
    page = requests.get(special_diet_url)
    web_tree =  BeautifulSoup(page.text, 'html.parser')
    page_list = list()
    if web_tree.find(class_ = 'page-num-list'):
        page_num = web_tree.find(class_ = 'page-num-list')
    else:
        return None
    #print(help(page_num))
    next_page = page_num.find_all('td', class_ = 'page-arrow')
    for i in range(0,len(next_page)):
        if  next_page[i].attrs['id'] == 'next-page':
            return next_page[i].attrs['data-page']
    return None


def check_and_return_nutritions(web_tree_recipe,recipe_name):
    if  web_tree_recipe.find(class_='nutrition-container')!= None:
        nutritional_description = web_tree_recipe.find(class_='nutrition-container').find(class_= 'description')
        temp_string = ''
        for x in nutritional_description.find_all('span'):
            temp_string += x.text
        temp_nutritions =  temp_string.split(';')
        for el in temp_nutritions:
            if el.isspace():
                temp_nutritions.remove(el)
        return temp_nutritions
    else:
        return None

def return_ingredients_quantity_to_lists(web_tree_recipe,recipe_name):
    ingredient_list  = list()
    quantity_list = list()
    for recipe in web_tree_recipe.find_all(class_ = 'recipe-ingredients'):
        counter = 0
        quantity = False
        for ingredient in  recipe.find_all('span',{'class':['ingredient-name','quantity']}):
            counter = counter+1
            temp_ingr = ingredient.text.strip()
            if not str(ingredient.text).isspace() or quantity==True:
                temp_ingr = ingredient.text.strip()
                if (counter % 2 )!= 0:
                    if str(temp_ingr) == '':
                        quantity_list.append('NULL')
                    else:
                        quantity= False
                        quantity_list.append(temp_ingr)
                else:
                    quantity = True
                    ingredient_list.append(temp_ingr)
            else:
                print('shittttttttttttttttttttttttttttttttttt',recipe_name,'      ',temp_ingr)
    return ingredient_list,quantity_list


def return_recipe_special_diets(diet, page_counter):
    inner_recipe_dict = {}
    nutritional_dict  = {}
    ingredient_list = list()
    quantity_list = list()
    recipes_link = list()
    special_diet_url =' https://cooking.nytimes.com/search?filters%5Bspecial_diets%5D%5B%5D='+ diet + '&q=&page='+ str(page_counter)
    print(special_diet_url)
    page = requests.get(special_diet_url)
    web_tree =  BeautifulSoup(page.text, 'html.parser')
    for recipes in web_tree.find_all('a',{'class':'card-recipe-info card-link'}):
        new_url = recipe_base_url+recipes['href']
        recipe = requests.get(new_url)
        web_tree_recipe =  BeautifulSoup(recipe.text, 'html.parser')
        tree_name = web_tree_recipe.find(class_ = 'recipe-title title name')
        if tree_name == None:
            continue
        recipe_name = tree_name.text.strip()
        nutritional_dict[recipe_name] = check_and_return_nutritions(web_tree_recipe,recipe_name)
        dictionary = dict(zip(return_ingredients_quantity_to_lists(web_tree_recipe,recipe_name)[0],return_ingredients_quantity_to_lists(web_tree_recipe,recipe_name)[1]))
        inner_recipe_dict[recipe_name] = dictionary
    if nutritional_dict != None:
        save_data('nutrional_dict.json',nutritional_dict)
    return inner_recipe_dict

def parse_special_diets():
    save_diet()

parse_special_diets()
