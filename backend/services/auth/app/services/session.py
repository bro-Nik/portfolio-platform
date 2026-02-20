from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from app.core.utils import get_real_ip
from app.repositories import SessionRepository, TokenRepository
from app.schemas import LoginSessionCreate, LoginSessionUpdate


class SessionService:
    """Сервис для управления сессиями входа пользователей."""

    def __init__(
        self,
        session: AsyncSession,
        session_repo: SessionRepository | None = None,
        token_repo: TokenRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = session_repo or SessionRepository(session)
        self.token_repo = token_repo or TokenRepository(session)

    async def create_session(
        self,
        user_id: int,
        refresh_token_id: int,
        request: Request,
    ) -> None:
        """Создает запись о новой сессии входа."""
        ip_address = get_real_ip(request)
        user_agent = request.headers.get('user-agent')

        session_info = self._parse_user_agent(user_agent)

        login_session = LoginSessionCreate(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            ip_address=ip_address,
            user_agent=user_agent,
            **session_info,
        )
        await self.repo.create(login_session)

    async def update_session(
        self,
        refresh_token_id: int,
        request: Request,
    ) -> None:
        """Обновить запись о сессии входа."""
        db_login_session = await self.repo.get_by_token_id(refresh_token_id)
        if not db_login_session:
            return

        ip_address = get_real_ip(request)
        user_agent = request.headers.get('user-agent')

        session_info = self._parse_user_agent(user_agent)

        login_session = LoginSessionUpdate(
            ip_address=ip_address,
            last_activity_at=datetime.now(UTC),
            user_agent=user_agent,
            **session_info,
        )
        await self.repo.update(db_login_session.id, login_session)

    @staticmethod
    def _parse_user_agent(user_agent_string: str) -> dict:
        """Парсит User-Agent строку."""
        if not user_agent_string:
            return {}

        ua = parse(user_agent_string)

        device_type = 'unknown'
        if ua.is_mobile:
            device_type = 'mobile'
        elif ua.is_tablet:
            device_type = 'tablet'
        elif ua.is_pc:
            device_type = 'desktop'

        return {
            'browser': ua.browser.family,
            'os': ua.os.family,
            'device_type': device_type,
        }
