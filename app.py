from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

if __name__ == '__main__':
	app.run()