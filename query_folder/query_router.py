from fastapi import APIRouter, Depends, HTTPException, Response, status
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import query_crud, query_schemas
from query_database import get_db_session
from query_models import User
import bcrypt
from sqlalchemy import select
from pydantic import BaseModel


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=status.HTTP_200_OK)
async def register(user_data: query_schemas.UserCreate, db: AsyncSession = Depends(get_db_session)):
    user_dict = user_data.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict["password"])
    del user_dict["password"]  
    user_obj = User(**user_dict)
    created_user = await query_crud.create_user(db=db, user=user_obj)
    return {"message": "User created successfully"}

@router.post("/signin", status_code=200)
async def signin(user_data: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        db_user = await db.execute(select(User).where(User.username == user_data.username))
        db_user = db_user.scalar_one_or_none()
        
        if not db_user or not verify_password(user_data.password, db_user.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Некорректное имя пользователя или пароль"}
            )
            
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Вход выполнен успешно"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Внутренняя ошибка сервера: {str(e)}"}
        )

@router.post("/add_user")
async def add_user(user: query_schemas.UserCreate, db: AsyncSession = Depends(get_db_session)):
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict["password"])
    del user_dict["password"]
    user_obj = User(**user_dict)
    created_user = await query_crud.create_user(db=db, user=user_obj)

    return JSONResponse(
        content={"message": "User created successfully"},
        status_code=201
    )


@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        deleted_user = await query_crud.delete_user(db=db, user_id=user_id)

        if deleted_user == "Пользователь не найден":
            return JSONResponse(
                content={"message": "User not found"},
                status_code=404
            )
        if deleted_user == f"Пользователь с id {user_id} успешно удален":
            return JSONResponse(
                content={"message": "User deleted successfully"},
                status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"Error deleting user: {str(e)}"},
            status_code=400
        )

@router.get("/get_user/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        db_user = await query_crud.get_user(db=db, user_id=user_id)
        if db_user is None:
            return JSONResponse(
                content={"message": "User not found"},
                status_code=404
            )
        return JSONResponse(
            content={"message": "User found", "data": db_user},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"Error getting user: {str(e)}"},
            status_code=400
        )

@router.get("/get_all_users")
async def get_all_users(db: AsyncSession = Depends(get_db_session)):
    try:
        users = await query_crud.get_users(db=db)
        return JSONResponse(
            content={"message": "Users retrieved successfully", "data": users},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"Error getting users: {str(e)}"},
            status_code=400
        )
