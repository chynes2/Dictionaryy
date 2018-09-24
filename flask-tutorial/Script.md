# Flask Lunch-and-Learn Script

*Thesis*: Python syncs up nicely with HTML/CSS to create dynamic web applications.

### Setup
1. Download my Dictionaryy repository
2. pip install flask
3. Create a new folder to hold your project
4. Create a new text file called `app.py`

### `app.py`
Put the following code into `app.py`

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
	return "Hello World"

if __name__ == "__main__":
	app.run(debug=True)
```

- the backbone of our app, the backend. 
- all in Python
- so far, there is no HTML, let's add some

### layout.html & home.html
Create a new folder in your application folder called `templates`.

Inside that folder, create a file called `layout.html`.

Inside `layout.html`, write the following:

```html
<html>
<head>
	<title>My app</title>
<style>
body{
	text-align: center;
}
h1{
	font-family: monospace;
	font-size: 2.5em;
	color: blue;
}
</style>
</head>
<body>
	<h1>My Awesome App</h1>

	{% block body %}{% endblock %}

	<a href='/'>return home</a>
</body>
</html>
```

- this is the base template for every page in your app
- includes CSS
- any page html you write will extend this template, being injected into the block body
- add a title and subtitle to your layout template

Now create a file called `home.html` and write the following in it:

```html
{% extends "layout.html" %}
{% block body %}

<h2>This is the homepage!</h2>

{% endblock %}
```

Finally, we need to tell Flask to load this html when we load the page. In `app.py` make the
following changes:

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

if __name__ == "__main__":
	app.run(debug=True)
```

- add pages by adding new routes to `app.py` and new templates to `templates/` folder
- can incorporate variables and python constructs like loops and conditionals inside the html

### Show & Tell: Dictionaryy
- Download the required libraries
	- pip install PyDictionary
	- pip install wordnik-py3
	- pip install ast
- Home page
- Add word
- Show Definition
- Study