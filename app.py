from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình kết nối MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:22062003La.@localhost/students'
# Cấu hình kết nối MySQL deploy Web lên server
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://rosetla:22062003La.@rosetla.mysql.pythonanywhere-services.com/rosetla$students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Định nghĩa mô hình User
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define your models here
class Student(db.Model):
    __tablename__ = 'students'
    ma_sinh_vien = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    achievement = db.Column(db.String(255))
    ngay_sinh = db.Column(db.String(20))
    image_url = db.Column(db.String(255))

@app.route('/')
def base():
    return render_template('show_home.html')

@app.route('/show_home')
def show_home():
    return render_template('show_home.html')

@app.route('/show_achievement')
def show_achievement():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Number of students per page
    students = Student.query.filter(Student.achievement.isnot(None), Student.achievement != '').paginate(page=page, per_page=per_page)
    return render_template('show_achievement.html', students=students)

@app.route('/show_all_students')
def show_all_students():
    classes = db.session.query(Student.class_name).distinct().all()
    classes = [cls[0] for cls in classes]
    return render_template('show_all_students.html', classes=classes)

@app.route('/class/<class_name>')
def show_students_by_class(class_name):
    students = Student.query.filter_by(class_name=class_name).all()
    return render_template('class_students.html', class_name=class_name, students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    ma_sinh_vien = request.form['ma_sinh_vien']
    name = request.form['name']
    class_name = request.form['class_name']
    achievement = request.form.get('achievement', '')
    ngay_sinh = request.form.get('ngay_sinh', '')

    existing_student = Student.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
    if existing_student:
        flash('Mã sinh viên đã tồn tại!', 'danger')
        return redirect(url_for('show_all_students'))

    new_student = Student(ma_sinh_vien=ma_sinh_vien, name=name, class_name=class_name, achievement=achievement, ngay_sinh=ngay_sinh)
    db.session.add(new_student)
    db.session.commit()
    flash('Thêm sinh viên thành công!', 'success')
    return redirect(url_for('show_all_students'))

@app.route('/delete_student', methods=['POST'])
def delete_student():
    ma_sinh_vien = request.form['ma_sinh_vien']
    class_name = request.form['class_name']

    student = Student.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Xóa sinh viên thành công!', 'success')
    else:
        flash('Sinh viên không tồn tại!', 'danger')

    return redirect(url_for('show_students_by_class', class_name=class_name))

@app.route('/edit_student/<string:ma_sinh_vien>', methods=['GET', 'POST'])
def edit_student(ma_sinh_vien):
    student = Student.query.filter_by(ma_sinh_vien=ma_sinh_vien).first()

    if request.method == 'POST':
        if student:
            student.name = request.form['name']
            student.class_name = request.form['class_name']
            student.achievement = request.form.get('achievement', '')
            student.ngay_sinh = request.form.get('ngay_sinh', '')
            db.session.commit()
            flash('Sửa thông tin sinh viên thành công!', 'success')
        else:
            flash('Sinh viên không tồn tại!', 'danger')

        return redirect(url_for('show_students_by_class', class_name=request.form['class_name']))

    return render_template('edit_student.html', student=student)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return redirect(url_for('show_home'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return redirect(url_for('show_home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            session['logged_in'] = True
    return redirect(url_for('show_home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    return redirect(url_for('show_home'))

if __name__ == '__main__':
    app.run(debug=True)
