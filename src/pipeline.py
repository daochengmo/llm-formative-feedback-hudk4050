import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


def _safe_json_loads(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = value if isinstance(value, str) else str(value)
    s = s.strip()
    if not s:
        return None

    try:
        return json.loads(s)
    except Exception:
        cleaned = s.replace("\\n", "\n").replace("\\t", "\t")
        try:
            return json.loads(cleaned)
        except Exception:
            return None


def _extract(obj: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not obj:
        return {"overall_summary": "", "positives": "[]", "feedback_items": "[]"}

    overall = obj.get("overall_summary") or obj.get("summary") or ""
    positives = obj.get("positives") or []
    feedback_items = obj.get("feedback_items") or []

    return {
        "overall_summary": str(overall),
        "positives": json.dumps(positives, ensure_ascii=False),
        "feedback_items": json.dumps(feedback_items, ensure_ascii=False),
    }


def build_eval_pack_review(
    eval_pack_raw_path: str | Path,
    sample_set_path: str | Path,
    output_path: str | Path,
    *,
    v1_col: str = "v1_json",
    v2_col: str = "v2_json",
    id_col: str = "essay_id",
) -> pd.DataFrame:
    """
    Create outputs/eval_pack_review.csv from cached raw outputs.

    Offline and reproducible:
      - No LLM API calls
      - Parse cached v1_json/v2_json from eval_pack_raw.csv
      - Ensure essay_text exists (join sample_50_set1.csv if needed)

    Output columns:
      essay_id, essay_set, domain1_score, essay_text,
      v1_overall_summary, v2_overall_summary,
      v1_positives, v2_positives,
      v1_feedback_items, v2_feedback_items
    """
    eval_pack_raw_path = Path(eval_pack_raw_path)
    sample_set_path = Path(sample_set_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(eval_pack_raw_path)
    essays = pd.read_csv(sample_set_path)

    # Normalize common essay columns
    if "essay_text" not in essays.columns and "essay" in essays.columns:
        essays = essays.rename(columns={"essay": "essay_text"})
    if "essay_set" not in essays.columns and "set" in essays.columns:
        essays = essays.rename(columns={"set": "essay_set"})

    # Only bring columns that are missing in raw to avoid _x/_y collisions
    join_cols = [id_col]
    for c in ["essay_set", "domain1_score", "essay_text"]:
        if c not in raw.columns and c in essays.columns:
            join_cols.append(c)

    if len(join_cols) > 1:
        raw = raw.merge(essays[join_cols], on=id_col, how="left")

    required = ["essay_id", "essay_set", "domain1_score", "essay_text", v1_col, v2_col]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns after join: {missing}")

    v1_obj = raw[v1_col].apply(_safe_json_loads)
    v2_obj = raw[v2_col].apply(_safe_json_loads)

    v1 = v1_obj.apply(_extract).apply(pd.Series).add_prefix("v1_")
    v2 = v2_obj.apply(_extract).apply(pd.Series).add_prefix("v2_")

    out = pd.concat(
        [
            raw[["essay_id", "essay_set", "domain1_score", "essay_text"]],
            v1[["v1_overall_summary", "v1_positives", "v1_feedback_items"]],
            v2[["v2_overall_summary", "v2_positives", "v2_feedback_items"]],
        ],
        axis=1,
    )

    out = out[
        [
            "essay_id",
            "essay_set",
            "domain1_score",
            "essay_text",
            "v1_overall_summary",
            "v2_overall_summary",
            "v1_positives",
            "v2_positives",
            "v1_feedback_items",
            "v2_feedback_items",
        ]
    ]

    out.to_csv(output_path, index=False)
    return out

