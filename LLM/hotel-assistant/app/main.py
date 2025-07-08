from fastapi import FastAPI
from app.api.endpoints.hotels import router as hotels_router

app = FastAPI(title="Hotel Recommendation Assistant")

app.include_router(hotels_router, prefix="/api")
