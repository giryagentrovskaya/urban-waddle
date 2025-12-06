import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "secret"

def db():
    con = sqlite3.connect("chat.db")
    con.row_factory = sqlite3.Row
    return con

@app.before_request
def init():
    c = db()
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, email TEXT, text TEXT)")
    c.commit()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    f = request.form
    try:
        db().execute("INSERT INTO users(email,password) VALUES (?,?)",(f["email"],f["password"]))
        db().commit()
        return {"ok":True}
    except:
        return {"ok":False}

@app.route("/login", methods=["POST"])
def login():
    f = request.form
    u = db().execute("SELECT * FROM users WHERE email=?",(f["email"],)).fetchone()
    if u and u["password"]==f["password"]:
        session["user"]=u["email"]
        return {"ok":True}
    return {"ok":False}

@app.route("/chat")
def chat():
    if "user" not in session: return redirect("/")
    return render_template("chat.html")

@app.route("/messages")
def messages():
    m = db().execute("SELECT * FROM messages").fetchall()
    return jsonify([{"email":x["email"],"text":x["text"]} for x in m])

@app.route("/send", methods=["POST"])
def send():
    if "user" not in session: return {"ok":False}
    db().execute("INSERT INTO messages(email,text) VALUES(?,?)",(session["user"],request.form["text"]))
    db().commit()
    return {"ok":True}

app.run()
