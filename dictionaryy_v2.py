"""Dictionaryy: an app that makes a personal dictionary,
which you can study like flashcards

Dictionary's Data Structure:
{word1: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 word2: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 ...}
 """

import pandas as pd
from random import randint
from PyDictionary import PyDictionary
from wordnik import *
import ast

# write a dictionary to CSV
def write_dictionary_to_file(d):
    d.to_csv('My_Dictionary.csv', index=False)

# read a dictionary from CSV
def read_dictionary_from_file():
    return(pd.read_csv('My_Dictionary.csv'))

# # edit a definition
# def edit_definition(d):
#     print("WARNING: this action will permanently edit a card in your dictionary.")
#     print("To do back to the main menu, press Enter.")
#     k = input("Word you want to edit: ")
#     if k not in d.Word.values:  ## i.e. if the word can't be found...
#         print("Word not found. Capitalization? Spelling?...")
#     else:
#         v = input("New defintion: ")
#         d[k] = v

# print the definition dict for a word in pretty format
def print_definition(d, word):
    defn_str = d[d.Word == word]['Definition'].values[0]
    for pos, defn_list in ast.literal_eval(defn_str).items():
        print(pos + ":")
        for defn in defn_list:
            print("  ", defn, "\n")
    
# study a random word like a flashcard
def study(d):
    rand_index = randint(0,len(d)-1)
    word = d.Word[rand_index]
    print(word)
    input("Press Enter to see the definition!")
    print("\n#####  Definition  ############\n")
    print_definition(d, word)
    print("\n###############################\n\n\n")

def delete_card(d, word):
    print(len(d), ">>", len(d[d.Word != word]))
    d = d[d.Word != word].reset_index(drop=True)
    return(d)

def add_card(d, clients, word):
    # what if the word already exists in the dictionary?!
    if word in set(d.Word.values): # if it exists, print the below and quit
        print("This word already exists in the dictionary!")

    else:
        for ctype, client in clients.items():
            if ctype == 'PyDictionary':
                defn = client.meaning(word)
            elif ctype == 'Wordnik':
                word_api = WordApi.WordApi(client)
                defn_data = word_api.getDefinitions(word)
                print("DEFN DATA")
                print(defn_data)
                if defn_data is not None:
                    defn = {}
                    for dfn in defn_data:
                        defn[dfn.partOfSpeech] = [dfn.text]

            if defn in [None, {}]:
                print("NULLITY!")
            else:
                break

        print("Adding word:", word)
        print("Definition:", defn)

        new_entry = pd.DataFrame([[word, defn]], columns=d.columns)
        d = pd.concat([d, new_entry], ignore_index=True)
        d.sort_values('Word', inplace=True)
        d.reset_index(drop=True, inplace=True)

        write_dictionary_to_file(d)
        return(d)

################
###   MAIN   ###
################
def main():
    ## init word api 1
    client_1 = ("PyDictionary", PyDictionary())

    ## init word api 2
    apiUrl = 'http://api.wordnik.com/v4'
    apiKey = '263a2b19c795b9844520302bf530266a76754c313e57a5b2d'
    client_2 = ("Wordnik", swagger.ApiClient(apiKey, apiUrl))

    clients = dict([client_1, client_2])

    d = read_dictionary_from_file()
    d.columns = ['Word', 'Definition']

    while True:
        print("You have " + str(len(d)) + " words in your dictionary!")
        print("""        [S] Study!
        [A] Add a word
        [D] Delete a card
        [P] Print my dictionary
        [Q] Quit""")
        choice = input("Choose an action! ")
        choice = str(choice.lower())
        if choice == "s":
            study(d)
        elif choice == "a":
            word = input("Word to add: ")
            d = add_card(d, clients, word)
        # elif choice == "e":
        #     edit_definition(d)
        elif choice == "d":
            word_to_del = input("Word to delete: ")
            d = delete_card(d, word_to_del)
        elif choice == "p":
            print(d)
        elif choice == "q":
            return
        else:
            print("please enter a valid choice: S, A, E, D, Q")

if __name__ == "__main__":
	main()
