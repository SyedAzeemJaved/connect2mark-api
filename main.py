from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_pagination import add_pagination

from routers import jwt_tokens
from routers.admin import (
    users as admin_users,
    locations as admin_locations,
    schedules as admin_schedules,
    schedule_instances as admin_schedule_instances,
)
from routers.staff import (
    schedule_instances as staff_schedule_instances,
    attendance as staff_attendance,
)

tags_metadata = [
    # Auth
    {
        "name": "auth",
        "description": "Create JWT based access tokens that use SHA256 enterprise level security.",
    },
    # Admin level routes
    {
        "name": "admin - users",
        "description": "Create, update and view all users saved on the database.",
    },
    {
        "name": "admin - locations",
        "description": "Create, update and view all locations saved on the database.",
    },
    {
        "name": "admin - schedules",
        "description": "Create, update and view all schedules saved on the database.",
    },
    {
        "name": "admin - schedule instances or classes",
        "description": "Update and view all schedule instances saved on the database.",
    },
    # Staff member level routes
    {
        "name": "staff - schedule instances or classes",
        "description": "View all schedule instances for current user saved on the database.",
    },
    {
        "name": "staff - attendance",
        "description": "Add attendance for a schedule instance or class in the database.",
    },
    # Common user level routes
    {
        "name": "common - me",
        "description": "Manage current user.",
    },
]
origins = [
    "*",
]

app = FastAPI(
    title="Connect2Mark Backend API and Server Module",
    description="Python based API to act as a backend for both Connect2Mark FE clients. Note that all date(s) and time(s) to be provided and returned must be/and are in UTC.",
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
# Admin level routes
app.include_router(admin_users.router)
app.include_router(admin_locations.router)
app.include_router(admin_schedules.router)
app.include_router(admin_schedule_instances.router)
# Staff member level routes
app.include_router(staff_schedule_instances.router)
app.include_router(staff_attendance.router)
# Common user level routes

add_pagination(app)  # add pagination to your app
