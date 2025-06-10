from typing import Dict
from pathlib import Path
import requests

from uprchat.harvester.logger import setup_logger

logger = setup_logger(__name__)

class Downloader:
    """
    Asynchronous downloader for fetching content from URLs.
    """

    def fetch(self, url: str) -> Dict | None:
        """
        Fetches the content from the specified URL.
        Args:
            url (str): The URL to fetch content from.
        Returns:
            bytes: The content retrieved from the URL.
        """
        try:
            response = requests.get(url)
            content = response.content
            data = {
                "content": content, 
                "content-type": response.headers.get("Content-Type", "")
            }
            return data 
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {}

    def save_file(self, content: bytes, path: Path) -> None:
        """
        Saves the given content to the specified file path.
        Args:
            content (bytes): The content to save.
            path (Path): The file path to save the content to.
        """
        try:
            with open(path, "wb") as f:
                f.write(content)
                logger.info(f"Saved file to {path}")
        except Exception as e:
            logger.error(f"Error saving file {path}: {e}")
