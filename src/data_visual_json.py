from pandas.io.json import json_normalize
import json
from os import chdir,getcwd


def visualize_json_data(path):
    path = 'C:/Users/gregh/Desktop/data_for_visual'
    barcode_file_path = path

    with open(path + barcode_file_path) as json_file:
        barcode_data = json.load(json_file)

    provider = json_normalize(data=barcode_data)
    provider.head()


def main_for_visual():
    ##barcode visualization first all barcodes and then show the translated version
    ##perform some test to check the difference
    visualize_json_dat('/barcodes_all_codes_test2_real.json')
    visualize_json_data('/translated_barcodes.json')

    ##recipe visualization 
    visualize_json_dat('/final_cuisine_recipes.json')
    visualize_json_data('/final_special_diets.json')


main_for_visual()