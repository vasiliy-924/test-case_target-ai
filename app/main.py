from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "WebSocket Service is running"}