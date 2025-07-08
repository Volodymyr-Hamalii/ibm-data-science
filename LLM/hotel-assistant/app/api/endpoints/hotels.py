from fastapi import APIRouter, Query
from app.services.rag_service import recommend_hotels
from app.models.hotel import Hotel

router = APIRouter()

@router.get("/recommendations", response_model=list[Hotel])
async def hotel_recommendations(
        query: str = Query(..., example="Family-friendly hotel with pool"),
    ) -> list[Hotel]:
    return recommend_hotels(query)
