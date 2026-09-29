from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_NAME
from legalEaseAPI.routes import router


app = FastAPI(
    title=APP_NAME,
    description="AI-powered legal document generation API",
    version="1.0.0",
)


# Allow the Streamlit frontend to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to LegalEase API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "legalEaseAPI.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )