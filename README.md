# SepsisGuard - AI-Powered Sepsis Prediction System

A comprehensive sepsis prediction system using GRU-D neural network for multi-output early warning predictions. Features a premium medical dashboard with real-time risk visualization.

![SepsisGuard Dashboard](https://img.shields.io/badge/Status-Active-brightgreen) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![Python](https://img.shields.io/badge/Python-3.10+-blue)

## Features

- **Multi-Output Predictions**: Sepsis probability, SOFA component scores (cardiovascular, respiration, coagulation, liver, CNS, renal), time-to-sepsis, and mortality risk
- **70+ Input Features**: Comprehensive patient data form with demographics, vitals, lab results, blood gas, electrolytes, liver function, GCS, and cardiac markers
- **Interactive 3D Visualization**: Real-time organ-level risk display with color-coded severity
- **Dynamic Warnings**: Automatic alerts for critical conditions based on prediction thresholds
- **Premium UI/UX**: Glassmorphism design, smooth animations, responsive layout

## Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ORCA_PURAPURANINJA
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start Backend (Terminal 1)**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend will be available at `http://localhost:8000`

2. **Start Frontend (Terminal 2)**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

3. **Open in Browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Usage

1. **Fill Patient Data**: Use the accordion form on the left to enter patient information across 8 categories
2. **Submit Assessment**: Click "Run Assessment" to send data to the prediction API
3. **View Results**: See the prediction results panel with risk gauge, SOFA scores, and warnings
4. **Monitor 3D View**: Organs change color based on risk level (green→yellow→red)

## Project Structure

```
ORCA_PURAPURANINJA/
├── frontend/                 # Next.js 16 frontend
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   │   ├── dashboard/    # Dashboard components
│   │   │   ├── form/         # Form components
│   │   │   └── ui/           # UI primitives
│   │   └── lib/              # Utilities & config
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── main.py               # FastAPI app
│   ├── api.py                # API routes
│   ├── schemas.py            # Pydantic schemas
│   └── requirements.txt
├── dataset/                  # Training data
│   └── dataset.csv
└── notebook/                 # Model training notebooks
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/predict` | Submit patient data for prediction |

### Prediction Request Example

```json
{
  "age": 65,
  "hr": 0,
  "f0_": "M",
  "heart_rate_min": 70,
  "heart_rate_max": 100,
  "sbp_min": 110,
  "sbp_max": 140
}
```

### Prediction Response

```json
{
  "sepsis": 0.75,
  "respiration": 2.5,
  "coagulation": 1.0,
  "liver": 0.5,
  "cardiovascular": 3.0,
  "cns": 1.0,
  "renal": 2.0,
  "hours_beforesepsis": 4.5,
  "fod": 0.3,
  "hours_beforedeath": 24.0
}
```

## Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS v4, Framer Motion, React Three Fiber
- **Backend**: FastAPI, Pydantic
- **ML**: GRU-D Neural Network (PyTorch)
- **Data**: MIMIC-IV ICU dataset

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
