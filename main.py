from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_pagination import add_pagination

from contextlib import asynccontextmanager
from sqlite.database import sessionmanager

from routers import jwt_tokens, temporary
from routers.admin import (
    users as admin_users,
    locations as admin_locations,
    schedules as admin_schedules,
    schedule_instances as admin_schedule_instances,
    attendance_tracking as admin_attendance_tracking,
    attendance_result as admin_attendance_result,
    stats as admin_stats,
)
from routers.academic import (
    schedule_instances as academic_schedule_instances,
    attendance as academic_attendance,
    attendance_tracking as academic_attendance_tracking,
    attendance_result as academic_attendance_result,
)
from routers.common import me as common_me


tags_metadata = [
    # Auth
    {
        "name": "auth",
        "description": "Create JWT based access tokens that use SHA256 "
        + "enterprise level security.",
    },
    # Admin user level routes
    {
        "name": "admin - users",
        "description": "Create, update and view all users saved on the "
        + "database.",
    },
    {
        "name": "admin - locations",
        "description": "Create, update and view all locations saved on the "
        + "database.",
    },
    {
        "name": "admin - schedules",
        "description": "Create, update and view all schedules saved on the "
        + "database.",
    },
    {
        "name": "admin - schedule instances or classes",
        "description": "Update and view all schedule instances saved on the "
        + "database.",
    },
    {
        "name": "admin - attendance-tracking",
        "description": "Get attendance tracking results from the database.",
    },
    {
        "name": "admin - attendance-result",
        "description": "View attendance result(s) for schedule "
        + "instances/classes or academic users in the database.",
    },
    {
        "name": "admin - stats",
        "description": "Get stats for the dashboard.",
    },
    # Academic user level routes
    {
        "name": "academic - schedule instances or classes",
        "description": "View all schedule instances for current user saved on "
        + "the database.",
    },
    {
        "name": "academic - attendance",
        "description": "Mark attendance of a schedule instance or class for "
        + "current user in the database.",
    },
    {
        "name": "academic - attendance-tracking",
        "description": "Track attendance of a schedule instance or class for "
        + "current user in the database.",
    },
    {
        "name": "academic - attendance-result",
        "description": "View attendance result of a schedule instance or class "
        + "for current user in the database.",
    },
    # Common user level routes
    {
        "name": "common - me",
        "description": "Manage current user.",
    },
    # Temporary routes
    {
        "name": "temporary",
        "description": "Temporary routes.",
    },
]
origins = [
    "*",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(
    lifespan=lifespan,
    title="Safe Check: Multi Layer Classroom Presence System",
    description="Python based API to act as a backend for both "
    + "SafeCheck FE clients. Note that all date(s) and time(s) "
    + "to be provided and returned must be/and are in UTC.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    redoc_url=None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jwt_tokens.router)
# Admin user level routes
app.include_router(admin_users.router)
app.include_router(admin_locations.router)
app.include_router(admin_schedules.router)
app.include_router(admin_schedule_instances.router)
app.include_router(admin_attendance_tracking.router)
app.include_router(admin_attendance_result.router)
app.include_router(admin_stats.router)
# Academic user level routes
app.include_router(academic_schedule_instances.router)
app.include_router(academic_attendance.router)
app.include_router(academic_attendance_result.router)
app.include_router(academic_attendance_tracking.router)
# Common user level routes
app.include_router(common_me.router)
# Temporary routes
app.include_router(temporary.router)

add_pagination(app)  # add pagination to your app
