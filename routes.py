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
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Taco_Types")
    locations_names = cur.fetchall()
    return render_template("order.html",
                           locations_names=locations_names)


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
    cur.execute('SELECT name FROM Tortilla WHERE id = ?', (taco[3],))
    tortilla = cur.fetchone()
    cur.execute('SELECT * FROM Ingrediants WHERE id IN(SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,))
    ingrediants = cur.fetchall()
    cur.execute('SELECT * FROM Seasonings WHERE id IN(SELECT sid FROM Taco_Seasonings WHERE tid = ?)', (id,))
    seasonings = cur.fetchall()
    return render_template('tacos.html',
                           ingrediants=ingrediants, tortilla=tortilla,
                           taco=taco, seasonings=seasonings)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/secret")
def secret():
    return render_template("secret.html", title="Easter Egg")


if __name__ == "__main__":
    app.run(debug=True)
