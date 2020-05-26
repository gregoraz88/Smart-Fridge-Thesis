 def parse_barcodes(recipe_ingredients,list_of_recipe):
    similar_ingredient = False
    similar_ingredient_ind =list()
    #print(type(recipe_ingredients))
    #print(recipe_ingredients[0])
    #r = ' '.join(recipe_ingredients)
    # doc = nlp(r)
    # for x in recipe_ingredients:
    #     x_doc = nlp(x)
    #     #print('this is doc',x_doc)
    #     break
    #print('this is doc',doc)
    #tokens = list(set([w.text for w in doc if w.is_alpha]))
    #recipe_list = recipe_ingredients.split(' ')
    #print(r[0])
####################################
    # #print(sentvec(r))
    #
    # for r in recipe_list:
    #     print(r)
    # for  f in fridge:
    #     print(f)
    # for i in range(0,len(fridge)):
    #     for j in range(0,len(recipe_list)):
    #         print('this is cosine for fridge el',fridge[i], 'and recipe ingredient' , recipe_list[j], cosine(vec(fridge[i]), vec(recipe_list[j])))
    # exit()
    # print(recipe_doc)
    # recipe_sent = list(recipe_doc.sents)
        ####print(temp_fridge)
    #fridge_list,fridge_list_vec = sample_n_barcode(10)
    fridge_sent = ''.join(fridge_list)
#    print('this is recipe', r)
    flag = False
    if len(fridge_list) > 2:
        for recipe in list_of_recipe: ## recipe contains - [0] -- recipe ingredients [1] -- recipe_id
            if check_extension(fridge_list,nlp(recipe[0]))[0]:
                print('EXTENSION TRUE WITH RECIPE', recipe[0])
                r = ' '.join(recipe[0])
                recipe_string_list = recipe[0].split(' ')
                r_id = recipe[1]
                for i in range(0,len(fridge_list)):
                    #reipce_doc_to_check = ' '.join(list_of_recipe)
                    print('fridge el', fridge_list[i])
                    #print(spacy_closest(tokens, vec('milk'),len(tokens)))
                    #exit()
                    #Matcher_func(fridge_list[i],doc)
                    #exit()
                    print(' ')
                    #print('this is cosine between all fridge ingre and all recipe ingre',cosine(sentvec(fridge_sent),sentvec(r)))
                    #print(' ')
                    #print('this is the cosine: ',cosine(sentvec(r), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i])
                    #print(' ')
                    for t_r in recipe[0]:
                        if cosine(sentvec(t_r), sentvec(fridge_list[i])) > 0.3:
                            print('this is the cosine: ',cosine(sentvec(t_r), sentvec(fridge_list[i])), 'for fridge el', fridge_list[i],'and recipe ingredient sent ', t_r )
                            for j in range(0,len(fridge_list_vec[i])):
                                if not fridge_list_vec[i][j] or fridge_list_vec[i][j] == '':
                                    continue
                                for g in range(0,len(recipe_string_list)):
                                    print('this is cosine for fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_string_list[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])))
                                    if cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])) > 0.7: ## when two strings matches we need to work with n-gram model to extract more meaning
                                        similar_ingredient = True
                                        similar_ingredient_ind.append((i,j,r_id)) ## here append the indexes of sent_vec similr fridge el, where i - is the list index , j - the string index - r_id - recipe_id
                                        print(' ')
                                        print('this is cosine for inner fridge el',fridge_list_vec[i][j], 'and recipe ingredient' , recipe_string_list[g], cosine(vec(fridge_list_vec[i][j]), sentvec(recipe_string_list[g])))
                                        print(' ')
                                    else:
                                        continue
                        else:
                            print('value too low for ingre', fridge_list[i])
                            continue

            else:
                print('NO EXTENSION')
                continue
        print(similar_ingredient_ind)
        return similar_ingredient,similar_ingredient_ind,fridge_list_vec
    else:
        print('too few ingredients')
    exit()


 #####################################################################
 parse recepis

    if not str.isalpha():
            #print(str)
            #print('Do i know it' , full_ingredient[str_index+1])
            if str_index > (len(full_ingredient)-3):
                break
            else:
                print(full_ingredient[str_index+1])
                if full_ingredient[str_index+1] in quantity_list:
                    if plus:
                        plus = False
                        quantity = temp_quantity+ ' plus ' + full_ingredient[str_index] + ' ' + full_ingredient[str_index+1]
                        quantity_ingredient_tuple = ( (full_ingredient[str_index+2:len(full_ingredient)]) ,quantity)
                        inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])]= quantity_ingredient_tuple[1]
                        #print('plus qunatity',quantity_ingredient_tuple)
                        break
                    else:
                        quantity = full_ingredient[str_index] + ' ' + full_ingredient[str_index+1]
                        if full_ingredient[str_index+2] != 'plus' and full_ingredient[str_index+2] != 'to':
                            quantity_ingredient_tuple = ((full_ingredient[str_index+2:len(full_ingredient)]),quantity)
                            inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                            #print('no plus' , quantity_ingredient_tuple)
                else:
                    if plus == False and full_ingredient[str_index+1] != 'to':
                        quantity_ingredient_tuple = ((full_ingredient[str_index+1:len(full_ingredient)]),str)
                        inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                    if full_ingredient[str_index+1] ==  'to':
                        quantity = full_ingredient[str_index]
                    if to == True:
                        to= False
                        quantity = temp_quantity +  ' to ' + full_ingredient[str_index]
                        quantity_ingredient_tuple = ((full_ingredient[str_index+1:len(full_ingredient)]),quantity)
                        inner_recipes_dict[(' ').join(quantity_ingredient_tuple[0])] = quantity_ingredient_tuple[1]
                        #print(quantity_ingredient_tuple)
                        #print('no quantity fund')
                    break
        else:
            if full_ingredient[str_index] == 'plus':
                plus = True
                temp_quantity = quantity
                continue
            if  full_ingredient[str_index] == 'to':
                to = True
                temp_quantity = quantity
                continue