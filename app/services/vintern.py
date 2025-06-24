from app.utils.prom import GET_FULL_TEXT_PROMPT, GET_DETAIL_PROMPT
import httpx
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class VinternAIService:
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key

    async def call_model(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        """
        Call the external AI model API with an image and a prompt.
        Args:
            image_bytes (bytes): The image data to send
            prompt (str): The prompt to use (e.g., GET_FULL_TEXT_PROMPT)
        Returns:
            Dict[str, Any]: The API response
        """
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        try:
            async with httpx.AsyncClient() as client:
                files = {
                    'image': ('image.png', image_bytes, 'image/png'),
                    'prompt': (None, prompt)
                }
                response = await client.post(self.api_url, files=files, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error calling AI model API: {str(e)}")
            raise

    async def load_model(self) -> bool:
        """
        Load or initialize the AI model for inference.
        For remote API models, this can be a health check or a no-op.
        For local/on-premise models, implement actual loading logic here.
        Returns:
            bool: True if the model is ready, False otherwise
        """
        # Example for remote API: perform a health check
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url + '/health')
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error loading or checking AI model: {str(e)}")
            return False

# Example usage (fill in your API URL and key):
# vintern_ai_service = VinternAIService(api_url='https://your-ai-api-endpoint', api_key='your-api-key')
