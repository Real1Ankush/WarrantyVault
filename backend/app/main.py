from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.assets import router as assets_router
from backend.app.api.assistant import router as assistant_router
from backend.app.api.receipts import router as receipts_router


app = FastAPI(
    title="AI Warranty Assistant",
    description="AI-powered receipt and warranty management system",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

app.include_router(receipts_router)
app.include_router(assets_router)
app.include_router(assistant_router)


# ---------------------------------------------------------
# BASIC ENDPOINTS
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Warranty Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }