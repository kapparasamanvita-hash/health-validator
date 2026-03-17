from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

app = FastAPI(
    title="Health Record Validator",
    description="Validacltes and checks health record data quality",
    version="1.0.0"
)


# --- Models ---

class HealthRecord(BaseModel):
    patient_id: str = Field(..., min_length=3, max_length=20)
    age: int = Field(..., ge=0, le=150)
    blood_pressure_systolic: int = Field(..., ge=50, le=300)
    blood_pressure_diastolic: int = Field(..., ge=30, le=200)
    heart_rate: int = Field(..., ge=20, le=300)
    record_date: str  # expects "YYYY-MM-DD"

    @field_validator("record_date")
    @classmethod
    def validate_date(cls, v):
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("record_date must be in YYYY-MM-DD format")
        return v


class ValidationResult(BaseModel):
    patient_id: str
    is_valid: bool
    warnings: list[str]
    errors: list[str]


# --- Endpoints ---

@app.get("/health")
def health_check():
    """Service health check — used by Kubernetes liveness probe."""
    return {"status": "ok", "service": "health-record-validator"}


@app.post("/validate", response_model=ValidationResult)
def validate_record(record: HealthRecord):
    """
    Validate a single health record.
    Returns validation result with warnings and errors.
    """
    warnings = []
    errors = []

    # Blood pressure checks
    if record.blood_pressure_systolic <= record.blood_pressure_diastolic:
        errors.append("Systolic BP must be greater than diastolic BP")

    if record.blood_pressure_systolic > 180 or record.blood_pressure_diastolic > 120:
        warnings.append("Blood pressure is in hypertensive crisis range (>180/120)")
    elif record.blood_pressure_systolic > 130 or record.blood_pressure_diastolic > 80:
        warnings.append("Blood pressure is elevated (>130/80)")

    # Heart rate checks
    if record.heart_rate > 100:
        warnings.append(f"Heart rate {record.heart_rate} bpm is above normal range (60-100)")
    elif record.heart_rate < 60:
        warnings.append(f"Heart rate {record.heart_rate} bpm is below normal range (60-100)")

    # Age-specific checks
    if record.age < 18 and record.blood_pressure_systolic > 120:
        warnings.append("Elevated BP noted for patient under 18 — verify reading")

    # Future date check
    record_date = date.fromisoformat(record.record_date)
    if record_date > date.today():
        errors.append("record_date cannot be in the future")

    return ValidationResult(
        patient_id=record.patient_id,
        is_valid=len(errors) == 0,
        warnings=warnings,
        errors=errors
    )


@app.post("/validate/batch", response_model=list[ValidationResult])
def validate_batch(records: list[HealthRecord]):
    """
    Validate a batch of health records (max 100).
    Mirrors the bulk validation work done at Providence.
    """
    if len(records) > 100:
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 100 records"
        )
    return [validate_record(record) for record in records]