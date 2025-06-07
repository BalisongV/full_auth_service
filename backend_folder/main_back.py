from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx  # Для запросов к Postgres
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Прописать exception errors например httpx.ConnectError: All connection attempts failed

# Конфигурация (в docker работать не будет, нужен файл с конфигурацией .env)

POSTGRES_SERVICE_URL = "http://query-service-masha:8003"  # URL Postgres-сервиса


# Модель данных
class UserCreate(BaseModel):
    user_id: int
    name: str
    age: int
    email: EmailStr
    role: str
    username: str
    hashed_password: str

class ErrorResponse(BaseModel):
    detail: str
    error_type: Optional[str] = None

# Обработчик ошибок подключения
async def handle_postgres_request(method: str, url: str, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await getattr(client, method)(url, **kwargs)
            response.raise_for_status()
            return response
            
    except httpx.ConnectError as e:
        logger.error(f"Connection error to Postgres service: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Postgres service unavailable",
                "type": "connection_error"
            }
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Postgres service error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": f"Postgres service returned error: {str(e)}",
                "type": "http_error"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "type": "unexpected_error"
            }
        )

# Маршруты
@app.post("/add_user", response_model=UserCreate, responses={
    503: {"model": ErrorResponse, "description": "Service unavailable"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def add_user(user_data: UserCreate):
    try:
        postgres_response = await handle_postgres_request(
            "post",
            f"{POSTGRES_SERVICE_URL}/add_user",
            json=user_data.dict()
        )
        return JSONResponse(content=postgres_response.json(), status_code=postgres_response.status_code)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Unexpected error in add_user")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_user/{user_id}", responses={
    503: {"model": ErrorResponse, "description": "Service unavailable"},
    404: {"model": ErrorResponse, "description": "User not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def delete_user(user_id: int):
    try:
        postgres_response = await handle_postgres_request(
            "delete",
            f"{POSTGRES_SERVICE_URL}/delete_user/{user_id}"
        )
        return JSONResponse(content=postgres_response.json(), status_code=postgres_response.status_code)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Unexpected error in delete_user")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_user/{user_id}", responses={
    503: {"model": ErrorResponse, "description": "Service unavailable"},
    404: {"model": ErrorResponse, "description": "User not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_user(user_id: int):
    try:
        postgres_response = await handle_postgres_request(
            "get",
            f"{POSTGRES_SERVICE_URL}/get_user/{user_id}"
        )
        return JSONResponse(content=postgres_response.json(), status_code=postgres_response.status_code)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Unexpected error in get_user")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_all_users", responses={
    503: {"model": ErrorResponse, "description": "Service unavailable"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_all_users():
    try:
        postgres_response = await handle_postgres_request(
            "get",
            f"{POSTGRES_SERVICE_URL}/get_all_users"
        )
        return JSONResponse(content=postgres_response.json(), status_code=postgres_response.status_code)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Unexpected error in get_all_users")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_back:app", host="0.0.0.0", port=8000, reload=True)
