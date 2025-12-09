from fastapi import APIRouter

from app.api.v1.endpoints import auth, roadmaps, interview, learning, oauth, feedback_chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(feedback_chat.router, prefix="/feedback", tags=["feedback"])
