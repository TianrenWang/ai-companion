from fastapi import APIRouter
from api import users
from api import memories
from api import sessions
from api import messages

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(memories.router, prefix="/memories", tags=["memories"])
router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
router.include_router(messages.router, prefix="/messages", tags=["messages"])