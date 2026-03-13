"""
Vision Handler - Multimodal RAG support using Gemini 1.5.
Uses direct REST API to bypass SDK-specific 'models/' prefixing issues.
"""

import base64
import json
import requests
from typing import Any, Dict, List, Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VisionHandler:
    """Uses Gemini 1.5 Vision capabilities via direct REST API (AI Studio Compatible)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash") -> None:
        """Initialize vision handler."""
        self.api_key = api_key or settings.GOOGLE_API_KEY
        
        # Clean model name
        model_str = str(model).strip()
        if model_str.lower().startswith("models/"):
            model_str = model_str.replace("models/", "", 1)
            
        self.model_name = model_str
        
        if self.api_key:
            logger.info(f"✅ VisionHandler initialized (REST API) with model: {self.model_name}")
        else:
            logger.warning("VisionHandler initialized without API key. OCR features will be disabled.")

    def _make_vision_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to make vision REST calls with v1 -> v1beta fallback."""
        url_v1 = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        
        logger.info(f"🌐 Calling Gemini Vision REST API (v1): gemini-1.5-flash")
        
        try:
            response = requests.post(
                url_v1,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json=payload,
                timeout=60
            )
            
            logger.info(f"📊 Vision v1 Response status: {response.status_code}")
            
            if response.status_code == 404:
                logger.warning("⚠️ Vision v1 endpoint failed with 404, trying v1beta...")
                url_beta = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                
                response = requests.post(
                    url_beta,
                    headers={"Content-Type": "application/json"},
                    params={"key": self.api_key},
                    json=payload,
                    timeout=60
                )
                logger.info(f"📊 Vision v1beta Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Gemini Vision API returned {response.status_code}: {response.text}")
                return {"success": False, "error": response.text}
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Vision REST call exception: {e}")
            return {"success": False, "error": str(e)}

    async def extract_text_from_image(self, base64_image: str, prompt: str = "Extract all text from this image accurately.") -> str:
        """Sends an image to Gemini using direct REST API to extract text."""
        if not self.api_key:
            return "OCR Error: Gemini API key not configured."

        try:
            # Prepare image for Gemini
            if "," in base64_image:
                base64_image = base64_image.split(",")[1]
            
            # Direct REST payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "maxOutputTokens": 2048,
                }
            }
            
            call_result = self._make_vision_call(payload)
            if not call_result["success"]:
                return f"OCR Error: {call_result['error']}"
            
            result = call_result["data"]
            candidates = result.get("candidates", [])
            if not candidates or not candidates[0].get("content"):
                return "OCR Error: No content returned from Gemini Vision API."
                
            parts = candidates[0]["content"].get("parts", [])
            return "".join([p.get("text", "") for p in parts])

        except Exception as e:
            logger.error("Vision OCR failed: %s", e)
            return f"OCR Error: {str(e)}"

    async def analyze_document_image(self, base64_image: str) -> Dict[str, Any]:
        """Analyzes a document image (like a tax return or legal ID)."""
        prompt = """
        Analyze this document image and return a JSON structured summary:
        1. Document Type
        2. Key Entities (Names, ID numbers)
        3. Financial Figures (if any)
        4. Important Dates
        5. Detailed Text Extraction
        """
        raw_text = await self.extract_text_from_image(base64_image, prompt=prompt)
        return {"analysis": raw_text}
