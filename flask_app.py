
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, url_for

app = Flask(__name__)

#debug mode
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template("layout.html")

@app.route("/checkout/<int:purchased>", methods=["GET", "POST"])
def checkout(purchased):
    return "temp"