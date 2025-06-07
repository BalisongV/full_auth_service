from fastapi import APIRouter, status, Response
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from models.user import UserCreate

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(register_data: UserCreate, response: Response):
    return JSONResponse(
            status_code=response.status_code,
            detail=response.body
        )

@router.post("/signin")
async def signin(login_data: LoginRequest, response: Response):
    return JSONResponse(
            status_code=response.status_code,
            detail=response.body
        )
