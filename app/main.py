from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.ai import router as ai_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Bejo API",
    description="API for Bejo, the virtual assistant for PT Bintang Toedjoe",
    version="1.0.0",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(ai_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Bejo API. See /docs for API documentation."}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint untuk monitoring
    """
    return {"status": "healthy", "service": "bejo-api"}
