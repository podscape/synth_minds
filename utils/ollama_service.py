from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import Tuple
import logging


class OllamaService:
    def __init__(self,
                 model_name: str = "llama3.1:8b-instruct-fp16",
                 embed_model_name: str = "BAAI/bge-m3",
                 request_timeout: float = 120.0,
                 context_window: int = 131072):
        self.model_name = model_name
        self.embed_model_name = embed_model_name
        self.request_timeout = request_timeout
        self.context_window = context_window
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> Tuple[Ollama, HuggingFaceEmbedding]:
        try:
            Settings.llm = Ollama(
                model=self.model_name,
                request_timeout=self.request_timeout,
                context_window=self.context_window
            )

            Settings.embed_model = HuggingFaceEmbedding(
                model_name=self.embed_model_name
            )

            self.logger.info(f"Successfully initialized Ollama with model {self.model_name}")
            return Settings.llm, Settings.embed_model

        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama service: {str(e)}")
            raise

    def get_model_info(self) -> dict:
        return {
            "llm_model": self.model_name,
            "embedding_model": self.embed_model_name,
            "context_window": self.context_window,
            "timeout": self.request_timeout
        }

    def switch_model(self, new_model_name: str) -> None:
        self.model_name = new_model_name
        self.initialize()


if __name__ == "__main__":
    ollama_service = OllamaService(
        model_name="llama3.2:latest",
        embed_model_name="BAAI/bge-m3"
    )
    llm, embed_model = ollama_service.initialize()
    config = ollama_service.get_model_info()
    print(config)