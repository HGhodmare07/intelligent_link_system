import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Add ml-service/src to Python import path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


from predict_production import check_url


app = FastAPI(title="URL Validation Service")


class UrlRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "message": "URL Validation Service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/check")
def check(req: UrlRequest):
    try:
        result = check_url(req.url)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )