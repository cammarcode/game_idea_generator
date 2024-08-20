from flask import Flask, jsonify, render_template, request, session
from flask import url_for, redirect
import sqlite3
import random
from hashlib import sha256
import key
from random import choice
from gc import collect

uvtaf = 0  # uselessvariabletoavoidflake


def remove_brackets(thing):
    return thing[0]


# Code from
# https://pynative.com/python-generate-random-string/#h-how-to-create-a-random-string-in-python
def generate_salt(length):
    letters = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    result_str = ''.join(choice(letters) for i in range(length))
    return result_str


##############################################################################
app = Flask(__name__)
db = "gamedb.db"
app.secret_key = key.key
##############################################################################


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

    uvtaf = list(map(int, str(settings).split("n")))
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
    # Check for if password or username failed, and pass that on to html
    # Thanks, Aditya!
    if ('passwordFailed' in session):
        del session['passwordFailed']
        return render_template('signup.html',
                               usernameFailed=False, passwordFailed=True)
    if ('usernameFailed' in session):
        del session['usernameFailed']
        return render_template('signup.html',
                               usernameFailed=True, passwordFailed=False)
    else:
        return render_template('signup.html',
                               usernameFailed=False, passwordFailed=False)


@app.route('/signupsumbit', methods=["POST"])
def signupsubmit():
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    # Check if passwords match
    if password1 == password2:
        username = request.form.get('username')
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        # Ensure that no other users have the same name
        cur.execute('SELECT id FROM Account WHERE username = ?', (username,))
        if len(cur.fetchall()) == 0:
            # Generate a salt, add it to password, hash,
            # and then insert this user info into the user table
            salt = generate_salt(6)
            password1 += salt  # type: ignore THIS MIGHT BREAK!!!!
            hasher = sha256()
            hasher.update(password1.encode())
            hashed = hasher.hexdigest()
            uvtaf = 'INSERT INTO Account (username,hash,salt) VALUES (?,?,?)'
            cur.execute(uvtaf, (username, hashed, salt,))
            conn.commit()
            # Remove passwords immediately
            del password1
            del password2
            collect()
            session.clear()
            return redirect(url_for('login'))
        session['usernameFailed'] = True
        return redirect(url_for('signup'))
    session['passwordFailed'] = True
    return redirect(url_for('signup'))


@app.route('/triangles/<size>/<type>/<chara>')
def triangles(size, type, chara):
    spacchar = " " * len(chara)
    return render_template("triangles.html", size=int(size), type=type,
                           chara=chara, spacchar=spacchar)


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()  # retrieve the data sent from JavaScript
    settingsfromurl = data['value']

    print(settingsfromurl)

    uvtaf = list(map(int, str(settingsfromurl).split("n")))
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
