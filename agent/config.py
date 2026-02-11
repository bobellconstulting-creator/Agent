import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str
    risk_require_confirmation: set[str]


settings = Settings(
    app_name=os.getenv("APP_NAME", "buckgrid-agent"),
    database_url=os.getenv("DATABASE_URL", "sqlite:///./agent.db"),
    risk_require_confirmation={
        item.strip()
        for item in os.getenv("RISK_REQUIRE_CONFIRMATION", "money,destructive,external_commitment").split(",")
        if item.strip()
    },
)
