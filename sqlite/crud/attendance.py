from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from sqlite import models
from sqlite.enums import AttendanceEnum


async def get_attendance_by_schedule_instance_id(
    schedule_instance_id: int, db: AsyncSession
):
    return await db.scalar(
        select(models.AttendanceModel).where(
            models.AttendanceModel.schedule_instance_id == schedule_instance_id
        )
    )


async def get_attendance_by_id(attendance_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.AttendanceModel).where(
            models.AttendanceModel.id == attendance_id
        )
    )


def get_all_attendance_by_schedule_instance_ids_query(
    schedule_ids: list[int],
):
    return select(models.AttendanceModel).where(
        models.AttendanceModel.schedule_instance_id.in_(schedule_ids)
    )


async def create_attendance(
    schedule_instance_id: int,
    attendance_status: AttendanceEnum,
    db: AsyncSession,
):
    db_attendance = models.AttendanceModel(
        schedule_instance_id=schedule_instance_id,
        attendance_status=attendance_status,
    )

    db.add(db_attendance)

    await db.commit()

    return db_attendance
