import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'
db_path = os.path.join(os.environ.get('RENDER_DISK_PATH', '.'), 'students.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(80), unique=True, nullable=False); password_hash = db.Column(db.String(120), nullable=False); role = db.Column(db.String(20), nullable=False, default='counselor')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return db.session.get(User, int(user_id))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True); name = db.Column(db.String(100), nullable=False, unique=True); student_class = db.Column(db.String(20), nullable=False); advisor = db.Column(db.String(100)); risk_level = db.Column(db.String(20), default='Unknown')
    def to_dict(self): return {'id': self.id, 'name': self.name, 'class': self.student_class, 'advisor': self.advisor, 'risk_level': self.risk_level}

# --- API Routes ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({"message": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/students')
@login_required
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])