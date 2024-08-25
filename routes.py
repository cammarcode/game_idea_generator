from flask import Flask, jsonify, render_template, request, session
from flask import url_for, redirect
import sqlite3
import random
from hashlib import sha256
import key
from random import choice

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


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


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
    genreamount, settingamount, mechanicamount, dim = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    counts = [[], [], []]
    if dim == 0:
        cur.execute("SELECT name, description FROM Genre WHERE _2D = 1")  # add
    elif dim == 1:
        cur.execute("SELECT name, description FROM Genre WHERE _3D = 1")  # add
    else:
        cur.execute("SELECT name, description FROM Genre")  # add conditions he
    counts[0] = cur.fetchall()
    cur.execute("SELECT name, description FROM Mechanic")  # add conditions her
    counts[1] = cur.fetchall()
    cur.execute("SELECT name, description FROM Setting")  # add conditions here
    counts[2] = cur.fetchall()

    gchoice = list(random.sample(counts[0], genreamount))
    mchoice = list(random.sample(counts[1],
                                 mechanicamount))
    schoice = list(random.sample(counts[2], settingamount))
    # This is a string version of the results which can be used 
    resultstosave=''


    return render_template("results.html", gchoice=gchoice,
                           mchoice=mchoice, schoice=schoice, settings=settings, resultstosave=resultstosave)


@app.route('/login')
def login():
    if 'failed' in session:
        session.clear()
        return render_template("login.html", failed=True)
    else:
        return render_template("login.html", failed=False)


@app.route('/signup')
def signup():
    # Check for if password or username failed, and pass that on to html
    uf = False
    pf = False
    if ('usernameFailed' in session):
        del session['usernameFailed']
        uf = True
    if ('passwordFailed' in session):
        del session['passwordFailed']
        pf = True
    return render_template('signup.html', usernameFailed=uf, passwordFailed=pf)


@app.route('/signupsumbit', methods=["POST"])
def signupsubmit():
    # Thanks, Aditya!
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    username = request.form.get('username')
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # Ensure that no other users have the same name
    cur.execute('SELECT id FROM Account WHERE username = ?', (username,))
    usernametest = cur.fetchall()
    if password1 == password2:
        if len(usernametest) == 0:
            # Generate a salt, add it to password, hash,
            # and then insert hash and salt into account table
            salt = generate_salt(6)
            password1 += salt  # type: ignore THIS MIGHT (not?) BREAK!!!!
            hasher = sha256()
            hasher.update(password1.encode())
            hashed = hasher.hexdigest()
            uvtaf = 'INSERT INTO Account (username,hash,salt) VALUES (?,?,?)'
            cur.execute(uvtaf, (username, hashed, salt,))
            conn.commit()
            session.clear()
            return redirect(url_for('login'))
    if len(usernametest) != 0:
        session['usernameFailed'] = True
    if password1 != password2:
        session['passwordFailed'] = True
    return redirect(url_for('signup'))


@app.route('/loginsubmit', methods=['POST'])
def loginsubmit():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute('SELECT id, hash, salt FROM Account WHERE username = ?',
                (username,))
    data = cur.fetchone()
    if data is not None:
        # Hash the password plus salt, compare to db
        hasher = sha256()
        password += data[2]
        hasher.update(password.encode())
        hashed = hasher.hexdigest()
        if hashed == data[1]:
            session['id'] = data[0]
            return redirect(url_for('home'))
    session['failed'] = True
    return redirect(url_for('login'))


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
    genreamount, settingamount, mechanicamount, dim = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    print('only here')
    counts = [[], [], []]
    if dim == 0:
        cur.execute("SELECT name, description FROM Genre WHERE _2D = 1")  # add
    elif dim == 1:
        cur.execute("SELECT name, description FROM Genre WHERE _3D = 1")  # add
    else:
        cur.execute("SELECT name, description FROM Genre")  # add conditions he
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
