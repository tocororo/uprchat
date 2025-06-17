from threading import Lock
from typing import List, Optional
from langchain_openai import ChatOpenAI

class APIKeyIterator:
    _instance = None
    _lock = Lock()

    def __new__(cls, 
                api_keys: Optional[List[str]] = None, 
                model_name: Optional[str] = None, 
                base_url: Optional[str] = None
                ):
        with cls._lock:
            if cls._instance is None:
                if api_keys is None:
                    raise ValueError("First initialization requires a list of API keys.")
                cls._instance = super().__new__(cls)
                cls._instance._init(api_keys, model_name, base_url)
            return cls._instance

    def _init(self,
              api_keys: Optional[List[str]] = None, 
              model_name: Optional[str] = None, 
              base_url: Optional[str] = None
              ):
        if not api_keys:
            raise ValueError("API key list must not be empty.")
        self.__api_keys = api_keys
        self.index = 0
        self.api_keys_expired = 0
        self._lock = Lock()
        self.llm = ChatOpenAI(
            model_name=model_name,
            base_url=base_url,
            api_key=self.__api_keys[self.index]
        )

    def get_current_apikey(self)-> str:
        return self.__api_keys[self.index]
    
    def change_apikey(self)-> str:
        self.index += 1
        self.api_keys_expired += 1
        if self.index >= len(self.__api_keys):
            self.index = 0
        if self.api_keys_expired >= len(self.__api_keys):
            raise NoAvailableAPIKeysError("All API keys have been used.")
        self.llm = ChatOpenAI(
            model_name=self.llm.model_name,
            base_url=self.llm.base_url,
            api_key=self.__api_keys[self.index]
        )
        return self.__api_keys[self.index]
    
    def get_llm(self):
        """
        Returns the current LLM instance.
        """
        return self.llm
    
    def reset_fails_counter(self):
        self.api_keys_expired = 0

class NoAvailableAPIKeysError(Exception):
    """Raised when no API keys are available for use."""

    def __init__(self, message="No API keys are available."):
        super().__init__(message)

