from flask import Flask, render_template, flash, request, redirect, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    entries = db.relationship("Entry", backref="user", lazy=True)

class Entry(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id


@app.route('/')
def main():
    return render_template('hello.html')


@app.route('/register', methods=["POST", "GET"])
def register(): 
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user= User.query.filter_by(username=name).first()
        if existing_user:
            flash("Username is already taken")
            return redirect(url_for('register'))
            
        new_user = User(username=name, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registeration successful")
            return redirect(url_for('homepage'))
        except IntegrityError:
            db.session.rollback()
        flash("Email is already in use.")
    return render_template('register.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session["logged_in"] = True
            session["user_id"] = user.id
            return redirect(url_for("homepage"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route('/profiles', methods=["GET", "POST"])
def profiles():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f"Profile for {user.username} deleted successfully.")
        else:
            flash("Profile not found.")
        return redirect(url_for('profiles'))
    else:
        # Retrieve all users from the database
        users = User.query.all()
        return render_template('profiles.html', users=users)


@app.route('/homepage', methods=["GET", "POST"])
def homepage():
    if not session.get("logged_in", False):
        return redirect(url_for("login"))

    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if entry_id:
            entry = Entry.query.get(entry_id)
            if entry:
                user_id = session["user_id"]
                if entry.user_id == user_id:
                    db.session.delete(entry)
                    db.session.commit()
                    flash("Entry deleted successfully")
                else:
                    flash("You are not authorized to delete this entry")
            else:
                flash("Entry not found")

    user_id = session["user_id"]
    entries = Entry.query.filter_by(user_id=user_id).order_by(Entry.created_at.desc()).all()
    return render_template("homepage.html", entries=entries)


@app.route('/create', methods=["POST", "GET"])
def create_entry():
    if not session.get("logged_in", False):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = session["user_id"]
        new_entry = Entry(title=title, content=content, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()

        flash("Entry saved")
        return redirect(url_for("homepage"))
    
    return render_template('create-entries.html')
"""
@app.route('/homepage', methods=["GET", "POST"])
def homepage():
    if not session.get("logged_in", False):
        return redirect(url_for("login"))

    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if entry_id:
            entry = Entry.query.get(entry_id)
            if entry:
                user_id = session["user_id"]
                if entry.user_id == user_id:
                    db.session.delete(entry)
                    db.session.commit()
                    flash("Entry deleted successfully")
                else:
                    flash("You are not authorized to delete this entry")
            else:
                flash("Entry not found")

    user_id = session["user_id"]
    entries = Entry.query.filter_by(user_id=user_id).order_by(Entry.created_at.desc()).all()
    return render_template("homepage.html", entries=entries)

@app.route('/create', methods=["POST", "GET"])
def create_entry():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = session["user_id"]
        new_entry = Entry(title=title, content=content, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()
        
        flash("Entry saved")
        return redirect(url_for("homepage"))
    return render_template('create-entries.html')
"""

if __name__ == "__main__":
    with app.app_context():
        # Create the tables
        db.create_all()
        #db.drop_all()

    app.run(host='0.0.0.0', port=81)
