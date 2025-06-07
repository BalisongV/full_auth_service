from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

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
    

class UserRead(BaseModel):
    user_id: int
    username: str
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = "user"

    class Config:
        from_attributes = True

