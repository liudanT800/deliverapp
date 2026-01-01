from fastapi import APIRouter

from app.api.routes import auth, tasks, users, maps, chat, evaluation, payment, appeal

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(maps.router)
api_router.include_router(chat.router)
api_router.include_router(evaluation.router)
api_router.include_router(payment.router)
api_router.include_router(appeal.router)

