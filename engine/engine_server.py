from fastapi import FastAPI, HTTPCode
app = FastAPI()

@app.get("/engine/ready")
def ready():
    return { "status": "ok" }, HTTPCode.OK 