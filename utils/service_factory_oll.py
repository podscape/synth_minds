from utils.ollama_service import OllamaService

# for when we need more instances of the same service (not in the beginning)
class ServiceFactory:
    _ollama_service = None

    @classmethod
    def get_ollama_service(cls):
        if cls._ollama_service is None:
            cls._ollama_service = OllamaService()
        return cls._ollama_service

# Use:
# from utils.service_factory_oll import ServiceFactory
# ollama = ServiceFactory.get_ollama_service()