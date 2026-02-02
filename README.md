# llm-formative-feedback-hudk4050

Reproducible pipeline for generating and evaluating LLM-based formative feedback for K–12 student writing (HUDK 4050 final project).

## Key Output
- `outputs/eval_pack_review.csv` (main deliverable)

## Repo Structure
- `data/` input datasets (de-identified samples)
- `notebooks/` exploratory notebook used during development
- `src/` reusable pipeline modules (LLM client, prompts, utilities)
- `scripts/` entry points for running the pipeline
- `outputs/` generated artifacts

## Quickstart (SDK only)

### 0) Prereqs
- Python 3.10+ recommended
- A Gemini API key

### 1) Set environment variables
Create a `.env` file at repo root (or export env vars in your shell):

```bash
cp .env.example .env
# then edit .env and fill GOOGLE_API_KEY
