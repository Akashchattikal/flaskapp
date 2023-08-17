from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)


def select_database(statement, id, mode):
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    if id is None:
        cur.execute(statement)
    else:
        cur.execute(statement, id)
    if mode == 1:
        results = cur.fetchall()
    else:
        results = cur.fetchone()
    return results


@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


@app.route("/orders")
def orders():
    return render_template("orders.html", title="Recipt")


@app.route("/place_order", methods=["POST"])
def place_order():
    conn = sqlite3.connect('tacoshop.db')
    cur = conn.cursor()
    taco_id = request.form.get("taco")
    cur.execute("INSERT INTO Orders (taco) VALUES (?)", (taco_id,))
    conn.commit()
    taco = select_database('SELECT * FROM Taco_Types WHERE id = ?',
                           (taco_id,), 2)
    photo = taco[1]
    name = taco[2]
    cost = taco[5]
    location_id = taco[6]
    location = select_database('SELECT name FROM Locations WHERE id = ?',
                               (location_id,), 2)
    return render_template("/orders.html", photo=photo, name=name,
                           cost=cost, location=location[0])


@app.route("/order")
def order():
    locations_names = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("order.html", locations_names=locations_names)


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
    cur.execute('SELECT * FROM Ingrediants WHERE id IN(SELECT iid FROM \
Taco_Ingrediants WHERE tid = ?)', (id,))
    ingrediants = cur.fetchall()
    cur.execute('SELECT * FROM Seasonings WHERE id IN(SELECT sid FROM \
Taco_Seasonings WHERE tid = ?)', (id,))
    seasonings = cur.fetchall()
    location_id = taco[6]
    location = select_database('SELECT name FROM Locations WHERE id = ?',
                               (location_id,), 2)
    return render_template('tacos.html',
                           ingrediants=ingrediants, tortilla=tortilla,
                           taco=taco, seasonings=seasonings,
                           location=location[0])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/secret")
def secret():
    return render_template("secret.html", title="Easter Egg")


if __name__ == "__main__":
    app.run(debug=True)
