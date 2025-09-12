from fastapi import APIRouter
from src.api.routes import login, users, utils


main_router = APIRouter()

main_router.include_router(login.router)
main_router.include_router(users.router)
main_router.include_router(utils.router)