"""Dictionaryy: an app that makes a personal dictionary,
which you can study like flashcards"""

import pandas as pd
from random import randint
from PyDictionary import PyDictionary

"""Data Structure:
{word1: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 word2: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 ...}
"""

# write a dictionary to CSV
def write_dictionary_to_file(d):
    d.to_csv('My_Dictionary.csv', index=False)

# read a dictionary from CSV
def read_dictionary_from_file():
    return(pd.read_csv('My_Dictionary.csv'))

# edit a definition
def edit_definition(d):
    print("WARNING: this action will permanently edit a card in your dictionary.")
    print("To do back to the main menu, press Enter.")
    k = input("Word you want to edit: ")
    if d.get(k) == None:  ## i.e. if the word can't be found...
        print("Word not found. Capitalization? Spelling?")
    else:
        v = input("New defintion: ")
        d[k] = v

# print the definition dict for a word in pretty format
def print_definition(d, word):
    for pos, defn_list in dict(d['Definition'][word]):
        print(pos + ":")
        for defn in defn_list:
            print("  ", defn, "\n")
    
# study a random word like a flashcard
def study(d):
    rand_index = randint(0,len(d)-1)
    word = d.Word[rand_index]
    print(word)
    input("Press Enter to see the definition!")
    print("\n#####  Definition  #####\n")
    print_definition(d, word)
    print("\n########################\n\n\n")

def delete_card(d, word):
    d = d[d.Word != word].reset_index()
    del d['index']
    return(d)

def add_card(d, client, word):
    # what if the word already exists in the dictionary?!
    if word in d.Word.values: # if it exists, print the below and quit
        print("This word already exists in the dictionary!")
    else:
        defn = client.meaning(word)
        print("Adding word:", word)
        print("Definition:", defn)
        new_entry = pd.DataFrame([[word, defn]], columns=d.columns)
        d = pd.concat([d, new_entry], ignore_index=True)
        #write_dictionary_to_file(d)
        return(d)

################
###   MAIN   ###
################
def main():
    client = PyDictionary()

    d = read_dictionary_from_file()

    print(d.head())

    print("CHECK Before:", 'pinioned' in d.Word.values)

    d = delete_card(d, 'pinioned')

    print("CHECK Before:", 'pinioned' in d.Word.values)

    print(d.head())

    d = add_card(d, client, 'pinioned')

    print("CHECK After:", 'pinioned' in d.Word.values)

    print(d)

    # print_definition(d, 'pinioned')

    words = d.Word.values

    # for word in words[:2]:
    #     delete_card(d, word)
    #     print('Getting defn for:', word)
    #     add_card(d, client, word)

    # print(d)

    # while True:
    #     d = read_dictionary_from_file()
    #     print("You have " + str(len(d)) + " words in your dictionary!")
    #     print("""        [S] Study!
    #     [A] Add a word
    #     [E] Edit a card
    #     [D] Delete a card
    #     [P] Print my dictionary
    #     [Q] Quit""")
    #     choice = input("Choose an action! ")
    #     choice = str(choice.lower())
    #     if choice == "s":
    #         study(d)
    #     elif choice == "a":
    #         word = input("Word to add: ")
    #         add_card(d, client, word)
    #     elif choice == "e":
    #         edit_definition(d)
    #     elif choice == "d":
    #         word_to_del = input("Word to delete: ")
    #         delete_card(d, word_to_del)
    #     elif choice == "p":
    #         print(d)
    #     elif choice == "q":
    #         return
    #     else:
    #         print("please enter a valid choice: S, A, E, D, Q")

if __name__ == "__main__":
	main()
