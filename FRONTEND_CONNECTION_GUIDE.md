# 🔗 LifeShield AI — Complete Frontend ↔ ML Backend Connection Guide

## 📋 Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Backend API Details](#2-backend-api-details)
3. [Step-by-Step: Connect Frontend Locally](#3-step-by-step-connect-frontend-locally)
4. [Step-by-Step: Deploy Backend to Render (Free)](#4-step-by-step-deploy-backend-to-render-free)
5. [Step-by-Step: Connect Frontend to Deployed Backend](#5-step-by-step-connect-frontend-to-deployed-backend)
6. [API Reference — All Endpoints](#6-api-reference--all-endpoints)
7. [Frontend JavaScript Code Explained](#7-frontend-javascript-code-explained)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Architecture Overview

```
┌──────────────────────┐         HTTP (JSON)         ┌─────────────────────────┐
│                      │ ──────────────────────────▶ │                         │
│   FRONTEND (HTML)    │    POST /predict             │   BACKEND (FastAPI)     │
│   index.html         │                              │   main.py               │
│                      │ ◀────────────────────────── │                         │
│   - User enters      │    JSON Response             │   - Loads ML Model      │
│     health data      │    {risk_level, score...}    │   - Scales features     │
│   - Sends to API     │                              │   - Predicts risk       │
│   - Shows results    │                              │   - Returns JSON        │
└──────────────────────┘                              └─────────────────────────┘
                                                              │
                                                              ▼
                                                      ┌─────────────────┐
                                                      │  ML Model Files │
                                                      │  best_model.pkl │
                                                      │  scaler.pkl     │
                                                      │  feature_columns│
                                                      └─────────────────┘
```

**How it works:**
1. The **frontend** (HTML/JS) collects user health data from a form
2. It sends the data as **JSON** to the backend API via `fetch()`
3. The **backend** (Python FastAPI) receives the data, runs it through the **ML model**
4. The backend returns a **JSON response** with risk predictions
5. The **frontend** displays the results with animations

---

## 2. Backend API Details

### Base URL
| Environment | URL |
|-------------|-----|
| Local       | `http://localhost:8000` |
| Deployed (Render) | `https://your-app-name.onrender.com` |

### CORS (Cross-Origin Resource Sharing)
Your backend already has CORS enabled for **all origins** (`allow_origins=["*"]`), so any frontend can connect to it — whether it's running on `localhost`, GitHub Pages, or any other domain.

---

## 3. Step-by-Step: Connect Frontend Locally

### Step 1: Start the Backend Server

```bash
# Navigate to your project folder
cd /Users/kalibabupragada/lifeshield-backend.zip

# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the backend server
python main.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading model artifacts...
INFO:     All artifacts loaded and validated successfully.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Verify Backend is Running

Open your browser and go to:
- `http://localhost:8000` → Should show welcome JSON
- `http://localhost:8000/docs` → Interactive Swagger UI to test API
- `http://localhost:8000/health` → Health check

### Step 3: Open the Frontend

Your `index.html` is already configured to connect to `http://localhost:8000/predict`.

```bash
# Open the frontend in your browser
open index.html
```

### Step 4: Test It!
1. Enter health data (Age, BMI, Health Rating, etc.)
2. Click **"Analyze Bio-Risk"**
3. The frontend sends data to `http://localhost:8000/predict`
4. Results appear with vitality score, risk level, and recommendation

---

## 4. Step-by-Step: Deploy Backend to Render (Free)

Your project already has `render.yaml` and `Procfile` configured!

### Step 1: Create a Render Account
Go to [https://render.com](https://render.com) and sign up (free).

### Step 2: Create a New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo: `Kalibabu0770/heallth-ai`
3. Render will auto-detect your `render.yaml` settings

### Step 3: Configure Settings
| Setting | Value |
|---------|-------|
| **Name** | `lifeshield-backend` |
| **Environment** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

### Step 4: Deploy!
Click **"Create Web Service"** and wait ~3-5 minutes for deployment.

Your backend will be live at: **`https://lifeshield-backend.onrender.com`**

### Step 5: Verify Deployment
Visit these URLs in your browser:
- `https://lifeshield-backend.onrender.com/` → Welcome message
- `https://lifeshield-backend.onrender.com/health` → Health check
- `https://lifeshield-backend.onrender.com/docs` → API documentation

---

## 5. Step-by-Step: Connect Frontend to Deployed Backend

Once your backend is deployed, update **one single line** in `index.html`:

### Change this line (line 319):
```javascript
// ❌ OLD — Only works when backend runs locally
const API_URL = 'http://localhost:8000/predict';
```

### To this:
```javascript
// ✅ NEW — Points to your deployed Render backend
const API_URL = 'https://lifeshield-backend.onrender.com/predict';
```

That's it! Your frontend can now be hosted **anywhere** (GitHub Pages, Netlify, Vercel, etc.) and it will communicate with your deployed ML backend.

---

## 6. API Reference — All Endpoints

### `GET /` — Welcome
```json
// Response
{
    "message": "Welcome to the LifeShield AI Backend",
    "status": "online",
    "documentation": "/docs",
    "health_check": "/health"
}
```

### `GET /health` — Health Check
```json
// Response
{
    "status": "healthy",
    "artifacts_loaded": true
}
```

### `POST /predict` — ⭐ Main Prediction Endpoint

**Request:**
```json
{
    "features": {
        "age": 45,
        "bmi": 24.5,
        "genhlth": 3,
        "gender": 1,
        "smoker": 0,
        "income": 50000,
        "physhlth": 0,
        "menthlth": 0
    }
}
```

**Response:**
```json
{
    "risk_probability": 0.2534,
    "risk_level": "Low",
    "confidence": 0.4932,
    "vitality_score": 74.66,
    "recommendation": "Your health indicators look great. Maintain your current lifestyle and regular checkups."
}
```

### Feature Fields Explained:
| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `age` | int | User's age in years | 1–120 |
| `bmi` | float | Body Mass Index | 15.0–50.0 |
| `genhlth` | int | General health rating | 1=Excellent, 2=Very Good, 3=Good, 4=Fair, 5=Poor |
| `gender` | int | Gender | 1=Male, 0=Female |
| `smoker` | int | Smoking status | 0=Never, 1=Current smoker |
| `income` | int | Income level (default) | e.g., 50000 |
| `physhlth` | int | Physical health days (bad) | 0–30 |
| `menthlth` | int | Mental health days (bad) | 0–30 |

### Response Fields Explained:
| Field | Type | Description |
|-------|------|-------------|
| `risk_probability` | float | 0.0 (no risk) to 1.0 (highest risk) |
| `risk_level` | string | "Low" (<0.3), "Moderate" (0.3–0.7), "High" (>0.7) |
| `confidence` | float | 0.0 to 1.0 — how certain the AI is |
| `vitality_score` | float | 0 to 100 — overall health vitality score |
| `recommendation` | string | AI-generated health recommendation |

---

## 7. Frontend JavaScript Code Explained

Here's exactly how the frontend connects to the ML backend:

```javascript
// 1️⃣ DEFINE THE API URL
const API_URL = 'http://localhost:8000/predict';
// Change to your Render URL after deployment

// 2️⃣ COLLECT USER INPUT FROM THE FORM
const payload = {
    features: {
        age: parseInt(document.getElementById('age').value),
        bmi: parseFloat(document.getElementById('bmi').value),
        genhlth: parseInt(document.getElementById('genhlth').value),
        gender: parseInt(document.getElementById('gender').value),
        smoker: parseInt(document.getElementById('smoker').value),
        income: 50000,        // default value (not in UI form)
        physhlth: 0,          // default value (not in UI form)
        menthlth: 0           // default value (not in UI form)
    }
};

// 3️⃣ SEND DATA TO BACKEND VIA fetch()
const response = await fetch(API_URL, {
    method: 'POST',                              // HTTP POST request
    headers: { 'Content-Type': 'application/json' }, // Tell backend it's JSON
    body: JSON.stringify(payload)                 // Convert JS object to JSON string
});

// 4️⃣ RECEIVE AND PARSE THE RESPONSE
const data = await response.json();

// 5️⃣ DISPLAY RESULTS
// data.risk_probability → "15.2%"
// data.risk_level       → "Low"
// data.confidence       → "92.4%"
// data.vitality_score   → "85"
// data.recommendation   → "Your health indicators look great..."
```

---

## 8. Troubleshooting

### ❌ "Analysis failed. Make sure the backend server is running."
**Cause:** Frontend can't reach the backend.
**Fix:**
- If running locally: Make sure `python main.py` is running in terminal
- If deployed: Check your Render dashboard for errors
- Check the API_URL in `index.html` matches your backend URL

### ❌ CORS Error in Browser Console
**Cause:** Backend doesn't allow your frontend's origin.
**Fix:** Your backend already has `allow_origins=["*"]` so this should not happen. If it does, check that the CORS middleware is properly configured.

### ❌ "Model artifacts are not loaded" (503 Error)
**Cause:** The `.pkl` files failed to load on startup.
**Fix:** Make sure `best_model.pkl`, `scaler.pkl`, and `feature_columns.pkl` exist in the project root.

### ❌ "Prediction failed" (500 Error)
**Cause:** Feature mismatch between frontend data and what the model expects.
**Fix:** Make sure you're sending all required features in the `features` object. Missing features will be filled with `0` by default via `reindex(fill_value=0)`.

### ❌ Render Deploy Fails
**Fix:**
- Ensure `.pkl` files are committed to Git (not in `.gitignore`)
- Check `requirements.txt` has all dependencies
- Check Render build logs for specific error

---

## ✅ Quick Checklist

- [ ] Backend code pushed to GitHub ✅ (Done!)
- [ ] Backend runs locally with `python main.py`
- [ ] Frontend connects to `http://localhost:8000/predict`
- [ ] Deploy backend to Render
- [ ] Update `API_URL` in `index.html` to Render URL
- [ ] Frontend works with deployed backend
- [ ] Host frontend on GitHub Pages / Netlify (optional)
