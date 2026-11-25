from fastapi import FastAPI
from backend.recommendations import router

# Create a temporary FastAPI application for testing.
app = FastAPI(title="AI Resume Recommendation Test Server")

# Register our recommendation router.
app.include_router(router)


# Verify that the server is running.
@app.get("/api/health")
def health():
    return {"status": "ok"}