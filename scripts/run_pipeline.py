import argparse
import os
import pandas as pd

from src.pipeline import run_llm_stage, raw_to_wide, build_review_pack


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean_csv", default="data/sample_50_with_clean.csv")
    ap.add_argument("--meta_csv", default="data/sample_50_set1.csv")
    ap.add_argument("--out_dir", default="outputs")
    ap.add_argument("--skip_llm", action="store_true")
    ap.add_argument("--raw_csv", default="data/eval_pack_raw.csv")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    out_raw = os.path.join(args.out_dir, "eval_pack_raw.csv")
    out_wide = os.path.join(args.out_dir, "eval_pack_wide.csv")
    out_review = os.path.join(args.out_dir, "eval_pack_review.csv")

    df_clean = pd.read_csv(args.clean_csv)
    df_meta = pd.read_csv(args.meta_csv)

    if args.skip_llm:
        df_raw = pd.read_csv(args.raw_csv)
    else:
        df_raw = run_llm_stage(df_clean, out_raw)

    df_wide = raw_to_wide(df_raw, out_wide)

    # meta uses original essay_text, not the cleaned one
    df_review = build_review_pack(df_meta, df_wide, out_review)

    print("Wrote:")
    print(out_raw if not args.skip_llm else "(skipped llm, used raw_csv)")
    print(out_wide)
    print(out_review)
    print("Rows:", len(df_review))


if __name__ == "__main__":
    main()
