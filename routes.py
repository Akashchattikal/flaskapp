from flask import Flask, render_template, request, redirect, url_for, abort, session
from math import ceil
import sqlite3


app = Flask(__name__)
app.secret_key = "secret_key"


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
    deal_list = []
    deals = select_database("SELECT * FROM Deals WHERE percentage>0;", None, 1)
    print(deals)
    for deal in deals:
        percent = deal[1]
        taco_name = select_database("SELECT name FROM Taco_Types WHERE id=?;", (deal[0],), 2)
        deal_list.append((taco_name[0], percent))
    return render_template("home.html", title="Home", deals=deal_list)


# Creates a URL route called "/about" and renders it into about.html
@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


# Creates a URL route called "/orders" and renders it into orders.html
@app.route("/orders")
def orders():
    return render_template("orders.html", title="Recipt")


# Creates a URL route called "/admin" and renders it into log.html
@app.route("/admin")
def admin():
    if session["admin"] is True:
        taco_names = select_database("SELECT name, id FROM Taco_Types;", None,
                                     1)
        # The following data qu ery selects the items from the table "Orders"
        # "fetchall()"  from the function makes the dataquery select everything
        # from the table
        tranc = select_database('SELECT * FROM Orders', None, 1)
        # The following code makes a list variable to display all the orders
        # in the admin page
        transaction_list = []
        for i in tranc:
            id_num = i[0]
            taco_list = []
            for taco in range(len(i)):
                if i[taco] is not None and taco != 0:
                    taco_info = select_database('SELECT name, price, location \
                    FROM Taco_Types WHERE id = ?', (i[taco],), 2)
                    name = taco_info[0]
                    price = taco_info[1]
                    location_id = taco_info[2]
                    location = select_database('SELECT name FROM Locations\
                    WHERE id = ?', (location_id,), 2)
                    taco_list.append([name, price, location[0]])
            transaction_list.append([id_num, taco_list])
        return render_template("admin.html", tranc=transaction_list,
                               tacos=taco_names, title="Admin")
    if session["admin"] is False:
        abort(404)
    else:
        redirect(url_for("home"))


@app.route("/set_deal", methods=["POST"])
def deal():
    taco_id = request.form["taco"]
    percentage = request.form["percent"]
    if taco_id:
        # Prepares statement by having the variable taco_name as the designated column
        sql_statement = "UPDATE Deals SET percentage=%s WHERE tid=%s;" % (int(percentage), taco_id)
        commit_database(sql_statement, None)
        taco_price = select_database("SELECT price FROM Taco_Types WHERE id=?;", (taco_id,), 2)
        taco_price = taco_price[0].split(" ")[0]
        new_price = ceil(int(taco_price)*(1-int(percentage)/100))
        new_price = "%s Gold Coins" % (str(new_price),)
        print(new_price)
        sql_statement = "UPDATE Taco_Types SET discount_price='%s' WHERE id=?;" % (new_price,)
        commit_database(sql_statement, taco_id)
    else:
        return redirect(url_for("admin"))
    return redirect(url_for("home"))


# Creates a URL route called "/log" and renders it into log.html
@app.route("/log", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    session["admin"] = False
    if password == ":)" and username == ":)":
        session["admin"] = True
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("home"))


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
    taco_id = request.form.getlist("taco")
    taco_list = []
    total_cost = 0
    if taco_id:
        for i in range(len(taco_id)):
            # The following code is used to create variables out of the items
            # in the columns in the table "Taco_types"
            taco = select_database('SELECT * FROM Taco_Types WHERE id = ?',
                                   (taco_id[i],), 2)
            photo = taco[1]
            name = taco[2]
            cost = taco[5]
            location_id = taco[6]
            # The following database query is used select the name from the
            # Locations tabe where the id is the number used as the foreighn
            # key for thechosen taco
            location = select_database('SELECT name FROM Locations WHERE \
id = ?', (location_id,), 2)
            taco_name = "taco"+str(i+1)
            taco_list.append([photo, name, cost, location])
            # Adds all costs together
            total_cost += int(cost.split(" ")[0])
            if i == 0:
                # Prepares statement by having the variable taco_name as the designated column
                sql_statement = "INSERT INTO Orders (%s) \
VALUES (?)" % (taco_name,)
                commit_database(sql_statement, (int(taco[0]),))
            else:
                last_id = select_database("SELECT id FROM Orders ORDER BY \
id DESC;", None, 2)
                last_id = last_id[0]
                sql_statement = "UPDATE Orders SET %s = %s WHERE \
id = %s" % (taco_name, taco_id[i], last_id)
                commit_database(sql_statement, None)
    else:
        return redirect(url_for("order"))
    return render_template("/orders.html", tacos=taco_list,
                           total_cost=total_cost)


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
    if taco:
        # The following data query is used to select the name of the Tortialla used
        # for taco the user selected with the use of the id in the 4th column of
        # the table "Taco_Types"
        tortilla = select_database('SELECT name FROM Tortilla WHERE id = ?',
                                   (taco[3],), 2)
        # The following data query is used to select sall the ingrediants used for
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
        location_id = taco[7]
        # The following code establishes a connection with the function used to
        # create a connection to the database where the data query can be used
        # The following data query is used to select the specifc item from the
        # column "name" in the table Locations where the id is the location_id
        # variable
        original_cost = taco[5]
        discount_cost = taco[7]
        location = select_database('SELECT name FROM Locations WHERE id = ?',
                                   (location_id,), 2)
        return render_template('tacos.html', ingrediants=ingrediants,
                               tortilla=tortilla, taco=taco,
                               seasonings=seasonings, disc_cost=discount_cost,
                               cost=original_cost, location=location[0])
    else:
        abort(404)


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
