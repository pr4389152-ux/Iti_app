from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pooja_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static'

db = SQLAlchemy(app)

# -------- DATABASE CREATE FIX --------


# -------- MODELS --------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    trade = db.Column(db.String(50))
    password = db.Column(db.String(100))
with app.app_context():
    db.create_all()
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

class PYQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200))
    answer = db.Column(db.String(200))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    score = db.Column(db.Integer)

# -------- ADMIN --------
ADMIN_USER = "pooja"
ADMIN_PASS = "admin123"

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
        user = User.query.filter_by(
            name=request.form.get('name'),
            password=request.form.get('password')
        ).first()

        if user:
            session['user'] = user.name
            session['trade'] = user.trade
            return redirect('/dashboard')

    return render_template('login.html')

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    videos = Video.query.filter_by(trade=session['trade']).all()
    pdfs = PDF.query.filter_by(trade=session['trade']).all()

    return render_template('dashboard.html', videos=videos, pdfs=pdfs, name=session['user'])

# -------- PROFILE --------
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    user = User.query.filter_by(name=session['user']).first()
    results = Result.query.filter_by(username=session['user']).all()

    return render_template('profile.html', user=user, results=results)

# -------- ADMIN LOGIN --------
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin')
    return render_template('admin_login.html')

# -------- ADMIN PANEL --------
@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'admin' not in session:
        return redirect('/admin_login')

    if request.method == 'POST':
        file = request.files['file']
        file_type = request.form['type']

        if file:
            if file_type == 'video':
                path = os.path.join('static/videos', file.filename)
                file.save(path)
                db.session.add(Video(title=request.form['title'], filename=file.filename, trade=request.form['trade']))

            elif file_type == 'pdf':
                path = os.path.join('static/pdfs', file.filename)
                file.save(path)
                db.session.add(PDF(title=request.form['title'], filename=file.filename, trade=request.form['trade']))

            db.session.commit()

    videos = Video.query.all()
    pdfs = PDF.query.all()

    return render_template('admin.html', videos=videos, pdfs=pdfs)

# -------- DELETE --------
@app.route('/delete_video/<int:id>')
def delete_video(id):
    video = Video.query.get(id)
    if video:
        db.session.delete(video)
        db.session.commit()
    return redirect('/admin')

@app.route('/delete_pdf/<int:id>')
def delete_pdf(id):
    pdf = PDF.query.get(id)
    if pdf:
        db.session.delete(pdf)
        db.session.commit()
    return redirect('/admin')

# -------- MCQ --------
@app.route('/mcq', methods=['GET','POST'])
def mcq():
    if 'user' not in session:
        return redirect('/login')

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

        db.session.add(Result(username=session['user'], score=score))
        db.session.commit()

        return render_template('result.html', score=score, wrong=wrong)

    return render_template('mcq.html', questions=questions)

# -------- ADD MCQ --------
@app.route('/add_mcq', methods=['GET','POST'])
def add_mcq():
    if request.method == 'POST':
        db.session.add(MCQ(
            question=request.form['question'],
            op1=request.form['op1'],
            op2=request.form['op2'],
            op3=request.form['op3'],
            op4=request.form['op4'],
            answer=request.form['answer']
        ))
        db.session.commit()

    return render_template('add_mcq.html')

# -------- PYQ --------
@app.route('/pyq')
def pyq():
    data = PYQ.query.all()
    return render_template('pyq.html', questions=data)

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
