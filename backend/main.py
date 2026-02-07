from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from api import router
from model_wrapper import ModelWrapper
import os

app = FastAPI(title="Sepsis Prediction API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def on_startup():
    # Helper: Ensure the cwd is correct for relative paths if needed, 
    # but using absolute based on __file__ is safer.
    print("Initializing Database...")
    init_db()
    
    print("Loading Model...")
    model_dir = os.path.join(os.path.dirname(__file__), "../new_model")
    # Check if model dir exists
    if os.path.exists(model_dir):
        app.state.model = ModelWrapper(model_dir)
    else:
        print(f"WARNING: Model directory not found at {model_dir}")
        app.state.model = None

@app.get("/")
async def root():
    return {"message": "Sepsis Prediction API is running"}
