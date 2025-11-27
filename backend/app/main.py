from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="LoadmapAI API",
    description="AI 기반 학습 로드맵 관리 플랫폼",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "LoadmapAI API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
