from flask import Flask, flash, redirect, render_template, request, session, abort
import pandas as pd
import random
import os
from PyDictionary import PyDictionary
from wordnik import *

pd.set_option('display.max_colwidth', -1)

app = Flask(__name__)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        my_dict = pd.read_csv('My_Dictionary.csv')
        num_words = len(my_dict)
        return render_template('home.html', **locals())

@app.route('/login', methods=['POST'])
def user_login():
    if request.form['password'] == 'dictionaryy' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Wrong username or password :/')
    return home()

@app.route('/study')
def study():
    my_dict = pd.read_csv('My_Dictionary.csv')
    rand_index = random.randint(0,len(my_dict)-1)
    word = my_dict.Word[rand_index]
    return render_template('study.html', **locals())

@app.route('/add')
def add():
    return render_template('add.html', **locals())

@app.route('/add', methods=['POST'])
def add_post():
    word = request.form['word']
    my_dict = pd.read_csv('My_Dictionary.csv')
    num_words = len(my_dict)

    if word in set(my_dict.Word.str.lower().values): # if it exists, print the below and quit
        response_string = "This word already exists in the dictionary!"
        return render_template('add_response.html', **locals())

    else:
        client_1 = ("PyDictionary", PyDictionary())
        apiUrl = 'http://api.wordnik.com/v4'
        apiKey = '263a2b19c795b9844520302bf530266a76754c313e57a5b2d'
        client_2 = ("Wordnik", swagger.ApiClient(apiKey, apiUrl))

        clients = dict([client_1, client_2])

        for ctype, client in clients.items():
            if ctype == 'PyDictionary':
                defn = client.meaning(word)
            elif ctype == 'Wordnik':
                word_api = WordApi.WordApi(client)
                defn_data = word_api.getDefinitions(word)
                if defn_data != None:
                    defn = {}
                    for dfn in defn_data:
                        defn[dfn.partOfSpeech] = [dfn.text]
            if defn in [None, {}]:
                continue
            else:
                break

        if defn in [None, {}]:
            response_string = 'Could not find a definition for that word :('
            return render_template('add_response.html', **locals())
        else:
            response_string = ''
            for pos, text in defn.items():
                response_string += pos + '\n'
                for t in text:
                    response_string += '\t' + t + '\n'

        new_entry = pd.DataFrame([[word, defn]], columns=my_dict.columns)
        my_dict = pd.concat([my_dict, new_entry], ignore_index=True)
        my_dict.sort_values('Word', inplace=True)
        my_dict.reset_index(drop=True, inplace=True)
        my_dict.to_csv('My_Dictionary.csv', index=False)
        num_words = len(my_dict)
        
        return render_template('add_response.html', **locals())

@app.route('/lookup_word')
def lookup_word():
    return render_template('lookup.html', **locals())

@app.route('/lookup_word', methods=['POST'])
def lookup_word_post():
    word = request.form['word']
    my_dict = pd.read_csv('My_Dictionary.csv')
    num_words = len(my_dict)
    if word in set(my_dict.Word.str.lower().values):
        definition = my_dict[my_dict.Word == word]['Definition'].values[0]
    else:
        definition = "There is no entry in your dictionary for that word :("
    return render_template('show_definition.html', **locals())

@app.route('/delete')
def delete():
    return render_template('delete.html', **locals())

@app.route('/delete', methods=['POST'])
def delete_word_post():
    word = request.form['word']
    my_dict = pd.read_csv('My_Dictionary.csv')
    num_words = len(my_dict)
    if word in set(my_dict.Word.str.lower().values):
        my_dict = my_dict[my_dict.Word != word].reset_index(drop=True)
        my_dict.to_csv('My_Dictionary.csv', index=False)
        definition = 'deleted'
        num_words = len(my_dict)
    else:
        definition = "There is no entry in your dictionary for that word :("
    return render_template('show_definition.html', **locals())

@app.route('/print_dict')
def print_dict():
    my_dict = pd.read_csv('My_Dictionary.csv')
    num_words = len(my_dict)
    dict_html = my_dict.to_html(justify='left')
    return render_template('print.html', **locals())

@app.route('/show_definition/<string:word>/')
def show_definition(word):
    my_dict = pd.read_csv('My_Dictionary.csv')
    num_words = len(my_dict)
    definition = my_dict[my_dict.Word == word]['Definition'].values[0]
    return render_template('show_definition.html', **locals())

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You are logged out.')
    return home()

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)