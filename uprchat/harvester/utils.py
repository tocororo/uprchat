from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

def get_filename_from_url(url: str) -> str:
    """
    Generates a unique filename based on the URL and current timestamp.
    Args:
        url (str): The URL to generate the filename from.
    Returns:
        str: Generated filename.
    """
    parsed_url = urlparse(url)
    name = Path(parsed_url.path).stem
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{name}_{timestamp}"


