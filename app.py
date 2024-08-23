from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Cấu hình kết nối SQL Server
server = 'TUAN-LA\SQLEXPRESS'
database = 'students'
username = 'sa'  # Tên đăng nhập SQL Server
password = 'sa'  # Mật khẩu SQL Server

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    return pyodbc.connect(connection_string)

@app.route('/')
def base():
    return render_template('show_home.html')

@app.route('/show_home')
def show_home():
    return render_template('show_home.html')

@app.route('/show_achievement')
def show_achievement():
    conn = get_db_connection()
    students = []
    try:
        cur = conn.cursor()
        # Cập nhật câu lệnh SQL để lọc các sinh viên có thành tích không phải là '' và trường achievement không phải NULL
        query = """
        SELECT * FROM students 
        WHERE (achievement IS NOT NULL AND achievement != '')
        """
        cur.execute(query)
        students = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('show_achievement.html', students=students)

@app.route('/show_all_students')
def show_all_students():
    conn = get_db_connection()
    cur = conn.cursor()
    # Truy vấn để lấy danh sách các lớp không trùng lặp
    cur.execute("SELECT DISTINCT class_name FROM students")
    classes = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    # Truyền danh sách lớp học đến template
    return render_template('show_all_students.html', classes=classes)

@app.route('/class/<class_name>')
def show_students_by_class(class_name):
    conn = get_db_connection()
    students = []
    try:
        cur = conn.cursor()
        query = "SELECT * FROM students WHERE class_name = ?"
        cur.execute(query, class_name)
        students = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('class_students.html', class_name=class_name, students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    ma_sinh_vien = request.form['ma_sinh_vien']
    name = request.form['name']
    class_name = request.form['class_name']
    achievement = request.form.get('achievement', '')  # Default to empty string if not provided
    ngay_sinh = request.form.get('ngay_sinh', '')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Kiểm tra xem mã sinh viên đã tồn tại chưa
        check_query = "SELECT COUNT(*) FROM students WHERE ma_sinh_vien = ?"
        cur.execute(check_query, (ma_sinh_vien,))
        count = cur.fetchone()[0]
        
        if count > 0:
            # Nếu mã sinh viên đã tồn tại, hiển thị thông báo lỗi và redirect về trang trước đó
            flash('Mã sinh viên đã tồn tại!', 'danger')
            return redirect(url_for('show_all_students'))
        # Thực hiện thêm sinh viên nếu mã sinh viên chưa tồn tại
        insert_query = """
        INSERT INTO students (ma_sinh_vien, name, class_name, achievement, ngay_sinh)
        VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(insert_query, (ma_sinh_vien, name, class_name, achievement, ngay_sinh))
        conn.commit()
        flash('Thêm sinh viên thành công!', 'success')
    except Exception as e:
        print(f"Error inserting data: {e}")
        flash('Đã xảy ra lỗi khi thêm sinh viên!', 'danger')
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('show_all_students'))

@app.route('/delete_student', methods=['POST'])
def delete_student():
    ma_sinh_vien = request.form['ma_sinh_vien']
    class_name = request.form['class_name']

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Thực hiện xóa sinh viên
        delete_query = "DELETE FROM students WHERE ma_sinh_vien = ?"
        cur.execute(delete_query, (ma_sinh_vien,))
        conn.commit()
        flash('Xóa sinh viên thành công!', 'success')
    except Exception as e:
        print(f"Error deleting data: {e}")
        flash('Đã xảy ra lỗi khi xóa sinh viên!', 'danger')
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('show_students_by_class', class_name=class_name))

@app.route('/edit_student/<string:ma_sinh_vien>', methods=['GET', 'POST'])
def edit_student(ma_sinh_vien):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.form['name']
        class_name = request.form['class_name']
        achievement = request.form.get('achievement', '')  # Default to empty string if not provided
        ngay_sinh = request.form.get('ngay_sinh', '')  # Ngày sinh

        try:
            # Cập nhật thông tin sinh viên trong cơ sở dữ liệu
            update_query = """
            UPDATE students
            SET name = ?, class_name = ?, achievement = ?, ngay_sinh = ?
            WHERE ma_sinh_vien = ?
            """
            cur.execute(update_query, (name, class_name, achievement, ngay_sinh, ma_sinh_vien))
            conn.commit()
            flash('Sửa thông tin sinh viên thành công!', 'success')
        except Exception as e:
            print(f"Error updating data: {e}")
            flash('Đã xảy ra lỗi khi sửa thông tin sinh viên!', 'danger')
        finally:
            conn.close()

        return redirect(url_for('show_students_by_class', class_name=request.form['class_name']))
    
    else:
        # Lấy thông tin sinh viên từ cơ sở dữ liệu để hiển thị trên modal
        cur.execute("SELECT * FROM students WHERE ma_sinh_vien = ?", (ma_sinh_vien,))
        student = cur.fetchone()
        conn.close()
        
        if student:
            return render_template('edit_student.html', student=student)
        else:
            flash('Sinh viên không tồn tại!', 'danger')
            return redirect(url_for('show_all_students'))

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
