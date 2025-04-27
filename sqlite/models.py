from datetime import datetime

from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    Time,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

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


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_student = Column(Boolean, nullable=False)

    # Define the one-to-one relationship with UserAdditionalDetailModel
    additional_details = relationship(
        "UserAdditionalDetailModel",
        uselist=False,
        primaryjoin="UserModel.id == UserAdditionalDetailModel.user_id",
        cascade="all, delete-orphan",
        # This will delete associated additional_details when a user is deleted
    )

    schedules = relationship("ScheduleModel", secondary="schedule_users")
    schedule_instances = relationship(
        "ScheduleInstanceModel", secondary="schedule_instance_users"
    )

    created_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, default=datetime.utcnow
    )
    updated_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, onupdate=datetime.utcnow
    )

    def update(self, user: UserUpdateClass, **kwargs):
        self.full_name = user.full_name
        self.email = user.email

    def update_password(self, new_password: str, **kwargs):
        self.password = new_password


class UserAdditionalDetailModel(Base):
    __tablename__ = "user_additional_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    phone = Column(String, unique=True, nullable=True, default=None)
    department = Column(
        Enum(DepartmentsEnum),
        nullable=True,
        default=DepartmentsEnum.NOT_SPECIFIED,
    )
    designation = Column(
        Enum(DesignationsEnum),
        nullable=True,
        default=DesignationsEnum.NOT_SPECIFIED,
    )

    def update(self, user: UserUpdateClass, **kwargs):
        self.phone = user.additional_details.phone
        self.department = user.additional_details.department
        self.designation = user.additional_details.designation


class LocationModel(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    bluetooth_address = Column(String, unique=True, nullable=False)
    coordinates = Column(String, unique=True, nullable=False)

    created_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, default=datetime.utcnow
    )
    updated_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, onupdate=datetime.utcnow
    )

    def update(self, location: LocationCreateOrUpdateClass, **kwargs):
        self.title = location.title
        self.bluetooth_address = location.bluetooth_address
        self.coordinates = location.coordinates


# Bridge table for many-to-many relationship
# between ScheduleModel and UserModel
class ScheduleUserModel(Base):
    __tablename__ = "schedule_users"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    schedule_id = Column(
        Integer, ForeignKey("schedules.id"), primary_key=True, nullable=False
    )


class ScheduleModel(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)

    # academic_user_id = Column(
    #     Integer,
    #     ForeignKey("users.id"),
    #     unique=False,
    #     nullable=False,
    # )
    # # Define the one-to-one relationship with UserModel
    # academic_user = relationship(
    #     "UserModel",
    #     uselist=False,
    #     primaryjoin="ScheduleModel.academic_user_id == UserModel.id",
    # )
    ##
    # check back populates and cascade
    academic_users = relationship("UserModel", secondary="schedule_users")

    location_id = Column(
        Integer, ForeignKey("locations.id"), unique=False, nullable=False
    )
    # Define the one-to-one relationship with LocationModel
    location = relationship(
        "LocationModel",
        uselist=False,
        primaryjoin="ScheduleModel.location_id == LocationModel.id",
        cascade="none",
    )

    title = Column(String, nullable=False)
    is_reoccurring = Column(Boolean, default=True)
    # Date will be null for reoccurring classes
    date = Column(Date, nullable=True)
    day = Column(Enum(DaysEnum), nullable=False)
    start_time_in_utc = Column(Time, nullable=False)
    end_time_in_utc = Column(Time, nullable=False)

    created_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, default=datetime.utcnow
    )
    updated_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, onupdate=datetime.utcnow
    )

    def update_reoccurring(self, schedule: ScheduleReoccurringUpdateClass, **kwargs):
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

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    schedule_instance_id = Column(
        Integer,
        ForeignKey("schedule_instances.id"),
        primary_key=True,
        nullable=False,
    )


# ScheduleInstance (Class)
class ScheduleInstanceModel(Base):
    __tablename__ = "schedule_instances"

    id = Column(Integer, primary_key=True, index=True)

    # academic_user_id = Column(
    #     Integer, ForeignKey("users.id"), unique=False, nullable=False
    # )
    # # Define the one-to-one relationship with UserModel
    # academic_user = relationship(
    #     "UserModel",
    #     uselist=False,
    #     primaryjoin="ScheduleInstanceModel.academic_user_id == UserModel.id",
    #     cascade="none",
    # )
    ##
    # check back populates and cascade
    academic_users = relationship("UserModel", secondary="schedule_instance_users")

    location_id = Column(
        Integer, ForeignKey("locations.id"), unique=False, nullable=False
    )
    # Define the one-to-one relationship with LocationModel
    location = relationship(
        "LocationModel",
        uselist=False,
        primaryjoin="ScheduleInstanceModel.location_id == LocationModel.id",
        cascade="none",
    )

    schedule_id = Column(
        Integer,
        ForeignKey("schedules.id", ondelete="CASCADE"),
        unique=False,
        nullable=False,
    )
    # Define the one-to-one relationship with ScheduleModel
    schedule = relationship(
        "ScheduleModel",
        uselist=False,
        primaryjoin="ScheduleInstanceModel.schedule_id == ScheduleModel.id",
        cascade="none",
    )

    date = Column(Date, nullable=False)
    start_time_in_utc = Column(Time, nullable=False)
    end_time_in_utc = Column(Time, nullable=False)

    created_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, default=datetime.utcnow
    )
    updated_at_in_utc = Column(
        DateTime(timezone=False), nullable=True, onupdate=datetime.utcnow
    )

    # def update(self, schedule_instance: ScheduleInstanceUpdateClass, **kwargs):
    #     self.academic_user_id = schedule_instance.academic_user_id
    #     self.location_id = schedule_instance.location_id


class AttendanceModel(Base):
    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint(
            "schedule_instance_id",
            "user_id",
            name="uix_attendance_schedule_instance_user",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=False,
        nullable=False,
    )
    # Define the one-to-one relationship with UserModel
    user = relationship(
        "UserModel",
        uselist=False,
        primaryjoin="AttendanceModel.user_id == UserModel.id",
    )

    schedule_instance_id = Column(
        Integer,
        ForeignKey("schedule_instances.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    # Define the one-to-one relationship with ScheduleInstanceModel
    schedule_instance = relationship(
        "ScheduleInstanceModel",
        uselist=False,
        primaryjoin="AttendanceModel.schedule_instance_id == ScheduleInstanceModel.id",
        cascade="none",
    )

    attendance_status = Column(Enum(AttendanceEnum), nullable=False)

    created_at_in_utc = Column(
        DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
