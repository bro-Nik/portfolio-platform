from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from fastapi import HTTPException, status

from app.common.schemas import Context

from app.modules.auth.repositories import SessionRepository, TokenRepository
from app.modules.auth.schemas import LoginSessionCreate, LoginSessionUpdate


class SessionService:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.session = session
        self.repo = SessionRepository(session)
        self.token_repo = TokenRepository(session)

    async def create(self, refresh_token_id: int, user_id: int) -> None:
        session_info = self._parse_user_agent(self.ctx.user_agent)
        session_to_db = LoginSessionCreate(
            user_id=user_id, refresh_token_id=refresh_token_id,
            ip_address=self.ctx.client_ip, user_agent=self.ctx.user_agent,
            **session_info,
        )
        await self.repo.create(session_to_db.model_dump())

    async def update(self, refresh_token_id: int) -> None:
        db_session = await self.repo.get_by_token_id(refresh_token_id)
        if not db_session:
            return
        session_to_db = LoginSessionUpdate(ip_address=self.ctx.client_ip, last_activity_at=datetime.now(UTC))
        await self.repo.update(db_session.id, session_to_db.model_dump())

    async def get_user_sessions(self, user_id: int) -> list:
        return await self.repo.get_all_by_user_id(user_id)

    async def delete_session(self, session_id: int, user_id: int) -> None:
        db_session = await self.repo.get(session_id)
        if not db_session or db_session.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сессия не найдена')
        if db_session.refresh_token_id:
            await self.token_repo.delete(db_session.refresh_token_id)
        await self.repo.delete(session_id)

    async def delete_all_other_sessions(self, user_id: int, current_token_id: int) -> None:
        sessions = await self.repo.get_all_by_user_id(user_id)
        for s in sessions:
            if s.refresh_token_id != current_token_id:
                if s.refresh_token_id:
                    await self.token_repo.delete(s.refresh_token_id)
                await self.repo.delete(s.id)

    @staticmethod
    def _parse_user_agent(user_agent_string: str) -> dict:
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
        return {'browser': ua.browser.family, 'os': ua.os.family, 'device_type': device_type}
