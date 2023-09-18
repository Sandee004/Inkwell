from flask import Flask, render_template, flash, request, redirect, url_for, make_response
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

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
            response = make_response(redirect(url_for("homepage")))
            expiration = datetime.now() + timedelta(minutes=8)
            response.set_cookie("user_id", str(user.id), expires=expiration, httponly=True)
            return response
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
    user_id = request.cookies.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        entry_id = request.form.get("entry_id")
        if entry_id:
            entry = Entry.query.get(entry_id)
            if entry:
                if entry.user_id == int(user_id):
                    db.session.delete(entry)
                    db.session.commit()
                    flash("Entry deleted successfully")
                else:
                    flash("You are not authorized to delete this entry")
            else:
                flash("Entry not found")

    entries = Entry.query.filter_by(user_id=user_id).order_by(Entry.created_at.desc()).all()
    return render_template("homepage.html", entries=entries)



@app.route('/create_entry', methods=["POST", "GET"])
@app.route('/create_entry/<int:entry_id>', methods=["POST", "GET"])
def create_entry(entry_id=None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = int(user_id)

        if entry_id:
            entry = Entry.query.filter_by(id=entry_id, user_id=user_id).first()
            if entry:
                entry.title = title
                entry.content = content
                db.session.commit()
                flash("Entry updated successfully")
                return redirect(url_for("homepage"))
            else:
                flash("Entry not found")
        else:
            new_entry = Entry(title=title, content=content, user_id=user_id)
            db.session.add(new_entry)
            db.session.commit()
            flash("Entry saved")
            return redirect(url_for("homepage"))

    if entry_id is not None:
        entry = Entry.query.filter_by(id=entry_id, user_id=user_id).first()
        if entry:
            return render_template("create-entries.html", entry=entry)
        else:
            flash("Entry not found")

    return render_template('create-entries.html')


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("user_id")
    return response
    
if __name__ == "__main__":
    with app.app_context():
        # Create the tables
        db.create_all()
        #db.drop_all()

    app.run(host='0.0.0.0', port=81)
