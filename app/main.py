from flask import Flask, jsonify, request
from services import (
    fetch_data,
    fetch_by_id,
    update_record,
    add_student,
    init_db,
    delete_student,
)
from schemas import studentBase
from pydantic import ValidationError
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
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
    try:
        entry = studentBase(**payload)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422
    add_student(entry.model_dump())
    return jsonify({"Message": "Record added Successfully"})


@app.route("/delete/<int:student_id>", methods=["DELETE"])
def delete_record(student_id):
    deleted = delete_student(student_id)
    if not deleted:
        return jsonify({"error": f"No record with id:{student_id} found"}), 404
    return jsonify({"Message": f"Record {student_id} deleted successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
