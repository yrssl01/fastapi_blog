from fastapi import APIRouter
from src.api.routes import login 


main_router = APIRouter()

main_router.include_router(login.router)