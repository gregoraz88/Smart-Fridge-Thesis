import json
from fuzzywuzzy import fuzz
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
from map_ingredients_to_fridge import return_recipe_notification
from barcode_parser import parse_barcodes 
from parse_recipes import map_ingredients_to_special_diets,return_country_cuisine
from parse_recipes import mix_country_with_diet_recipes
from barcode_parser import sample_n_barcode,start_notification
import random
import pathlib 

src_path = pathlib.Path.cwd()
cuisine_path = src_path.parent / 'all_cuisine_data' / 'final_cuisine_recipes.json'
diet_path = src_path.parent / 'special_diets'/'final_special_diets.json'



## function to check the presence of 'temp_country' in our all_cuisine_data database, containing a json file per each country,
## and it returns the recipes from 'temp_country' if there are any.
def check_and_return_country_existance(temp_country):
    with open(cuisine_path) as json_file:
        recipes_data = json.load(json_file)
    for country,recipes in recipes_data.items():
        if fuzz.ratio(country.lower(),temp_country.lower()) >= 90:
            return (True,country,recipes)
    return False,None,None

## function to check the presence of 'temp_diet' in our special_diets database, containing a json file per each diet,
## and it returns the recipes from 'temp_diet' if there are any.
def check_and_return_diet_existance(temp_diet):
    with open(diet_path) as json_file:
        recipes_data = json.load(json_file)
    for diet,recipes in recipes_data.items():
        if fuzz.ratio(diet.lower(),temp_diet.lower()) >= 85:
            return (True,recipes_data[diet])
    return False,None

 ## class : that manages 'fridge_el' object, is practically the fridge brain, it also knows about the prequisites set by
 ## the user regarding their food preference.
class fridge_contet:
    def __init__(self,name, content_list=None,diet=None,country_cuisine=None,food_preference = None, fridge_list_vec=None):##init fridge_content 
        self.name = name
        if diet is None:
            self.diet_dict  = {}
        if country_cuisine is None:
            self.country_cuisine_dict = {}
        if content_list is None:
            self.content_list = {}
        if food_preference is None:
            self.food_preference = ''
        if fridge_list_vec is None:
            self.fridge_list_vec = list()
    def get_content_list(self):
        return self.content_list.keys()  
    def get_obj_content_list(self):
        return self.content_list.values()
    def is_content_list_empty(self):
        if self.content_list:
            return False
        else:
            return True
    def add_country_cuisine(self,country):
        if check_and_return_country_existance(country)[0]:## check the existence of 'country' in the all_cuisine_data
            print('adding this country cuisine: ', country)
            self.country_cuisine_dict[country]  = check_and_return_country_existance(country)[2]##append a dictionary : - id - rating - recipeName - ingredients 
        else:
            print('there is no such a country cuisine, sorry try again')
    def get_country_cuisine(self):
        return self.country_cuisine_dict

    def check_country_and_diet_cuisine(self):
        if bool(fridge.get_diet()) and bool(fridge.get_country_cuisine()):
            if self.food_preference == '':
                self.set_food_preference(self)
            else:
                return True
            return True
        else:
            if bool(self.get_diet()):
                self.food_preference = 'd'
                False
            if bool(self.get_country_cuisine()):
                self.food_preference = 'c'
                False
            
    def set_food_preference(self):
        print('Which food preference do you prioritize?')
        print(' ')
        print('Type ''c'' for country cuisine or ''d'' for diet or ''m'' for mixed recipes')
        choice =  input()
        self.food_preference =  choice

    def set_food_preference_for_test(self,fPref):
        self.food_preference = fPref

    def get_food_preference(self):
        return self.food_preference

    def add_diet(self,diet):
        if check_and_return_diet_existance(diet)[0]: ## check the existance of 'diet' in the special_diets database
            print('adding this diet: ', diet)
            self.diet_dict[diet] = check_and_return_diet_existance(diet)[1]
        else:
            print('there is no such a diet,sorry for the incovenience')
    def remove_diet(self,diet):
        if diet in self.diet_dict.keys():
            del self.diet_dict[diet]
        else:
            print('this diet: ',diet,' is not present in your diet dictionary')
    def remove_country_cuisine(self,country):
         if country in self.country_cuisine_dict.keys():
            del self.country_cuisine_dict[country]
         else:
            print('this country: ',country,' is not present in your country cuisine dictionary')
    def get_diet(self):
        return self.diet_dict
    def add(self,fridge_el):
        print('fridge',  fridge_el.name, self.content_list)
        if self.is_content_list_empty():
            print('list is empty')
            self.content_list[fridge_el.name] = fridge_el
            print('thiis objs from content' , self.content_list[fridge_el.name])
        else:
            if fridge_el.name in self.content_list:
                self.increment_freq(fridge_el)
            else:
                self.content_list[fridge_el.name] = fridge_el
                self.increment_freq(fridge_el)
                print(self.content_list)


    def increment_freq(self,fridge_el):
        self.content_list[fridge_el.name].increment_freq

    def return_content_size(self):
        return len(self.content_list)
    def remove(self,fridge_el):
        if self.content_list[fridge_el.name] == 1:
            del self.content_list[fridge_el.name]
        else:
            self.decrement_freq(fridge_el)
    def decrement_freq(self, fridge_el):
        self.content_list[fridge_el.name].decrement_freq
    def __str__(self):
        return 'fridge elements at '+ str(self.name)+' ^s fridge are: '+ (','.join(str(element)for element in self.content_list.items()))


## class : it represents a fridge element, this object is initiate every time an fridge element is detected. 
class fridge_el: 
    ### based on the element added, include its nutritional values
    def __init__(self,name,quantity):
        self.name = name
        self.label = 'IN' #label parameter is not implemented - future implementation
        self.freq = 1
        self.quantity =quantity
    def __str__(self):
        return str(self.name)
    def return_vec_string(self):
        return self.name.split(' ')
    def increment_freq(self):
        self.freq = self.freq+1
        print('this is freq ', self.freq)
    def decrement_freq(self):
        self.freq = self.freq-1
        print('this is minus freq ', self.freq)


#def : check for the existencde of 'barcode' --barcode from scanned element --mapping to a 'barcodes.json' -- json dictionary of barcodes and respective element
#- if the 'barcode' exists in dictionary - return a True, the value of the key of the barcode -- else return false and the barcode which does not exists in the
#dictionary
def check_and_return_barcode_existance(barcode,fridge_obj):
    print(fridge_obj)
    path = 'C:/Users/gregh/Desktop/thesis/Smart-Fridge-Thesis/barcode_data'
    barcode = barcode[2:len(barcode)-1]
    barcode_file_path = 'barcodes_all_codes_test2_real.json'
    with open(path + '/' + barcode_file_path) as json_file:
        barcode_data = json.load(json_file)
    if barcode in barcode_data:
        el = fridge_el(barcode_data[barcode][0], barcode_data[barcode][1])
        fridge_obj.add(el)
        print(fridge_obj)
        map_ingredients_to_recipes(fridge_obj)
        return tuple((True,barcode_data[barcode]))
    else:
        print('this is the input barcode which does not exists', barcode)
        return tuple((False,barcode))

#
def map_ingredients_to_recipes(fridge):
    print('in mapping')
    list_country_recipes = list()
    recipe_string_list = list()
    if not  fridge.is_content_list_empty():
        fridge.check_country_and_diet_cuisine()
        if fridge.get_food_preference == 'm':
            mixed_recipe = mix_country_with_diet_recipes(fridge)
            ##process_notification_system(recipes,fridge)
            parse_barcodes(mixed_recipes, fridge)
            exit()

        if bool(fridge.get_diet()) or fridge.get_food_preference == 'd':
            print('speciallllllllllllllllllllll')
            map_ingredients_to_special_diets(fridge)
            exit()
        else:
            print('no diettt recipes')
        if bool(fridge.get_country_cuisine()) or fridge.get_food_preference == 'c':
            country_string_list = return_country_cuisine(fridge)
            print(country_string_list)
            start_notification(country_string_list,Fridge)
            #parse_barcodes(country_string_list,fridge)
            exit()
        else:
            print('no country cuisine')
    else:
        print('There is not fridge element')
                    #return_recipe_notification(raw1,fridge.content_list,recipe_id)








## test section:

#create three different tests with different size of fridge element from 5-20-50
#each of sample size will be tested on three different recipes correlation -
# 1 we will random select a country cuisine from the all_cuisine_data and test it and all size
# 2 we will random select a special diet from special_diets and test is and all size
# 3 we will  select a mix of recipes between a random special diet and a random country cuisine and test is and all size


obj1 = fridge_el('sandwi-bread', 1)
obj2 = fridge_el('dark chocolate and sea salt farm brothers',1)
obj3 = fridge_el('buttermilks', 1)
# obj3 = fridge_el('breadcorn', 1)
# obj4 = fridge_el('red-pepper', 1)
# obj5 = fridge_el('sage', 1)
# obj6 = fridge_el('eggs', 1)
# obj7 = fridge_el('onions', 1)
# obj8 = fridge_el('g', 1)
# obj9 = fridge_el('butter', 1)
# obj10 = fridge_el('chicken-soup', 1)
# obj11= fridge_el('chicken-stock', 1)
# obj12 = fridge_el('pasta',1)
# obj13= fridge_el('oil', 1)



def add_sampled_elements_and_food_preference_to_fridge(n,food_preference):
    print('callingggg')
    #fridge.set_food_preference() -- instead of letting the user set_food_preference, i create another function that return one of the three choice - country cuisine - special diet - or mixed recipes
    fridge.set_food_preference_for_test(food_preference)
    fridge_list,fridge_list_vec = sample_n_barcode(n)
    print('There are  ', len(fridge_list), 'in your fridge, with food_preference ', fridge.get_food_preference())

    for i in range(0,len(fridge_list)):
        print('this is ellll ', fridge_list[i])
        temp_obj = fridge_el(fridge_list[i],1)
        fridge.add(temp_obj)


    #process_random_recipe_type()
    set_random_cuisine_recipe()

    #print(fridge.get_country_cuisine())

def set_random_cuisine_recipe():
    print('thisss ', fridge.food_preference)
    if fridge.food_preference == 'c':
        with open(cuisine_path) as json_file:
            recipes_data = json.load(json_file)
        fridge.add_country_cuisine(random.choice(list(recipes_data.keys())))


    if fridge.food_preference == 'd':
        with open(diet_path) as json_file:
            recipes_data = json.load(json_file)
        print(random.choice(list(recipes_data.keys())))
        fridge.add_diet(random.choice(list(recipes_data.keys())))

      
fridge = fridge_contet('JIM')
     
def main():
    add_sampled_elements_and_food_preference_to_fridge(10,'d')
    map_ingredients_to_recipes(fridge)
    exit()

main()


#fridge.add_country_cuisine('american')
#fridge.add_country_cuisine('mexican')
#fridge.add_diet('dairy-free')
#fridge.add_diet('gluten-free')
#print(fridge.get_diet())
#print(fridge.get_country_cuisine())
#fridge.add(obj3)


#print(fridge.get_content_list())
# fridge.add(obj4)
# fridge.add(obj5)
# fridge.add(obj6)
# fridge.add(obj7)
# fridge.add(obj8)
# fridge.add(obj9)
# fridge.add(obj10)
# fridge.add(obj11)
# fridge.add(obj12)
# fridge.add(obj13)

    ## two procedure
    #1 - use a sequence model to determine the correlation between fridge ingredients and different ingredients in each recipe.
    # So basically find the correlation between each ingredients in the fridge to first the title of the recipe, then ingredient in recipe.
    # when a corellation of itemX is found in fridge and recipe, then I look at the recipe which has the highest correlation, call it Y,  and then check if in my
    # fridge content there are a lot of correlation to recipe Y.
    #2 --

