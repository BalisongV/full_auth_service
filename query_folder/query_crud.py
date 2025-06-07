from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from query_models import User
from query_schemas import UserRead


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        return UserRead.from_orm(user).model_dump()
    else:
        return None

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    users =result.scalars().all()
    users_list = [UserRead.from_orm(user).model_dump() for user in users]
    return users_list

async def create_user(db: AsyncSession, user:User):
    db_user = user
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError as error:
        if "(username)" in str(error):
            raise HTTPException(
                detail="Username already exists",
                status_code = 409
            )
        elif "(email)" in str(error):
            raise HTTPException(
                detail="Email already exists",
                status_code = 409
            )
        else:
            raise HTTPException(
                status_code = 409,
                detail="Database integrity error"
            )
    await db.refresh(db_user)
    return True

async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    print(db_user)
    if db_user:
        await db.execute(delete(User).where(User.user_id == user_id))
        await db.commit()
        return f"Пользователь с id {user_id} успешно удален"
    return "Пользователь не найден"
