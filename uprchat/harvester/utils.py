from datetime import datetime
import re
from typing import Dict
from urllib.parse import urlparse

def get_filename_from_url(url: str) -> str:
    """
    Generates a unique filename based on the URL and current timestamp.
    Args:
        url (str): The URL to generate the filename from.
    Returns:
        str: Generated filename.
    """
    name = re.sub(r"^(?:https?://)", "", url, flags=re.IGNORECASE)
    name = re.sub(r"[^A-Za-z0-9_-]", "", name)
    if not name:
        name = "file"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{name}_{timestamp}"

def extract_source_information(url: str) -> Dict:
    """
    Extracts the site name and root URL from a given URL.
    Parameters:
        url (str): The input URL from which the site name should be extracted.
    Returns:
        Dict: A simplified name representing the main part of the site and root URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    url = domain
    if domain.startswith('www.'):
        domain = domain[4:]

    parts = domain.split('.')
    if len(parts) <= 2:
        name = parts[0]
    else:
        name = '.'.join(parts[:2])
    return {
        "name":name,
        "url":url
    }

def clean_text_for_neo4j(text: str) -> str:
    """
    Cleans an arbitrary text string for safe insertion into Neo4j.
    
    This function will:
      1. Replace all control characters (U+0000–U+001F, U+007F) with spaces.
      2. Collapse runs of whitespace into a single space.
      3. Escape single (') and double (") quotes with a backslash.
      4. Strip leading and trailing whitespace.
    Parameters:
        text (str): The raw input string.
    Returns:
        str: A sanitized string safe for use in Cypher queries.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    forbidden = re.compile(r"[\x00-\x1F\x7F'\"`\\{}()\[\];,:|]")
    text = forbidden.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
