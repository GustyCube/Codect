from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add parent directory to path to import from core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core', 'python'))

from python_analyzer import analyze_python_code
from javascript_analyzer import analyze_javascript_code

app = FastAPI(
    title="Codect API",
    description="AI-generated code detection API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = "python"

class BasicAnalysisResponse(BaseModel):
    result: int  # 0 = human-written, 1 = AI-generated

class DetailedAnalysisResponse(BaseModel):
    result: int
    language: str
    classification: str
    features: Dict[str, Any]

@app.get("/")
async def root():
    return {
        "message": "Codect API",
        "endpoints": {
            "/basic": "Basic analysis - returns only the classification result",
            "/premium": "Detailed analysis - returns classification and all features",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/basic", response_model=BasicAnalysisResponse)
async def basic_analysis(request: CodeAnalysisRequest):
    """
    Basic analysis endpoint: returns only the classification result.
    Returns 1 if AI-generated, 0 if human-written.
    """
    try:
        language = request.language.lower()
        
        if language == 'python':
            features, classification = analyze_python_code(request.code)
        elif language == 'javascript':
            features, classification = analyze_javascript_code(request.code)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
        
        result = 1 if classification == "AI-Generated Code" else 0
        return BasicAnalysisResponse(result=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/premium", response_model=DetailedAnalysisResponse)
async def premium_analysis(request: CodeAnalysisRequest):
    """
    Premium analysis endpoint: returns detailed analysis including all extracted features.
    """
    try:
        language = request.language.lower()
        
        if language == 'python':
            features, classification = analyze_python_code(request.code)
        elif language == 'javascript':
            features, classification = analyze_javascript_code(request.code)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
        
        result = 1 if classification == "AI-Generated Code" else 0
        
        return DetailedAnalysisResponse(
            result=result,
            language=language,
            classification=classification,
            features=features
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)