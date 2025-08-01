import uvicorn
from fastapi import FastAPI

from .routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Welcome to Vounofasaious"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        reload_excludes=["*.txt"],
    )
