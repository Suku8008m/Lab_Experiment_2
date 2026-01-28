from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_fallback_secret_key")

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["fullstack_ai_lab"]
users_collection = db["users"]

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "email" in session:
        return render_template("dashboard.html", email=session["email"])
    return redirect(url_for("login"))

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation
        if not email or not password:
            flash("Email and password are required!", "error")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # Insert user
        users_collection.insert_one({
            "email": email,
            "password": hashed_password
        })

        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["email"] = email
            return redirect(url_for("home"))

        flash("Invalid email or password", "error")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
