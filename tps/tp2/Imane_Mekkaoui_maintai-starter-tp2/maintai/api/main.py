"""API MaintAI : expose le modèle de prédiction de panne.

Lancement : uvicorn maintai.api.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from maintai import __version__
from maintai.api.schemas import HealthOut, PredictionOut, SensorReading
from maintai.api.security import require_api_key
from maintai.config import get_settings
from maintai.predict import Predictor

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle au démarrage de l'API et libère son état à l'arrêt."""
    try:
        state["predictor"] = Predictor.load(get_settings())
    except FileNotFoundError:
        # L'API peut démarrer sans modèle ; /health le signale et /predict renverra 503.
        state["predictor"] = None
    yield
    state.clear()


app = FastAPI(
    title="MaintAI API",
    version=__version__,
    description="Prédiction de panne à partir de relevés de capteurs.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().cors_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# TODO (TP2) : Protégez toutes les routes /v1 : ajoutez require_api_key comme dépendance du router (dependencies=[Depends(...)])
# FastAPI applique cette dépendance à chaque route du router /v1. La route /health
# est déclarée directement sur l'application et reste donc accessible sans clé.
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    """Expose l'état de l'API et indique si le modèle a été chargé."""
    return HealthOut(status="ok", model_loaded=state.get("predictor") is not None)


@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    """Prédit le risque de panne pour un relevé de capteurs validé."""
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API",
        )
    return PredictionOut(**predictor.predict(reading.model_dump()))


# Enregistre les routes du router sous le préfixe /v1.
app.include_router(router)
