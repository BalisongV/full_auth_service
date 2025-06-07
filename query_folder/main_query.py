from fastapi import FastAPI
import uvicorn
import logging
import sys
import asyncio
from query_database import Base, async_engine 
from query_router import router

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"), 
    ]
)

app = FastAPI(
    title="Query Service",
    description="Service to interact with PostgreSQL database for user data.",
)


@app.on_event("startup")
async def startup_event():
    try:
        async with async_engine.begin() as conn:
            print("Checking database tables...")
            # Удаляем таблицы при запуске, чтобы обновить структуру
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables are ready.")
    except Exception as e:
        print(f"Error during startup: {e}")
        sys.exit(1)

app.include_router(router)

async def run_server(app, port):
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_server(app, 8003),
    )

if __name__ == '__main__':
       asyncio.run(main())
