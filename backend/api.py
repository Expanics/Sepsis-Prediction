from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import func, String, cast
from database import get_db, PatientData
from schemas import PredictionInput, PredictionOutput
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("/stats")
def get_dataset_stats(db: Session = Depends(get_db)):
    try:
        # Improve performance by caching or simplified info?
        # For now, standard queries.
        
        # 1. Total Patients
        subq = db.query(PatientData.age, PatientData.f0_, PatientData.sepsis, PatientData.stay_id).group_by(PatientData.stay_id).subquery()
        
        total_patients = db.query(func.count()).select_from(subq).scalar()
        
        # 2. Avg Age
        avg_age = db.query(func.avg(subq.c.age)).scalar()
        
        # 3. Gender Distribution
        male_count = db.query(func.count()).select_from(subq).filter(subq.c.f0_.in_(['M', 'Male'])).scalar()
        female_count = db.query(func.count()).select_from(subq).filter(subq.c.f0_.in_(['F', 'Female'])).scalar()
        
        # 4. Sepsis Distribution
        sepsis_count = db.query(func.count()).select_from(subq).filter(subq.c.sepsis == 1).scalar()
        normal_count = (total_patients or 0) - (sepsis_count or 0)
        
        # 5. Age Distribution (Simplified Buckets for Charts)
        # 0-18, 19-40, 41-60, 61-80, 80+
        # This is hard in SQLite without CASE. We can do separate counts or fetch all ages and bucket in python?
        # Fetching all ages for 100k might be heavy? No, just 100k ints.
        # But aggregate in SQL is better.
        age_groups = {
            "0-18": db.query(func.count()).select_from(subq).filter(subq.c.age <= 18).scalar(),
            "19-40": db.query(func.count()).select_from(subq).filter(subq.c.age > 18, subq.c.age <= 40).scalar(),
            "41-60": db.query(func.count()).select_from(subq).filter(subq.c.age > 40, subq.c.age <= 60).scalar(),
            "61-80": db.query(func.count()).select_from(subq).filter(subq.c.age > 60, subq.c.age <= 80).scalar(),
            "80+": db.query(func.count()).select_from(subq).filter(subq.c.age > 80).scalar(),
        }

        return {
            "total_patients": total_patients,
            "avg_age": round(avg_age, 1) if avg_age else 0,
            "gender_distribution": {
                "Male": male_count,
                "Female": female_count
            },
            "sepsis_cases": {
                "Sepsis": sepsis_count,
                "Normal": normal_count
            },
            "age_distribution": age_groups
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            "total_patients": 0, 
            "avg_age": 0, 
            "gender_distribution": {"Male": 0, "Female": 0},
            "sepsis_cases": {"Sepsis": 0, "Normal": 0},
            "age_distribution": {}
        }

@router.get("/patients/emergency")
def get_emergency_patients(limit: int = 50, db: Session = Depends(get_db)):
    try:
        # Find patients with Sepsis=1
        # Group by stay_id to get unique patients
        query = db.query(PatientData.stay_id, PatientData.subject_id, PatientData.age, PatientData.f0_, PatientData.sepsis)\
                     .filter(PatientData.sepsis == 1)\
                     .group_by(PatientData.stay_id)
        
        patients = query.limit(limit).all()
        return [{"stay_id": p.stay_id, "subject_id": p.subject_id, "age": p.age, "gender": p.f0_, "sepsis": p.sepsis} for p in patients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients")
def get_patients(search: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(PatientData.stay_id, PatientData.subject_id, PatientData.age, PatientData.f0_)\
                     .group_by(PatientData.stay_id)
        
        if search:
            # Filter by stay_id (cast to string for wildcards if needed, or exact match)
            # For simplicity in sqlite:
            query = query.filter(cast(PatientData.stay_id, String).contains(search))
        
        patients = query.limit(50).all()
        return [{"stay_id": p.stay_id, "subject_id": p.subject_id, "age": p.age, "gender": p.f0_} for p in patients]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{stay_id}")
def get_patient_history(stay_id: int, db: Session = Depends(get_db)):
    rows = db.query(PatientData).filter(PatientData.stay_id == stay_id).order_by(PatientData.hr).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Patient not found")
    return rows

@router.post("/patient")
def add_patient_data(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    try:
        valid_cols = {c.name for c in PatientData.__table__.columns}
        
        # 1. Logic for Auto-Increment HR
        stay_id = data.get('stay_id')
        if not stay_id:
             raise HTTPException(status_code=400, detail="stay_id is required")

        # Get last record for this stay
        from sqlalchemy import desc
        last_record = db.query(PatientData)\
            .filter(PatientData.stay_id == stay_id)\
            .order_by(desc(PatientData.hr))\
            .first()
            
        new_hr = (last_record.hr + 1) if last_record else 1
        
        # 2. Logic for Forward Fill (ffill)
        # If a field is missing in new data, use value from last_record
        final_data = {}
        
        # Pre-fill with last record's data if it exists
        if last_record:
            # We copy all valid columns from last_record
            for col in valid_cols:
                if col not in ['id', 'hr', 'starttime', 'endtime']: # Don't copy PK or time
                    val = getattr(last_record, col)
                    if val is not None:
                        final_data[col] = val
                        
        # Override with new data (only if not None)
        # However, data dict might contain empty strings or None?
        for k, v in data.items():
            if k in valid_cols and k != 'id':
                # If value is provided (not None), use it
                if v is not None:
                     final_data[k] = v
        
        # Set the calculated HR
        final_data['hr'] = new_hr
        
        # Create row
        row = PatientData(**final_data)
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"message": "Data added successfully", "id": row.id, "hr": new_hr}
    except Exception as e:
        db.rollback()
        print(f"Error adding patient: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/predict/{stay_id}", response_model=PredictionOutput)
def predict_patient(stay_id: int, request: Request, window_hours: int = 6, db: Session = Depends(get_db)):
    rows = db.query(PatientData).filter(PatientData.stay_id == stay_id).order_by(PatientData.hr).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Patient data not found")
    
    model = getattr(request.app.state, "model", None)
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Convert window_hours to window_id (0=6h, 1=12h, 2=24h)
    window_map = {6: 0, 12: 1, 24: 2}
    window_id = window_map.get(window_hours, 0)
    
    records = []
    for r in rows:
        d = r.__dict__.copy()
        d.pop('_sa_instance_state', None)
        records.append(d)
        
    try:
        result = model.predict(records, window_id=window_id)
        if not result:
             raise HTTPException(status_code=500, detail="Prediction returned empty")
        return result
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Prediction Error: {tb}")
        raise HTTPException(status_code=500, detail=f"Prediction logic error: {e}. Traceback: {tb}")

@router.post("/predict", response_model=PredictionOutput)
def predict_manual(data: PredictionInput, request: Request, window_hours: int = 6):
    model = getattr(request.app.state, "model", None)
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Convert window_hours to window_id (0=6h, 1=12h, 2=24h)
    window_map = {6: 0, 12: 1, 24: 2}
    window_id = window_map.get(window_hours, 0)
        
    try:
        records = [data.dict()]
        result = model.predict(records, window_id=window_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
