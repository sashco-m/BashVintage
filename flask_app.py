
import os
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

key=os.urandom(24)
app.secret_key = key

#configure sessions
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#debug mode
app.config["DEBUG"] = True

#database
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="sashco",
    password="schnookybenzene1430",
    hostname="sashco.mysql.pythonanywhere-services.com",
    databasename="sashco$stock",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("layout.html")

@app.route("/checkout/<int:purchased>", methods=["GET", "POST"])
def checkout(purchased):
    return "temp"