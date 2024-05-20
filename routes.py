from flask import Flask, render_template
import sqlite3
import random

app = Flask(__name__)
db = "gamedb.db"


@app.route('/')
def home():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Genre")
    genre = cur.fetchall()
    settings = str(random.randint(0, len(genre)-1))
    return render_template("home.html", genre=genre, settings=settings)


@app.route('/results/<settings>')
def results(settings):
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


@app.route('/triangles/<size>/<type>')
def triangles(size, type):
    return render_template("triangles.html", size=int(size), type=type)


@app.route("/process/<i>")
def process(i):
    print('hit')
    test = int(i)+1
    return render_template("home.html", genre=1, settings=3, test=test)


if __name__ == "__main__":
    app.run(debug=True)
