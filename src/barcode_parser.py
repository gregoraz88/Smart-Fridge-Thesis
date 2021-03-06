import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer,TfidfTransformer
import en_core_web_sm
import spacy
import os
import os.path
from spacy.tokens import Doc,Span,Token
from spacy.matcher import Matcher
from numpy import dot
from numpy.linalg import norm
import numpy as np
import random
import string
from nltk.corpus import stopwords
from process_syntax import parse_semantic
import itertools
import pathlib
nlp = spacy.load('en_core_web_md')


src_path = pathlib.Path.cwd() ## initialize src path
barcode_path = src_path.parent / 'barcode_data' / 'translated_barcode.json'
output_path = os.path.join(str(src_path.parent) , 'output_data\Evaluation')
preSimilarityProcess = {}

def meanv(coords):#return mean between vector
    if bool(coords):
        sumv = [0] * len(coords[0]) ##check for error here - there is no index zero so no element is passsed, it s an indexerrro
        for item in coords:
            for i in range(len(item)):
                sumv[i] += item[i]
        mean = [0] * len(sumv)
        for i in range(len(sumv)):
            mean[i] = float(sumv[i]) / len(coords)
    else:
        return None
    return mean

def CountVectorizer_special_recipe(chunck):#returns features name of the passed vector
    cv2=CountVectorizer(analyzer = 'word' ,stop_words = 'english', lowercase = True , ngram_range=(1,2))
    for x in chunck:
        if  x not in stopwords.words('english'):
                word_count_vector2=cv2.fit_transform(chunck)
                v2 = cv2.get_feature_names()
                return v2
        else:
            continue
    return None

def cosine(v1, v2):#returns cosine value between two vectors
    if type(v1)  == None or type(v2) == None:
        return 0.0
    else:
        if norm(v1) > 0 and norm(v2) > 0:
            return dot(v1, v2) / (norm(v1) * norm(v2))
        else:
            return 0.0

def spacy_closest(token_list, vec_to_check, n):#returns sorted token_list in descending order of cosine value to the vec_to_check
    print('vec to cechk', vec_to_check)
    return sorted(token_list,
                  key=lambda x: cosine(vec_to_check, vec(x)),
                  reverse=True)[:n]

def vec(s):# returns a vector of 300 dimension of the passed string s
    return nlp.vocab[s].vector

def sentvec(s):## returns a vector made of multiple vector in a sentence
    sent = nlp(s)
    return meanv([w.vector for w in sent])

def spacy_closest_sent(space, input_str, n=10):#returns sorted token_list in descending order of cosine value to the vec_to_check
    print('input string', input_str)
    input_vec = sentvec(input_str)
    return sorted(space,
                  key=lambda x: cosine(np.mean([w.vector for w in x], axis=0), input_vec),
                  reverse=True)[:n]

def sample_n_barcode(n):#this function returns a sample number barcodes taken from the dataset translated_barcode in the barcode_data folder
    with open(barcode_path) as json_file:
        barcode_data = json.load(json_file)
    dictionary = random.sample(barcode_data.items(),n)
    fridge_list = list()
    fridge_list_vec = list()
    for barcode, ingredient in dict(dictionary).items():#ingredient - list(ingredient,quantity)
        cleaned_fridge_ingredients = re.sub(r"[^A-Za-z()]", " ", ingredient[0])
        try:
            vector = CountVectorizer_special_recipe(cleaned_fridge_ingredients.split(' '))
        except ValueError:
                    print('empty vocabulary')
                    continue
        if not vector:
            print('this is empty vector',vector)
            continue
        temp_fridge = ' '.join(vector)
        ##delete some redundant and useless informations from barcode 
        temp_fridge = temp_fridge.replace('albert','')
        temp_fridge = temp_fridge.replace('heijn','')
        temp_fridge = temp_fridge.replace('ah','')
        temp_fridge = temp_fridge.replace('jumbo','')
        temp_fridge = temp_fridge.replace('ekoplaza','')
        temp_fridge = temp_fridge.replace('hellmann','')
        temp_fridge =  temp_fridge.replace('hema','')
        if temp_fridge and temp_fridge != ' ':
            temp_fridge  = parse_semantic(temp_fridge)## returns a fridge ingredient after the syntax parsing
            fridge_list.append(temp_fridge.strip())
            fridge_list_vec.append(temp_fridge.split(' '))
            continue
        else:
            print('empty element')
            continue

    return fridge_list, fridge_list_vec

def check_extension(fride_doc, recipe_doc):# this function checks if at least one correlation between fridge element and a recipe ingredient is bigger than 0.70, if there is it return True
    print('this is recipe', recipe_doc)
    for f in fride_doc:
        #print('this is fridge',f )
        if f == '':
            continue
        else:
            has_similar_to_fridge = lambda r_obj : any([cosine(sentvec(f),sentvec(r.text))> 0.7 for r in r_obj])
            Doc.set_extension('has_similar_element', getter = has_similar_to_fridge, force = True)
            if recipe_doc._.has_similar_element:
                return True, f , recipe_doc
            else:
                continue
    return False, None , None


def start_notification(recipes,fridge_obj,cuisine):#this function starts the notification process, first calls parse_barcode and retrieves similar ingredients between fridge and recipe then a notification object is created and the process notifications is called
    similar_ingredients= parse_barcodes(recipes,fridge_obj)#define similar ingredient before notification check
    if similar_ingredients != None:#check if there exists any similar ingredient
        n_obj = notification(fridge_obj.food_preference,similar_ingredients,recipes, fridge_obj)#initialize the notification object for further comparison checking
        n_obj.fridge_obj.set_current_cuisine(cuisine)
        process_notification(n_obj)#start the notification check on the interested notification object
        
def compareFridge_toRecipeIngre(split_fridge,split_recipe): #return missing element,similar element and,close element between fridge ingre and recipe ingre
    print('Compare Fridge Ingredient to Recipe Ingredient')
    print('')
    tempSimilar = list()
    close_temp = list()
    diffFridgeComp = list()
    whatisPresent = list()
    for r in split_recipe:
        if r == None or r == '' or r == ' ':
            continue
        for f in split_fridge:
            #print('this is super inner cosine ', cosine(vec(r),vec(f) ),'for recipe ', r , 'for fridge ', f)
            if cosine (vec(r),vec(f)) >= 0.99:
                print('There is an exact match between fridge element  ', f , 'and recipe ingredient ', r)
                if f not in whatisPresent:
                    whatisPresent.append(f)
                    whatisPresent.append(r)
                continue
            if cosine(vec(r),vec(f)) >= 0.70 and  cosine(vec(r),vec(f)) < 0.99:
                #print('PLUSSSSSSSSSSSSSSSSSSSS for ', r , 'with ', f)
                print('thre is a high similarity between ', f, 'and recipe ingredient ', r)
                if f not in tempSimilar:
                    tempSimilar.append(f)
                continue
            else:
                print('bad cosine ratio for fridge element' , f,  ' with  ', r )
                if f not in diffFridgeComp:
                    #print('f not in diff ,  ',  f)
                    diffFridgeComp.append(f)
                continue
    if tempSimilar or whatisPresent:
        print(' ')
        print('There is something present or similar in this comparison')
        #print('this is diffFridgeComp before intersectioon ' , diffFridgeComp)
        whatisMissing =list(set(split_recipe) - (set(tempSimilar).union(set(whatisPresent)) ))
        if whatisMissing == split_recipe:
            NoSameFridgeEl = True
        else:
            NoSameFridgeEl = False

        diffFridgeComp = list(set(diffFridgeComp) -  (set(tempSimilar).union(set(whatisPresent)) ))

        print('Missing ', whatisMissing, 'Present ', whatisPresent, 'Temp close ', diffFridgeComp, 'Temp similar ' , tempSimilar)
        return whatisMissing,whatisPresent,tempSimilar,diffFridgeComp,NoSameFridgeEl

    else:
        print('')
        print('There is not something present or similar in this comparison')
        print(' ')
        print('All recipe is Missing ',  split_recipe, 'difference in fridge elements ', diffFridgeComp)
        return split_recipe,None,None,diffFridgeComp,True

#class notification which defines a set of correlation between fridge ingredients and recipes, at each corellation the notification parameters are updated pointing to the interested correlations
class notification:
    def __init__(self,food_preference1, similar_ingredient_ind1, dict_of_recipe1, fridge_obj1 ):
        self.food_preference = food_preference1
        self.similar_ingredient_ind = similar_ingredient_ind1   
        self.dict_of_recipe = dict_of_recipe1
        self.recipe_size =  len(self.dict_of_recipe)
        self.fridge_obj = fridge_obj1
        self.id = None
        self.j = None
        self.ingre = None
        self.cosine_value = None
        self.r_id = None
        self.recipe_name = None
        self.r_country = None
        self.notification_outputDict = {}
        self.identification_number = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))

    def set_notification_parameter(self,output):#this parameters for the notification object are updated for each correlation between fridge and recipe ingredient
        print('this is obj ', output[0])
        self.id = output[0]
        self.j = int(output[1])
        self.ingre = int(output[2])
        self.cosine_value = output[4]
        if self.food_preference == 'c':
            self.recipe_name = str(output[3])
            temp = str(output[3]).split('-')
            self.r_id = temp[0]
            self.r_country = temp[1]
        else:
            self.recipe_name = str(output[3])

    def set_notification_output(self,notification_outputDict):
        self.notification_outputDict.update( notification_outputDict)
        print('this is updated notification dict,' , self.notification_outputDict)

    def get_identification_number(self):
        return self.identification_number
  

def save_output(filename,data):
    with open(filename, 'w') as f:
        json.dump(data, f)
        
def parse_barcodes(dict_of_recipe,fridge_obj):#this function returns a list of correlations between recipe and fridge ingredient, it returns similar_ingredient list each element has all informations necessary to print the correlation between the two
    list_of_recipe = list()
    for recipe_dict in dict_of_recipe:
        list_of_recipe.append((  ( list( itertools.chain.from_iterable( (list(recipe_dict.values())) ) ) ) , list(recipe_dict.keys()) ))
    similar_ingredient = False
    similarityCounter=  0
    similar_ingredient_ind =list()
    possible_options = list()
    cosine_val  = 0.0
    flag = False
    if fridge_obj.return_content_size() > 2:##return content list size
        for recipe in list_of_recipe: ## recipe contains - [0] -- recipe ingredients [1] -- recipe_id
            recipe_doc = nlp(' '.join(recipe[0]))
            #print('doc', recipe_doc)
            if check_extension(fridge_obj.get_content_list(),recipe_doc)[0]:#if check_extension returns true we start comparing each element of two dataset
                print('EXTENSION TRUE WITH RECIPE', recipe[0])
                recipe_string_list = recipe[0]
                r_id = ' '.join(recipe[1])
                for obj in fridge_obj.get_obj_content_list():#loop through all fridge objects
                    vectorized_fridge_name = obj.return_vec_string()
                    print(' ')
                    if cosine(sentvec(' '.join(recipe_string_list )), sentvec(obj.name)) >= 0.55:
                        similar_ingredient = False
                        #print('this is the cosine: ',cosine(sentvec(' '.join(recipe_string_list )), sentvec(obj.name)), 'for fridge el', obj.name,'and recipe ingredient sent ', ' '.join(recipe_string_list ) )
                        for j in range(0,len(vectorized_fridge_name)):
                            if not vectorized_fridge_name or vectorized_fridge_name == '' and similar_ingredient == True:
                                #print('contnueeeeee for fridge', vectorized_fridge_name)
                                continue
                            for g in range(0,(len(recipe_string_list))):
                                if cosine(vec(vectorized_fridge_name[j]), sentvec(recipe_string_list[g])) > 0.75: 
                                    print('inner correlation ' , vectorized_fridge_name[j],' ',  recipe_string_list[g] )
                                    if cosine(sentvec(obj.name), sentvec(recipe_string_list[g])) >= 0.80:
                                        print('There is correlation between ' , obj.name,' '  ,recipe_string_list[g])
                                        cosine_val = cosine(sentvec(obj.name), sentvec(recipe_string_list[g]))
                                        ##pass the id of object and find it in content_list
                                        similar_ingredient = True
                                        if ((obj,j,g,r_id,cosine_val) not in similar_ingredient_ind):
                                            similar_ingredient_ind.append((obj,j,g,r_id,cosine_val))
                                            split_recipe  = recipe_string_list[g].split(' ')
                                            split_fridge = obj.name
                                            break
                                        #print('this is spit recipe' , split_recipe)
                                        #print('this is split fridge' , split_fridge)
                                else:
                                    print('value low ', obj.name)
                                    continue
                    else:
                        print('value too low for ingre', obj.name)
                        continue

            else:
                print('NO EXTENSION')
                continue

        print('this is similar ingredients index' , similar_ingredient_ind)
        print('this is length ', len(similar_ingredient_ind))
        
        return similar_ingredient_ind #in similar ingredient there is stored per each corellation
                                      #(the notification object, (j)the index at which the string of the fridge ingredient is most similar to the ingredient recipe, the index of the ingredient in the recipe, the recipe id, the cosine value between the two ingredients )
    else:
        print('too few ingredients')
        return None

def save_output_for_evaluation(n_obj, percentage_similarity_list):#save the pre and post 
  
    food_path = ''
    if n_obj.fridge_obj.get_food_preference()  == 'c':
        cuisine_dir =''
        cuisine_dir = n_obj.fridge_obj.get_current_cuisine()

        temp_cuisine_path= os.path.join(str(output_path),'Country-Cuisine')
        cuisine_path = os.path.join(str(temp_cuisine_path), cuisine_dir)
        if not os.path.isdir(cuisine_path):
            os.mkdir(cuisine_path)
        food_path = cuisine_path
      

    else:
       diet_dir = ''
       diet_dir = n_obj.fridge_obj.get_current_cuisine()
       temp_diet_path= os.path.join(str(output_path),'Diets')
       diet_path = os.path.join(str(temp_diet_path), diet_dir)
     
       if not os.path.isdir(diet_path):
           os.mkdir(diet_path)
       food_path = diet_path

    if not os.path.isdir(os.path.join(str(food_path), n_obj.get_identification_number())):
        os.mkdir(os.path.join(str(food_path), n_obj.get_identification_number()))


    
    food_path =  os.path.join(str(food_path), n_obj.get_identification_number())


    save_output(os.path.join(food_path, 'prenotification_process'+n_obj.identification_number+'.json'), preSimilarityProcess)
    save_output(os.path.join(food_path,'postnotification_process'+n_obj.identification_number+'-'+str(n_obj.fridge_obj.get_len_content_list())+'-'+n_obj.fridge_obj.get_food_preference()+'.json'), n_obj.notification_outputDict)
    save_output(os.path.join(food_path,'fridgeElements'+n_obj.identification_number+'.json'), list(n_obj.fridge_obj.get_content_list()))
    preVspostnotification_dict = compare_Pre_Post_Notification(food_path,n_obj)
    evalaution_dict = {'fridge_size' : n_obj.fridge_obj.get_len_content_list() ,  'correlated_recipe_size' : len(n_obj.notification_outputDict.keys()),  'recipe_size' : n_obj.recipe_size, 'percentage_similarity' : percentage_similarity_list, 'pre_post_notification_difference': preVspostnotification_dict  }
    save_output(os.path.join(food_path,'statistical_evaluation.json'), evalaution_dict)

    
  
def compare_Pre_Post_Notification(food_path,n_obj):
    open_pre_json = open(os.path.join(str(food_path),'prenotification_process'+n_obj.identification_number+'.json') )
    pre_notifiction_json = json.load(open_pre_json)

   
    open_post_json = open(os.path.join(str(food_path),'postnotification_process'+n_obj.identification_number+'-'+str(n_obj.fridge_obj.get_len_content_list())+'-'+n_obj.fridge_obj.get_food_preference()+'.json') )
    post_notifiction_json = json.load(open_post_json)

    evaluatio_tuple_list = dict()

    
    for key,items in pre_notifiction_json.items():
        if key not in list(post_notifiction_json.keys()):
            continue
            print('For this key ', key, 'there is not post notification')
        else:
            similar_pairs,diff_pairs, evaluatio_tuple_list[key] = return_union_intersection(key,pre_notifiction_json, post_notifiction_json)
            print('')      
            print('For recipe key ,', key)
            print(' ')
            print('Prenotificatio ', pre_notifiction_json[key])
            print(' ')
            print('Postnotitication ', post_notifiction_json[key])
            print(' ')
            print('simialr pairs ',similar_pairs)
            print(' ')
            print('diif pairs ',diff_pairs)
    return evaluatio_tuple_list
    
def return_union_intersection(key,pre_notifiction_json,post_notifiction_json):
    temp_post = post_notifiction_json[key]
    temp_pre = pre_notifiction_json[key]    
    diff_between_pre_and_post = len(temp_pre) - len(temp_post) 
    diff_pairs  =list()
    similar_pairs = list()

    for pre in temp_pre:
        tag_adding=True
        for post in temp_post:
            if pre != post[0:len(post)-1]:
                if tag_adding:
                    tag_adding = True
                else:
                    break
            else:
                tag_adding=False
        if tag_adding:
            if pre not in diff_pairs:
                    print('this is not equal', pre, 'with' ,  post[0:len(post)-1])
                    diff_pairs.append(pre)


    return temp_post,diff_pairs,diff_between_pre_and_post

def print_notification(n_obj):#print notification for recipes in which there is at least one correlation
    recipe_list = list()
    recipe_percentage_list = list()
    recipe_dictionary = {}
    #make a dictionary out of list of dictionary
    keys = list()
    values  = list()
    for dict_r in n_obj.dict_of_recipe:
        keys.append(list(dict_r.keys())[0])
        values.append(list(dict_r.values())[0])
    recipe_dictionary = dict(zip(keys, values))

    #print('this is reciepe dictionary ' ,recipe_dictionary.keys())
    print()
    print('this are the fridge ingredients ' , n_obj.fridge_obj.get_content_list())
    print()
    ##check on accuracy 
   

    #prepare the printing for each recipe, print both the similar ingredient and the missing ingredients if there are any.
    if not n_obj.notification_outputDict:
        print('There no recipes correlation between your fridge ingredients and the recipes suggested, from category: ',n_obj.fridge_obj.get_current_cuisine() , ' for recipes ID' , keys )
    else:
        print('The output dict is not empty for cuisine type ', n_obj.fridge_obj.get_current_cuisine())
        for recipe_key, possible_ingredients in n_obj.notification_outputDict.items():
            print()
            #print('recipe key ', recipe_key)
            #print('possible ingredients ', possible_ingredients)
            #print('full recipe: ', recipe_dictionary[recipe_key])
            #print()
            missing_ingredients = list(recipe_dictionary[recipe_key])
            for tuple_el in possible_ingredients:
                missing_ingredients.remove(str(tuple_el[1]))

            recipe_length = len(list(recipe_dictionary[recipe_key]))
            similar_ingredient=  len(possible_ingredients)

            percentage_similarity = (100*similar_ingredient)/recipe_length

            recipe_percentage_list.append(percentage_similarity) 
            print('  ')
            if n_obj.fridge_obj.get_food_preference() == 'c':
                recipe_id = recipe_key.split('-') # recipe_id[0]- number of the recipe id needed for retrieving the recipe in the dictionary , recipeid[1] contains the country cuisine 
                country_dict = n_obj.fridge_obj.get_country_cuisine()
                if len(recipe_id) > 2:
                    temp_recipe_key = ('-').join(recipe_id[1:len(recipe_id)])
                else:
                    temp_recipe_key = recipe_id[1]

                print(' For recipe  ',  country_dict[temp_recipe_key]['recipeName'][recipe_id[0]], 'there is ',percentage_similarity,' similarity. \n  There are ',  len(possible_ingredients) , 'ingredients that are similar to the actual recipe.\n    This is are the following:' ,  possible_ingredients, '\n    and there are ', len(recipe_dictionary[recipe_key])-len(possible_ingredients), ' missing ingredients, \n    which are the following: ',missing_ingredients  )
                print()
            else:
                print(' For recipe  ',  recipe_key, 'there is ',percentage_similarity,' similarity. \n  There are ',  len(possible_ingredients) , 'ingredients that are similar to the actual recipe.\n    This is are the following:' ,  possible_ingredients, '\n    and there are ', len(recipe_dictionary[recipe_key])-len(possible_ingredients), ' missing ingredients, \n    which are the following: ',missing_ingredients  )
           
            if recipe_key not in recipe_list:
                recipe_list.append(recipe_key)
            else:
                continue
    save_output_for_evaluation(n_obj, recipe_percentage_list)
           
def processComparison(split_fridge,split_recipe):#process an external comparison between recipe and ingredient correlation of what the 'compareFridge_toRecipeIngre' returns, check what are the main differnces and similarities between the two correlated ingredients
  
    missingElements,presentElements,similarElements,differenceInFridge,NoSameFridgeEl = compareFridge_toRecipeIngre(split_fridge,split_recipe)
    print(' ')
    print('Process the comparison of compareFridge_toRecipeIngre')
    print(' ')
    if presentElements != None or similarElements != None:
        
        if not missingElements and not differenceInFridge:
            return (True,'No missing',[],split_fridge,[],split_recipe)
            
        if not missingElements:
            print('nothing missing for recipe but some extra ingree, this is what is extra from fridge ',differenceInFridge )
            return (True,'No missing',[],split_fridge,[],split_recipe)
            
        if missingElements :
            checkFlag = False
            missing_only = True
            similarityCounter = 0
            if presentElements:
                missing_only = False
                similarityCounter += 1
            print('there is something missing and something extra in the comparison')
            if differenceInFridge:
                missing_only = False
                for m in missingElements:
                    for f in differenceInFridge:
                        if cosine(sentvec(m), sentvec(f)) >= 0.75:
                            print('not too bad cosine' , cosine(sentvec(m), sentvec(f)), 'between m and s' , m ,' and ' , f)
                            checkFlag = True
                            continue
                        else:
                            print(' baaaaaad cosine' , cosine(sentvec(m), sentvec(f)), 'between m and s' , m ,' and ' , f)
                            continue
            if similarElements:
                missing_only = False
                for m in missingElements:
                    for s in similarElements:
                        if cosine(sentvec(m), sentvec(s)) >= 0.75:
                                print('not too bad cosine' , cosine(sentvec(m), sentvec(s)), 'between m and p' , m ,' and ' , s)
                                checkFlag = True
                                continue
            if  missing_only:
                print('only missing ingredientsssssssss')
                return ('True', 'Missing', missingElements,similarElements)
            else:
                if checkFlag == False:
                    similarityCounter -= 1
                else:
                    similarityCounter += 1
            
                if len(missingElements) == 1:       
                    if (similarityCounter >= len(missingElements)):
                        return(True,'Incomplete_High',missingElements,differenceInFridge,similarElements)
                    else:
                        return (False,'Incomplete_Low',missingElements,differenceInFridge,similarElements)

                else:
                    if similarityCounter >= len(missingElements)-1 :
                        print('adding while something missing')
                        return (True,'Incomplete_High',missingElements,differenceInFridge,similarElements)
           
                    else:
                        print('nothing added similarity counter too low  ', similarityCounter)
                        return (False,'Incomplete_Low',missingElements,differenceInFridge,similarElements)
                                            
        if  differenceInFridge:
            good_extra = list()
            bad_extra = list()
            notToBad = 0
            print('there is something extra in fridge')
            for f in differenceInFridge:
                for s in similarElements:
                    if cosine(sentvec(f), sentvec(s)) >= 0.80:
                        good_extra.append((f,s))
                        notToBad += 1
                        continue
                    else:
                        bad_extra.append( (f,s))
                        continue
            if good_extra:
                    #print('adding while something extra is in fridge')
                    return (True,'Good_Extra' , [],good_extra,bad_extra,similarElements)
            else:
                return (False, 'Bad_Extra', [],[], bad_extra,similarElements)

        else:
            print('look more in depthhhhhhhhhhhhhhhhhhhhhh')
    else:
        print('no correlation between fridge ',  split_fridge,' to recipe ' ,split_recipe)
        #print('this is badddddddddddddddddddddd cosine for inner fridge el',fridge_list[i],' and recipe ingredient' , recipe_string_list[g], cosine(sentvec(fridge_list[i]), sentvec(recipe_string_list[g])))
        return (False,'Bad')

def make_notification(n_obj):#in this function we updated we set_notification_output and we make sure only relevant correlations are used to set_notification_output, this function updates a the notification_outputDict dictionary, in which per each recipes we have the interested correlations. 
    
    print('calling make notificatiin with obj ', n_obj)
    notification_outputDict = {}
    for dict_r in n_obj.dict_of_recipe:
        if n_obj.recipe_name in dict_r.keys():
            print('')
            print('U have a correlation with recipe :'  , n_obj.recipe_name )
            print(' ')
            print('Start process of checking comparison')
            split_recipe  = list(dict_r[n_obj.recipe_name])[n_obj.ingre].split(' ')#one element of the recipe at ingre
            split_fridge = n_obj.id.return_vec_string() # one fridge element at i
            if n_obj.recipe_name not in list(preSimilarityProcess.keys()):
                preSimilarityProcess[n_obj.recipe_name] = list()
            
            temp_list = ((' ').join(split_fridge),(' ').join(split_recipe),n_obj.cosine_value)
            preSimilarityProcess[n_obj.recipe_name].append(temp_list)
            print('')
            print('fridge' ,split_fridge)
            print('recipe',split_recipe)
            if n_obj.recipe_name not in n_obj.notification_outputDict.keys():#if the name of the recipe is not in our suggested recipes
                comparison = processComparison(split_fridge,split_recipe)#process a comparisong between fridge el and recipe el
                print(' ')
                if comparison[0]:# if there is a True, it means the comparison should be strong enough
                    ingredient_counter = 0
                    first_temp = list()
                    first_temp.append((n_obj.id.name , list(dict_r[n_obj.recipe_name])[n_obj.ingre], n_obj.cosine_value,len(comparison[2])))
                    notification_outputDict[n_obj.recipe_name] = first_temp
                    n_obj.set_notification_output(notification_outputDict)
                    continue
                else:
                    print('bad estimation')
                    continue
            else:# if there is already an element similar in recipe name
                
                temp_el = n_obj.notification_outputDict[n_obj.recipe_name]
                comparison = processComparison(split_fridge,split_recipe)
                if comparison[0]:
                    if  (n_obj.id.name,list(dict_r[n_obj.recipe_name])[n_obj.ingre],n_obj.cosine_value, len(comparison[2]) ) not in  temp_el:
                        print('NOT IN DICT ', n_obj.id.name)
                        check = False
                        cosine_flag = False
                        better_value = ''
                        for value in n_obj.notification_outputDict[n_obj.recipe_name]:
                            if value[1] == list(dict_r[n_obj.recipe_name])[n_obj.ingre]:
                                print('recipe ingredient is the same')
                                check =  True
                                if value[2] > n_obj.cosine_value:# if the cosine of the fridge ingredient already correlated with a recipe is higher than the current comparison, keep the previous comparison
                                    cosine_flag =  True
                                    continue
                                else:
                                    print('cosine value is better for same recipe ingredient')
                                    to_switch = value
                                    better_value =  (n_obj.id.name , list(dict_r[n_obj.recipe_name])[n_obj.ingre], n_obj.cosine_value, len(comparison[2]))
                                    break         
                            else:
                                continue

                            if value[0] == n_obj.id.name:
                                print('fridge ingredients is tehe same')
                                if value[2] > n_obj.cosine_value:
                                    continue
                                else:
                                    print(value[0] ,' and ', n_obj.id.name, ' are the same, and cosine value is bigger at nobj ', n_obj.cosine_value ,  ' ,', value[2])
                                    temp_el.remove(value)
                                    check = False
                            else:
                                continue
                            
                                
                        if not check:
                            print('Add obj without problems ' , n_obj.id.name)
                            temp_el.append((n_obj.id.name , list(dict_r[n_obj.recipe_name])[n_obj.ingre], n_obj.cosine_value, len(comparison[2])))
                            notification_outputDict[n_obj.recipe_name] = temp_el
                            n_obj.set_notification_output(notification_outputDict)
                                    
                        if check and not cosine_flag:
                            print('change output dict')
                            if to_switch in temp_el:
                                temp_el.remove(to_switch)
                                temp_el.append(better_value)
                                notification_outputDict[n_obj.recipe_name] = temp_el
                                n_obj.set_notification_output(notification_outputDict)
                                continue   
                    else:
                        print(' ')
                        print('fridge el already present ' , n_obj.id.name)
                        print( ' ')
                        continue
                else:
                    print('bad estimation')
                    continue
            print( '  ')
        else:
            continue

def return_missing_and_similar_notification(n_obj):
    counter  = 0
    for output in n_obj.similar_ingredient_ind:#loop through similar_ingredient
        print('this is countereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',counter, ' at outputtttttttttttt ', output )
        counter += 1
        n_obj.set_notification_parameter(output)#for each correlation the notification parameters are updated, this defines the ingredients of both datasets and the recipe of interest of that correlation.
        make_notification(n_obj)#make a notification regarding the current comparison in n_obj
    print_notification(n_obj)#print the notifications that were proff checked
     
def process_notification(n_obj):
    if bool(n_obj.fridge_obj.get_diet()):
        if not n_obj.similar_ingredient_ind: 
            print_notification(n_obj)
            #print('There are not correlations between yuor ingredients and your current diets: ', n_obj.fridge_obj.get_diet().keys() )
        else:
            print('U have a correlation between fridge and recipe of diet: ' , n_obj.fridge_obj.get_diet().keys() )
            return_missing_and_similar_notification(n_obj)
            
    if bool(n_obj.fridge_obj.get_country_cuisine()):
        if not n_obj.similar_ingredient_ind:
            print_notification(n_obj)
            #print('There are not correlations between yuor ingredients and your current country cusisine selection: ', n_obj.fridge_obj.get_country_cuisine().keys() )
        else:
           
            print('U have a correlation between fridge and recipe of diet:' , n_obj.fridge_obj.get_country_cuisine().keys() )
            return_missing_and_similar_notification(n_obj)



    







