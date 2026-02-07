# 🏥 Sepsis Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**An AI-powered early warning system for sepsis prediction using MIMIC-IV ICU data**

[Features](#-features) • [Installation](#-installation) • [Dataset](#-obtaining-mimic-iv-dataset) • [API Docs](#-api-endpoints) • [Deployment](#-deployment)

</div>

---

## 📋 Overview

This application leverages machine learning to predict sepsis risk in ICU patients using the **MIMIC-IV** clinical database. The system provides:

- **Real-time sepsis risk prediction** with probability scores
- **Multi-organ dysfunction scoring** (SOFA-based: Respiratory, Cardiovascular, Renal, CNS)
- **Patient monitoring dashboard** with emergency patient tracking
- **Beautiful, modern UI** with dark theme and responsive design

> ⚠️ **Important**: This project uses the MIMIC-IV dataset which requires credentialed access. See [Obtaining MIMIC-IV Dataset](#-obtaining-mimic-iv-dataset) for instructions.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔮 **AI Prediction** | XGBoost-based model for sepsis probability prediction |
| 📊 **Multi-output** | Predicts multiple SOFA component scores (6h, 12h, 24h windows) |
| 🏥 **Patient Dashboard** | View hospital-wide statistics and emergency patients |
| 📝 **Data Entry** | Add new patient measurements with auto-forward-fill |
| 📈 **Visualizations** | Risk gauges, charts, and patient body visualization |
| 🔄 **Real-time Updates** | Auto-refresh patient data and predictions |

---

## 📁 Project Structure

```
Sepsis-Prediction/
├── backend/                    # FastAPI Backend Server
│   ├── api.py                  # API endpoint definitions
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLAlchemy database models
│   ├── model_wrapper.py        # ML model loading & prediction logic
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Python virtual environment (create yourself)
│
├── frontend/                   # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   │   ├── page.tsx        # Main page component
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── globals.css     # Global styles
│   │   ├── components/
│   │   │   ├── dashboard/      # Dashboard components
│   │   │   │   ├── HospitalOverview.tsx
│   │   │   │   ├── PatientDashboard.tsx
│   │   │   │   ├── PredictionResults.tsx
│   │   │   │   └── DistributionChart.tsx
│   │   │   ├── form/           # Form components
│   │   │   │   └── SepsisForm.tsx
│   │   │   ├── ui/             # Reusable UI components
│   │   │   │   ├── RiskGauge.tsx
│   │   │   │   ├── MinMaxInput.tsx
│   │   │   │   └── ...
│   │   │   └── layout/
│   │   │       └── BodyVisualizer.tsx
│   │   └── lib/                # Utilities
│   ├── package.json
│   └── .env.local              # Environment variables (create yourself)
│
├── new_model/                  # Trained ML Model Artifacts
│   ├── model_joblib.pkl        # Main XGBoost model
│   ├── scaler_X.pkl            # Feature scaler
│   ├── scaler_y_reg.pkl        # Target scaler
│   └── global_feat_mean30.npy  # Feature means for imputation
│
├── sql/                        # Database Queries
│   └── select_query.sql        # MIMIC-IV data extraction query
│
├── dataset/                    # Dataset files (NOT included - see instructions)
│
├── notebook/                   # Jupyter notebooks for training
│
├── .gitignore                  # Git ignore rules
├── .gitattributes              # Git LFS configuration
└── README.md                   # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Git LFS** (for large model files)

### 1. Clone Repository

```bash
git clone https://github.com/Expanics/Sepsis-Prediction.git
cd Sepsis-Prediction

# Pull LFS files (model artifacts)
git lfs pull
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
```

---

## 🗄️ Obtaining MIMIC-IV Dataset

The MIMIC-IV database is a **restricted dataset** requiring credentialed access from PhysioNet.

### Step 1: Get PhysioNet Access

1. Go to [PhysioNet](https://physionet.org/)
2. Create an account and complete the **CITI training course**
3. Request access to [MIMIC-IV](https://physionet.org/content/mimiciv/3.1/)
4. Wait for approval (usually 1-2 weeks)

### Step 2: Access via Google BigQuery

Once approved, you can access MIMIC-IV via Google BigQuery:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the BigQuery API
4. Link your PhysioNet credentials to access `physionet-data.mimiciv_3_1_derived`

### Step 3: Run the Data Extraction Query

Execute the SQL query in `sql/select_query.sql` using BigQuery:

```sql
-- This query extracts hourly patient data with vital signs, 
-- lab values, and sepsis labels from MIMIC-IV

-- See sql/select_query.sql for the complete query
```

**Export the results** to CSV or Parquet format.

### Step 4: Prepare the Database

After obtaining the dataset, load it into the SQLite database:

```python
# In backend/ directory
import pandas as pd
from database import init_db, get_db, PatientData
from sqlalchemy.orm import Session

# Load your exported data
df = pd.read_csv('your_mimic_data.csv')  # or parquet

# Initialize database
init_db()

# Insert data (use your own script or modify database.py)
```

---

## 🏃 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
export OMP_NUM_THREADS=1  # Recommended for model performance
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 📡 API Endpoints

Base URL: `http://localhost:8000`

### Statistics & Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check - API status |
| `GET` | `/stats` | Get hospital statistics (total patients, sepsis cases, demographics) |

### Patient Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/patients` | List all patients (with optional `?search=` query) |
| `GET` | `/patients/emergency` | Get patients with sepsis (limit=50) |
| `GET` | `/patient/{stay_id}` | Get patient's complete history |
| `POST` | `/patient` | Add new patient measurement record |

### Predictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/{stay_id}?window_hours=6` | Predict for existing patient (6/12/24h window) |
| `POST` | `/predict?window_hours=6` | Predict from manual input data |

### Example Requests

**Get Patient List:**
```bash
curl http://localhost:8000/patients?search=12345
```

**Get Prediction for Patient:**
```bash
curl -X POST "http://localhost:8000/predict/30001234?window_hours=6"
```

**Manual Prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate_min": 70,
    "heart_rate_max": 90,
    "temperature_min": 36.5,
    "temperature_max": 37.2,
    ...
  }'
```

### Response Format

**Prediction Output:**
```json
{
  "sepsis": 0.45,           // Sepsis probability (0-1)
  "respiration": 1.2,       // Respiratory SOFA score
  "cardiovascular": 0.8,    // Cardiovascular SOFA score
  "renal": 0.3,             // Renal SOFA score
  "cns": 0.5                // CNS SOFA score
}
```

---

## 🛠️ Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Environment Variables

**Backend** (`backend/.env`):
```env
DATABASE_URL=sqlite:///./patients.db
MODEL_PATH=../new_model
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## 📦 Model Information

The prediction model is built using:

- **Algorithm**: XGBoost Multi-output Regressor
- **Features**: 80+ clinical variables (vital signs, lab values, etc.)
- **Outputs**: Sepsis probability + 4 SOFA component scores
- **Training Data**: MIMIC-IV ICU dataset (~100k patients)

### Feature Categories

| Category | Features |
|----------|----------|
| **Vital Signs** | Heart rate, BP, Temperature, SpO2, Respiratory rate |
| **Blood** | WBC, Platelets, Hemoglobin, Neutrophils, INR, PT |
| **Respiratory** | PO2, PCO2, FiO2, P/F ratio, Ventilation status |
| **Acid-Base** | pH, Lactate, Bicarbonate, Base excess |
| **Electrolytes** | Na, K, Cl, Ca, Glucose |
| **Chemistry** | Creatinine, BUN, Albumin, Bilirubin, Liver enzymes |
| **Neurological** | GCS (motor, verbal, eyes) |
| **Cardiac** | Troponin, CK-MB, NT-proBNP |
| **Vasopressors** | Dopamine, Epinephrine, Norepinephrine doses |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This application is for **research and educational purposes only**. It should NOT be used for clinical decision-making without proper validation and regulatory approval. Always consult qualified healthcare professionals for medical decisions.

---

## 🙏 Acknowledgments

- [MIMIC-IV Database](https://mimic.mit.edu/) - PhysioNet
- [Sepsis-3 Definitions](https://jamanetwork.com/journals/jama/fullarticle/2492881) - JAMA
- Built with ❤️ using FastAPI, Next.js, and XGBoost
