from flask import Flask, render_template
from flask_pymongo import PyMongo
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)

# Cấu hình kết nối MongoDB với tham số tlsCAFile
app.config["MONGO_URI"] = "mongodb+srv://tuan:tuan@students.kptlr.mongodb.net/students?retryWrites=true&w=majority&tlsCAFile=C:/Users/Tuan/Downloads/WebS/static/isrgrootx1.pem"

# Khởi tạo PyMongo với Flask
mongo = PyMongo(app)

# Khởi tạo MongoClient để kiểm tra kết nối
client = MongoClient(app.config["MONGO_URI"])

try:
    # Kiểm tra kết nối
    client.admin.command('ping')  # Lệnh ping đơn giản để kiểm tra kết nối
    print("Connection successful")
except ServerSelectionTimeoutError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")

@app.route('/')
def index():
    try:
        # Truy vấn dữ liệu từ bộ sưu tập 'students' trong cơ sở dữ liệu 'students'
        students = mongo.db.students.find()
        return render_template('index.html', students=students)
    except ServerSelectionTimeoutError as e:
        logging.error(f"MongoDB Server Selection Timeout Error: {e}")
        return f"Error connecting to MongoDB: {e}", 500
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return f"An unexpected error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
