import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.v1.routers.posts import router as posts_router
from src.api.v1.routers.auth  import router as auth_router
from src.api.v1.routers.users import router as users_router
from src.api.v1.routers.tags  import router as tags_router
from src.api.v1.routers.telegram import router as telegram_router

app = FastAPI(
    title="Ads Manager API",
    version="1.0.0",
    description="Система планирования рекламных кампаний",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

PREFIX = "/api/v1"
app.include_router(auth_router,  prefix=PREFIX)
app.include_router(users_router, prefix=PREFIX)
app.include_router(posts_router, prefix=PREFIX)
app.include_router(tags_router,  prefix=PREFIX)
app.include_router(telegram_router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
