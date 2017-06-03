# Dictionaryy :: an app that makes a personal dictionary,
#  which you can study like flashcards

import csv
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from wordnik import *

#####################
###   FUNCTIONS   ###
#####################
# write a dictionary to CSV
def write_dictionary_to_file(d):
    with open('My_Dictionary.csv', 'wb') as f:
        writer = csv.writer(f)
        for k, v in d.items():
           writer.writerow([k, v])
        
def write_list_to_any_file(d, fname):
    fname = str(fname)
    with open(fname, 'wb') as f:
        writer = csv.writer(f)
        for k in d:
           writer.writerow([k])

# read a dictionary from CSV
def read_dictionary_from_file():
    with open('My_Dictionary.csv', 'rb') as f:
        reader = csv.reader(f)
        dictionary = dict(reader)
    return(dictionary)
    
# erase dictionary
def erase_dictionary(d):
    return(d.clear())

# edit a definition
def edit_definition(d):
    k = raw_input("Word you want to edit: ")
    if d.get(k) == None:  ## i.e. if the word can't be found...
        print("Word not found. Capitalization? Spelling?")
    else:
        v = raw_input("New defintion: ")
        d[k] = v
        return(d)
    
# study a random word like a flashcard
def study(d):
    rand_index = randint(0,len(d)-1)
    word = d.keys()[rand_index]
    print(word)
    raw_input("Press Enter to see the definition!")
    print("#####  Definition  #####")
    print(d[word])
    print("########################")
    print("")
    print("")
    print("")

def delete_card(d, word):
    try:
        del d[word]
        write_dictionary_to_file(d)
    except:
        print("Word does not exist in dictionary!")

def print_dict(d):
    for k in d.keys():
        if len(k) % 2 == 0:
            spaces = (14 - len(k)) / 2
        else:
            spaces = (13 - len(k)) / 2
        for s in range(spaces):
            print(" "),
        print(k),
        print(": "),
        print(d[k])
    print("")
    print("")

def add_cards_wordnik(d, client, word):
    # what if the word already exists in the dictionary?!
    if d.get(word) != None: # if it exists, print the below and quit
        print("This word already exists in the dictionary!")
    else:
        wordApi = WordApi.WordApi(client)
        defn = wordApi.getDefinitions(word, limit='1')
        defn = defn[0].text
        print(defn)
        defn = defn.encode("utf-8")
        d[word] = defn
        write_dictionary_to_file(d)
        return(d)

################
###   MAIN   ###
################
def main():
    #initiate API client
    apiUrl = 'http://api.wordnik.com/v4'
    apiKey = '263a2b19c795b9844520302bf530266a76754c313e57a5b2d'
    client = swagger.ApiClient(apiKey, apiUrl)
    while True:
        d = read_dictionary_from_file()
        print("You have " + str(len(d)) + " words in your dictionary!")
        print("""        [S] Study!
        [A] Add a word
        [E] Edit a card
        [D] Delete a card
        [P] Print my dictionary
        [Q] Quit""")
        choice = raw_input("Choose an action! ")
        choice = str(choice.lower())
        if choice == "s":
            study(d)
        elif choice == "a":
            word = raw_input("Word to add: ")
            add_cards_wordnik(d, client, word)
        elif choice == "e":
            edit_definition(d)
        elif choice == "d":
            word_to_del = raw_input("Word to delete: ")
            delete_card(d, word_to_del)
        elif choice == "p":
            print_dict(d)
        elif choice == "q":
            return
        else:
            print("please enter a valid choice: S, A, E, D, Q")

if __name__ == "__main__":
	main()