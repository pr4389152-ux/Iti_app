from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pooja_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# -------- MODELS --------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    trade = db.Column(db.String(50))
    password = db.Column(db.String(100))

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    trade = db.Column(db.String(50))

class PDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    trade = db.Column(db.String(50))

# -------- CREATE DATABASE --------
with app.app_context():
    db.create_all()

# -------- HOME --------
@app.route('/')
def home():
    return render_template('index.html')

# -------- REGISTER --------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            user = User(
                name=request.form.get('name'),
                trade=request.form.get('trade'),
                password=request.form.get('password')
            )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            return str(e)

    return render_template('register.html')

# -------- LOGIN --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(
                name=request.form.get('name'),
                password=request.form.get('password')
            ).first()

            if user:
                session['user'] = user.name
                session['trade'] = user.trade
                return redirect('/dashboard')
            else:
                return "Invalid Username or Password"

        except Exception as e:
            return str(e)

    return render_template('login.html')

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    videos = Video.query.filter_by(trade=session['trade']).all()
    pdfs = PDF.query.filter_by(trade=session['trade']).all()

    return render_template('dashboard.html', videos=videos, pdfs=pdfs, name=session['user'])
# admin login 
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == "pooja" and request.form['password'] == "admin123":
            session['admin'] = True
            return redirect('/admin')
    return render_template('admin_login.html')
# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# -------- FILE SERVE --------
@app.route('/video/<filename>')
def video(filename):
    return send_from_directory('static/videos', filename)

@app.route('/pdf/<filename>')
def pdf(filename):
    return send_from_directory('static/pdfs', filename)

# -------- RUN --------
if __name__ == '__main__':
    app.run(debug=True)
