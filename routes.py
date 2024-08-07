from flask import Flask, jsonify, render_template, request
import sqlite3
import random

uvtaf = 0  # uselessvariabletoavoidflake

app = Flask(__name__)
db = "gamedb.db"


def get_ids():
    pass


@app.route('/')
def home():  # Homepage, no values loaded in
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur = cur
    settings = 2
    genreinfo = ["Genre", "Genre", "Genre",]
    settinginfo = ["Setting",]
    mechanicinfo = ["Mechanic",]
    return render_template("home.html",  settings=settings, test=1,
                           genreinfo=genreinfo,
                           settinginfo=settinginfo, mechanicinfo=mechanicinfo)


@app.route('/results/<settings>')
def results(settings):
    """Settings are a string of letters/numbers which
    represent: genreamount, settingsamount, mechanicamount """
    # total = []  # list of lists of genre, set, mec results
    # result = []  # each result goes here
    uvtaf = list(map(int, str(settings).split("'n")))
    genreamount, settingamount, mechanicamount = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    counts = [[], [], []]
    cur.execute("SELECT name FROM Genre")  # add conditions here
    counts[0] = cur.fetchall()
    cur.execute("SELECT name FROM Mechanic")  # add conditions here
    counts[1] = cur.fetchall()
    cur.execute("SELECT name FROM Setting")  # add conditions here
    counts[2] = cur.fetchall()

    print(counts)

    gchoice = random.sample(counts[0], genreamount)
    mchoice = random.sample(counts[1], mechanicamount)
    schoice = random.sample(counts[2], settingamount)

    return render_template("results.html", gchoice=gchoice,
                           mchoice=mchoice, schoice=schoice)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/triangles/<size>/<type>/<chara>')
def triangles(size, type, chara):
    spacchar = " " * len(chara)
    return render_template("triangles.html", size=int(size), type=type,
                           chara=chara, spacchar=spacchar)


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()  # retrieve the data sent from JavaScript
    result = data['value'] * 2
    return jsonify(result=result)  # return the result to JavaScript


if __name__ == "__main__":
    app.run(debug=True)
