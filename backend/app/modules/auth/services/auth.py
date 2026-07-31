from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import AuthenticationError
from app.common.schemas import AuthUser, Context

from app.modules.auth.models import RefreshToken, User
from app.modules.auth.repositories import TokenRepository
from app.modules.auth.schemas import (
    DeleteAccountRequest,
    RefreshTokenCreate, RefreshTokenUpdate, RefreshTokenRequest,
    RegisterResponse, TokensResponse, UserCreateRequest, UserLogin,
    UserRegister, UserRole,
)
from app.modules.auth.security import SecurityService
from app.modules.auth.services.user import UserService
from app.modules.auth.services.session import SessionService


@dataclass
class AuthResult:
    tokens: TokensResponse
    user_id: int
    refresh_token_id: int


@dataclass
class RegisterTaskData:
    email: str
    token: str
    message: str


@dataclass
class RegisterResult:
    tokens: TokensResponse
    user_id: int
    refresh_token_id: int
    email: str
    verification_token: str


class AuthService:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.session = session
        self.token_repo = TokenRepository(session)
        self.user_service = UserService(session, ctx)
        self.session_service = SessionService(session, ctx)
        self.security = SecurityService()

    async def register(self, data: UserRegister) -> RegisterResult:
        user_data = UserCreateRequest(**data.model_dump(), role=UserRole.USER)
        user = await self.user_service.create(user_data)
        token = self.security.create_email_verification_token(user.id)
        auth_result = await self._create_tokens(user)
        await self.session.commit()
        return RegisterResult(
            tokens=auth_result.tokens,
            user_id=auth_result.user_id,
            refresh_token_id=auth_result.refresh_token_id,
            email=user.email,
            verification_token=token,
        )

    async def verify_email(self, token: str) -> RegisterResponse:
        user_id, new_email = self.security.verify_email_token(token)
        user = await self.user_service.get_for_auth(id=user_id)
        if new_email:
            if user.email == new_email and user.is_verified:
                return RegisterResponse(message='Email уже подтверждён')
            if await self.user_service.repo.exists_by(User.email == new_email):
                return RegisterResponse(message='Этот email уже занят')
            await self.user_service.repo.update(user_id, {'email': new_email, 'is_verified': True})
        else:
            if user.is_verified:
                return RegisterResponse(message='Email уже подтверждён')
            await self.user_service.repo.update(user_id, {'is_verified': True})
        await self.session.commit()
        return RegisterResponse(message='Email успешно подтверждён')

    async def resend_verification(self, email: str) -> RegisterTaskData | RegisterResponse:
        user = await self.user_service.get_for_auth(email=email)
        if user.is_verified:
            return RegisterResponse(message='Email уже подтверждён')
        token = self.security.create_email_verification_token(user.id)
        return RegisterTaskData(
            email=user.email,
            token=token,
            message='Письмо с подтверждением отправлено повторно',
        )

    async def login(self, data: UserLogin) -> AuthResult:
        user = await self.user_service.get_for_auth(email=data.email)
        if not self.security.verify_password(data.password, user.password_hash):
            raise AuthenticationError('Неверный email или пароль')
        result = await self._create_tokens(user)
        await self.session.commit()
        return result

    async def refresh_tokens(self, data: RefreshTokenRequest) -> AuthResult:
        payload = self.security.verify_token(data.token)
        if payload.get('type') != 'refresh' or not payload.get('id'):
            raise AuthenticationError('Невалидный refresh токен')
        user_id = int(payload['id'])
        user = await self.user_service.get_for_auth(id=user_id)
        token = await self._get_db_refresh_token(data.token)
        result = await self._create_tokens(user, token)
        await self.session.commit()
        return result

    async def logout(self, refresh_token: str) -> bool:
        token = await self._get_db_refresh_token(refresh_token)
        deleted = bool(await self.token_repo.delete(token.id))
        await self.session.commit()
        return deleted

    async def logout_all(self, user_id: int | None = None) -> bool:
        user_id = user_id or self.ctx.actor.id
        deleted = bool(await self.token_repo.delete_all_by_user(user_id))
        await self.session.commit()
        return deleted

    async def reset_password(self, token: str, new_password: str) -> User:
        user_id = await self.user_service.reset_password(token, new_password)
        user = await self.user_service.get_for_auth(id=user_id)
        await self.logout_all(user_id)
        await self.session.commit()
        return user

    async def delete_account(self, user_id: int, data: DeleteAccountRequest) -> None:
        await self.user_service.delete_account(user_id, data)
        await self.logout_all(user_id)
        await self.session.commit()

    async def _get_db_refresh_token(self, refresh_token: str) -> RefreshToken:
        token_hash = self.security.hash_token(refresh_token)
        if not (token := await self.token_repo.get_by_token_hash(token_hash)):
            raise AuthenticationError('Токен не найден в базе')
        return token

    async def _create_tokens(self, user: User, db_token: RefreshToken | None = None) -> AuthResult:
        login = user.email.split('@')[0] if user.email else ''
        auth_user = AuthUser(id=user.id, role=user.role, login=login)
        token_data = self.security.create_token_pair(auth_user)
        token_hash = self.security.hash_token(token_data.refresh_token)

        if db_token:
            update = RefreshTokenUpdate(token_hash=token_hash, expires_at=token_data.refresh_expires_at)
            token = await self.token_repo.update(db_token.id, update.model_dump())
        else:
            create = RefreshTokenCreate(user_id=user.id, token_hash=token_hash, expires_at=token_data.refresh_expires_at)
            token = await self.token_repo.create(create.model_dump())
            await self.session.flush()

        return AuthResult(
            tokens=TokensResponse(access_token=token_data.access_token, refresh_token=token_data.refresh_token),
            user_id=user.id,
            refresh_token_id=token.id,
        )
