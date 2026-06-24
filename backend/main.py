from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, beans, extractions, equipment, water, users
from fastapi.staticfiles import StaticFiles
import os

# Create all tables in the database (for Oracle or fallback SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BaristaPRO API",
    description="Backend API for BaristaPRO Desktop and Mobile Applications.",
    version="1.0.0"
)

# Mount static files for avatars
os.makedirs("/app/static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# CORS middleware for mobile/web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, restrict this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Profile"])
app.include_router(beans.router, prefix="/api/beans", tags=["Beans & Batches"])
app.include_router(extractions.router, prefix="/api/extractions", tags=["Extraction Logs"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment & Maintenance"])
app.include_router(water.router, prefix="/api/water", tags=["Water Recipes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the BaristaPRO API"}
