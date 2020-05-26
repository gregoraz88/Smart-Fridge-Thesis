import requests
from bs4 import BeautifulSoup
import config
from os import getcwd,path,chdir
import json
import re
import numpy as np


counter = 0
page_url = 'https://world.openfoodfacts.org'
base_url = 'https://world.openfoodfacts.org/country/netherlands'
barcode_dict= {}
page_links = []

def save_barcodes(filename, barcode_dict):
    with open(filename, 'w') as f:
        json.dump(barcode_dict, f)

def retun_page_products(url):
    try:
        page = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise return_page_products(url)
    web_tree =  BeautifulSoup(page.text, 'html.parser')
    page_links = 0
    products = web_tree.find(class_='products')
    return products,page_links


def return_product_quantity(product_page):
    tree= BeautifulSoup(product_page.text,'html.parser')
    if tree.find('div',class_="medium-12 large-8 xlarge-8 xxlarge-8 columns") != None:
        div = tree.find('div',class_="medium-12 large-8 xlarge-8 xxlarge-8 columns").find_all('p')
    else:
        return 'Null'
    temp_str = div[0].text.split(':')
    if temp_str[0] == 'Quantity':
        quantity = temp_str[1]
        return quantity
    else:
        return 'Null'


def scrape_barcode():
    chdir('..')
    chdir('barcode_data')
    project_path = getcwd()
    path1 = path.join(project_path, 'barcodes_all_codes_test2_real.json')
    page_counter =1
    products,page_links = retun_page_products(base_url)
    while ( counter < 341):
        if (counter % 30)==0:
            #x = json.loads(barcode_dict)
            save_barcodes(path1,barcode_dict)
            barcode_dict = {}
        for info in  products.find_all('a', href= True):
            if info.text:
                temp_info = info['href']
                print(temp_info)
                temp_list = temp_info.split('/')
                if len(temp_list) > 3:
                    try:
                        quantity = return_product_quantity(requests.get(page_url+temp_info))
                    except requests.exceptions.RequestException as e:  # This is the correct syntax
                        quantity = return_product_quantity(requests.get(page_url+temp_info))
                    barcode_dict[temp_list[2]] = tuple((temp_list[3],quantity))
                else: continue
        page_counter += 1
        print('Done with pageeeeeeeeeeeeeeeee')
        print('moving to page',  base_url + '/'+ str(page_counter))
        next_url = base_url + '/'+ str(page_counter)
        products,page_links = retun_page_products(next_url)
        counter += 1
    save_barcodes(path1,barcode_dict)
