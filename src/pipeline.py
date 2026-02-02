import json
import os
from typing import Dict, Any

import pandas as pd
from tqdm import tqdm

from .llm_client import LLMClient
from .prompts import V1_PROMPT, V2_PROMPT, render_prompt
from .utils import compact_json_dumps


def run_llm_stage(df_in: pd.DataFrame, out_raw_csv: str) -> pd.DataFrame:
    client = LLMClient()

    rows = []
    for _, r in tqdm(df_in.iterrows(), total=len(df_in), desc="LLM feedback"):
        essay_id = int(r["essay_id"])
        essay_text = str(r["essay_clean"])

        v1_prompt = render_prompt(V1_PROMPT, essay_text)
        v2_prompt = render_prompt(V2_PROMPT, essay_text)

        v1_obj = client.generate_feedback_obj(v1_prompt)
        v2_obj = client.generate_feedback_obj(v2_prompt)

        rows.append(
            {
                "essay_id": essay_id,
                "v1_json": compact_json_dumps(v1_obj),
                "v2_json": compact_json_dumps(v2_obj),
            }
        )

    df_raw = pd.DataFrame(rows)
    df_raw.to_csv(out_raw_csv, index=False)
    return df_raw


def raw_to_wide(df_raw: pd.DataFrame, out_wide_csv: str) -> pd.DataFrame:
    def parse_col(s: str) -> Dict[str, Any]:
        try:
            return json.loads(s) if isinstance(s, str) else {}
        except Exception:
            return {}

    out = []
    for _, r in df_raw.iterrows():
        v1 = parse_col(r.get("v1_json", ""))
        v2 = parse_col(r.get("v2_json", ""))

        out.append(
            {
                "essay_id": int(r["essay_id"]),
                "v1_overall_summary": v1.get("overall_summary", ""),
                "v2_overall_summary": v2.get("overall_summary", ""),
                "v1_positives": json.dumps(v1.get("positives", []), ensure_ascii=False),
                "v2_positives": json.dumps(v2.get("positives", []), ensure_ascii=False),
                "v1_feedback_items": json.dumps(v1.get("feedback_items", []), ensure_ascii=False),
                "v2_feedback_items": json.dumps(v2.get("feedback_items", []), ensure_ascii=False),
            }
        )

    df_wide = pd.DataFrame(out)
    df_wide.to_csv(out_wide_csv, index=False)
    return df_wide


def build_review_pack(df_meta: pd.DataFrame, df_wide: pd.DataFrame, out_review_csv: str) -> pd.DataFrame:
    # df_meta should contain: essay_id, essay_set, domain1_score, essay_text
    df = df_meta.merge(df_wide, on="essay_id", how="inner")
    cols = [
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
    df = df[cols]
    df.to_csv(out_review_csv, index=False)
    return df

