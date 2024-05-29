from flask import Flask, render_template
import sqlite3
import random

app = Flask(__name__)
db = "gamedb.db"


@app.route('/')
def home(): #Homepage, no values loaded in
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Genre WHERE id = 1")
    genre = cur.fetchall()
    settings = str(random.randint(0, len(genre)-1))
    return render_template("home.html", genre=genre, settings=settings, test=1)


@app.route('/results/<settings>') 
def results(settings): # Settings are a string of letters/numbers which represent: 
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Genre WHERE id = ?", (settings,))
    results = cur.fetchall()
    return render_template("results.html", settings=settings, results=results)


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


@app.route("/process/<i>")
def process(i):
    print('hit')
    test = int(i)+1      
    resp = app.make_response(str(test))
    return resp


if __name__ == "__main__":
    app.run(debug=True)
