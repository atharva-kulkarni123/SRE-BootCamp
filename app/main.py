from flask import Flask, jsonify, request
from services import fetch_data, fetch_by_id, update_record, add_student, init_db
from schemas import studentBase

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET"])
def home():
    return "This is Student Database"

@app.route("/fetch", methods=["GET"])
def fetch():
    data = fetch_data()
    return jsonify(data)

@app.route("/fetch/<int:student_id>", methods=["GET"])
def fetch_student_by_id(student_id):
    record = fetch_by_id(student_id)
    return jsonify(record)

@app.route("/update/<int:student_id>", methods=["POST"])
def update_record_by_id(student_id):
    payload = request.get_json()
    record = update_record(student_id, payload)
    return jsonify(record)

@app.route("/add", methods=["POST"])
def add_record_to_database():
    payload = request.get_json()
    entry = studentBase(**payload)
    add_student(entry.model_dump())
    return jsonify({"Message": "Record added Successfully"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)