import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)
else:
    # No .env file; environment variables must be set elsewhere
    pass

def get_secret(key: str) -> str:
    """Retrieve a secret from the environment.

    Raises a clear error if the key is missing.
    """
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value
