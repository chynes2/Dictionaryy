from PyDictionary import PyDictionary
from wordnik import *
import pandas as pd
import ast

# write a dictionary to CSV
def write_dictionary_to_file(d):
    d.to_csv('../data/My_Dictionary.csv', index=False)

# read a dictionary from CSV
def read_dictionary_from_file():
    return(pd.read_csv('../data/My_Dictionary.csv'))

def delete_card(d, word):
    #print("Words:", len(d), ">>", len(d[d.Word != word]))
    d = d[d.Word != word].reset_index(drop=True)
    write_dictionary_to_file(d)
    return(d)

def add_card(d, clients, word):
	# what if the word already exists in the dictionary?!
	if word in set(d.Word.values): # if it exists, print the below and quit
	    print("This word already exists in the dictionary!")
	    return(d)

	else:
	    for ctype, client in clients.items():
	        if ctype == 'PyDictionary':
	            defn = client.meaning(word)
	        elif ctype == 'Wordnik':
	            word_api = WordApi.WordApi(client)
	            defn_data = word_api.getDefinitions(word)
	            if defn_data is not None:
	                defn = {}
	                for dfn in defn_data:
	                    defn[dfn.partOfSpeech] = [dfn.text]
	        if defn in [None, {}] and ctype == 'Wordnik':
	            print("\nWord not found in these clients:", [d for d in clients.keys()], "\n")
	            return(d)
	        if defn in [None, {}]:
	            continue
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
	    

client_1 = ("PyDictionary", PyDictionary())
## init word api 2
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '263a2b19c795b9844520302bf530266a76754c313e57a5b2d'
client_2 = ("Wordnik", swagger.ApiClient(apiKey, apiUrl))

clients = dict([client_1, client_2])

## get list of all words in the dictionary
d = read_dictionary_from_file()
word_list = d.Word

print("Words in Dict:", len(d))

## for each word, delete the word and then call add_card()
for word in word_list:
	d = delete_card(d, word)
	d = add_card(d, clients, word)

print("DONE. Words in Dict:", len(d))