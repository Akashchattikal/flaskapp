from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", title = "Home")

@app.route("/about")
def about_us ():
    return render_template("about.html", title = "About Us")

@app.route("/order")
def order ():
    return render_template("order.html", title = "Order & Delivery")

@app.route("/all_tacos")
def all_pizzas():
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor() 
    cur.execute("SELECT * FROM Taco_Types") 
    results = cur.fetchall()
    return render_template("all_tacos.html", results = results)

if __name__ == "__main__":
    app.run(debug=True)
