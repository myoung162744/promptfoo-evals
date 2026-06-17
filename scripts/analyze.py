#!/usr/bin/env python3
"""Compute grading-agreement statistics from promptfoo results JSON.

Promptfoo pass-rates alone can't rank graders; the field-standard metric is
Quadratic Weighted Kappa (QWK) between model and human scores. Human-human
QWK on ASAP is ~0.75 — that's the bar a good model grader should approach.

Usage:
    promptfoo eval -c configs/asap-essays.yaml -o output/asap-essays.json
    python scripts/analyze.py output/asap-essays.json [--traits]
"""
import argparse
import json
import re
import sys
from collections import defaultdict

import numpy as np


def extract_json(text: str):
    if not isinstance(text, str):
        return None
    t = re.sub(r"```(json)?", "", text).strip()
    s = t.find("{")
    if s == -1:
        return None
    o = None
    # Greedy first try; then fall back to the first brace-balanced object.
    # Some models (notably Opus) emit a stray premature "}" — e.g.
    # {... "evidence": "..."}, "feedback": "..."} — which breaks a naive
    # first-{ .. last-} slice. Balanced scanning recovers the leading object,
    # which still carries "overall" and "trait_scores" (all QWK needs).
    try:
        o = json.loads(t[s:t.rfind("}") + 1])
    except json.JSONDecodeError:
        depth, in_str, esc = 0, False, False
        for i in range(s, len(t)):
            c = t[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        o = json.loads(t[s:i + 1])
                    except json.JSONDecodeError:
                        o = None
                    break
    if o is None:
        return None
    # Tolerate "overall" nested inside trait_scores (mirrors evals/parse_output.js)
    if isinstance(o, dict) and not isinstance(o.get("overall"), (int, float)):
        ts = o.get("trait_scores")
        if isinstance(ts, dict) and isinstance(ts.get("overall"), (int, float)):
            o["overall"] = ts.pop("overall")
    return o


def qwk(human, model) -> float:
    """Quadratic weighted kappa on integer-coded labels."""
    h = np.asarray(human)
    m = np.asarray(model)
    lo, hi = int(min(h.min(), m.min())), int(max(h.max(), m.max()))
    n_levels = hi - lo + 1
    if n_levels == 1:
        return 1.0
    obs = np.zeros((n_levels, n_levels))
    for a, b in zip(h, m):
        obs[a - lo, b - lo] += 1
    weights = np.array([[(i - j) ** 2 for j in range(n_levels)] for i in range(n_levels)])
    weights = weights / (n_levels - 1) ** 2
    expected = np.outer(obs.sum(axis=1), obs.sum(axis=0)) / obs.sum()
    denom = (weights * expected).sum()
    if denom == 0:
        return 1.0
    return 1.0 - (weights * obs).sum() / denom


def iter_results(data):
    res = data.get("results", data)
    if isinstance(res, dict):
        res = res.get("results", [])
    for r in res:
        provider = r.get("provider")
        if isinstance(provider, dict):
            provider = provider.get("label") or provider.get("id")
        vars_ = r.get("vars") or r.get("testCase", {}).get("vars", {})
        output = (r.get("response") or {}).get("output")
        yield provider, vars_, output


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_json")
    ap.add_argument("--traits", action="store_true", help="also report per-trait QWK")
    args = ap.parse_args()

    with open(args.results_json) as f:
        data = json.load(f)

    rows = defaultdict(lambda: {"human": [], "model": [], "n": 0, "fail": 0,
                                "traits": defaultdict(lambda: {"human": [], "model": []})})
    half_scale = False
    for provider, vars_, output in iter_results(data):
        rec = rows[provider]
        rec["n"] += 1
        parsed = extract_json(output)
        human = vars_.get("human_overall")
        if parsed is None or not isinstance(parsed.get("overall"), (int, float)) or human is None:
            rec["fail"] += 1
            continue
        if float(vars_.get("tolerance", 1)) == 0.5:
            half_scale = True
        rec["human"].append(float(human))
        rec["model"].append(float(parsed["overall"]))
        for trait in str(vars_.get("traits", "")).split(","):
            trait = trait.strip()
            ht = vars_.get(f"human_{trait}")
            mt = (parsed.get("trait_scores") or {}).get(trait)
            if trait and ht is not None and isinstance(mt, (int, float)):
                rec["traits"][trait]["human"].append(float(ht))
                rec["traits"][trait]["model"].append(float(mt))

    if not rows:
        sys.exit("No results found in file — is this a promptfoo -o output?")

    # half-point scales (ELLIPSE) are doubled to integers for QWK
    code = (lambda xs: [round(x * 2) for x in xs]) if half_scale else (lambda xs: [round(x) for x in xs])
    tol = 0.5 if half_scale else 1.0

    print(f"\n## {args.results_json}\n")
    header = "| model | n | parse fail | QWK | exact | adjacent (±{}) | mean signed err | r |".format(tol)
    print(header)
    print("|" + "---|" * 8)
    summary = []
    for provider, rec in sorted(rows.items()):
        h, m = np.array(rec["human"]), np.array(rec["model"])
        if len(h) < 2:
            print(f"| {provider} | {rec['n']} | {rec['fail']} | — | — | — | — | — |")
            continue
        k = qwk(code(h), code(m))
        exact = float(np.mean(np.abs(m - h) < 1e-9))
        adj = float(np.mean(np.abs(m - h) <= tol + 1e-9))
        bias = float(np.mean(m - h))
        r = float(np.corrcoef(h, m)[0, 1]) if np.std(h) > 0 and np.std(m) > 0 else float("nan")
        summary.append((k, provider))
        print(f"| {provider} | {rec['n']} | {rec['fail']} | {k:.3f} | {exact:.0%} | {adj:.0%} "
              f"| {bias:+.2f} | {r:.3f} |")

    if args.traits:
        print("\n### Per-trait QWK\n")
        traits = sorted({t for rec in rows.values() for t in rec["traits"]})
        if traits:
            print("| model | " + " | ".join(traits) + " |")
            print("|" + "---|" * (len(traits) + 1))
            for provider, rec in sorted(rows.items()):
                cells = []
                for t in traits:
                    th, tm = rec["traits"][t]["human"], rec["traits"][t]["model"]
                    cells.append(f"{qwk(code(th), code(tm)):.3f}" if len(th) >= 2 else "—")
                print(f"| {provider} | " + " | ".join(cells) + " |")
        else:
            print("(no trait scores in this results file)")

    if summary:
        best = max(summary)
        print(f"\nBest QWK: {best[1]} ({best[0]:.3f}). "
              "Reference: human-human agreement on ASAP is ~0.75.")
        print("Mean signed error > 0 means the model grades more leniently than humans.")


if __name__ == "__main__":
    main()
