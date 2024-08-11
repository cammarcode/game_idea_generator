from flask import Flask, jsonify, render_template, request
import sqlite3
import random

uvtaf = 0  # uselessvariabletoavoidflake


def remove_brackets(thing):
    return thing[0]


app = Flask(__name__)
db = "gamedb.db"


@app.route('/')
def home():  # Homepage, no values loaded in

    print("yay")

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

    print("we here")

    """Settings are a string of letters/numbers which
    represent: genreamount, settingsamount, mechanicamount """

    uvtaf = list(map(int, str(settings).split("'n")))
    genreamount, settingamount, mechanicamount = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    counts = [[], [], []]
    cur.execute("SELECT name, description FROM Genre")  # add conditions here
    counts[0] = cur.fetchall()
    cur.execute("SELECT name, description FROM Mechanic")  # add conditions her
    counts[1] = cur.fetchall()
    cur.execute("SELECT name, description FROM Setting")  # add conditions here
    counts[2] = cur.fetchall()

    gchoice = list(random.sample(counts[0], genreamount))
    mchoice = list(random.sample(counts[1],
                                 mechanicamount))
    schoice = list(random.sample(counts[2], settingamount))

    return render_template("results.html", gchoice=gchoice,
                           mchoice=mchoice, schoice=schoice, settings=settings)


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
    settingsfromurl = data['value'] * 2

    print(settingsfromurl)

    uvtaf = list(map(int, str(settingsfromurl).split("'n")))
    genreamount, settingamount, mechanicamount = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    print('only here')
    counts = [[], [], []]
    cur.execute("SELECT name, description FROM Genre")  # add conditions here
    counts[0] = cur.fetchall()
    cur.execute("SELECT name, description FROM Mechanic")  # add conditions her
    counts[1] = cur.fetchall()
    cur.execute("SELECT name, description FROM Setting")  # add conditions here
    counts[2] = cur.fetchall()

    gchoice = list(random.sample(counts[0], genreamount))
    mchoice = list(random.sample(counts[1],
                                 mechanicamount))
    schoice = list(random.sample(counts[2], settingamount))
    print('here')
    return jsonify(result=[gchoice, mchoice, schoice])  # return to js


if __name__ == "__main__":
    app.run(debug=True)
