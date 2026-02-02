import os
import time
import requests
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from .utils import extract_first_json_object, safe_json_loads, normalize_feedback_obj

load_dotenv()


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
BACKEND = os.getenv("LLM_BACKEND", "sdk").lower()  # "sdk" or "rest"
API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()


def _sleep_backoff(attempt: int) -> None:
    time.sleep(min(2 ** attempt, 8))


class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        if not API_KEY:
            raise RuntimeError("Missing GOOGLE_API_KEY in environment.")
        self.model = model
        self.backend = BACKEND
        self._sdk_client = None

        if self.backend == "sdk":
            # Official: pip install google-genai, from google import genai
            from google import genai  # type: ignore

            self._sdk_client = genai.Client(api_key=API_KEY)

    def generate_json_text(self, prompt: str, temperature: float = 0.2) -> str:
        if self.backend == "sdk":
            return self._generate_sdk(prompt, temperature=temperature)
        return self._generate_rest(prompt, temperature=temperature)

    def _generate_sdk(self, prompt: str, temperature: float = 0.2) -> str:
        # Keep it simple: prompt-constrained JSON
        resp = self._sdk_client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature": temperature,
            },
        )
        return getattr(resp, "text", "") or ""

    def _generate_rest(self, prompt: str, temperature: float = 0.2) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY,
        }
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return ""

    def generate_feedback_obj(self, prompt: str, max_attempts: int = 4) -> Dict[str, Any]:
        last_text = ""
        for attempt in range(max_attempts):
            text = self.generate_json_text(prompt)
            last_text = text

            raw_json = extract_first_json_object(text) or text
            obj = safe_json_loads(raw_json)
            if isinstance(obj, dict):
                return normalize_feedback_obj(obj)

            _sleep_backoff(attempt)

        # Fallback empty object
        return normalize_feedback_obj({"overall_summary": "", "positives": [], "feedback_items": []})

