from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.hotels import router as hotels_router
from app.api.endpoints.chat import router as chat_router

app = FastAPI(title="Hotel Recommendation Assistant")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # NextJS default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
