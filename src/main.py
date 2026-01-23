from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.v1.endpoints import login

app = FastAPI(
    title="Task Manager API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# TODO: Configure CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO: Implement your API
# Consider:
# - Authentication endpoints
# - Task CRUD operations
# - Project management
# - Permission checking
# - Health check endpoint

app.include_router(login.router, prefix=settings.API_V1_STR, tags=["login"])

@app.get("/")
async def root():
    return {"message": "Task Manager API"}
