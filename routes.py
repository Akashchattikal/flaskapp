from flask import Flask, render_template, request, redirect, url_for, abort, \
    session
import sqlite3


app = Flask(__name__)
app.secret_key = "secret_key"


# SQL function for SELECT statements, returns queries
def select_database(statement, id, mode):
    # Connects to database
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    # If the SELECT statement does not require an ID
    if id is None:
        cur.execute(statement)
    else:
        cur.execute(statement, id)
    # If SELECT statement wants multiples
    if mode == 1:
        results = cur.fetchall()
    else:
        results = cur.fetchone()
    return results


# SQL fucntion for statements that UPDATE or INSERT
def commit_database(statement, id):
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    # If ID is none execute statement
    if id is None:
        cur.execute(statement)
    else:
        cur.execute(statement, id)
    conn.commit()


# Gets all deals, then checks for percentage
# Multiplies percentage by original cost
# Updates Taco_Types with the new discounted price
def update_prices():
    taco_deals = select_database("SELECT * FROM Deals;", None, 1)
    # Error prevention if taco_deals query returns an empty list
    if taco_deals:
        for taco in taco_deals:
            taco_id = taco[0]
            percentage = taco[1]
            taco_price = select_database("SELECT price FROM Taco_Types WHERE id=?;", (taco_id,), 2)
            # Take price by splitting string (e.g  22 gold coins) -> 22
            taco_price = taco_price[0].split(" ")[0]
            # Times the taco_price with the percentage left over from taking
            # away the discount percent (e.g 22 * (1-0.2))
            new_price = round(int(taco_price)*(1-int(percentage)/100))
            # Add the new price with the string "Gold Coins"
            new_price = "%s Gold Coins" % (str(new_price),)
            sql_statement = "UPDATE Taco_Types SET discount_price='%s' WHERE id=?;" % (new_price,)
            commit_database(sql_statement, (taco_id,))
    else:
        abort(404)


# Calls update_prices() to check for discounts and displays deals
@app.route("/")
def home():
    update_prices()
    deal_list = []
    # Gets all deals that have a sale (NOT 0% off)
    deals = select_database("SELECT * FROM Deals WHERE percentage>0;", None, 1)
    # If nothing is on sale then sets deal_list to None where an jinja if statement will say something special
    if deals:
        for deal in deals:
            percent = deal[1]
            taco_name = select_database("SELECT name FROM Taco_Types WHERE id=?;", (deal[0],), 2)
            # Appends the taco name and percentage of the taco to deal_list to be organised nicely
            deal_list.append((taco_name[0], percent))
    else:
        deal_list = None
    return render_template("home.html", title="Home", deals=deal_list)


@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


@app.route("/orders")
def orders():
    return render_template("orders.html", title="Recipt")


# Gives an overview of all transactions
# Allows user changes deals
# Allows Admin with password only
@app.route("/admin")
def admin():
    if session["admin"] is True:
        taco_names = select_database("SELECT name, id FROM Taco_Types;", None, 1)
        # Gets all transactions from Orders
        tranc = select_database('SELECT * FROM Orders', None, 1)
        transaction_list = []
        # Splits transactions into individual entries and loops for each one
        for i in tranc:
            id_num = i[0]
            taco_list = []
            # Loops through all the columns in each individual entry (id -> taco1 -> taco2 etc.)
            for taco in range(len(i)):
                # If taco == 0 (the first index which is the transaction ID as I only want taco information
                if i[taco] is not None and taco != 0:
                    taco_info = select_database('SELECT name, price, location \
                    FROM Taco_Types WHERE id = ?', (i[taco],), 2)
                    # Assigns name, price, location_id, and location to easy to read variables
                    name = taco_info[0]
                    price = taco_info[1]
                    location_id = taco_info[2]
                    location = select_database('SELECT name FROM Locations\
                    WHERE id = ?', (location_id,), 2)
                    # Appends it to an organised list so it is easy to load in the information using Jinja
                    taco_list.append([name, price, location[0]])
            # Appends taco_list with the corresponding ID so they're linked together and sends it to Jinja in admin.html
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
        # Updates deals with the input percentage
        commit_database(sql_statement, None)
        # Updates deal prices in Taco_Types
        update_prices()
    else:
        return redirect(url_for("admin"))
    return redirect(url_for("home"))


# When user tries to log in POST requests "username" and "password" from the HTML form
# If the details are correct then it logs them into the admin page
@app.route("/log", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]
    # Sets session to false so they cannot access the admin page from just typing /admin
    session["admin"] = False
    if password == ":)" and username == ":)":
        session["admin"] = True
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("home"))



@app.route("/order")
def order():
    locations_names = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("order.html", locations_names=locations_names)


# Connects orders table in the database to orders.html through the URL route
# "/place_order"
@app.route("/place_order", methods=["POST"])
def place_order():
    update_prices()
    # This code makes "taco_id" into a request form of tacos
    taco_id = request.form.getlist("taco")
    taco_list = []
    total_cost = 0
    if taco_id:
        for i in range(len(taco_id)):
            taco = select_database('SELECT * FROM Taco_Types WHERE id = ?', (taco_id[i],), 2)           
            photo = taco[1]
            name = taco[2]
            cost = taco[6]
            location_id = taco[7]
            location = select_database('SELECT name FROM Locations WHERE \
id = ?', (location_id,), 2)
            # The taco column names are taco1, taco2 etc. so to get the correct column names we just use i
            taco_name = "taco"+str(i+1)
            taco_list.append([photo, name, cost, location])
            # Adds all costs together, splits from gold coins (e.g 22 gold coins -> 22)
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
    update_prices()
    # The following data query selects the items from the table "Taco_Types"
    # "fetchall()" makes the dataquery select everything from the table
    results = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("all_tacos.html", results=results)


@app.route('/tacos/<int:id>')
def tacos(id):
    taco = select_database('SELECT * FROM Taco_Types WHERE id = ?', (id,), 2)
    if taco:
        tortilla = select_database('SELECT name FROM Tortilla WHERE id = ?',
                                   (taco[3],), 2)
        ingrediants = select_database('SELECT * FROM Ingrediants WHERE id IN \
    (SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,), 1)
        seasonings = select_database('SELECT * FROM Seasonings WHERE id IN \
    (SELECT sid FROM Taco_Seasonings WHERE tid = ?)', (id,), 1)
        # Assigns location_id, original_cost and discount_cost to easy to read variables
        location_id = taco[7]
        original_cost = taco[5]
        discount_cost = taco[6]
        location = select_database('SELECT name FROM Locations WHERE id = ?',
                                   (location_id,), 2)
        return render_template('tacos.html', ingrediants=ingrediants,
                               tortilla=tortilla, taco=taco,
                               seasonings=seasonings, disc_cost=discount_cost,
                               cost=original_cost, location=location[0])
    else:
        abort(404)


# Diplays 404.html when the flaskapp needs to use errorhandler for 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/secret")
def secret():
    return render_template("secret.html", title="Easter Egg")


if __name__ == "__main__":
    app.run(debug=True)
