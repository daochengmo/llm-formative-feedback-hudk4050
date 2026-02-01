import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import build_eval_pack_review  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build eval_pack_review.csv from cached raw outputs and sample essays."
    )
    p.add_argument("--data-dir", type=str, default="data")
    p.add_argument("--out-dir", type=str, default="outputs")
    p.add_argument("--eval-pack-raw", type=str, default="eval_pack_raw.csv")
    p.add_argument("--sample-set", type=str, default="sample_50_set1.csv")
    p.add_argument("--out-file", type=str, default="eval_pack_review.csv")
    args = p.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    build_eval_pack_review(
        eval_pack_raw_path=data_dir / args.eval_pack_raw,
        sample_set_path=data_dir / args.sample_set,
        output_path=out_dir / args.out_file,
    )

    print(f"Saved: {out_dir / args.out_file}")


if __name__ == "__main__":
    main()

