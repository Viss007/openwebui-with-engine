from fastapi import FastAPI, HJSONResponse
app = FastAPI()

@app.get("/engine/ready")
def ready():
 Return 200 JSON: {"status":"ok"}, JSONResponse.OK 