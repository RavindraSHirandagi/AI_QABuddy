
# Configuration for LLM Providers
import os

class LLMConfig:
    PROVIDERS = {
        "ollama": {
            "name": "Ollama",
            "base_url": "http://localhost:11434",
            "api_path": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
            "default_model": "llama3", 
            "supports_system_message": True
        }
    }
    
    # Active Provider
    ACTIVE_PROVIDER = "ollama"

    @classmethod
    def get_config(cls, provider_name=None):
        return cls.PROVIDERS["ollama"]

    @classmethod
    def get_base_url(cls, provider_name=None):
        return cls.get_config()["base_url"]
