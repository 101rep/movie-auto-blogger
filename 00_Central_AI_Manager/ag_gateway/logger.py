import logging
from pathlib import Path

def get_logger(name: str = "ag_gateway") -> logging.Logger:
    """Configure and return a logger for the AG Gateway.

    Logs are written to a file `logs/ag_gateway.log` under the project root.
    The log level is taken from the Settings (see config.py).
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel("INFO")
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "ag_gateway.log"

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
