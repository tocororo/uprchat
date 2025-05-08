from pathlib import Path
import fitz
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader, 
    UnstructuredPowerPointLoader
    )
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
import pptx
from uprchat.harvester.config import llms_providers
from uprchat.harvester.logger import setup_logger

logger = setup_logger(__name__)

class Parser:
    """
    Parser for extracting text summaries from various document types.
    """

    def parse_pdf(self, path: Path) -> str:
        """
        Extracts text from the first page of a PDF file.
        Args:
            path:(Path)  to the PDF file.
        Returns:
            str: Extracted text summary.
        """
        try:
            with fitz.open(path) as doc:
                first_page = doc.load_page(0)
                return first_page.get_text()
        except Exception as e:
            logger.error(f"Error parsing PDF {path}: {e}")
            return ""

    def parse_docx(self, path: Path) -> str:
        """
        Extracts text from the first 30 paragraphs of a DOCX file.
        Args:
            path:(Path)  to the DOCX file.
        Returns:
            str: Extracted text summary.
        """
        try:
            f = open(path, "rb")
            document = docx.Document(f)
            i = 0
            summary = ""
            while i < len(document.paragraphs) and i < 30:
                summary += f" {document.paragraphs[i].text}"
                i += 1
            return summary
        except Exception as e:
            logger.error(f"Error parsing DOCX {path}: {e}")
            return ""

    def parse_pptx(self, path: Path) -> str:
        """
        Extracts text from the first 30 slides of a PPTX file.
        Args:
            path:(Path)  to the PPTX file.
        Returns:
            str: Extracted text summary.
        """
        try:
            with open(path, "rb") as f:
                presentation = pptx.Presentation(f)
                i = 0
                summary = ""
                while i < len(presentation.slides) and i < 30:
                    for shape in presentation.slides[i].shapes:
                        if shape.has_text_frame:
                            summary += f" {shape.text}"
                    i += 1
                return summary
        except Exception as e:
            logger.error(f"Error parsing PPTX {path}: {e}")
            return ""

class ParserAI:
    """
    Parser for extracting text summaries from various document types.
    """
    
    def __init__(self, provider: str):
        self.agent = llms_providers[provider]["interface"]
        prompt = """
            Escribe un resumen detallado en español del siguiente texto: 
            {text}
        """
        self.prompt_template = PromptTemplate(template=prompt, input_variables=["text"])

    def parse_pdf(self, path: Path) -> str:
        """
        Extracts text from the first page of a PDF file.
        Args:
            path:(Path)  to the PDF file.
        Returns:
            str: Extracted text summary.
        """
        try:
            documents = PyMuPDFLoader(path).load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_documents = text_splitter.split_documents(documents)
            chain = load_summarize_chain(
                self.agent,
                chain_type="map_reduce",
                map_prompt=self.prompt_template,
                combine_prompt=self.prompt_template,
                verbose=True
            )
            summary = chain.run(split_documents)
            return summary
        except Exception as e:
            logger.error(f"Error parsing PDF {path}: {e}")
            return ""

    def parse_docx(self, path: Path) -> str:
        """
        Extracts text from the first 30 paragraphs of a DOCX file.
        Args:
            path:(Path)  to the DOCX file.
        Returns:
            str: Extracted text summary.
        """
        try:
            documents = UnstructuredWordDocumentLoader(path, mode="single")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_documents = text_splitter.split_documents(documents)
            chain = load_summarize_chain(
                self.agent,
                chain_type="map_reduce",
                map_prompt=self.prompt_template,
                combine_prompt=self.prompt_template,
                verbose=True
            )
            summary = chain.run(split_documents)
            return summary
        except Exception as e:
            logger.error(f"Error parsing PDF {path}: {e}")
            return ""

    def parse_pptx(self, path: Path) -> str:
        """
        Extracts text from the first 30 slides of a PPTX file.
        Args:
            path:(Path)  to the PPTX file.
        Returns:
            str: Extracted text summary.
        """
        try:
            documents = UnstructuredPowerPointLoader(path, mode="single")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_documents = text_splitter.split_documents(documents)
            chain = load_summarize_chain(
                self.agent,
                chain_type="map_reduce",
                map_prompt=self.prompt_template,
                combine_prompt=self.prompt_template,
                verbose=True
            )
            summary = chain.run(split_documents)
            return summary
        except Exception as e:
            logger.error(f"Error parsing PDF {path}: {e}")
            return ""
        
