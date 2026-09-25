# Name → Gender Classifier (Pakistani names)

A character-level text classifier that predicts gender from a name alone, trained on labels decoded from real CNIC numbers in Pakistan's Active Taxpayer List (ATL) — no name dictionary, no lookup table, just spelling patterns.

**[Live demo →](#demo)** (runs entirely in your browser, model included — see `web/index.html`)

## How it works

1. **Data**: FBR's public Active Taxpayer List — ~2.5 million individual taxpayer records after cleaning (deduped, businesses filtered out). See [`data/README.md`](data/README.md).
2. **Labeling**: for individuals, FBR uses the CNIC number as the NTN. The last digit of a CNIC is odd for male, even for female (NADRA's own convention) — so gender labels are decoded directly from the ID, not guessed. The first digit similarly decodes a province code. See `scripts/train_model.py` for the exact rule, and the caveat in `data/README.md` about the province decode's reliability.
3. **Model**: character n-gram (2–4 chars) TF-IDF features + logistic regression, `class_weight='balanced'` to handle the ~81/19 male/female imbalance in the source data.
4. **Web demo**: the trained model's weights are exported to JSON (`model/model_export.json`) and the exact same tokenizing → TF-IDF → logistic regression math is reimplemented in vanilla JavaScript, so `web/index.html` is a single self-contained file — no backend, no API calls, works offline.

## Results

Evaluated on a held-out 20% stratified test set (~492k names):

| Metric | Male | Female |
|---|---|---|
| Precision | 99.4% | 93.5% |
| Recall | 98.4% | 97.5% |
| F1 | 98.9% | 95.4% |

Overall accuracy: **98.3%**. Precision/recall by class matter more than the headline accuracy number here, since the training data itself is imbalanced (~81% male) — see the notebook for the full discussion.

## Demo

`web/index.html` is fully self-contained (model weights embedded, ~700KB) — open it directly in a browser, or enable **GitHub Pages** on this repo (Settings → Pages → deploy from `/web`) to get a shareable live link.

## Repo structure

```
notebooks/    Colab-ready notebook: loads raw data, decodes labels, trains, evaluates
scripts/      Same pipeline as plain Python scripts (merge → train → export)
model/        Exported model weights used by the web demo
web/          Self-contained HTML/JS demo (no server needed)
data/         Data format + where to get the real dataset (not committed — see below)
```

## Getting started

```bash
pip install -r requirements.txt

# 1. Merge and clean the raw FBR ATL export (see data/README.md for the source)
python scripts/merge_sheets.py --input ATL_IT.xlsx --output data/ATL_IT_merged_clean.csv

# 2. Train
python scripts/train_model.py --input data/ATL_IT_merged_clean.csv

# 3. Export weights for the web demo
python scripts/export_web_model.py
```

Or open `notebooks/name_gender_classifier.ipynb` in Google Colab and run it top to bottom.

## A note on the data and what this actually shows

This isn't a lookup of anyone's real gender — it's a statistical pattern match on spelling, learned from a large but imbalanced, real-world-messy dataset. The `data/README.md` file documents a real data-quality finding from this project (an implausible province distribution once decoded) rather than smoothing it over — worth reading if you're evaluating this as a class project, since that kind of caveat is usually more informative than a clean-looking number.

The full 2.5M-row dataset isn't included in this repo; see `data/README.md` for why and how to regenerate it.

## License

MIT — see [LICENSE](LICENSE).
