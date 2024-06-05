from flask import Flask, jsonify, render_template, request
import sqlite3
import random

app = Flask(__name__)
db = "gamedb.db"


@app.route('/')
def home(): #Homepage, no values loaded in
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    settings = 2
    genreinfo = ["Genre","Genre","Genre",]
    settinginfo = ["Genre","Genre","Genre",]
    mechanicinfo = ["Genre","Genre","Genre",]
    return render_template("home.html",  settings=settings, test=1, genreinfo=genreinfo, settinginfo=settinginfo, mechanicinfo=mechanicinfo)


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


#@app.route("/process/<info>")
#def process(info):
    print('hit')
    settings, genreinfo, settinginfo, mechanicinfo = deconstruct(info)      
    resp = app.make_response(render_template("home.html", settings=settings, test=1, genreinfo=genreinfo, settinginfo=settinginfo, mechanicinfo=mechanicinfo))
    return resp

@app.route('/process', methods=['POST']) 
def process(): 
    data = request.get_json() # retrieve the data sent from JavaScript 
    # process the data using Python code 
    result = data['value'] * 2
    return jsonify(result=result) # return the result to JavaScript 

#def deconstruct(info):
#    print(str(info).split())
#    return list(map(int,str(info).split()))


if __name__ == "__main__":
    app.run(debug=True)
