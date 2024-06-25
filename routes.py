from flask import Flask, jsonify, render_template, request
import sqlite3
import random

app = Flask(__name__)
db = "gamedb.db"

def get_ids():
    pass

@app.route('/')
def home(): #Homepage, no values loaded in
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    settings = 2
    genreinfo = ["Genre","Genre","Genre",]
    settinginfo = ["Setting",]
    mechanicinfo = ["Mechanic",]
    return render_template("home.html",  settings=settings, test=1, genreinfo=genreinfo, settinginfo=settinginfo, mechanicinfo=mechanicinfo)


@app.route('/results/<settings>') 
def results(settings): # Settings are a string of letters/numbers which represent: genreamount, settingsamount, mechanicamount
    total = [] # list of lists of genre, set, mec results
    result = [] # each result goes here
    genreamount, settingsamount, mechanicamount = list(map(int, str(settings).split("'n")))
    print(genreamount, settingsamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Genre") # add conditions here
    options = cur.fetchall()
    choice = random.sample(options, genreamount)
    return render_template("results.html", results=choice)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/triangles/<size>/<type>/<chara>')
def triangles(size, type, chara):
    spacchar = " " * len(chara)
    return render_template("triangles.html", size=int(size), type=type, chara=chara, spacchar=spacchar)



@app.route('/process', methods=['POST']) 
def process(): 
    data = request.get_json() # retrieve the data sent from JavaScript 
    result = data['value'] * 2
    return jsonify(result=result) # return the result to JavaScript 

def Jon_Arbuckle(self, green, hoes):
    print(self)


if __name__ == "__main__":
    app.run(debug=True) 
