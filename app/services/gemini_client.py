"""
Gemini API client for REST API integration.

This client directly calls the Gemini REST API without using SDK wrappers,
following the latest API specification.
"""

from typing import List, Dict, Any, Optional
import httpx
import json

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiClientError(RuntimeError):
    """Raised when the Gemini API cannot fulfill a request."""


class Message:
    """Represents a message in conversation history."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        # Convert 'assistant' role to 'model' for Gemini API
        gemini_role = "model" if self.role == "assistant" else "user"
        return {
            "role": gemini_role,
            "parts": [{"text": self.content}],
        }


class GeminiClient:
    """
    Client for Gemini REST API.
    Handles direct HTTP calls to the Gemini API endpoints.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "",
        base_url: str = "",
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to settings)
            model: Model name (defaults to settings)
            base_url: API base URL (defaults to settings)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.base_url = base_url or settings.GEMINI_BASE_URL
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self.max_retries = settings.GEMINI_MAX_RETRIES

        if not self.api_key:
            logger.warning("Gemini API key not configured")

    def _build_request_body(
        self,
        messages: List[Message],
        temperature: float = None,
        max_output_tokens: int = None,
        system_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the request body for Gemini API.

        Args:
            messages: List of Message objects
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens
            system_instruction: System instruction text

        Returns:
            Request body dictionary
        """
        temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        max_output_tokens = max_output_tokens or settings.GEMINI_MAX_OUTPUT_TOKENS

        # Build contents array from messages
        contents = [msg.to_dict() for msg in messages]

        request_body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "topP": settings.GEMINI_TOP_P,
                "topK": settings.GEMINI_TOP_K,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": "text/plain",
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ],
        }

        if system_instruction:
            request_body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        return request_body

    async def generate_response(
        self,
        messages: List[Message],
        temperature: float = None,
        max_output_tokens: int = None,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Generate a response from the Gemini API.

        Args:
            messages: List of Message objects
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens
            system_instruction: System instruction text

        Returns:
            Generated response text

        Raises:
            GeminiClientError: If API call fails
        """
        if not self.api_key:
            raise GeminiClientError("Gemini API key is not configured")

        url = f"{self.base_url}/models/{self.model}:generateContent"

        request_body = self._build_request_body(
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction,
        )

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        logger.debug(f"Calling Gemini API: {url}")
        logger.debug(f"Request body: {json.dumps(request_body)}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=request_body,
                    headers=headers,
                )

            response.raise_for_status()
            response_data = response.json()

            logger.debug(f"Gemini API response: {json.dumps(response_data)}")

            # Extract text from response
            if "candidates" not in response_data or not response_data["candidates"]:
                raise GeminiClientError("No candidates in Gemini response")

            candidate = response_data["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                raise GeminiClientError("Invalid response structure from Gemini")

            if not candidate["content"]["parts"]:
                raise GeminiClientError("No response parts from Gemini")

            generated_text = candidate["content"]["parts"][0].get("text", "")

            if not generated_text:
                raise GeminiClientError("Empty response from Gemini")

            logger.info(f"Successfully generated response from Gemini")
            return generated_text

        except httpx.HTTPStatusError as e:
            error_msg = f"Gemini API HTTP error: {e.response.status_code}"
            logger.error(error_msg)
            error_detail_message = ""
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {error_detail}")
                if isinstance(error_detail, dict):
                    nested_error = error_detail.get("error", {})
                    if isinstance(nested_error, dict):
                        error_detail_message = nested_error.get("message", "")
                    elif nested_error:
                        error_detail_message = str(nested_error)
                    elif error_detail.get("message"):
                        error_detail_message = str(error_detail.get("message"))
                    else:
                        error_detail_message = json.dumps(error_detail)
                else:
                    error_detail_message = str(error_detail)
            except Exception:
                logger.error(f"Error response: {e.response.text}")
                error_detail_message = e.response.text.strip()

            if error_detail_message:
                error_msg = f"{error_msg} - {error_detail_message}"

            raise GeminiClientError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Gemini API request error: {str(e)}"
            logger.error(error_msg)
            raise GeminiClientError(error_msg) from e
        except GeminiClientError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error calling Gemini API: {str(e)}"
            logger.error(error_msg)
            raise GeminiClientError(error_msg) from e

    async def count_tokens(self, messages: List[Message]) -> int:
        """
        Count tokens for the given messages.

        Args:
            messages: List of Message objects

        Returns:
            Token count

        Raises:
            RuntimeError: If API call fails
        """
        url = f"{self.base_url}/models/{self.model}:countTokens"

        request_body = {
            "contents": [msg.to_dict() for msg in messages]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=request_body,
                    headers=headers,
                )

            response.raise_for_status()
            response_data = response.json()
            return response_data.get("totalTokens", 0)

        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            # Return estimate if counting fails
            return len(str(messages)) // 4  # Rough estimate

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Model information
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
        }
