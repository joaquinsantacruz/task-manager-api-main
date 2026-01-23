from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Manager API")

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


@app.get("/")
async def root():
    return {"message": "Task Manager API"}
