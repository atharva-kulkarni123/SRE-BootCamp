import pytest
from unittest.mock import patch
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Home ────────────────────────────────────────────────────────────────────


def test_home(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Student Database" in res.data


# ── Fetch all ───────────────────────────────────────────────────────────────


def test_fetch_all_returns_list(client):
    mock_data = [
        {"student_id": 1, "student_name": "Alice", "age": 20, "standard": 10},
        {"student_id": 2, "student_name": "Bob", "age": 21, "standard": 11},
    ]
    with patch("main.fetch_data", return_value=mock_data):
        res = client.get("/fetch")
        assert res.status_code == 200
        assert res.get_json() == mock_data


def test_fetch_all_empty(client):
    with patch("main.fetch_data", return_value=[]):
        res = client.get("/fetch")
        assert res.status_code == 200
        assert res.get_json() == []


# ── Fetch by ID ─────────────────────────────────────────────────────────────


def test_fetch_by_id_found(client):
    mock_record = {"student_id": 1, "student_name": "Alice", "age": 20, "standard": 10}
    with patch("main.fetch_by_id", return_value=mock_record):
        res = client.get("/fetch/1")
        assert res.status_code == 200
        assert res.get_json() == mock_record


def test_fetch_by_id_not_found(client):
    with patch(
        "main.fetch_by_id", return_value=({"error": "No record with id:99 found"}, 404)
    ):
        res = client.get("/fetch/99")
        assert res.status_code == 200
        data = res.get_json()
        assert "error" in data[0]


# ── Add student ─────────────────────────────────────────────────────────────


def test_add_student_success(client):
    payload = {"student_name": "Charlie", "age": 19, "standard": 9}
    with patch("main.add_student", return_value=True):
        res = client.post("/add", json=payload)
        assert res.status_code == 200
        assert res.get_json()["Message"] == "Record added Successfully"


def test_add_student_missing_field(client):
    # "age" is missing — Pydantic should raise a ValidationError
    payload = {"student_name": "Charlie", "standard": 9}
    with patch("main.add_student", return_value=True):
        res = client.post("/add", json=payload)
        assert res.status_code == 422


def test_add_student_wrong_type(client):
    # age should be int, not string
    payload = {"student_name": "Charlie", "age": "nineteen", "standard": 9}
    with patch("main.add_student", return_value=True):
        res = client.post("/add", json=payload)
        assert res.status_code == 422


# ── Update student ──────────────────────────────────────────────────────────


def test_update_record_success(client):
    updated = {"student_id": 1, "student_name": "Alice", "age": 22, "standard": 10}
    with patch("main.update_record", return_value=updated):
        res = client.post("/update/1", json={"age": 22})
        assert res.status_code == 200
        assert res.get_json()["age"] == 22


def test_update_record_not_found(client):
    with patch(
        "main.update_record",
        return_value=({"error": "No record with id:99 found"}, 404),
    ):
        res = client.post("/update/99", json={"age": 22})
        assert res.status_code == 200
        assert "error" in res.get_json()[0]


# ── Delete student ──────────────────────────────────────────────────────────


def test_delete_student_success(client):
    with patch("main.delete_student", return_value=True):
        res = client.delete("/delete/1")
        assert res.status_code == 200
        assert "deleted successfully" in res.get_json()["Message"]


def test_delete_student_not_found(client):
    with patch("main.delete_student", return_value=False):
        res = client.delete("/delete/99")
        assert res.status_code == 404
        assert "error" in res.get_json()
