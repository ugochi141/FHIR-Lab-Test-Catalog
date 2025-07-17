from fastapi import FastAPI
from typing import List, Dict

app = FastAPI()

meta_health_data = [
    {
        "patient_id": "P001",
        "age": 45,
        "gender": "Female",
        "height_cm": 165,
        "weight_kg": 68,
        "blood_type": "A+",
        "conditions": ["Hypertension", "Type 2 Diabetes"],
        "medications": ["Metformin", "Lisinopril"],
        "lab_results": {
            "glucose_mg_dL": 126,
            "hba1c_percent": 6.8,
            "cholesterol_total_mg_dL": 189
        }
    },
    # Add more patient data here...
]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Health Meta Data API"}

@app.get("/patients")
async def get_patients():
    return {"patients": meta_health_data}

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    patient = next((p for p in meta_health_data if p["patient_id"] == patient_id), None)
    if patient:
        return patient
    return {"error": "Patient not found"}

@app.get("/statistics")
async def get_statistics():
    total_patients = len(meta_health_data)
    avg_age = sum(p["age"] for p in meta_health_data) / total_patients
    gender_distribution = {}
    for p in meta_health_data:
        gender_distribution[p["gender"]] = gender_distribution.get(p["gender"], 0) + 1
    
    return {
        "total_patients": total_patients,
        "average_age": round(avg_age, 2),
        "gender_distribution": gender_distribution
    }
