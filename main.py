import os
import logging
import joblib
import pandas as pd
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("lifeshield-backend")

# --- Global Variables for Artifacts ---
model = None
scaler = None
feature_columns = None

# --- Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler, feature_columns
    logger.info("Starting up LifeShield Backend...")
    
    try:
        # Load Artifacts
        logger.info("Loading model artifacts...")
        model = joblib.load("best_model.pkl")
        scaler = joblib.load("scaler.pkl")
        feature_columns = joblib.load("feature_columns.pkl")
        
        # Validation
        if not hasattr(model, "predict_proba"):
            raise ValueError("Loaded model does not support predict_proba")
        if not isinstance(feature_columns, list):
            raise ValueError("feature_columns.pkl must contain a list of column names")
            
        logger.info(f"Loaded {len(feature_columns)} feature columns.")
        logger.info("All artifacts loaded and validated successfully.")
        
    except Exception as e:
        logger.error(f"Failed to load artifacts: {str(e)}")
        # In production, we might want to prevent startup if artifacts are missing
        raise RuntimeError(f"Startup failed: Could not load required artifacts. {e}")

    yield
    
    logger.info("Shutting down LifeShield Backend...")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="LifeShield AI Backend",
    description="Machine Learning Health Risk Prediction API",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class HealthFeatures(BaseModel):
    # Accepting a flexible dictionary to handle potential schema variations
    # while reindexing ensures the model gets exactly what it needs.
    features: Dict[str, Any] = Field(
        ..., 
        json_schema_extra={
            "example": {
                "age": 45,
                "gender": 1,
                "income": 50000,
                "genhlth": 3,
                "bmi": 24.5
            }
        }
    )

class PredictionResponse(BaseModel):
    risk_probability: float
    risk_level: str
    confidence: float
    vitality_score: float
    recommendation: str

# --- Helper Functions ---
def get_risk_metadata(prob: float) -> tuple:
    if prob < 0.3:
        level = "Low"
        rec = "Your health indicators look great. Maintain your current lifestyle and regular checkups."
    elif prob < 0.7:
        level = "Moderate"
        rec = "Some indicators suggest potential risks. Consider consulting a professional and reviewing your diet/exercise habits."
    else:
        level = "High"
        rec = "High-risk indicators detected. We strongly recommend scheduling a comprehensive medical evaluation."
    
    # Confidence is simplified as the certainty of the prediction
    # (distance from the 0.5 decision boundary)
    confidence = abs(prob - 0.5) * 2
    vitality_score = (1 - prob) * 100
    
    return level, confidence, vitality_score, rec

# --- Endpoints ---
@app.get("/")
async def root():
    """Welcome page for the API."""
    return {
        "message": "Welcome to the LifeShield AI Backend",
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "artifacts_loaded": model is not None and scaler is not None and feature_columns is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: HealthFeatures):
    """
    Predict health risk based on input features.
    """
    if model is None or scaler is None or feature_columns is None:
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded.")

    try:
        # Create input DataFrame
        input_df = pd.DataFrame([input_data.features])
        
        # 1. Prepare features for SCALER
        # The scaler was trained on a specific subset. We must match it exactly.
        scaler_features = getattr(scaler, "feature_names_in_", feature_columns)
        df_for_scaler = input_df.reindex(columns=scaler_features, fill_value=0)
        
        # Transform using scaler
        scaled_features = scaler.transform(df_for_scaler)
        
        # 2. Prepare features for MODEL
        # The model was trained on the full set (including gender/income/smoker)
        model_features = getattr(model, "feature_names_in_", feature_columns)
        
        # We need to combine the scaled features back with the unscaled features (like gender)
        # to match the model's expected input structure.
        final_df = input_df.reindex(columns=model_features, fill_value=0)
        
        # Update the scaled columns in the final dataframe
        for i, col in enumerate(scaler_features):
            final_df[col] = scaled_features[:, i]
            
        # 3. Predict
        # We use .values to avoid any remaining "feature name mismatch" warnings
        prediction_proba = model.predict_proba(final_df.values)[0][1]
        
        # 4. Generate Metadata
        risk_level, confidence, vitality_score, recommendation = get_risk_metadata(prediction_proba)
        
        return PredictionResponse(
            risk_probability=round(float(prediction_proba), 4),
            risk_level=risk_level,
            confidence=round(float(confidence), 4),
            vitality_score=round(float(vitality_score), 2),
            recommendation=recommendation
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Use environment variable for port (Render compatibility)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
