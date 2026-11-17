
import logging
from pathlib import Path


def setup_logging():
    """
    Configure VibeFinder logging.

    Logs are saved to vibefinder.log in the project root.
    """

    log_file = Path(__file__).resolve().parent.parent / "vibefinder.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return logging.getLogger("vibefinder")
