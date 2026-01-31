from pydantic import BaseModel
from typing import Optional

class PredictionInput(BaseModel):
    # Demographics & Meta
    hr: float
    age: float
    height: Optional[float] = None
    f0_: str # Gender (M/F)
    
    # Vitals (Min/Max)
    heart_rate_min: Optional[float] = None
    heart_rate_max: Optional[float] = None
    sbp_min: Optional[float] = None
    sbp_max: Optional[float] = None
    dbp_min: Optional[float] = None
    dbp_max: Optional[float] = None
    mbp_min: Optional[float] = None
    mbp_max: Optional[float] = None
    resp_rate_min: Optional[float] = None
    resp_rate_max: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    spo2_min: Optional[float] = None
    spo2_max: Optional[float] = None
    glucose_min: Optional[float] = None
    glucose_max: Optional[float] = None
    
    # Labs (Min/Max)
    wbc_min: Optional[float] = None
    wbc_max: Optional[float] = None
    platelet_min: Optional[float] = None
    platelet_max: Optional[float] = None
    hemoglobin_min: Optional[float] = None
    hemoglobin_max: Optional[float] = None
    neutrophils_abs_min: Optional[float] = None
    neutrophils_abs_max: Optional[float] = None
    bands_min: Optional[float] = None
    bands_max: Optional[float] = None
    immature_granulocytes_min: Optional[float] = None
    immature_granulocytes_max: Optional[float] = None
    lymphocytes_abs_min: Optional[float] = None
    lymphocytes_abs_max: Optional[float] = None
    fibrinogen_min: Optional[float] = None
    fibrinogen_max: Optional[float] = None
    inr_min: Optional[float] = None
    inr_max: Optional[float] = None
    pt_min: Optional[float] = None
    pt_max: Optional[float] = None
    
    # Medication / Intervention
    antibiotic_count: Optional[float] = None
    
    # Blood Gases
    so2_min: Optional[float] = None
    so2_max: Optional[float] = None
    po2_min: Optional[float] = None
    po2_max: Optional[float] = None
    pco2_min: Optional[float] = None
    pco2_max: Optional[float] = None
    fio2_min: Optional[float] = None
    fio2_max: Optional[float] = None
    pfratio_min: Optional[float] = None
    pfratio_max: Optional[float] = None
    ventilation_flag: Optional[float] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    baseexcess_min: Optional[float] = None
    baseexcess_max: Optional[float] = None
    bicarbonate_min: Optional[float] = None
    bicarbonate_max: Optional[float] = None
    totalco2_min: Optional[float] = None
    totalco2_max: Optional[float] = None
    lactate_min: Optional[float] = None
    lactate_max: Optional[float] = None
    
    # Electrolytes
    sodium_min: Optional[float] = None
    sodium_max: Optional[float] = None
    potassium_min: Optional[float] = None
    potassium_max: Optional[float] = None
    chloride_min: Optional[float] = None
    chloride_max: Optional[float] = None
    calcium_min: Optional[float] = None
    calcium_max: Optional[float] = None
    
    # Other Labs
    glucose_min_1: Optional[float] = None
    glucose_max_1: Optional[float] = None
    albumin_min: Optional[float] = None
    albumin_max: Optional[float] = None
    aniongap_min: Optional[float] = None
    aniongap_max: Optional[float] = None
    bun_min: Optional[float] = None
    bun_max: Optional[float] = None
    creatinine_min: Optional[float] = None
    creatinine_max: Optional[float] = None
    total_protein_min: Optional[float] = None
    total_protein_max: Optional[float] = None
    globulin_min: Optional[float] = None
    globulin_max: Optional[float] = None
    
    # Liver Function
    alt_min: Optional[float] = None
    alt_max: Optional[float] = None
    ast_min: Optional[float] = None
    ast_max: Optional[float] = None
    alp_min: Optional[float] = None
    alp_max: Optional[float] = None
    ggt_min: Optional[float] = None
    ggt_max: Optional[float] = None
    bilirubin_total_min: Optional[float] = None
    bilirubin_total_max: Optional[float] = None
    bilirubin_direct_min: Optional[float] = None
    bilirubin_direct_max: Optional[float] = None
    bilirubin_indirect_min: Optional[float] = None
    bilirubin_indirect_max: Optional[float] = None
    
    # GCS
    gcs_min: Optional[float] = None
    gcs_max: Optional[float] = None
    gcs_motor_min: Optional[float] = None
    gcs_motor_max: Optional[float] = None
    gcs_verbal_min: Optional[float] = None
    gcs_verbal_max: Optional[float] = None
    gcs_eyes_min: Optional[float] = None
    gcs_eyes_max: Optional[float] = None
    
    # Inflammation / Cardiac
    crp_min: Optional[float] = None
    crp_max: Optional[float] = None
    urineoutput_min: Optional[float] = None
    urineoutput_max: Optional[float] = None
    troponin_t_min: Optional[float] = None
    troponin_t_max: Optional[float] = None
    ck_mb_min: Optional[float] = None
    ck_mb_max: Optional[float] = None
    ntprobnp_min: Optional[float] = None
    ntprobnp_max: Optional[float] = None

class PredictionOutput(BaseModel):
    sepsis: int
    respiration: float
    coagulation: float
    liver: float
    cardiovascular: float
    cns: float
    renal: float
    hours_beforesepsis: float
    fod: float
    hours_beforedeath: float
