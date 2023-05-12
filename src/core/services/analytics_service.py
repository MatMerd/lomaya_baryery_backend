from datetime import datetime
from io import BytesIO
from urllib.parse import quote_plus
from uuid import UUID

from fastapi import Depends
from openpyxl import Workbook

from src.core.db.repository.shift_repository import ShiftRepository
from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.shift_builder import ShiftAnalyticReportSettings
from src.excel_generator.task_builder import TaskAnalyticReportSettings


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(
        self,
        task_repository: TaskRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        task_report_builder: AnalyticReportBuilder = Depends(),
    ) -> None:
        self.__task_report_builder = task_report_builder
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository

    async def __generate_task_report(self, workbook: Workbook) -> Workbook:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        await self.__task_report_builder.generate_report(
            tasks_statistic,
            workbook=workbook,
            analytic_task_report_full=TaskAnalyticReportSettings,
        )

    async def __generate_shift_report_by_id(self, workbook: Workbook, shift_id: UUID) -> Workbook:
        """Генерация отчёта по выбранной смене."""
        current_shift_statistic = await self.__shift_repository.get_shift_statistics_report_by_id(shift_id)
        await self.__task_report_builder.generate_report(
            current_shift_statistic,
            workbook=workbook,
            analytic_task_report_full=ShiftAnalyticReportSettings,
        )

    async def generate_full_report(self) -> BytesIO:
        """Генерация полного отчёта."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_task_report(workbook)
        await self.__generate_task_report(workbook)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_task_report(self) -> BytesIO:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_task_report(workbook)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_shift_report_by_id(self, shift_id: UUID) -> BytesIO:
        """Генерация отчёта по выбранной смене."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_shift_report_by_id(workbook, shift_id)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_shift_report_filename(self, shift_id: UUID):
        """Генерация названия файла отчета по смене."""
        shift = await self.__shift_repository.get(shift_id)
        shift_name = '_'.join(shift.title.split()).replace('.', '')
        filename = f"Отчёт_по_смене_№{shift.sequence_number}_{shift_name}_{datetime.now()}.xlsx"
        return quote_plus(filename)
