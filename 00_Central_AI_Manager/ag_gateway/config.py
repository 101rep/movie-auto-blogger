import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application configuration loaded from environment variables or a .env file.

    The .env file should reside at the project root (same level as this module) and contain
    ``GEMINI_API_KEY``, ``GITHUB_TOKEN`` and ``MCP_TOKEN`` among other optional settings.
    """

    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    GITHUB_TOKEN: str = Field(..., env="GITHUB_TOKEN")
    MCP_TOKEN: str = Field(..., env="MCP_TOKEN")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    MEMORY_DB_PATH: str = Field("ag_memory.db", env="MEMORY_DB_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
