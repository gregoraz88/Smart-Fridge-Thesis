import json
#from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
from map_ingredients_to_fridge import return_recipe_notification
from barcode_parser import parse_barcodes 
from parse_recipes import map_ingredients_to_special_diets



def check_and_return_country_existance(temp_country):
    path = 'C:/Users/gregh/Desktop/thesis/Smart-Fridge-Thesis/all_cuisine_data'
    recipes_path = '/final_cuisine_recipes.json'
    with open(path + recipes_path) as json_file:
        recipes_data = json.load(json_file)
    for country,recipes in recipes_data.items():
        if fuzz.ratio(country.lower(),temp_country.lower()) >= 90:
            return (True,country,recipes)
    return False,None,None

def check_and_return_diet_existance(temp_diet):
    path = 'C:/Users/gregh/Desktop/thesis/Smart-Fridge-Thesis/special_diets'
    recipes_path = '/final_special_diets.json'
    with open(path + recipes_path) as json_file:
        recipes_data = json.load(json_file)
    for diet,recipes in recipes_data.items():
        if fuzz.ratio(diet.lower(),temp_diet.lower()) >= 85:
            return (True,recipes_data[diet])
    return False,None


class fridge_contet:
    def __init__(self,name, content_list=None,diet=None,country_cuisine=None):
        self.name = name
        if diet is None:
            self.diet_dict  = {}
        if country_cuisine is None:
            self.country_cuisine_dict = {}
        if content_list is None:
            self.content_list = {}
    def get_content_list(self):
        return self.content_list
    def add_country_cuisine(self,country):
        if check_and_return_country_existance(country)[0]:
            print('adding this country cuisine: ', country)
            self.country_cuisine_dict[country]  = check_and_return_country_existance(country)[2]##append a dictionary : - id - rating - recipeName - ingredients 
        else:
            print('there is no such a country cuisine, sorry try again')
    def get_country_cuisine(self):
        return self.country_cuisine_dict
    def add_diet(self,diet):
        if check_and_return_diet_existance(diet)[0]:
            print('adding this diet: ', diet)
            self.diet_dict[diet] = check_and_return_diet_existance(diet)[1]
        else:
            print('there is no such a diet,sorry for the incovenience')
    def remove_diet(self,diet):
        if diet in self.diet_dict.keys():
            del self.diet_dict[diet]
        else:
            print('this diet: ',diet,'is not present in your diet dictionary')
    def remove_country_cuisine(self,country):
         if country in self.country_cuisine_dict.keys():
            del self.country_cuisine_dict[country]
         else:
            print('this country: ',country,'is not present in your country cuisine dictionary')
    def get_diet(self):
        return self.diet_dict
    def add(self,fridge_el):
        if fridge_el.name in self.content_list:
            self.increment_freq(fridge_el)
        else:
            self.content_list[fridge_el.name] = (fridge_el.quantity,1)
    def increment_freq(self,fridge_el):
        self.content_list[fridge_el.name] = self.content_list[fridge_el.name]+1
    def remove(self,fridge_el):
        if self.content_list[fridge_el.name] == 1:
            del self.content_list[fridge_el.name]
        else:
            self.decrement_freq(fridge_el)
    def decrement_freq(self, fridge_el):
        self.content_list[fridge_el.name] =  self.content_list[fridge_el.name]-1
    def __str__(self):
        return 'fridge elements at '+ str(self.name)+' ^s fridge are: '+ (','.join(str(element)for element in self.content_list.items()))


class fridge_el:
    ### based on the element added, include its nutritional values
    def __init__(self,name,quantity):
        self.name = name
        self.label = 'IN'
        self.freq = 1
        self.quantity =quantity
    def __str__(self):
        return str(self.name)

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


def map_ingredients_to_recipes(fridge):
    print('in mapping')
    list_country_recipes = list()
    recipe_string_list = list()
    if bool(fridge.get_diet):
        #Extractopic(fridge,check_and_return_diet_existance(fridge.get_diet()[0])[1])
        print('speciallllllllllllllllllllll')
        map_ingredients_to_special_diets(fridge)
        exit()
    else:
        if bool(fridge.country_cuisine_dict):
            country_recipe_dict =  fridge.get_country_cuisine()
            for key , informations in country_recipe_dict.items():
                print(key)
                #print(informations)              
                # recipes key are : id, recipeName, rating,totalTimeInSeconds, course, cuisine,ingredients
                for recipe_id,value in informations['ingredients'].items():
                    print('this is recie',recipe_id)
                    print('this name of recipes', informations['recipeName'][recipe_id])
                    exit()
                    raw1 = list()
                    raw = value.split(',')
                    for el in raw:
                        el = re.sub(r'[^\w\s]','',el)
                        el = re.sub(r"\s+", ' ', el.lstrip())
                        print(el)
                        #parse_barcodes(el)
                        #continue
                        raw1.append(el)
                    #print(raw1)
                    print('this is raw recipe', raw1)
                    recipe_string_list.append((raw1,recipe_id))
                    if len(recipe_string_list) > 3:
                        parse_barcodes(recipe_string_list)
                        exit()
                    else:
                        print('NOT YETTTTTTTTTTTTTTT')
                        continue

                # if parse_barcodes(raw1)[0] == False:
                #     print('PARSE BARCODE ITS FALSE')
                #     continue
                # else:
                #     print('this is id ', recipe_id)
                #     print('there is a similarity in recipe', recipes['recipeName'][recipe_id])
                #     result = parse_barcodes(raw1)
                #     print(raw1)
                #     ind = result[1]
                #     vec = result[2]
                #     print(vec)
                #     print(ind)
                #     # for i in range(0,len(ind)):
                #     #     print('similar ingredients to recipes',vec[i[0]][i[1]])
                #     exit()
        else:
            print('no country')
                #return_recipe_notification(raw1,fridge.content_list,recipe_id)



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

fridge = fridge_contet('JIM')
fridge.add(obj1)
fridge.add(obj2)
fridge.add_country_cuisine('american')
#fridge.add_country_cuisine('mexican')
fridge.add_diet('dairy-free')
fridge.add_diet('gluten-free')
#print(fridge.get_diet())
#print(fridge.get_country_cuisine())
fridge.add(obj3)
map_ingredients_to_recipes(fridge)
exit()
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
