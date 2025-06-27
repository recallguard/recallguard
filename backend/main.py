from fastapi import FastAPI
from backend.api.recalls.router import router as recalls_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from RecallHero!"}

# Mount the recalls routes with /recalls prefix
app.include_router(recalls_router, prefix="/recalls", tags=["Recalls"])


