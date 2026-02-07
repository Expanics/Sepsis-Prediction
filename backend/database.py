from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
import os

DATABASE_URL = "sqlite:///./patients.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PatientData(Base):
    __tablename__ = "patient_data"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, nullable=True)
    subject_id = Column(Integer, index=True)
    stay_id = Column(Integer, index=True)
    hr = Column(Integer)
    starttime = Column(String)
    endtime = Column(String)
    age = Column(Integer)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    f0_ = Column(String)  # Gender (mapped from 'gender' in parquet)
    
    # Vitals
    heart_rate_min = Column(Float, nullable=True)
    heart_rate_max = Column(Float, nullable=True)
    sbp_min = Column(Float, nullable=True)
    sbp_max = Column(Float, nullable=True)
    dbp_min = Column(Float, nullable=True)
    dbp_max = Column(Float, nullable=True)
    mbp_min = Column(Float, nullable=True)
    mbp_max = Column(Float, nullable=True)
    resp_rate_min = Column(Float, nullable=True)
    resp_rate_max = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    spo2_min = Column(Float, nullable=True)
    spo2_max = Column(Float, nullable=True)
    glucose_min = Column(Float, nullable=True)
    glucose_max = Column(Float, nullable=True)
    
    # Labs
    wbc_min = Column(Float, nullable=True)
    wbc_max = Column(Float, nullable=True)
    platelet_min = Column(Float, nullable=True)
    platelet_max = Column(Float, nullable=True)
    hemoglobin_min = Column(Float, nullable=True)
    hemoglobin_max = Column(Float, nullable=True)
    neutrophils_abs_min = Column(Float, nullable=True)
    neutrophils_abs_max = Column(Float, nullable=True)
    bands_min = Column(Float, nullable=True)
    bands_max = Column(Float, nullable=True)
    immature_granulocytes_min = Column(Float, nullable=True)
    immature_granulocytes_max = Column(Float, nullable=True)
    lymphocytes_abs_min = Column(Float, nullable=True)
    lymphocytes_abs_max = Column(Float, nullable=True)
    fibrinogen_min = Column(Float, nullable=True)
    fibrinogen_max = Column(Float, nullable=True)
    inr_min = Column(Float, nullable=True)
    inr_max = Column(Float, nullable=True)
    pt_min = Column(Float, nullable=True)
    pt_max = Column(Float, nullable=True)
    
    # Meds
    antibiotic_count = Column(Float, nullable=True)
    
    # Blood Gases
    so2_min = Column(Float, nullable=True)
    so2_max = Column(Float, nullable=True)
    po2_min = Column(Float, nullable=True)
    po2_max = Column(Float, nullable=True)
    pco2_min = Column(Float, nullable=True)
    pco2_max = Column(Float, nullable=True)
    fio2_min = Column(Float, nullable=True)
    fio2_max = Column(Float, nullable=True)
    pfratio_min = Column(Float, nullable=True)
    pfratio_max = Column(Float, nullable=True)
    ventilation_flag = Column(Float, nullable=True)
    ph_min = Column(Float, nullable=True)
    ph_max = Column(Float, nullable=True)
    baseexcess_min = Column(Float, nullable=True)
    baseexcess_max = Column(Float, nullable=True)
    bicarbonate_min = Column(Float, nullable=True)
    bicarbonate_max = Column(Float, nullable=True)
    totalco2_min = Column(Float, nullable=True)
    totalco2_max = Column(Float, nullable=True)
    lactate_min = Column(Float, nullable=True)
    lactate_max = Column(Float, nullable=True)
    
    # Electrolytes
    sodium_min = Column(Float, nullable=True)
    sodium_max = Column(Float, nullable=True)
    potassium_min = Column(Float, nullable=True)
    potassium_max = Column(Float, nullable=True)
    chloride_min = Column(Float, nullable=True)
    chloride_max = Column(Float, nullable=True)
    calcium_min = Column(Float, nullable=True)
    calcium_max = Column(Float, nullable=True)
    
    # Other Labs + Liver
    glucose_min_1 = Column(Float, nullable=True)
    glucose_max_1 = Column(Float, nullable=True)
    albumin_min = Column(Float, nullable=True)
    albumin_max = Column(Float, nullable=True)
    aniongap_min = Column(Float, nullable=True)
    aniongap_max = Column(Float, nullable=True)
    bun_min = Column(Float, nullable=True)
    bun_max = Column(Float, nullable=True)
    creatinine_min = Column(Float, nullable=True)
    creatinine_max = Column(Float, nullable=True)
    total_protein_min = Column(Float, nullable=True)
    total_protein_max = Column(Float, nullable=True)
    globulin_min = Column(Float, nullable=True)
    globulin_max = Column(Float, nullable=True)
    alt_min = Column(Float, nullable=True)
    alt_max = Column(Float, nullable=True)
    ast_min = Column(Float, nullable=True)
    ast_max = Column(Float, nullable=True)
    alp_min = Column(Float, nullable=True)
    alp_max = Column(Float, nullable=True)
    ggt_min = Column(Float, nullable=True)
    ggt_max = Column(Float, nullable=True)
    bilirubin_total_min = Column(Float, nullable=True)
    bilirubin_total_max = Column(Float, nullable=True)
    bilirubin_direct_min = Column(Float, nullable=True)
    bilirubin_direct_max = Column(Float, nullable=True)
    bilirubin_indirect_min = Column(Float, nullable=True)
    bilirubin_indirect_max = Column(Float, nullable=True)
    
    # GCS
    gcs_min = Column(Float, nullable=True)
    gcs_max = Column(Float, nullable=True)
    gcs_motor_min = Column(Float, nullable=True)
    gcs_motor_max = Column(Float, nullable=True)
    gcs_verbal_min = Column(Float, nullable=True)
    gcs_verbal_max = Column(Float, nullable=True)
    gcs_eyes_min = Column(Float, nullable=True)
    gcs_eyes_max = Column(Float, nullable=True)
    
    # Cardiac / Inflam
    crp_min = Column(Float, nullable=True)
    crp_max = Column(Float, nullable=True)
    urineoutput_min = Column(Float, nullable=True)
    urineoutput_max = Column(Float, nullable=True)
    troponin_t_min = Column(Float, nullable=True)
    troponin_t_max = Column(Float, nullable=True)
    ck_mb_min = Column(Float, nullable=True)
    ck_mb_max = Column(Float, nullable=True)
    ntprobnp_min = Column(Float, nullable=True)
    ntprobnp_max = Column(Float, nullable=True)
    
    # Output columns (from training data)
    respiration = Column(Float, nullable=True)
    coagulation = Column(Float, nullable=True)
    liver = Column(Float, nullable=True)
    cardiovascular = Column(Float, nullable=True)
    cns = Column(Float, nullable=True)
    renal = Column(Float, nullable=True)
    hours_beforesepsis = Column(Float, nullable=True)
    sepsis = Column(Integer, nullable=True)
    fod = Column(Float, nullable=True)
    hours_beforedeath = Column(Float, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed if empty
    db = SessionLocal()
    if db.query(PatientData).count() == 0:
        print("Seeding database from df_test30.parquet...")
        parquet_path = os.path.join(os.path.dirname(__file__), "../dataset/df_test30.parquet")
        
        if os.path.exists(parquet_path):
            try:
                import pyarrow.parquet as pq
                
                # Read parquet file
                table = pq.read_table(parquet_path)
                df = table.to_pandas()
                
                print(f"Loaded parquet with shape: {df.shape}")
                
                # Get valid columns for the database model
                valid_cols = [c.name for c in PatientData.__table__.columns if c.name != 'id']
                
                # Map 'gender' column to 'f0_' if needed (parquet might have 'gender')
                if 'gender' in df.columns:
                    # Check if gender is mostly null
                    null_ratio = df['gender'].isna().mean()
                    if null_ratio > 0.9:
                        print("Warning: Gender column is mostly empty. Imputing random gender...")
                        import numpy as np
                        # Randomly assign 0 (M) or 1 (F)
                        random_gender = np.random.choice([0, 1], size=len(df))
                        df['gender'] = random_gender
                        
                    if 'f0_' not in df.columns:
                        df['f0_'] = df['gender'].map({0: 'M', 1: 'F', 'M': 'M', 'F': 'F'})
                
                # Convert datetime columns to string
                for col in ['starttime', 'endtime']:
                    if col in df.columns:
                        df[col] = df[col].astype(str)
                
                # Replace NaN/inf with None for SQLite compatibility
                df = df.replace([np.inf, -np.inf], np.nan)
                
                # Filter to only columns that exist in both dataframe and model
                available_cols = [c for c in valid_cols if c in df.columns]
                df_filtered = df[available_cols].copy()
                
                # Convert numpy types to Python native types for SQLite
                for col in df_filtered.columns:
                    if df_filtered[col].dtype == 'float64':
                        df_filtered[col] = df_filtered[col].astype(object).where(df_filtered[col].notna(), None)
                    elif df_filtered[col].dtype == 'int64':
                        df_filtered[col] = df_filtered[col].astype(object).where(df_filtered[col].notna(), None)
                
                # Bulk insert in chunks
                chunksize = 10000
                total_inserted = 0
                
                for i in range(0, len(df_filtered), chunksize):
                    chunk = df_filtered.iloc[i:i+chunksize]
                    records = chunk.to_dict(orient='records')
                    
                    # Clean up None values and convert types
                    cleaned_records = []
                    for rec in records:
                        clean_rec = {}
                        for k, v in rec.items():
                            if pd.isna(v):
                                clean_rec[k] = None
                            elif isinstance(v, (np.floating, np.integer)):
                                clean_rec[k] = float(v) if isinstance(v, np.floating) else int(v)
                            else:
                                clean_rec[k] = v
                        cleaned_records.append(clean_rec)
                    
                    db.bulk_insert_mappings(PatientData, cleaned_records)
                    db.commit()
                    total_inserted += len(cleaned_records)
                    print(f"Inserted {total_inserted} records...")
                    
                print(f"Database seeding complete! Total records: {total_inserted}")
                
            except ImportError:
                print("pyarrow not installed. Please install: pip install pyarrow")
            except Exception as e:
                print(f"Error seeding database: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Dataset file not found at {parquet_path}")
    else:
        print(f"Database already has {db.query(PatientData).count()} records")
        
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
