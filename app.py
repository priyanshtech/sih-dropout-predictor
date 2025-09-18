import os
import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS,PUT')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(80), unique=True, nullable=False); password_hash = db.Column(db.String(120), nullable=False); role = db.Column(db.String(20), nullable=False, default='counselor')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return db.session.get(User, int(user_id))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True); name = db.Column(db.String(100), nullable=False, unique=True); student_class = db.Column(db.String(20), nullable=False); advisor = db.Column(db.String(100)); risk_level = db.Column(db.String(20), default='Unknown'); risk_score = db.Column(db.Float); attendance = db.Column(db.Integer); grade1 = db.Column(db.Float); grade2 = db.Column(db.Float); tuition_up_to_date = db.Column(db.Boolean)
    interventions = db.relationship('InterventionLog', backref='student', lazy=True, cascade="all, delete-orphan")
    notes = db.relationship('NoteLog', backref='student', lazy=True, cascade="all, delete-orphan")
    def to_dict(self):
        avg_grade = round((self.grade1 + self.grade2) / 2) if self.grade1 is not None and self.grade2 is not None else 0
        return {'id': self.id, 'name': self.name, 'class': self.student_class, 'advisor': self.advisor, 'risk_level': self.risk_level, 'risk_score': self.risk_score, 'attendance': self.attendance, 'average_grade': avg_grade}

class InterventionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True); intervention_type = db.Column(db.String(255), nullable=False); log_date = db.Column(db.DateTime, default=datetime.datetime.utcnow); student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    def to_dict(self): return {'id': self.id, 'intervention_type': self.intervention_type, 'log_date': self.log_date.strftime('%Y-%m-%d %H:%M:%S')}

class NoteLog(db.Model):
    id = db.Column(db.Integer, primary_key=True); note_text = db.Column(db.Text, nullable=False); log_date = db.Column(db.DateTime, default=datetime.datetime.utcnow); student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    def to_dict(self): return {'id': self.id, 'note_text': self.note_text, 'log_date': self.log_date.strftime('%Y-%m-%d %H:%M:%S')}

@app.cli.command("init-db")
def init_db_command():
    db.drop_all(); db.create_all()
    admin_user = User(username='admin', role='admin'); admin_user.set_password('admin123')
    counselor_user = User(username='counselor', role='counselor'); counselor_user.set_password('counselor123')
    db.session.add(admin_user); db.session.add(counselor_user)
    students = [Student(name='Ava Thompson', student_class='10A', advisor='Ms. Lee', risk_level='High', risk_score=82.0, attendance=82, grade1=75, grade2=68, tuition_up_to_date=True), Student(name='Liam Johnson', student_class='11C', advisor='Mrs. Alvarez', risk_level='High', risk_score=78.0, attendance=78, grade1=70, grade2=65, tuition_up_to_date=False), Student(name='Noah Patel', student_class='10B', advisor='Mr. Garcia', risk_level='Medium', risk_score=55.0, attendance=91, grade1=80, grade2=90, tuition_up_to_date=True)]
    db.session.bulk_save_objects(students)
    db.session.commit()
    print("Database initialized.")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(); user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')): login_user(user); return jsonify({"user": {"username": user.username, "role": user.role}})
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout(): logout_user(); return jsonify({"message": "Logged out successfully."})

@app.route('/api/status')
@login_required
def status(): return jsonify({"user": {"username": current_user.username, "role": current_user.role}})

@app.route('/api/students')
@login_required
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@app.route('/api/students/<int:student_id>/interventions', methods=['GET', 'POST'])
@login_required
def handle_interventions(student_id):
    student = db.get_or_404(Student, student_id)
    if request.method == 'POST':
        data = request.get_json(); new_log = InterventionLog(student_id=student.id, intervention_type=data['intervention_type']); db.session.add(new_log); db.session.commit(); return jsonify(new_log.to_dict()), 201
    return jsonify([log.to_dict() for log in student.interventions])

@app.route('/api/students/<int:student_id>/notes', methods=['GET', 'POST'])
@login_required
def handle_notes(student_id):
    student = db.get_or_404(Student, student_id)
    if request.method == 'POST':
        data = request.get_json(); new_log = NoteLog(student_id=student.id, note_text=data['note_text']); db.session.add(new_log); db.session.commit(); return jsonify(new_log.to_dict()), 201
    return jsonify([log.to_dict() for log in student.notes])

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_students():
    if current_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file'];
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    try:
        df = pd.read_csv(file); df.columns = [col.strip().lower() for col in df.columns];
        required_cols = ['name', 'class', 'advisor', 'attendance', 'grade1', 'grade2', 'tuition_up_to_date']
        if not all(col in df.columns for col in required_cols): return jsonify({"error": f"Missing columns. Please include: {required_cols}"}), 400
        for _, row in df.iterrows():
            if not Student.query.filter_by(name=row['name']).first():
                avg_grade = (row['grade1'] + row['grade2']) / 2
                risk_level = "Low";
                if avg_grade < 75 or row['attendance'] < 90: risk_level = "Medium"
                if avg_grade < 60 or row['attendance'] < 80 or not row['tuition_up_to_date']: risk_level = "High"
                new_student = Student(name=row['name'], student_class=str(row['class']), advisor=row.get('advisor', 'N/A'), attendance=int(row['attendance']), grade1=float(row['grade1']), grade2=float(row['grade2']), tuition_up_to_date=bool(row['tuition_up_to_date']), risk_level=risk_level, risk_score=round(100 - avg_grade))
                db.session.add(new_student)
        db.session.commit(); return jsonify({"message": f"{len(df)} records processed."}), 201
    except Exception as e: return jsonify({"error": f"Upload failed: {str(e)}"}), 500