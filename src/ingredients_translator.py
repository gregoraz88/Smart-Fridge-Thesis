from google.cloud import translate_v2 as translate
import json
import pandas as pd
from os import chdir,getcwd
import re
from pandas.io.json import json_normalize
import pathlib


src_path = pathlib.Path.cwd()
path_to_copy = src_path.parent/ 'barcode_data'
barcode_path_pre_translation = src_path.parent /'barcode_data '/ 'barcodes_all_codes_test2_real.json'


def translate_barcode_dict(text,keys):
    translated_barcode_dict = {}
    translate_client = translate.Client()
    for i,key in enumerate(keys):
        print('this is i ',i)
        temp_list = list()
        result = translate_client.translate(text[i], target_language='en')
        for el in result:
            temp_list.append(el['translatedText'])
        translated_barcode_dict[key] = temp_list
    save_barcodes(path_to_copy /'translated_barcode.json' , translated_barcode_dict)

def save_barcodes(filename, barcode_dict):
    with open(filename, 'a+') as f:
        json.dump(barcode_dict, f)

def translate_barcodeData_to_english():
    keysToRemove = list()
    with open(barcode_path_pre_translation) as json_file:
        barcode_data = json.load(json_file)
    for key,inner_list in barcode_data.items():
        ingre = inner_list[0].split('-')
        ingredient = ' '.join(ingre)
        quantity = inner_list[1]
        barcode_data[key] = [ingredient , quantity]
        counter = 0
        for el in ingre:
            el.replace(r"\(.*\)","")
            if not el.isalnum():
                keysToRemove.append(key)
                continue
    barcode_data = {key: barcode_data[key] for key in barcode_data if key not in keysToRemove}
    to_translate = list(barcode_data.values())
    key_list = list(barcode_data.keys())
    print(key_list[0])
    print(len(key_list))
    print(len(to_translate))
    translate_barcode_dict(to_translate,key_list)
    exit()

translate_barcodeData_to_english()

