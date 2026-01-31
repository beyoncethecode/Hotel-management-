from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "hotel_secret_key"  # required for session


# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                email TEXT,
                phone TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS bookings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                room TEXT,
                checkin TEXT,
                checkout TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS payments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                amount TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS staff(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                phone TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS services(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT,
                price TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT)""")

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # simple demo login (replace with DB check later)
        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- BOOKINGS ----------------
@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        room = request.form["room"]
        checkin = request.form["checkin"]
        checkout = request.form["checkout"]

        conn = sqlite3.connect("database.db")
        conn.execute(
            "INSERT INTO bookings(name, room, checkin, checkout) VALUES(?,?,?,?)",
            (name, room, checkin, checkout)
        )
        conn.commit()
        conn.close()
        return redirect("/payment")

    return render_template("bookings.html")


# ---------------- PAYMENT ----------------
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        amount = request.form["amount"]

        conn = sqlite3.connect("database.db")
        conn.execute("INSERT INTO payments(name, amount) VALUES(?,?)", (name, amount))
        conn.commit()
        conn.close()
        return redirect("/dashboard")

    return render_template("payment.html")


# ---------------- STAFF ----------------
@app.route("/staff", methods=["GET", "POST"])
def staff():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        phone = request.form["phone"]
        conn.execute("INSERT INTO staff(name, role, phone) VALUES(?,?,?)",
                     (name, role, phone))
        conn.commit()

    data = conn.execute("SELECT * FROM staff").fetchall()
    conn.close()
    return render_template("staff.html", staff=data)


# ---------------- SERVICES ----------------
@app.route("/services", methods=["GET", "POST"])
def services():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    if request.method == "POST":
        service = request.form["service"]
        price = request.form["price"]
        conn.execute("INSERT INTO services(service, price) VALUES(?,?)",
                     (service, price))
        conn.commit()

    data = conn.execute("SELECT * FROM services").fetchall()
    conn.close()
    return render_template("services.html", services=data)


# ---------------- FEEDBACK ----------------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        conn.execute("INSERT INTO feedback(name, message) VALUES(?,?)",
                     (name, message))
        conn.commit()

    data = conn.execute("SELECT * FROM feedback").fetchall()
    conn.close()
    return render_template("feedback.html", feedback=data)


if __name__ == "__main__":
    app.run(debug=True)
