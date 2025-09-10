import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import engine
from src.core.db_init import init_db


async def init(): 
    async with AsyncSession(engine) as session:
        await init_db(session)


async def main():
    await init()


if __name__ == "__main__":
    asyncio.run(main())