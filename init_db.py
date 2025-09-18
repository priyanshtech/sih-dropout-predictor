from app import app, db, User, Student

print("--- Initializing Database ---")
with app.app_context():
    db.drop_all()
    db.create_all()

    admin_user = User(username='admin', role='admin')
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    counselor_user = User(username='counselor', role='counselor')
    counselor_user.set_password('counselor123')
    db.session.add(counselor_user)

    students = [
        Student(name='Ava Thompson', student_class='10A', advisor='Ms. Lee', risk_level='High'),
        Student(name='Liam Johnson', student_class='11C', advisor='Mrs. Alvarez', risk_level='High'),
    ]
    db.session.bulk_save_objects(students)
    db.session.commit()
print("--- Database Initialized and Seeded ---")