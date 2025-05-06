from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from recommendations import get_assessments
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse   
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("frontend/info.png")  

@app.get("/health")
def health_check():
    return {"status" : "healthy"}

class RecommendRequest(BaseModel):
    query: str
    
class Assessment(BaseModel):
    url: str
    adaptive_support: str
    description: str
    duration: str
    remote_support: str
    test_type: str
    
class RecommendResponse(BaseModel):
    recommended_assessments: list[Assessment]
    
@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    results = await get_assessments(request.query)
    if not results:
        raise HTTPException(status_code=404, detail="No assessments found.")
    return {"recommended_assessments": results}    