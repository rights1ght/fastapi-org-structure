import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/company_db"
    )


settings = Settings()
