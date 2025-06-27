from fastapi import FastAPI
from api.routes import recalls, subscribe, unsubscribe  # or similar

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from RecallHero!"}

# Something like this must exist:
app.include_router(recalls.router, prefix="/recalls")
app.include_router(subscribe.router, prefix="/subscribe")
app.include_router(unsubscribe.router, prefix="/unsubscribe")
