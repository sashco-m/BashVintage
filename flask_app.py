import os
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from tempfile import mkdtemp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select,update
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

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

            return render_template("index.html", sold=sold,unsold=unsold,admin=session.get("admin",False),numItems=numItems)
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

            return render_template("index.html",sold=sold,unsold=unsold,admin=session.get("admin",False),numItems=numItems)
    else:
        sold, unsold = select_items()

        cart=session.get("cart",[])
        numItems=len(cart)

        return render_template("index.html",sold=sold,unsold=unsold,admin=session.get("admin",False),numItems=numItems)

@app.route("/item/<int:num>/<int:purchased>", methods=["GET", "POST"])
def item(num,purchased): #this id is passed from the index page
    if request.method == "POST":
        s=select([Stock]).where(Stock.id==num)
        data=db.session.execute(s).fetchone()
        #add data to session
        session.setdefault("cart",[])
        #only append the id
        session["cart"].append(num)

        cart=session.get("cart",[])
        numItems=len(cart)

        return render_template("item.html",items=data,inCart=True,numItems=numItems,admin=session.get("admin",False))
    else:
        if purchased==1:
            s=update(Stock).where(Stock.id==num).values(purchase_date=datetime.now())
            db.session.execute(s)
            db.session.commit()
            cartID=session.get("cart",[])
            if num in cartID:
                cartID.remove(num)
                session["cart"]=cartID
                #prevent double purchases in cart and in checkout page
        s=select([Stock]).where(Stock.id==num)
        data=db.session.execute(s).fetchone()
        inCart=False
        cart=session.get("cart",[])

        if data[0] in cart:
            inCart=True

        numItems=len(cart)

        return render_template("item.html",items=data,inCart=inCart,numItems=numItems,admin=session.get("admin",False))

@app.route("/checkout/<int:purchased>", methods=["GET", "POST"])
def checkout(purchased):
    if request.method=="POST":
        #used for removing items from cart
        item_id=request.form["remove_from_cart"]
        cartID=session.get("cart",[])
        cartID.remove(int(item_id,10))
        session["cart"]=cartID

        return redirect("/checkout/0")
    elif request.method == "GET":
        if purchased==1:
            cartID=session.get("cart",[])
            for items in cartID:
                s=update(Stock).where(Stock.id==items).values(purchase_date=datetime.now())
                db.session.execute(s)

            db.session.commit()

            session["cart"]=[]
            cart=[]
            total=0

            return redirect("/")

        else:
            cart=[]
            cartID=session.get("cart",[])
            numItems=len(cartID)
            #select all items in cart
            for items in cartID:
                s=select([Stock]).where(Stock.id==items)
                cart.append(db.session.execute(s).fetchone())

            total=0
            for items in cart:
                total+=items[7]
            return render_template("checkout.html",numItems=numItems,cart=cart,total=total)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        password=request.form.get("password")
        username=request.form.get("username")
        # Ensure username was submitted
        if not request.form.get("username"):
          return render_template("login.html",error="No username inputted")
        # Ensure password was submitted
        if not request.form.get("password"):
          return render_template("login.html",error="No password inputted")
        # Query database for username
        s=select([Users]).where(Users.username==username)
        data=db.session.execute(s).fetchone()
        #check if correct
        if data==None or not check_password_hash(data[2], password):
            return render_template("login.html",error="Incorrect username/password")

        session["user_id"] = data[0]
        #admin check
        if session["user_id"] in [1]:
            session["admin"] = True;
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    #if they submit the form
    if request.method == "POST":

        password=request.form.get("password")
        username=request.form.get("username")

        # Ensure username was submitted
        if not username or not password:
          return render_template("register.html")

        # Ensure passwords are the same
        if request.form.get("password-confirm") != password:
          return render_template("register.html")

        #checks if the username already exists
        #update this with the new db method

        s=select([Users]).where(Users.username==username)
        data=db.session.execute(s).fetchone()

        if data:
          return render_template("register.html")

        #inserting the username and password
        user=Users(username=request.form.get("username"),hash=generate_password_hash(request.form.get("password")))
        db.session.add(user)
        db.session.commit()

        #getting the user id
        s=select([Users]).where(Users.username==username)
        data=db.session.execute(s).fetchone()

        # Remember which user has logged in
        session["user_id"] = data[0]
        #admin check
        #the first two accounts created are admin accounts
        if session["user_id"] in [1]:
          session["admin"] = True;

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")