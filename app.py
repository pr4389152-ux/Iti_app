from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pooja_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

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

class MCQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200))
    op1 = db.Column(db.String(100))
    op2 = db.Column(db.String(100))
    op3 = db.Column(db.String(100))
    op4 = db.Column(db.String(100))
    answer = db.Column(db.String(100))

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            trade=request.form['trade'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['name'], password=request.form['password']).first()
        if user:
            session['user'] = user.name
            session['trade'] = user.trade
            return redirect('/dashboard')
    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    videos = Video.query.filter_by(trade=session['trade']).all()
    pdfs = PDF.query.filter_by(trade=session['trade']).all()
    return render_template('dashboard.html', videos=videos, pdfs=pdfs, name=session['user'])

# ---------- VIDEO PLAY ----------
@app.route('/video/<filename>')
def video(filename):
    return send_from_directory('static/videos', filename)

# ---------- PDF VIEW ----------
@app.route('/pdf/<filename>')
def pdf(filename):
    return send_from_directory('static/pdfs', filename)

# ---------- MCQ ----------
@app.route('/mcq', methods=['GET','POST'])
def mcq():
    questions = MCQ.query.all()
    if request.method == 'POST':
        score = 0
        wrong = []
        for q in questions:
            ans = request.form.get(str(q.id))
            if ans == q.answer:
                score += 1
            else:
                wrong.append((q.question, q.answer))
        return render_template('result.html', score=score, wrong=wrong)
    return render_template('mcq.html', questions=questions)

# ---------- ADMIN ----------
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join('static/videos', file.filename))
        video = Video(title=request.form['title'], filename=file.filename, trade=request.form['trade'])
        db.session.add(video)
        db.session.commit()
    return render_template('admin.html')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
