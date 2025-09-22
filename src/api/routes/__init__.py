from fastapi import APIRouter
from src.api.routes import login, users, utils
from src.api.routes.categories import router as category_router


main_router = APIRouter()

main_router.include_router(login.router)
main_router.include_router(users.router)
main_router.include_router(utils.router)
main_router.include_router(category_router.router)