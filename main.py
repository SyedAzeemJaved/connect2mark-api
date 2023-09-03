from fastapi import FastAPI

from router import users

tags_metadata = [
    {
        "name": "users",
        "description": "Create, update and view all users saved on the database.",
    },
]

app = FastAPI(
    title="Connect2Mark Backend API and Server Module",
    description="Python based API to act as a backend for both Connect2Mark FE clients.",
    openapi_tags=tags_metadata,
    redoc_url=None,
)
app.include_router(users.router)
