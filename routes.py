from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)


# Adds a connection to the database and chooses whether the code A
# requires a fetchall() or fetchone() depending on the mode placed on the route
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


def commit_database(statement, id):
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    if id is None:
        cur.execute(statement)
    else:
        cur.execute(statement, id)
    conn.commit()


# Creates a URL route called "/" and renders it into home.html
@app.route("/")
def home():
    return render_template("home.html", title="Home")


# Creates a URL route called "/about" and renders it into about.html
@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


# Creates a URL route called "/orders" and renders it into orders.html
@app.route("/orders")
def orders():
    return render_template("orders.html", title="Recipt")


# Creates a URL route called "/log" and renders it into log.html
@app.route("/admin")
def admin():
    return render_template("admin.html", title="Admin")


# Creates a URL route called "/log" and renders it into log.html
@app.route("/log")
def login():
    return render_template("log.html", title="Login")


# Creates a URL route called "/order" and renders it into order.html
@app.route("/order")
def order():
    # The "select_databse" connects the def function at the beginning
    # of the routes.py to the order() function
    # The data query "SELECT * FROM Taco_Types" brings everything from the
    # table "Taco_Types" and renders it into the order.html
    locations_names = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("order.html", locations_names=locations_names)


# Connects orders table in the database to orders.html through the URL route
# "/place_order"
@app.route("/place_order", methods=["POST"])
def place_order():
    # This code makes "taco_id" into a request form
    taco_id = request.form.get("taco")
    taco = select_database('SELECT * FROM Taco_Types WHERE id = ?',
                           (taco_id,), 2)
    # The following code is used to create variables out of the items
    # in the columns in the table "Taco_types"
    photo = taco[1]
    name = taco[2]
    cost = taco[5]
    location_id = taco[6]
    # The following data query is used to select the items from the "name"
    # column of the table "locations" where the id is whatever the id is from
    # the "loations" column in "Taco_Types" table.
    location = select_database('SELECT name FROM Locations WHERE id = ?',
                               (location_id,), 2)
    commit_database("INSERT INTO Orders (taco) VALUES (?)", (taco_id,))
    return render_template("/orders.html", photo=photo, name=name,
                           cost=cost, location=location[0])


# Creates a URL route called "/all_tacos" and renders it into all_tacos.html
@app.route("/all_tacos")
def all_tacos():
    # The following data query selects the items from the table "Taco_Types"
    # "fetchall()" makes the dataquery select everything from the table
    results = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("all_tacos.html", results=results)


# Creates a URL route called "/tacos<id>" where the <id> is the id of the items
# selected in the all_tacos.html and renders it into tacos.html
@app.route('/tacos/<int:id>')
def tacos(id):
    # The follwing data query is used to select a specific item from the table
    # "Taco_Types" where the id is whatever the <id> is from the URL
    taco = select_database('SELECT * FROM Taco_Types WHERE id = ?', (id,), 2)
    # The following data query is used to select the name of the Tortialla used
    # for taco the user selected with the use of the id in the 4th column of
    # the table "Taco_Types"
    tortilla = select_database('SELECT name FROM Tortilla WHERE id = ?',
                               (taco[3],), 2)
    # The following data query is used to select all the ingrediants used for
    # taco where the id (tid) is whatever the id used in the URL is
    # through the table "Taco_Ingrediants"
    ingrediants = select_database('SELECT * FROM Ingrediants WHERE id IN \
(SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,), 1)
    # The following data query is used to select all the seasonings used for
    # taco where the id (tid) is whatever the id used in the URL is
    # through the table "Taco_Seasonings"
    seasonings = select_database('SELECT * FROM Seasonings WHERE id IN \
(SELECT sid FROM Taco_Seasonings WHERE tid = ?)', (id,), 1)
    # The follwing code is used to create a variable for items in column 7 of
    # the table "Taco_Types where the locations of where specific tacos are
    # availabe are inputed through its id
    location_id = taco[6]
    # The following code establishes a connection with the function used to
    # create a connection to the database where the data query can be used
    # The following data query is used to select the specifc item from the
    # column "name" in the table Locations where the id is the location_id
    # variable
    location = select_database('SELECT name FROM Locations WHERE id = ?',
                               (location_id,), 2)
    return render_template('tacos.html',
                           ingrediants=ingrediants, tortilla=tortilla,
                           taco=taco, seasonings=seasonings,
                           location=location[0])


# The following code is used to display "404.html" when the website goes
# into a page that does not exsist - Error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Creates a URL route called "/secret" and renders it into secret.html
@app.route("/secret")
def secret():
    return render_template("secret.html", title="Easter Egg")


if __name__ == "__main__":
    app.run(debug=True)
