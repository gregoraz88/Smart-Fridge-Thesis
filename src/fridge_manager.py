import json
#from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance


# def similar(a, b):
#     return SequenceMatcher(None, a, b).ratio()


class fridge_contet:
    def __init__(self,name, content_list=None):
        self.name = name
        if content_list is None:
            content_list = {}
        self.content_list = content_list
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



##
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
            return chunck_list
    else:
        counter  = 0
        flag = recipe_size/smaller_size
        flag = int(flag)
        for i in range(0,(recipe_size)):
            if counter == flag:
                print('what')
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
    #print('recipe ingredients',cv2.get_feature_names())
    v2 = cv2.get_feature_names()
    return v2

#This function compares each element of the two category and calculates and returns their similarities
def return_ratio(chunck_list,smallest,enough_ingredients,recipe_id):
    fridge_to_recipes = list()
    for i in range(0,len(chunck_list)):
        v2 = CountVectorizer_recipe(chunck_list[i])
        print('chunks of bigger', v2)
        if enough_ingredients:
            for i in range ( 0 , len(smallest)):
                for j in range (0, len(v2)):
                    if fuzz.ratio(smallest[i].lower(),v2[j].lower()) >= 60 and   fuzz.ratio(smallest[i].lower(),v2[j].lower()) < 90:
                        print(fuzz.ratio(smallest[i].lower(),v2[j].lower()), 'for', smallest[i], v2[j])
                    if fuzz.ratio(smallest[i].lower(),v2[j].lower()) >= 90 and str(v2[j]) != '':
                        print('this fridge element ', v2[j], 'is in recipe id' ,recipe_id )
                        if v2[j] not in fridge_to_recipes:
                            fridge_to_recipes.append(v2[j])
            print(fridge_to_recipes)

        else:
            print(' NOT ENOUGH')

def return_recipe_notification(raw_ingredients, content_list,recipe_id):
    fridge_counter =  0
    recipe_size = len(raw_ingredients)
    f_food = list()
    print('this is rawwwwwwww')
    print(' ')
    for name in content_list:
        f_food.append(name)
    fridge_size = len(f_food)
    print('fridge size',fridge_size)
    print(f_food)
    print('recipe size', recipe_size)
    print(raw_ingredients)
    #fit chunck on fridge_size
    if recipe_size > fridge_size:
        print('recipe is bigger')
        chunck_list = return_raw_ingredients_into_chuncks(raw_ingredients,fridge_size)
        temp_vector = CountVectorizer_recipe(f_food)
        print('smallest', temp_vector)
        return_ratio(chunck_list, temp_vector,False,recipe_id)
    #fit chuncks on recipe_size
    elif fridge_size > recipe_size:
        print('recipe is smaller')
        chunck_list = return_raw_ingredients_into_chuncks(f_food, recipe_size)
        temp_vector = CountVectorizer_recipe(raw_ingredients)
        print('smallest', temp_vector)
        return_ratio(chunck_list,temp_vector,True,recipe_id)
    elif fridge_size == recipe_size:
        CountVectorizer_recipe(f_food)
        CountVectorizer_recipe(raw_ingredients)
    print(chunck_list)
    exit()

    # print(l)
    # exit()
    # vectorizer = TfidfTransformer(use_idf=True, norm=None)
    # vectorizer.fit(word_count_vector)
    # count_vector=cv.transform(raw_ingredients)
    # tf_idf_vector=vectorizer.transform(count_vector)
    # feature_names = cv.get_feature_names()
    # print('these are the featuresssss:', feature_names)
    # recipe_df= pd.DataFrame()
    # for i in range(len(raw_ingredients)):
    #     first_document_vector=tf_idf_vector[i]
    #     df = pd.DataFrame(first_document_vector.T.todense(), index=feature_names, columns=["tfidf"])
    #     df = df.sort_values(by=["tfidf"],ascending=False)
    #     recipe_df[i] = df.iloc[:,0]
    # print(recipe_df)
    # exit()
    # return feature_names
#def : check for the existencde of 'barcode' --barcode from scanned element --mapping to a 'barcodes.json' -- json dictionary of barcodes and respective element
#- if the 'barcode' exists in dictionary - return a True, the value of the key of the barcode -- else return false and the barcode which does not exists in the
#dictionary
def check_and_return_barcode_existance(barcode,fridge_obj):
    print(fridge_obj)
    path = 'C:/Users/gregh/Desktop/thesis/barcode_data'
    barcode = barcode[2:len(barcode)-1]
    barcode_file_path = 'barcodes_all_codes_test2_real.json'
    with open(path + '/' + barcode_file_path) as json_file:
        barcode_data = json.load(json_file)
    if barcode in barcode_data:
        el = fridge_el(barcode_data[barcode][0], barcode_data[barcode][1])# NEED TO INITIALIZE QUANTITY AS WELL
        fridge_obj.add(el)
        print(fridge_obj)
        map_ingredients_to_recipes(fridge_obj)
        return tuple((True,barcode_data[barcode]))
    else:
        print('this is the input barcode which does not exists', barcode)
        return tuple((False,barcode))

def map_ingredients_to_recipes(fridge):
    path = 'C:/Users/gregh/Desktop/thesis/all_cuisine_data'
    recipes_path = '/all_cuisine_recipes.json'
    with open(path + recipes_path) as json_file:
        recipes_data = json.load(json_file)
    for country,recipes in recipes_data.items():
        if len(recipes) <  1:
            continue
        else:
            print(country)
            # recipes key are : id, recipeName, rating,totalTimeInSeconds, course, cuisine,ingredients
            # for id, value in recipes['recipeName'].items():
            #     print(id)
            #     print(value)
            #     exit()
            for recipe_id,value in recipes['ingredients'].items():
                raw1 = list()
                raw = value.split(',')
                for el in raw:
                    el = re.sub(r'[]]','',el)
                    el = re.sub(r'[[]','',el)
                    el = re.sub(r"\s+", '-', el.lstrip())
                    raw1.append(el)
                print(raw1)
                return_recipe_notification(raw1,fridge.content_list,recipe_id)
                exit()
                # for ingredient in value.split(','):
                #     for name,quantity in fridge.content_list.items():
                #         temp_name = re.sub(r'[^\w\s]',' ',name)
                #         if fuzz.ratio(temp_name.lower(),ingredient.lower()) >= 40:
                #             print('found similaritiesssssssssssssssssssssssssssssssssssss' ,fuzz.ratio(temp_name.lower(),ingredient.lower()),'this ingredient', ingredient,'with the obj',name)
            exit()


obj1 = fridge_el('sandwi-bread', 1)
obj2 = fridge_el('buttermilks', 1)
obj3 = fridge_el('breadcorn', 1)
obj4 = fridge_el('red-pepper', 1)
obj5 = fridge_el('sage', 1)
obj6 = fridge_el('eggs', 1)
obj7 = fridge_el('onions', 1)
obj8 = fridge_el('celery', 1)
obj9 = fridge_el('butter', 1)
obj10 = fridge_el('chicken-soup', 1)
obj11= fridge_el('chicken-stock', 1)
obj12 = fridge_el('spicy-pepper', 1)

fridge = fridge_contet('JIM')
fridge.add(obj1)
fridge.add(obj2)
fridge.add(obj3)
fridge.add(obj4)
fridge.add(obj5)
fridge.add(obj6)
fridge.add(obj7)
fridge.add(obj8)
fridge.add(obj9)
fridge.add(obj10)
fridge.add(obj11)
fridge.add(obj12)

    ## two procedure
    #1 - use a sequence model to determine the correlation between fridge ingredients and different ingredients in each recipe.
    # So basically find the correlation between each ingredients in the fridge to first the title of the recipe, then ingredient in recipe.
    # when a corellation of itemX is found in fridge and recipe, then I look at the recipe which has the highest correlation, call it Y,  and then check if in my
    # fridge content there are a lot of correlation to recipe Y.
    #2 --
map_ingredients_to_recipes(fridge)
