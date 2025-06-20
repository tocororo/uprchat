import argparse
import asyncio
from uprchat.app.config import get_settings
from uprchat.harvester.graphbuilder import GraphBuilder

def parse_recollection_args() -> tuple[str, str, int]:
    """
    Parse command-line arguments for the recollection process.

    Returns:
        A tuple (url, recollection, delay)
    """
    parser = argparse.ArgumentParser(description="Start recollection process.")
    parser.add_argument("url", help="URL to process")
    parser.add_argument(
        "--recollection", "-r",
        default="0",
        help="Optional recollection ID (default: 0)"
    )
    parser.add_argument(
        "--delay", "-d",
        type=int,
        default=60,
        help="Optional delay (in seconds)(default: 60)"
    )
    args = parser.parse_args()
    return args.url, args.recollection, args.delay

URL, RECOLLECTION, DELAY = parse_recollection_args()

settings = get_settings()

neo4j_config = {
    "neo4j_uri": settings.neo4j_uri,
    "neo4j_user": settings.neo4j_user,
    "neo4j_pass": settings.neo4j_pass,
    "neo4j_db": settings.neo4j_bb
    }

graph_builder = GraphBuilder(
        model_name=settings.mainmodel,
        base_url=settings.base_url,
        api_key=settings.model_api_key,
        model_type="openai",
        delay=DELAY,
        neo4j_config=neo4j_config
    )

def simple_recollection():
    asyncio.run(graph_builder.start_recollection(URL, recollection=RECOLLECTION))

def recollection_with_entity_extraction():
    asyncio.run(graph_builder.start_recollection(URL, recollection=RECOLLECTION, entity_extraction=True))

def recollection_with_summary_creation():
    asyncio.run(graph_builder.start_recollection(URL, recollection=RECOLLECTION, summary_creation=True))

def complete_recollection():
    asyncio.run(graph_builder.start_recollection(URL, recollection=RECOLLECTION, entity_extraction=True, summary_creation=True))
