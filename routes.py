from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


@app.route("/home")
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

@app.route('/Taco_Types/<int:id>')
def pizza(id):
    conn = sqlite3.connect('tacoshop.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Taco_Types WHERE id = ?', (id,))
    pizza = cur.fetchone()
    cur.execute('SELECT name FROM Base WHERE id = ?', (Taco_Types[3],))
    base = cur.fetchone()
    cur.execute('SELECT * FROM Ingrediants WHERE id IN(SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,))
    toppings = cur.fetchall()
    return render_template('tacos.html', Taco_Types = Taco_Types, base = base, toppings = toppings)

if __name__ == "__main__":
    app.run(debug=True)
