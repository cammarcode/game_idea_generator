from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
db = "gamedb.db"


@app.route('/')
def home():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Genre WHERE id = ?", (1,))
    genre = cur.fetchall()
    return render_template("home.html", genre=genre)


@app.route('/results/settings')
def results():
    return render_template("results.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)
