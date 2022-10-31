from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest, Status
from src.bot.services import send_approval_callback, send_rejection_callback
from src.core.db.models import Request, User
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Данная заявка уже была рассмотрена ранее"


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.request_repository = request_repository

    async def get_request(
        self,
        request_id: UUID,
    ) -> Request:
        """Получить объект заявку по id."""
        return await self.request_repository.get(request_id)

    async def status_update(
        self, request_id: UUID, new_status_data: RequestStatusUpdateRequest, user_request: Request = None
    ) -> Request:
        """Обновить статус заявки."""
        if user_request:
            request = user_request
        else:
            request = await self.get_request(request_id)
        if request.status == new_status_data.status:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=REVIEWED_REQUEST)
        request.status = new_status_data.status
        await self.send_message(request.user, request.status)
        return await self.request_repository.update(id=request.id, request=request)

    async def send_message(self, user: User, status: str) -> None:
        """Отправить сообщение о решении по заявке в telegram."""
        if status is Status.APPROVED:
            return await send_approval_callback(user)
        return await send_rejection_callback(user)

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.request_repository.get_shift_user_ids(shift_id)

    async def block_user(self, user_id: UUID, shift_id: UUID) -> None:
        """Переводит статус заявки участника в заблокированный.

        Участник не сможет получать новые задания в этой смене.

        Аргументы:
            user_id (UUID): id участника
            shift_id (UUID): id смены, в которой состоит участник
        """
        request = await self.get_request_by_user_id_and_shift_id(user_id, shift_id)
        new_request_status = RequestStatusUpdateRequest()
        new_request_status.status = Status.BLOCKED
        await self.status_update(request.id, new_request_status, request)
