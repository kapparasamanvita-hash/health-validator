
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- /health tests ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# --- /validate tests ---

def valid_record():
    return {
        "patient_id": "PAT001",
        "age": 35,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "heart_rate": 72,
        "record_date": "2024-01-15"
    }


def test_valid_record_passes():
    response = client.post("/validate", json=valid_record())
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["errors"] == []


def test_systolic_less_than_diastolic_fails():
    record = valid_record()
    record["blood_pressure_systolic"] = 70
    record["blood_pressure_diastolic"] = 90
    response = client.post("/validate", json=record)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert any("Systolic" in e for e in data["errors"])


def test_future_date_fails():
    record = valid_record()
    record["record_date"] = "2099-12-31"
    response = client.post("/validate", json=record)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert any("future" in e for e in data["errors"])


def test_invalid_date_format_rejected():
    record = valid_record()
    record["record_date"] = "15-01-2024"
    response = client.post("/validate", json=record)
    assert response.status_code == 422  # FastAPI validation error


def test_high_bp_generates_warning():
    record = valid_record()
    record["blood_pressure_systolic"] = 185
    record["blood_pressure_diastolic"] = 125
    response = client.post("/validate", json=record)
    assert response.status_code == 200
    data = response.json()
    assert any("hypertensive" in w for w in data["warnings"])


def test_elevated_bp_generates_warning():
    record = valid_record()
    record["blood_pressure_systolic"] = 135
    record["blood_pressure_diastolic"] = 85
    response = client.post("/validate", json=record)
    data = response.json()
    assert any("elevated" in w.lower() for w in data["warnings"])


def test_high_heart_rate_warning():
    record = valid_record()
    record["heart_rate"] = 110
    response = client.post("/validate", json=record)
    data = response.json()
    assert any("above normal" in w for w in data["warnings"])


def test_low_heart_rate_warning():
    record = valid_record()
    record["heart_rate"] = 45
    response = client.post("/validate", json=record)
    data = response.json()
    assert any("below normal" in w for w in data["warnings"])


def test_age_out_of_range_rejected():
    record = valid_record()
    record["age"] = 200
    response = client.post("/validate", json=record)
    assert response.status_code == 422


# --- /validate/batch tests ---

def test_batch_validates_multiple_records():
    records = [valid_record(), valid_record()]
    records[1]["patient_id"] = "PAT002"
    response = client.post("/validate/batch", json=records)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_batch_rejects_over_100_records():
    records = [{**valid_record(), "patient_id": f"PAT{i:03d}"} for i in range(101)]
    response = client.post("/validate/batch", json=records)
    assert response.status_code == 400