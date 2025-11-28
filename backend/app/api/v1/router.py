from fastapi import APIRouter

from app.api.v1.endpoints import auth, oauth, roadmaps, quizzes, roadmap_chat, interviews

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(oauth.router, prefix="/auth", tags=["oauth"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(roadmap_chat.router, prefix="/roadmaps", tags=["roadmap-chat"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
