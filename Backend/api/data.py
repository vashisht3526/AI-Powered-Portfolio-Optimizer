from fastapi import APIRouter

from services import data_service
from services import nifty50_pipeline

router = APIRouter()


@router.get("/update-status")
def get_update_status():
    return data_service.get_update_status()


@router.post("/refresh")
def refresh_data_and_metrics():
    return nifty50_pipeline.refresh_nifty50_data_and_metrics()
