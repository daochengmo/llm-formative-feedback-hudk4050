import os
import time
from typing import Any, Dict

from dotenv import load_dotenv

from .utils import extract_first_json_object, safe_json_loads, normalize_feedback_obj

load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()


def _sleep_backoff(attempt: int) -> None:
    time.sleep(min(2 ** attempt, 8))


class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        if not API_KEY:
            raise RuntimeError("Missing GOOGLE_API_KEY in environment (.env).")
        self.model = model

        # SDK only
        from google import genai  # pip install google-genai

        self._client = genai.Client(api_key=API_KEY)

    def generate_json_text(self, prompt: str, temperature: float = 0.2) -> str:
        resp = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"temperature": temperature},
        )
        return getattr(resp, "text", "") or ""

    def generate_feedback_obj(self, prompt: str, max_attempts: int = 4) -> Dict[str, Any]:
        for attempt in range(max_attempts):
            text = self.generate_json_text(prompt)
            raw_json = extract_first_json_object(text) or text
            obj = safe_json_loads(raw_json)
            if isinstance(obj, dict):
                return normalize_feedback_obj(obj)
            _sleep_backoff(attempt)

        return normalize_feedback_obj({"overall_summary": "", "positives": [], "feedback_items": []})
