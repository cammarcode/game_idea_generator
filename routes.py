from flask import Flask, jsonify, render_template, request, session
from flask import url_for, redirect, abort
import sqlite3
import random
from hashlib import sha256
import key
from random import choice


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


def session_to_str(value):
    result = session.get(value)
    if result is None:
        return ""
    else:
        del session[value]
        return result


def quick_query(query, values):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(query, values)
    result = cur.fetchall()
    conn.close()
    return result


def check_length(values):
    for value in values:
        if len(value) > 20:
            return False
    return True


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
                           text="You do not have access to this page"), 403


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", logged=check_logged(),
                           text="Bad Request, the url may be invalid."), 400


@app.route('/')
def home():  # Homepage, no values loaded in

    genre_info = ["Genre",]
    setting_info = ["Setting",]
    mechanic_info = ["Mechanic",]
    return render_template("home.html",
                           genre_info=genre_info,
                           setting_info=setting_info,
                           mechanic_info=mechanic_info,
                           logged=check_logged())


@app.route('/results/<settings>')
def results(settings):

    # Settings are a string of letters/numbers which
    # represent: genreamount, settingsamount, mechanicamount
    try:
        info = list(map(int, str(settings).split("n")))
    except Exception:
        abort(400)
    for i in range(3):
        if info[i] < 0 or info[i] > 9:
            abort(400)
    if info[3] < 0 or info[3] > 2:
        abort(400)
    genre_amount, setting_amount, mechanic_amount, dim = info

    box_lists = [[], [], []]
    if dim == 0:
        box_lists[0] = quick_query('''SELECT name, description, id FROM Genre
                                   WHERE _2D = 1''', ())
    elif dim == 1:
        box_lists[0] = quick_query('''SELECT name, description, id FROM
                                   Genre WHERE _3D = 1''', ())
    else:
        box_lists[0] = quick_query("SELECT name, description, id FROM Genre",
                                   ())
    genre_choice = list(random.sample(box_lists[0], genre_amount))
    genre_ids = [i[2] for i in genre_choice]
    # list in sql code from
    # https://stackoverflow.com/questions/5766230/select-from-sqlite-table-where-rowid-in-list-using-python-sqlite3-db-api-2-0
    box_lists[1] = quick_query(
                '''SELECT Mechanic.name,
                Mechanic.description
                FROM Mechanic
                WHERE id NOT IN (
                    SELECT mechanic
                    FROM GenreMechanic
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(genre_ids))),
                genre_ids)
    box_lists[2] = quick_query(
                '''SELECT Setting.name,
                Setting.description
                FROM Setting
                WHERE id NOT IN (
                    SELECT setting
                    FROM GenreSetting
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(genre_ids))),
                genre_ids)
    mechanic_choice = list(random.sample(box_lists[1],
                           mechanic_amount))
    setting_choice = list(random.sample(box_lists[2], setting_amount))

    # This is a string version of the results which can be used to save to db
    # ~~s will be replaced with <br> to create proper spacing
    resultstosave = ''
    resultstosave += "Genres:~~"
    for i in genre_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    resultstosave += "~~~~Settings:~~"
    for i in setting_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    resultstosave += '~~~~Mechanics:~~'
    for i in mechanic_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    return render_template("results.html", genre_choice=genre_choice,
                           mechanic_choice=mechanic_choice,
                           setting_choice=setting_choice, settings=settings,
                           resultstosave=resultstosave, logged=check_logged())


@app.route('/login')
def login():
    if session.get("id") is not None:
        abort(403)
    if not check_length:
        abort(400)
    if 'failed' in session:
        account_created = session.get('account_created')
        if account_created:
            session["account_created"] = False
            # remove from session after storing variable so it's gone next time
        return render_template("login.html", failed=True, viewfail=False,
                               logged=check_logged(),
                               account_created=account_created)
    else:
        account_created = session.get('account_created')
        if account_created:
            session["account_created"] = False
        return render_template("login.html", failed=False, viewfail=False,
                               logged=check_logged(),
                               account_created=account_created)


@app.route('/signup')
def signup():
    # Check for if password or username failed, and pass that on to html
    # It will toggle the errors to visible
    username_failed = False
    password_failed = False
    username = session_to_str('username')
    password1 = session_to_str('p1')
    password2 = session_to_str('p2')
    if ('username_failed' in session):
        del session['username_failed']
        username_failed = True
        username = ""
    if ('password_failed' in session):
        del session['password_failed']
        password_failed = True
        password1 = ""
        password2 = ""
    return render_template('signup.html', username_failed=username_failed,
                           password_failed=password_failed,
                           logged=check_logged(), username=username,
                           password1=password1, password2=password2)


@app.route('/signupsumbit', methods=["POST"])
def signupsubmit():
    # Thanks, Aditya!
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    username = request.form.get('username')
    # Ensure that no other users have the same name
    query = 'SELECT id FROM Account WHERE username = ?'
    username_test = quick_query(query, (username,))
    password_list = [password1, password2, username]
    if password1 == password2 and check_length(password_list):
        if len(username_test) == 0:
            # Generate a salt, add it to password, hash,
            # and then insert hash and salt into account table
            salt = generate_salt(6)
            password1 += salt  # type: ignore THIS MIGHT (not?) BREAK!!!!
            hasher = sha256()
            hasher.update(password1.encode())
            hashed = hasher.hexdigest()
            default_text = "No saved results"
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            query = '''INSERT INTO Account (username,hash,salt,res1,res2,res3)
                       VALUES (?,?,?,?,?,?)'''
            cur.execute(query, (username, hashed, salt, default_text,
                                default_text, default_text))
            conn.commit()
            session.clear()
            session['account_created'] = True
            return redirect(url_for('login'))
    if not check_length([password1, password2, username]):
        abort(400)
    if len(username_test) != 0:
        session['username_failed'] = True
    if password1 != password2:
        session['password_failed'] = True
    session["username"] = username
    session["p1"] = password1
    session["p2"] = password2
    return redirect(url_for('signup'))


@app.route('/loginsubmit', methods=['POST'])
def loginsubmit():
    if session.get("id") is not None:
        abort(403)
    session.clear()
    username = request.form.get('username')
    password = request.form.get('password')
    data = quick_query('SELECT id, hash, salt FROM Account WHERE username = ?',
                       (username,))[0]
    if data is not None:
        # Hash the password plus salt, compare to db
        hasher = sha256()
        password += data[2]
        hasher.update(password.encode())
        hashed = hasher.hexdigest()
        if hashed == data[1]:
            session['id'] = data[0]
            print("Session id:", session["id"])
            return redirect(url_for('home'))
    session['failed'] = True
    return redirect(url_for('login'))


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()  # retrieve the data sent from JavaScript
    settings_from_url = data['value']

    info = list(map(int, str(settings_from_url).split("n")))
    genre_amount, setting_amount, mechanic_amount, dim = info
    box_lists = [[], [], []]
    if dim == 0:
        query = "SELECT name, description, id FROM Genre WHERE _2D = 1"
    elif dim == 1:
        query = "SELECT name, description, id FROM Genre WHERE _3D = 1"
    else:
        query = "SELECT name, description, id FROM Genre"
    box_lists[0] = quick_query(query, ())
    genre_choice = list(random.sample(box_lists[0], genre_amount))
    genre_ids = [i[2] for i in genre_choice]
    # list in sql code from
    # https://stackoverflow.com/questions/5766230/select-from-sqlite-table-where-rowid-in-list-using-python-sqlite3-db-api-2-0
    box_lists[1] = quick_query(
                '''SELECT Mechanic.name,
                Mechanic.description
                FROM Mechanic
                WHERE id NOT IN (
                    SELECT mechanic
                    FROM GenreMechanic
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(genre_ids))),
                genre_ids)
    box_lists[2] = quick_query(
                '''SELECT Setting.name,
                Setting.description
                FROM Setting
                WHERE id NOT IN (
                    SELECT setting
                    FROM GenreSetting
                    WHERE genre IN ({replacethis})
                )'''.format(replacethis=','.join(['?']*len(genre_ids))),
                genre_ids)
    mechanic_choice = list(random.sample(box_lists[1],
                           mechanic_amount))
    setting_choice = list(random.sample(box_lists[2], setting_amount))
    # This is a string version of the results which can be used to save to db
    resultstosave = ''
    resultstosave += "Genres:~~"
    for i in genre_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    resultstosave += "~~~~Settings:~~"
    for i in setting_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    resultstosave += '~~~~Mechanics:~~'
    for i in mechanic_choice:
        resultstosave += '~~'
        resultstosave += i[0]
    return jsonify(result=[genre_choice, mechanic_choice, setting_choice,
                           resultstosave])
    # return to js


@app.route('/saveResults', methods=['POST'])
def saveResults():
    data = request.get_json()  # retrieve the data sent from JavaScript
    new_data = data['value']
    if session.get('id') is not None:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        id = session['id']
        cur.execute('''UPDATE Account SET res3 = (SELECT res2 FROM Account
                    WHERE id = ?), res2 = (SELECT res1 FROM Account WHERE id
                    = ?), res1 = ? WHERE id = ?''',
                    (id, id, str(new_data), id))
        conn.commit()
        conn.close()
        return jsonify(result="success")
    else:
        return jsonify(result="failed")


@app.route('/viewres')
def viewres():
    id = session.get('id')
    if id is not None:
        data = quick_query("SELECT res1, res2, res3 FROM Account WHERE id = ?",
                           (id,))
        res1, res2, res3 = data[0]
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
