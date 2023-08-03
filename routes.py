from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


@app.route("/order")
def order():
    return render_template("order.html", title="Order & Delivery")


@app.route("/all_tacos")
def all_tacos():
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Taco_Types")
    results = cur.fetchall()
    return render_template("all_tacos.html", results=results)


@app.route('/tacos/<int:id>')
def tacos(id):
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM Taco_Types WHERE id = ?', (id,))
    taco = cur.fetchone()
    cur.execute('SELECT name FROM Tortilla WHERE id = ?', (taco[4],))
    tortilla = cur.fetchone()
    cur.execute('SELECT name FROM Ingrediants WHERE id IN(SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,))
    ingrediants = cur.fetchall()
    return render_template('tacos.html', ingrediants=ingrediants, tortilla=tortilla, taco=taco)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
