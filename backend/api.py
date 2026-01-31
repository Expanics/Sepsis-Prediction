from fastapi import APIRouter
from schemas import PredictionInput, PredictionOutput

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
async def predict_sepsis(data: PredictionInput):
    # Mock logic for now
    return {
        "sepsis": 0,
        "respiration": 0.1,
        "coagulation": 0.2,
        "liver": 0.1,
        "cardiovascular": 0.3,
        "cns": 0.1,
        "renal": 0.2,
        "hours_beforesepsis": 100,
        "fod": 0,
        "hours_beforedeath": 200
    }
