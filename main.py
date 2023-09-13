from flask import Flask, render_template, flash, request, redirect, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@app.route('/')
def main():
    return render_template('hello.html')


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        #confirm = request.form.get("confirm")
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
        #print(f"Username: {username}")
        #print(f"Password: {password}")
        user = User.query.filter_by(username=username).first()
        #print(f"User: {user}")
        if user and user.password == password:
            session["logged_in"] = True
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


@app.route('/homepage')
def homepage():
    if not session.get("logged_in", False):
        return redirect(url_for("login"))
    return render_template("homepage.html")


if __name__ == "__main__":
    with app.app_context():
        # Create the tables
        db.create_all()
        #db.drop_all()

    app.run(host='0.0.0.0', port=81)
