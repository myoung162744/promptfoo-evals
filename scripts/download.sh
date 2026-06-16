#!/usr/bin/env bash
# Download all four grading datasets from public no-auth mirrors (no Kaggle account needed).
# Sources:
#   ASAP essays   : github.com/riaz/AES mirror of Kaggle asap-aes training_set_rel3.tsv
#   ASAP++ traits : lwsam.github.io/ASAP++ (official trait-score CSVs + rubric PDFs)
#   ASAP-SAS      : github.com/lijiazheng99/aera (official AERA paper repo; original
#                   Kaggle asap-sas answers/scores + question & rubric text)
#   ASAP 2.0      : github.com/scrosseye/ASAP_2.0 (PERSUADE 2.0 essays, holistic 1-6)
#   ELLIPSE       : github.com/scrosseye/ELLIPSE-Corpus (ELL essays, 6 trait scores)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAW="$ROOT/datasets/raw"
mkdir -p "$RAW"/{asap,asap-pp,asap-sas,asap2,ellipse}

fetch() { # fetch <url> <dest> — skip if already present and non-empty
  local url="$1" dest="$2"
  if [[ -s "$dest" ]]; then echo "skip   $(basename "$dest")"; return; fi
  echo "fetch  $(basename "$dest")"
  curl -sSLf "$url" -o "$dest"
}

# --- ASAP essays (text + holistic scores, 8 sets) ---
fetch "https://raw.githubusercontent.com/riaz/AES/master/training_set_rel3.tsv" \
      "$RAW/asap/training_set_rel3.tsv"

# --- ASAP++ trait scores (sets 1-6) + scoring guideline PDFs ---
for i in 1 2 3 4 5 6; do
  fetch "https://lwsam.github.io/ASAP++/Prompt-${i}.csv" "$RAW/asap-pp/Prompt-${i}.csv"
  fetch "https://lwsam.github.io/ASAP++/Prompt-${i}-Guidelines.pdf" "$RAW/asap-pp/Prompt-${i}-Guidelines.pdf"
done

# --- ASAP-SAS short answers (sets 1,2,5,6 have question+rubric text available) ---
AERA="https://raw.githubusercontent.com/lijiazheng99/aera/main/dataset"
for i in 1 2 5 6; do
  mkdir -p "$RAW/asap-sas/asap-$i"
  for split in train val test; do
    fetch "$AERA/asap-sas-splitted/asap-$i/$split.csv" "$RAW/asap-sas/asap-$i/$split.csv"
  done
  fetch "$AERA/chatgpt_api_0405/prompts/asap-$i/content.txt" "$RAW/asap-sas/asap-$i/content.txt"
done

# --- ASAP 2.0 / PERSUADE 2.0 (holistic 1-6, source-based persuasive essays) ---
ASAP2="https://raw.githubusercontent.com/scrosseye/ASAP_2.0/main"
fetch "$ASAP2/ASAP_2_Final_github_train.zip" "$RAW/asap2/train.zip"
fetch "$ASAP2/ASAP_2_source_texts.zip"       "$RAW/asap2/source_texts.zip"
fetch "$ASAP2/asap_scoring_rubric.docx"      "$RAW/asap2/asap_scoring_rubric.docx"
(cd "$RAW/asap2" && unzip -nq train.zip && unzip -nq source_texts.zip)

# --- ELLIPSE (ELL essays, 6 analytic traits, 1-5 in 0.5 steps) ---
ELL="https://raw.githubusercontent.com/scrosseye/ELLIPSE-Corpus/main"
fetch "$ELL/ELLIPSE_Final_github_train.csv" "$RAW/ellipse/ellipse_train.csv"
fetch "$ELL/ELL_Rubrics.docx"               "$RAW/ellipse/ELL_Rubrics.docx"

echo
echo "=== sanity checks ==="
wc -l "$RAW/asap/training_set_rel3.tsv" "$RAW/asap-pp/Prompt-1.csv" \
      "$RAW/asap-sas/asap-1/train.csv" "$RAW/ellipse/ellipse_train.csv" 2>/dev/null
ls "$RAW/asap2/"
