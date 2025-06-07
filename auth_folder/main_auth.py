# импорт библиотек
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# импорты из файлов
from routers.routes_8001 import router
from middleware_auth import AuthMiddleware


app = FastAPI()


app.include_router(router)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"], 
                   allow_headers=["*"],  
                   )


app.add_middleware(AuthMiddleware)


async def run_server(app, port):
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_server(app, 8001)
    )
# запуск

if __name__ == '__main__':
       asyncio.run("main_auth:app", host="0.0.0.0", port=8001, reload=True)
