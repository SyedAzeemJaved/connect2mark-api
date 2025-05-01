from typing import Optional, get_args

from datetime import datetime, time, timezone
from datetime import date as dtdate

from sqlalchemy import ForeignKey, Enum, UniqueConstraint

from sqlalchemy.orm import relationship, mapped_column, Mapped

from sqlite.database import Base, engine

from sqlite.schemas import (
    UserUpdateClass,
    LocationCreateOrUpdateClass,
    ScheduleReoccurringUpdateClass,
    ScheduleNonReoccurringUpdateClass,
    ScheduleInstanceUpdateClass,
)
from sqlite.enums import (
    DepartmentsEnum,
    DesignationsEnum,
    DaysEnum,
    AttendanceEnum,
)

Base.metadata.create_all(bind=engine)


class TimestampCreateOnlyBaseModel(Base):
    __abstract__ = True

    created_at_in_utc: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now(tz=timezone.utc)
    )


class TimestampBaseModel(TimestampCreateOnlyBaseModel):
    __abstract__ = True

    updated_at_in_utc: Mapped[Optional[datetime]] = mapped_column(
        onupdate=datetime.now(tz=timezone.utc),
    )


class UserModel(TimestampBaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_student: Mapped[bool] = mapped_column(default=False)

    # Define the one-to-one relationship with UserAdditionalDetailModel
    additional_details = relationship(
        "UserAdditionalDetailModel",
        uselist=False,
        primaryjoin="UserModel.id == UserAdditionalDetailModel.user_id",
        cascade="all, delete-orphan",
        # Will delete associated additional_details when a user is deleted
    )

    schedules = relationship("ScheduleModel", secondary="schedule_users")
    schedule_instances = relationship(
        "ScheduleInstanceModel", secondary="schedule_instance_users"
    )

    def update(self, user: UserUpdateClass, **kwargs):
        self.full_name = user.full_name
        self.email = user.email

    def update_password(self, new_password: str, **kwargs):
        self.password = new_password


class UserAdditionalDetailModel(Base):
    __tablename__ = "user_additional_details"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    phone: Mapped[Optional[str]] = mapped_column(unique=True, default=None)

    department: Mapped[DepartmentsEnum] = mapped_column(
        Enum(
            *get_args(DepartmentsEnum),
            name="department",
            create_constraint=True,
            validate_strings=True,
        ),
        default=DepartmentsEnum.NOT_SPECIFIED,
    )
    designation: Mapped[DesignationsEnum] = mapped_column(
        Enum(
            *get_args(DesignationsEnum),
            name="designation",
            create_constraint=True,
            validate_strings=True,
        ),
        default=DesignationsEnum.NOT_SPECIFIED,
    )

    def update(self, user: UserUpdateClass, **kwargs):
        if user.additional_details:
            self.phone = user.additional_details.phone
            self.department = user.additional_details.department
            self.designation = user.additional_details.designation


class LocationModel(TimestampBaseModel):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(unique=True)
    bluetooth_address: Mapped[str] = mapped_column(unique=True)
    coordinates: Mapped[str] = mapped_column(unique=True)

    def update(self, location: LocationCreateOrUpdateClass, **kwargs):
        self.title = location.title
        self.bluetooth_address = location.bluetooth_address
        self.coordinates = location.coordinates


# Bridge table for many-to-many relationship
# between ScheduleModel and UserModel
class ScheduleUserModel(Base):
    __tablename__ = "schedule_users"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedules.id"), primary_key=True
    )


class ScheduleModel(TimestampBaseModel):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Check back populates and cascade
    academic_users = relationship("UserModel", secondary="schedule_users")

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), unique=False
    )
    # Define the one-to-one relationship with LocationModel
    location = relationship(
        "LocationModel",
        uselist=False,
        primaryjoin="ScheduleModel.location_id == LocationModel.id",
        cascade="none",
    )

    title: Mapped[str]

    is_reoccurring: Mapped[bool] = mapped_column(default=True)

    # Date will be null for reoccurring classes
    date: Mapped[Optional[dtdate]] = mapped_column(default=False)
    day: Mapped[DaysEnum] = mapped_column(
        Enum(
            *get_args(DaysEnum),
            name="day",
            create_constraint=True,
            validate_strings=True,
        ),
    )

    start_time_in_utc: Mapped[time]
    end_time_in_utc: Mapped[time]

    def update_reoccurring(
        self, schedule: ScheduleReoccurringUpdateClass, **kwargs
    ):
        self.title = schedule.title
        self.day = schedule.day
        self.start_time_in_utc = schedule.start_time_in_utc
        self.end_time_in_utc = schedule.end_time_in_utc

    def update_non_reoccurring(
        self, schedule: ScheduleNonReoccurringUpdateClass, **kwargs
    ):
        self.title = schedule.title
        self.date = schedule.date
        self.day = kwargs["day"]
        self.start_time_in_utc = schedule.start_time_in_utc
        self.end_time_in_utc = schedule.end_time_in_utc


# Bridge table for many-to-many relationship
# between ScheduleInstanceModel and UserModel
class ScheduleInstanceUserModel(Base):
    __tablename__ = "schedule_instance_users"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    schedule_instance_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_instances.id"),
        primary_key=True,
    )


# ScheduleInstance (Class)
class ScheduleInstanceModel(TimestampBaseModel):
    __tablename__ = "schedule_instances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Check back populates and cascade
    academic_users = relationship(
        "UserModel", secondary="schedule_instance_users"
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), unique=False
    )
    # Define the one-to-one relationship with LocationModel
    location = relationship(
        "LocationModel",
        uselist=False,
        primaryjoin="ScheduleInstanceModel.location_id == LocationModel.id",
        cascade="none",
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedules.id", ondelete="CASCADE"),
        unique=False,
    )
    # Define the one-to-one relationship with ScheduleModel
    schedule = relationship(
        "ScheduleModel",
        uselist=False,
        primaryjoin="ScheduleInstanceModel.schedule_id == ScheduleModel.id",
        cascade="none",
    )

    date: Mapped[dtdate]

    start_time_in_utc: Mapped[time]
    end_time_in_utc: Mapped[time]

    def update(self, schedule_instance: ScheduleInstanceUpdateClass, **kwargs):
        self.academic_user_id = schedule_instance.academic_user_id
        self.location_id = schedule_instance.location_id


class AttendanceModel(TimestampCreateOnlyBaseModel):
    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint(
            "schedule_instance_id",
            "user_id",
            name="uix_attendance_schedule_instance_user",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=False,
    )
    # Define the one-to-one relationship with UserModel
    user = relationship(
        "UserModel",
        uselist=False,
        primaryjoin="AttendanceModel.user_id == UserModel.id",
    )

    schedule_instance_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_instances.id", ondelete="CASCADE"),
        unique=True,
    )
    # Define the one-to-one relationship with ScheduleInstanceModel
    schedule_instance = relationship(
        "ScheduleInstanceModel",
        uselist=False,
        primaryjoin="AttendanceModel.schedule_instance_id == ScheduleInstanceModel.id",  # noqa: E501
        cascade="none",
    )

    attendance_status: Mapped[AttendanceEnum] = mapped_column(
        Enum(
            *get_args(AttendanceEnum),
            name="attendance_status",
            create_constraint=True,
            validate_strings=True,
        ),
    )
