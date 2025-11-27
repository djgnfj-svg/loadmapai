from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# TODO: 라우터 추가 예정
# api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
# api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
