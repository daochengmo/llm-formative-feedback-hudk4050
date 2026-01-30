# llm-formative-feedback-hudk4050

Reproducible pipeline for generating and evaluating LLM-based formative feedback for K–12 student writing (HUDK 4050 final project).

## Key Output
- `outputs/eval_pack_review.csv` (main deliverable)

## Repo Structure
- `data/` input datasets (de-identified samples)
- `notebooks/` exploratory notebook used during development
- `src/` reusable pipeline modules (LLM client, prompts, evaluation utilities)
- `scripts/` entry points for running the pipeline
- `outputs/` generated artifacts

## Quickstart
1. Create environment and install dependencies
```bash
pip install -r requirements.txt
