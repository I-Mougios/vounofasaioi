from fastapi import FastAPI

from .routers import routers

app = FastAPI()

for router in routers:
    app.include_router(router)


@app.get("/")
def root():
    return {"message": "Welcome to Vounofasaious"}
