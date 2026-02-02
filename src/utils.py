import json
import re
from typing import Any, Dict, Optional


_JSON_OBJ_RE = re.compile(r"\{[\s\S]*\}")


def extract_first_json_object(text: str) -> Optional[str]:
    """
    Best-effort: extract the first JSON object substring from a model response.
    """
    if not text:
        return None
    m = _JSON_OBJ_RE.search(text)
    return m.group(0) if m else None


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def compact_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def normalize_feedback_obj(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize to the fields your eval_pack_review.csv expects.
    """
    out = {
        "overall_summary": str(obj.get("overall_summary", "")).strip(),
        "positives": obj.get("positives", []),
        "feedback_items": obj.get("feedback_items", []),
    }

    if not isinstance(out["positives"], list):
        out["positives"] = []
    out["positives"] = [str(x).strip() for x in out["positives"] if str(x).strip()]

    if not isinstance(out["feedback_items"], list):
        out["feedback_items"] = []

    norm_items = []
    for it in out["feedback_items"]:
        if not isinstance(it, dict):
            continue
        norm_items.append(
            {
                "category": str(it.get("category", "")).strip(),
                "issue": str(it.get("issue", "")).strip(),
                "suggestion": str(it.get("suggestion", "")).strip(),
                "evidence": str(it.get("evidence", "")).strip(),
                "confidence": str(it.get("confidence", "")).strip(),
            }
        )
    out["feedback_items"] = norm_items
    return out

