from flask import Flask, jsonify, render_template, request, session
from flask import url_for, redirect, abort
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


def check_logged():
    if session.get('id') is not None:
        return True
    else:
        return False


##############################################################################
app = Flask(__name__)
db = "gamedb.db"
app.secret_key = key.key
##############################################################################


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", logged=check_logged(),
                           text="Page not Found"), 404


@app.errorhandler(403)
def not_allowed(e):
    return render_template("error.html", logged=check_logged(),
                           text="You do not have access to this page"), 404


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", logged=check_logged(),
                           text="Malformed Request"), 404


@app.route('/')
def home():  # Homepage, no values loaded in

    genreinfo = ["Genre",]
    settinginfo = ["Setting",]
    mechanicinfo = ["Mechanic",]
    return render_template("home.html",
                           genreinfo=genreinfo,
                           settinginfo=settinginfo, mechanicinfo=mechanicinfo,
                           logged=check_logged())


@app.route('/results/<settings>')
def results(settings):

    print("we here")

    """Settings are a string of letters/numbers which
    represent: genreamount, settingsamount, mechanicamount """
    try:
        uvtaf = list(map(int, str(settings).split("n")))
    except Exception:
        abort(404)
    for i in range(3):
        if uvtaf[i] < 0 or uvtaf[i] > 9:
            abort(404)
    genreamount, settingamount, mechanicamount, dim = uvtaf
    print(genreamount, settingamount, mechanicamount)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    counts = [[], [], []]
    if dim == 0:
        cur.execute("SELECT name, description, id FROM Genre WHERE _2D = 1")
    elif dim == 1:
        cur.execute("SELECT name, description, id FROM Genre WHERE _3D = 1")
    else:
        cur.execute("SELECT name, description, id FROM Genre")
    counts[0] = cur.fetchall()
    gchoice = list(random.sample(counts[0], genreamount))
    gids = [i[2] for i in gchoice]
    # list in sql code from
    # https://stackoverflow.com/questions/5766230/select-from-sqlite-table-where-rowid-in-list-using-python-sqlite3-db-api-2-0
    cur.execute(
                '''SELECT Mechanic.name,
                Mechanic.description
                FROM Mechanic
                WHERE id NOT IN (
                    SELECT mechanic
                    FROM GenreMechanic
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(gids))), gids)
    counts[1] = cur.fetchall()
    cur.execute(
                '''SELECT Setting.name,
                Setting.description
                FROM Setting
                WHERE id NOT IN (
                    SELECT setting
                    FROM GenreSetting
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(gids))), gids)
    counts[2] = cur.fetchall()
    mchoice = list(random.sample(counts[1],
                                 mechanicamount))
    schoice = list(random.sample(counts[2], settingamount))
    # This is a string version of the results which can be used to save to db
    resultstosave = ''
    resultstosave += "Genres:"
    for i in gchoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    resultstosave += "<br>Settings:"
    for i in schoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    resultstosave += '<br>Mechanics:'
    for i in mchoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    print(resultstosave)
    return render_template("results.html", gchoice=gchoice,
                           mchoice=mchoice, schoice=schoice, settings=settings,
                           resultstosave=resultstosave, logged=check_logged())


@app.route('/login')
def login():
    if session.get("id") is not None:
        abort(403)
    if 'failed' in session:
        checkacccr = session.get('acccreated')
        if checkacccr:
            session["acccreated"] = False
        return render_template("login.html", failed=True, viewfail=False,
                               logged=check_logged(), acccreated=checkacccr)
    else:
        checkacccr = session.get('acccreated')
        if checkacccr:
            session["acccreated"] = False
        return render_template("login.html", failed=False, viewfail=False,
                               logged=check_logged(), acccreated=checkacccr)


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
    return render_template('signup.html', usernameFailed=uf, passwordFailed=pf,
                           logged=check_logged())


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
            session['acccreated'] = True
            return redirect(url_for('login'))
    if len(usernametest) != 0:
        session['usernameFailed'] = True
    if password1 != password2:
        session['passwordFailed'] = True
    return redirect(url_for('signup'))


@app.route('/loginsubmit', methods=['POST'])
def loginsubmit():
    if session.get("id") is not None:
        abort(403)
    session.clear()
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
    counts = [[], [], []]
    if dim == 0:
        cur.execute("SELECT name, description, id FROM Genre WHERE _2D = 1")
    elif dim == 1:
        cur.execute("SELECT name, description, id FROM Genre WHERE _3D = 1")
    else:
        cur.execute("SELECT name, description, id FROM Genre")
    counts[0] = cur.fetchall()
    gchoice = list(random.sample(counts[0], genreamount))
    gids = [i[2] for i in gchoice]
    # list in sql code from
    # https://stackoverflow.com/questions/5766230/select-from-sqlite-table-where-rowid-in-list-using-python-sqlite3-db-api-2-0
    cur.execute(
                '''SELECT Mechanic.name,
                Mechanic.description
                FROM Mechanic
                WHERE id NOT IN (
                    SELECT mechanic
                    FROM GenreMechanic
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(gids))), gids)
    counts[1] = cur.fetchall()
    cur.execute(
                '''SELECT Setting.name,
                Setting.description
                FROM Setting
                WHERE id NOT IN (
                    SELECT setting
                    FROM GenreSetting
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(gids))), gids)
    counts[2] = cur.fetchall()

    mchoice = list(random.sample(counts[1],
                                 mechanicamount))
    schoice = list(random.sample(counts[2], settingamount))
    # This is a string version of the results which can be used to save to db
    resultstosave = ''
    resultstosave += "Genres:"
    for i in gchoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    resultstosave += "<br>Settings:"
    for i in schoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    resultstosave += '<br>Mechanics:'
    for i in mchoice:
        resultstosave += '<br>'
        resultstosave += i[0]
    return jsonify(result=[gchoice, mchoice, schoice, resultstosave])
    # return to js


@app.route('/saveResults', methods=['POST'])
def saveResults():
    data = request.get_json()  # retrieve the data sent from JavaScript
    newdata = data['value']
    print('before')
    if session.get('id') is not None:
        print('after')
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        id = session['id']
        cur.execute('''UPDATE Account SET res3 = (SELECT res2 FROM Account
                    WHERE id = ?), res2 = (SELECT res1 FROM Account WHERE id
                    = ?), res1 = ? WHERE id = ?''', (id, id, str(newdata), id))
        conn.commit()
        conn.close()
        return jsonify(result="success")
    else:
        return jsonify(result="failed")


@app.route('/viewres')
def viewres():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    id = session.get('id')
    if id is not None:
        cur.execute("SELECT res1, res2, res3 FROM Account WHERE id = ?", (id,))
        res1, res2, res3 = cur.fetchall()[0]
        return render_template('viewres.html', res1=res1, res2=res2, res3=res3,
                               logged=check_logged())
    else:
        abort(403)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
