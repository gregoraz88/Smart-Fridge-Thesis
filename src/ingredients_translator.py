#from translate import Translator
from googletrans import Translator
import json
import pandas as pd
from os import chdir,getcwd



#
# for food_name in barcode_data.values():
#     translator = Translator()
#     translation = translator.translate(
#     food_name,dest='en')
#     print('Before------',food_name)
#     print('After-------',translation.text)


# Function for flattening
# json
def flatten_json(y):
    out = {}
    def flatten(x, name =''):

        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:

            i = 0

            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
print(getcwd())
chdir('..')
chdir('barcode_data')
print(getcwd())
#path = 'C:/Users/gregh/Desktop/thesis/barcode_data'
barcode_file_path = '/barcodes_all_codes.json'
pd = pd.read_json('/barcodes_all_codes.json')
print(pd)

#with open(path + barcode_file_path) as json_file:
    #print(flatten_json(json.load(json_file)))
    #barcode_data = json.load(json_file)
