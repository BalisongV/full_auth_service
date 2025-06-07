from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx  # Для запросов к Postgres
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import logging
from typing import Optional
import re

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Прописать exception errors например httpx.ConnectError: All connection attempts failed

# Конфигурация (в docker работать не будет, нужен файл с конфигурацией .env)

POSTGRES_SERVICE_URL = "http://query-service-masha:8003"  # URL Postgres-сервиса


# Модель данных
class UserCreate(BaseModel):
    username: str = Field(default=None, min_length=2, max_length=50)
    password: str
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    age: Optional[int] = Field(default=None, ge=0, le=150)
    email: Optional[EmailStr] = None
    role: Optional[str] = "user"

    class Config:
        from_attributes = True

    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        

        if not re.fullmatch(r'^(?!(\.+_+|_+\.+)$)[A-Za-z0-9._]+$', v):
            raise ValueError(
                "Username может содержать только латинские буквы (a-z), цифры, "
                "точки и подчёркивания, но не может состоять только из них"
            )
        
        if v.isdigit():
            raise ValueError("Username не может состоять только из цифр")

        return v

    @field_validator('name')
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        
        # Удаляем лишние пробелы и обрезаем края
        normalized_name = re.sub(r"\s+", " ", v.strip())
        
        # Проверяем, что остались только буквы и пробелы
        if not normalized_name.replace(" ", "").isalpha():
            raise ValueError('Имя должно содержать только буквы и пробелы')
        
        return normalized_name
    @field_validator('password')
    def validate_password(cls, v):
        # Минимум 8 символов
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов')
        
        # Должен содержать хотя бы одну цифру
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        
        # Должен содержать хотя бы одну букву в верхнем регистре
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        
        # Должен содержать хотя бы одну букву в нижнем регистре
        if not any(char.islower() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        
        # Должен содержать хотя бы один специальный символ
        special_chars = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if not special_chars.search(v):
            raise ValueError('Пароль должен содержать хотя бы один специальный символ (@_!#$%^&*()<>?/\|}{~:)')
        
        return v

    @field_validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'admin']
        if v.lower() not in allowed_roles:
            raise ValueError(f'Роль должна быть одной из: {", ".join(allowed_roles)}')
        return v.lower()
    


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
