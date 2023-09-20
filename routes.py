from flask import Flask, render_template, request, redirect, url_for, abort, \
    session
import sqlite3


app = Flask(__name__)
app.secret_key = "monkakey_secretkey"


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
    # If SELECT statement returns multiple
    if mode == 1:
        results = cur.fetchall()
    else:
        results = cur.fetchone()
    return results


# SQL fucntion for statements that UPDATE or INSERT
def commit_database(statement, id):
    conn = sqlite3.connect("tacoshop.db")
    cur = conn.cursor()
    # If ID is none only execute statement
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
            # Prepares statement using %s method
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


# Displays general information about website
@app.route("/about")
def about_us():
    return render_template("about.html", title="About Us")


# Once user's order has been processed, redirects to receipt
@app.route("/orders")
def orders():
    return render_template("orders.html", title="Recipt")


# Gives an overview of all transactions
# Allows user changes deals
# Only allows users who used the password instead of just typing /admin
@app.route("/admin")
def admin():
    # Users who type /admin cannot access the admin page. They must log in.
    if session["admin"] is True:
        taco_names = select_database("SELECT name, id FROM Taco_Types;", None, 1)
        # Gets all transactions from Orders
        trancs = select_database('SELECT * FROM Orders', None, 1)
        transaction_list = []
        # Splits transactions into individual entries and loops for each one. i = a single transaction
        for tranc in trancs:
            id_num = tranc[0]
            taco_list = []
            total_cost = 0
            # Loops through all the columns (skipping id and cost) in each individual entry (taco1 -> taco2 etc.)
            for i in range(1, len(tranc)-1):
                # If there is an ID in the current index then continue, else continue to next index number
                if tranc[i] is not None:
                    taco_info = select_database('SELECT name, location \
                    FROM Taco_Types WHERE id = ?', (tranc[i],), 2)
                    print(taco_info, print(tranc[i]))
                    # Assigns name, price, location_id, and location to easy to read variables
                    name = taco_info[0]
                    location_id = taco_info[1]
                    location = select_database('SELECT name FROM Locations\
                    WHERE id = ?', (location_id,), 2)
                    if total_cost == 0:
                        total_cost = select_database('SELECT cost FROM Orders WHERE id=?', (id_num,), 2)[0]
                        # Appends readable information to an organised list so it is easy to load in the information using Jinja
                        taco_list.append([name, total_cost, location[0]])
                    else:
                        # We will only need the total cost once
                        taco_list.append([name, "", location[0]])
            # Appends taco_list with the corresponding transaction ID so they're linked together and sends it to Jinja in admin.html
            transaction_list.append([id_num, taco_list])
        return render_template("admin.html", tranc=transaction_list,
                               tacos=taco_names, title="Admin")
    else:
        abort(404)


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


# Gets tacos from Taco_Types, puts tacos into drop-down box
# Users are redirected to /place_order after ordering
@app.route("/order")
def order():
    taco_names = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("order.html", taco_names=taco_names)


@app.route("/place_order", methods=["POST"])
def place_order():
    # Updates the prices so they are properly discounted
    update_prices()
    # Gets list of all taco orders the user made
    taco_id = request.form.getlist("taco")
    taco_list = []
    total_cost = 0
    # Error prevention, checks if the user didn't order nothing
    if taco_id:
        # For every taco ordered
        for i in range(len(taco_id)):
            # Gets readable taco information from Taco_Types
            taco = select_database('SELECT * FROM Taco_Types WHERE id = ?', (taco_id[i],), 2)
            # Assigns information to easy to read variables
            photo = taco[1]
            name = taco[2]
            cost = taco[6]
            location_id = taco[7]
            # Uses location_id (Foreign key) to find out the name of the location of specific tacos
            location = select_database('SELECT name FROM Locations WHERE \
id = ?', (location_id,), 2)
            # The taco column names are taco1, taco2 etc. so to get the correct column names we just use i
            taco_name = "taco"+str(i+1)
            # Appends information to organised list for easy access
            taco_list.append([photo, name, cost, location])
            # Adds all costs together, splits from gold coins (e.g 22 gold coins -> 22)
            total_cost += int(cost.split(" ")[0])
            # If i == 0 then creates entry, else updates entry
            if i == 0:
                # Prepares statement by having the variable taco_name as the designated column
                sql_statement = "INSERT INTO Orders (%s) \
VALUES (?)" % (taco_name,)
                commit_database(sql_statement, (int(taco[0]),))
                # Gets ID of newly created entry
                last_id = select_database("SELECT id FROM Orders ORDER BY \
id DESC;", None, 2)
                last_id = last_id[0]
            else:
                sql_statement = "UPDATE Orders SET %s = %s WHERE \
id = %s" % (taco_name, taco_id[i], last_id)
                commit_database(sql_statement, None)
        # Finally updates the final cost
        commit_database("UPDATE Orders SET cost = ? WHERE id = ?", (total_cost, last_id))
    # If the user didn't order anything, redirects them back to order page
    else:
        return redirect(url_for("order"))
        
    return render_template("/orders.html", tacos=taco_list,
                           total_cost=total_cost)


# Gets all taco information from Taco_Types and displays it w/ price info
@app.route("/all_tacos")
def all_tacos():
    # Checks for any discounts and changes prices accordingly
    update_prices()
    results = select_database("SELECT * FROM Taco_Types", None, 1)
    return render_template("all_tacos.html", results=results)


# When user clicks specific taco from all_tacos, gets readable taco information from database
@app.route('/tacos/<int:id>')
def tacos(id):
    # Gets specific taco information using taco id from Taco_Type
    taco = select_database('SELECT * FROM Taco_Types WHERE id = ?', (id,), 2)
    # Error prevention, if user types in searchbar a non-existant ID it calls abort(404)
    if taco:
        # Assigns readable information to variables from various tables
        tortilla = select_database('SELECT name FROM Tortilla WHERE id = ?',
                                   (taco[3],), 2)
        ingrediants = select_database('SELECT * FROM Ingrediants WHERE id IN \
    (SELECT iid FROM Taco_Ingrediants WHERE tid = ?)', (id,), 1)
        seasonings = select_database('SELECT * FROM Seasonings WHERE id IN \
    (SELECT sid FROM Taco_Seasonings WHERE tid = ?)', (id,), 1)
        # Assigns location, original_cost and discount_cost to easy to read variables
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


# Diplays 404.html when an actual 404 erro occurs or abort(404) is called
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/secret")
def secret():
    return render_template("secret.html", title="Easter Egg")


if __name__ == "__main__":
    app.run(debug=True)
