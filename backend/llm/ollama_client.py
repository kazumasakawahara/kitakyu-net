"""
Ollama client for local LLM inference.
"""
from typing import Dict, List, Optional, Any, Iterator
import httpx
from loguru import logger

from backend.config import settings


class OllamaClient:
    """Client for Ollama LLM server."""

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        logger.info(f"Ollama client initialized: {self.base_url}, model: {self.model}")

    def check_availability(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama server unavailable: {e}")
            return False

    def check_model_available(self) -> bool:
        """Check if configured model is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                available = self.model in models
                if not available:
                    logger.warning(f"Model {self.model} not found. Available: {models}")
                return available
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature for generation (optional)
            max_tokens: Max tokens to generate (optional)
            stream: Whether to stream response (not implemented)

        Returns:
            Generated text
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "num_predict": max_tokens or settings.ollama_max_tokens,
            },
        }

        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Chat with Ollama using chat format.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            max_tokens: Max tokens to generate

        Returns:
            Generated response
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "num_predict": max_tokens or settings.ollama_max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")

        except httpx.TimeoutException:
            logger.error(f"Ollama chat timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            raise


# Global Ollama client instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
