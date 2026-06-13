#!/usr/bin/env python3
"""Build promptfoo test cases from the raw grading datasets.

Samples are stratified: split evenly across essay sets/prompts, then round-robin
across human score levels within each stratum so low/mid/high scores are all
represented (random sampling would over-weight the modal middle scores).

Usage:
    python scripts/prepare.py --dataset all --n 50 --seed 42
"""
import argparse
import random
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "datasets" / "raw"
OUT = ROOT / "test-inputs" / "generated"


def stratified_sample(df: pd.DataFrame, score_col: str, n: int, rng: random.Random) -> pd.DataFrame:
    """Round-robin across score levels: one row per level per pass until n rows."""
    pools = {}
    for level, group in df.groupby(score_col):
        idx = list(group.index)
        rng.shuffle(idx)
        pools[level] = idx
    picked = []
    levels = sorted(pools)
    while len(picked) < n and any(pools.values()):
        for level in levels:
            if pools[level] and len(picked) < n:
                picked.append(pools[level].pop())
    return df.loc[picked]


def split_counts(n: int, k: int) -> list[int]:
    base, rem = divmod(n, k)
    return [base + (1 if i < rem else 0) for i in range(k)]


def read_rubric(name: str) -> str:
    return (ROOT / "rubrics" / name).read_text().strip()


# ---------------------------------------------------------------- ASAP++ ----
ASAP_PP_PROMPTS = {
    1: "More and more people use computers, but not everyone agrees that this benefits society. "
       "Write a letter to your local newspaper in which you state your opinion on the effects "
       "computers have on people. Persuade the readers to agree with you.",
    2: "Censorship in the Libraries. 'All of us can think of a book that we hope none of our "
       "children or any other children have taken off the shelf...' Write a persuasive essay to a "
       "newspaper reflecting your views on censorship in libraries. Do you believe that certain "
       "materials, such as books, music, movies, magazines, etc., should be removed from the "
       "shelves if they are found offensive? Support your position with convincing arguments.",
}
ASAP_PP_SCALE = {
    1: "Score each trait on a 1-6 scale. The overall score is on a 2-12 scale "
       "(it is the sum of two independent raters' 1-6 holistic scores).",
    2: "Score each trait and the overall score on a 1-6 scale.",
}
ASAP_PP_TRAITS = ["content", "organization", "word_choice", "sentence_fluency", "conventions"]


def prepare_asap_pp(n: int, rng: random.Random) -> list[dict]:
    essays = pd.read_csv(RAW / "asap" / "training_set_rel3.tsv", sep="\t", encoding="latin-1")
    tests = []
    for essay_set, n_set in zip((1, 2), split_counts(n, 2)):
        traits = pd.read_csv(RAW / "asap-pp" / f"Prompt-{essay_set}.csv")
        traits.columns = [c.strip().lower().replace(" ", "_").replace("essayid", "essay_id") for c in traits.columns]
        merged = essays[essays.essay_set == essay_set].merge(traits, on="essay_id")
        rubric = read_rubric(f"asap-pp-set{essay_set}.txt")
        sample = stratified_sample(merged, "domain1_score", n_set, rng)
        for _, row in sample.iterrows():
            tests.append({
                "description": f"asap-pp set {essay_set} essay {row.essay_id} (human {row.domain1_score})",
                "vars": {
                    "essay_prompt": ASAP_PP_PROMPTS[essay_set],
                    "scoring_rubric": rubric,
                    "scale_note": ASAP_PP_SCALE[essay_set],
                    "traits": ", ".join(ASAP_PP_TRAITS),
                    "essay": str(row.essay),
                    "human_overall": int(row.domain1_score),
                    **{f"human_{t}": int(row[t]) for t in ASAP_PP_TRAITS},
                },
            })
    return tests


# --------------------------------------------------------------- ASAP-SAS ---
def prepare_asap_sas(n: int, rng: random.Random) -> list[dict]:
    sets = (1, 2, 5, 6)
    tests = []
    for essay_set, n_set in zip(sets, split_counts(n, len(sets))):
        df = pd.read_csv(RAW / "asap-sas" / f"asap-{essay_set}" / "test.csv")
        question = (RAW / "asap-sas" / f"asap-{essay_set}" / "content.txt").read_text().strip()
        sample = stratified_sample(df, "Score1", n_set, rng)
        for _, row in sample.iterrows():
            tests.append({
                "description": f"asap-sas set {essay_set} answer {row.Id} (human {row.Score1})",
                "vars": {
                    "question": question,  # includes [Question], [Key Elements], [Marking Rubric]
                    "response": str(row.EssayText),
                    "human_overall": int(row.Score1),
                },
            })
    return tests


# --------------------------------------------------------------- PERSUADE ---
# Only prompts whose source-text PDFs have a text layer (the rest are scans
# and would need OCR; see README).
PERSUADE_SOURCES = {
    "Does the electoral college work?": "FL1_does_the_electoral_college_work.txt",
    "Car-free cities": "FL2_car-free_cities.txt",
}


def prepare_persuade(n: int, rng: random.Random) -> list[dict]:
    df = pd.read_csv(RAW / "asap2" / "ASAP_2_Final_github_train.csv")
    rubric = read_rubric("asap2.txt")
    tests = []
    prompts = list(PERSUADE_SOURCES)
    for prompt_name, n_set in zip(prompts, split_counts(n, len(prompts))):
        sub = df[df.prompt_name == prompt_name]
        source = (RAW / "asap2" / "source_txt" / PERSUADE_SOURCES[prompt_name]).read_text().strip()
        assignment = str(sub.assignment.iloc[0])
        sample = stratified_sample(sub, "score", n_set, rng)
        for _, row in sample.iterrows():
            tests.append({
                "description": f"persuade '{prompt_name}' essay {row.essay_id} (human {row.score})",
                "vars": {
                    "essay_prompt": assignment,
                    "source_text": source,
                    "scoring_rubric": rubric,
                    "scale_note": "Score the essay holistically on a 1-6 scale.",
                    "traits": "",
                    "essay": str(row.full_text),
                    "human_overall": int(row.score),
                },
            })
    return tests


# ---------------------------------------------------------------- ELLIPSE ---
ELLIPSE_TRAITS = ["cohesion", "syntax", "vocabulary", "phraseology", "grammar", "conventions"]


def prepare_ellipse(n: int, rng: random.Random) -> list[dict]:
    df = pd.read_csv(RAW / "ellipse" / "ellipse_train.csv")
    rubric = read_rubric("ellipse.txt")
    sample = stratified_sample(df, "Overall", n, rng)
    tests = []
    for _, row in sample.iterrows():
        tests.append({
            "description": f"ellipse {row.text_id_kaggle} (human {row.Overall})",
            "vars": {
                "essay_prompt": f"(English-language-learner essay; topic: {row.prompt})",
                "scoring_rubric": rubric,
                "scale_note": "Score each trait and the overall score on a 1-5 scale, "
                              "in half-point increments (1.0, 1.5, 2.0, ... 5.0).",
                "traits": ", ".join(ELLIPSE_TRAITS),
                "essay": str(row.full_text),
                "human_overall": float(row.Overall),
                **{f"human_{t}": float(row[t.capitalize()]) for t in ELLIPSE_TRAITS},
            },
        })
    return tests


PREPARERS = {
    "asap-pp": prepare_asap_pp,
    "asap-sas": prepare_asap_sas,
    "persuade": prepare_persuade,
    "ellipse": prepare_ellipse,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="all", choices=["all", *PREPARERS])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    names = list(PREPARERS) if args.dataset == "all" else [args.dataset]
    for name in names:
        tests = PREPARERS[name](args.n, random.Random(args.seed))
        path = OUT / f"{name}.yaml"
        with open(path, "w") as f:
            yaml.dump(tests, f, allow_unicode=True, width=10000, sort_keys=False)
        scores = [t["vars"]["human_overall"] for t in tests]
        print(f"{name}: {len(tests)} cases -> {path.relative_to(ROOT)} "
              f"(score range {min(scores)}-{max(scores)})")


if __name__ == "__main__":
    main()
