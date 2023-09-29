from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, FastAPIUsers, IntegerIDMixin,
                           InvalidPasswordException)
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

JWT_TOKEN_URL = 'auth/jwt/login'
JWT_TOKEN_LIFETIME_SECONDS = 3600

PASSWORD_LENGTH = 3
ERROR_PASSWORD_LENGTH = (
    f'Password should be at least {PASSWORD_LENGTH} characters'
)
ERROR_EMAIL = 'Password should not contain e-mail'

MESSAGE_ABOUT_A_REGISTERED_USER = 'Пользователь {email} зарегистрирован.'


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl=JWT_TOKEN_URL)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret, lifetime_seconds=JWT_TOKEN_LIFETIME_SECONDS
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ):
        if len(password) < PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=ERROR_PASSWORD_LENGTH
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason=ERROR_EMAIL
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        print(MESSAGE_ABOUT_A_REGISTERED_USER.format(email=user.email))


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
