from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import departments, employees


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Company Structure API",
    description="REST API для древовидной структуры компании",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(departments.router)
app.include_router(employees.router)


@app.get("/health")
def health():
    return {"status": "ok"}
