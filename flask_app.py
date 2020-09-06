
import os
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
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

class Stock(db.Model):
    __tablename__="stock"

    id=db.Column(db.Integer, primary_key=True)
    list_date=db.Column(db.DateTime)
    purchase_date=db.Column(db.DateTime)
    title=db.Column(db.String(100))
    cover_image=db.Column(db.String(2048))
    alt_image_1=db.Column(db.String(2048))
    alt_image_2=db.Column(db.String(2048))
    price=db.Column(db.Float)
    description=db.Column(db.Text)
    size=db.Column(db.Integer)

class Users(db.Model):
    __tablename__="users"

    user_id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.Text)
    hash=db.Column(db.Text)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("layout.html")

@app.route("/checkout/<int:purchased>", methods=["GET", "POST"])
def checkout(purchased):
    return "temp"