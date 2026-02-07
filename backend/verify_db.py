from database import SessionLocal, PatientData

def verify():
    db = SessionLocal()
    count = db.query(PatientData).count()
    print(f"Total rows in PatientData: {count}")
    
    # Check a sample
    if count > 0:
        first = db.query(PatientData).first()
        print(f"Sample row: StayID={first.stay_id}, Age={first.age}, HR={first.hr}")
    db.close()

if __name__ == "__main__":
    verify()
