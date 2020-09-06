import os
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select
from datetime import datetime
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
#config
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

#function for selecting all stock
#optional specific order used for sorting
def select_items(order=None):
    if not order == None:
        s=order
    else:
        s=select([Stock])

    data=db.session.execute(s)

    sold=[]
    unsold=[]
    for items in data:
        if items[2]==None:
            unsold.append(items)
        else:
            sold.append(items)
    return sold, unsold

#routes
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        #check if sort button was pressed
        if request.form['submit_button'] == 'sortItem':
            #run different commands based on sort method
            sortMethod=request.form.get("sort")

            if sortMethod=="dateAsc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.list_date.desc()))
            elif sortMethod=="dateDesc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.list_date))
            elif sortMethod=="sizeAsc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.size))
            elif sortMethod=="sizeDesc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.size.desc()))
            elif sortMethod=="priceAsc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.price))
            elif sortMethod=="priceDesc":
                sold,unsold=select_items(order=select([Stock]).order_by(Stock.price.desc()))

            cart=session.get("cart",[])
            numItems=len(cart)

            return render_template("index.html", sold=sold,unsold=unsold,admin=True,numItems=numItems)
        elif request.form['submit_button'] == 'addItem':
            #data from form
            #returns "sold" if sold
            sold=None
            if request.form.get("sold") == "sold":
                sold=datetime.now()
            #check if fields are filled
            if not request.form.get("title") or not request.form.get("url"):
                return redirect("/")
            #recreate as a single object!!!
            item=Stock(list_date=datetime.now(), purchase_date=sold, title=request.form.get("title"), cover_image=request.form.get("url"), alt_image_1=request.form.get("url_2"), alt_image_2=request.form.get("url_3"), price=request.form.get("price"), description=request.form.get("description"), size=request.form.get("size"))
            #send to database
            db.session.add(item)
            db.session.commit()
            #select all stock
            sold, unsold = select_items()

            cart=session.get("cart",[])
            numItems=len(cart)

            return render_template("index.html",sold=sold,unsold=unsold,admin=True,numItems=numItems)
    else:
        sold, unsold = select_items()

        cart=session.get("cart",[])
        numItems=len(cart)

        return render_template("index.html",sold=sold,unsold=unsold,admin=True,numItems=numItems)

@app.route("/item/<int:num>/<int:purchased>", methods=["GET", "POST"])
def item(num,purchased): #this id is passed from the index page
    return "temp"

@app.route("/checkout/<int:purchased>", methods=["GET", "POST"])
def checkout(purchased):
    return "temp"