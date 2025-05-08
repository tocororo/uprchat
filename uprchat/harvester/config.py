from pathlib import Path

from langchain_openai.llms import OpenAI
from pydantic import BaseModel, Field

from uprchat.app.config import get_settings

from langchain_ollama.llms import OllamaLLM

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "repositories" / "pdfs"
DOC_DIR = BASE_DIR / "repositories" / "docs"
PPT_DIR = BASE_DIR / "repositories" / "ppts"

for directory in [PDF_DIR, DOC_DIR, PPT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

settings = get_settings()

llms_providers = {
    "openai": {
        "name": settings.mainmodel,
        "api_key": settings.model_api_key,
        "base_url": settings.base_url,
        "interface": OpenAI(
            name=settings.mainmodel,
            api_key=settings.model_api_key,
            base_url=settings.base_url,
        ),
    },
    # "ollama": {"name": settings.mainmodel, "interface": OllamaLLM(name=settings.mainmodel)},
}


class PageInformation(BaseModel):
    title: str = Field(..., description="the title element for the page")
    body: str = Field(
        ..., description="The relevant information associated to the page title"
    )
