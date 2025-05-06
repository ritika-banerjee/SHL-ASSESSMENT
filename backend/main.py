from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommendations import get_assessments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Request/response models
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

# Main recommendation endpoint
@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    results = await get_assessments(request.query)
    if not results:
        raise HTTPException(status_code=404, detail="No assessments found.")
    return {"recommended_assessments": results}
