"""Dictionaryy: an app that makes a personal dictionary,
which you can study like flashcards

Dictionary's Data Structure:
{word1: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 word2: {PartOfSpeech1: [def1, def2, ...], PartOfSpeech2: [def1, def2, ...]},
 ...}
 """
import dash
import dash_core_components as dcc
import dash_html_components as html

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

# print the definition dict for a word in pretty format
def print_definition(d, word):
    defn_str = d[d.Word == word]['Definition'].values[0]
    for pos, defn_list in ast.literal_eval(defn_str).items():
        print("    ", pos + ":")
        for defn in defn_list:
            print("      ", defn, "\n")
    
# study a random word like a flashcard
def study(d):
    rand_index = randint(0,len(d)-1)
    word = d.Word[rand_index]
    print(word)
    input("Press Enter to see the definition!\n")
    print("\n#####  Definition  ############\n")
    print_definition(d, word)
    print("\n###############################\n\n\n")

def delete_card(d, word):
    print("Words:", len(d), ">>", len(d[d.Word != word]))
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

def look_up(d, word):
    ## check if the word is in the dict
    if word in d.Word.values:
        ## if yes, print_definition
        print_definition(d, word)
    else:
        print("That word doesn't exist in your dictionary!")

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
        [L] Look up a word
        [A] Add a word
        [D] Delete a card
        [P] Print my dictionary
        [Q] Quit""")
        choice = input("Choose an action! ")
        choice = str(choice.lower())
        if choice == "s":
            study(d)
        elif choice == "l":
            word = input("Word to look up: ")
            look_up(d, word)
        elif choice == "a":
            word = input("Word to add: ")
            d = add_card(d, clients, word)
        elif choice == "d":
            word_to_del = input("Word to delete: ")
            d = delete_card(d, word_to_del)
        elif choice == "p":
            for index, row in d.iterrows():
                print(row[0], "\n")
                print_definition(d, row[0])
        elif choice == "q":
            return
        else:
            print("please enter a valid choice: S, A, D, Q")

################################################## Dash

# Load logos / icons
dictionaryy_logo = 'https://tco17.topcoder.com/wp-content/uploads/sites/2/2017/02/bah-only-logo.png'

# App initialization
app = dash.Dash()
app.title = "Dictionaryy"
app.config.supress_callback_exceptions = True

app.layout = html.Div([
    # App layout
    # Defines a single div with id "page-content" that gets 
    # filled with content based on the url specified.
    # Buttons update the url and thus repopulate the page 
    # with the appropriate content--this is Dash's version of links.
    dcc.Location(id='url', refresh=False),
    html.Div(id='loadVizPageSignal', style={'display': 'none'}),
    html.Div(id='page-content'),
])

index_layout = html.Div([
    html.Div([

        # Dash by Plotly logo image that is linked to the dash website
        html.Div([
            dcc.Link(
                html.Img(src=dictionaryy_logo,
                    style={
                        'height': '55px',
                        'float': 'left',
                        'position': 'absolute',
                        'top': '23px',
                        'left': '15px'
                    },
                ),
                href='http://plot.ly/products/dash/'
            )]
        ),

        # Booz Allen logo image that is linked to the Booz Allen website
        html.Div([
            dcc.Link(
                html.Img(src='resources/dev_logo.png',
                    style={
                        'height': '30px',
                        'float': 'right',
                        'position': 'absolute',
                        'top': '35px',
                        'right': '25px'

                    },
                ),
                href='http://www.hynes.xyz'
            )]
        )],
        style={
            'padding': '5px 5px 0px 5px',
        }
    )
])

# Adjust page contents based on url pathname
# Returns page layout
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    ## to add more pages, return the entire div for
    ## the page here
    return index_layout

if __name__ == "__main__":
	#main()
    app.run_server(port=8050,threaded=True,debug=False)
