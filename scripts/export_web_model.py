"""
Export a trained model (from train_model.py) to the compact JSON format
that web/index.html runs entirely client-side, with no server or API calls.

The web demo reimplements this exact math in JavaScript: char_wb n-gram
tokenizing -> TF-IDF weighting -> L2 normalize -> logistic regression.
This script just dumps the numbers that math needs.

Usage:
    python scripts/export_web_model.py --model model/name_gender_classifier.joblib --output model/model_export.json
"""

import argparse
import json
import joblib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='model/name_gender_classifier.joblib')
    ap.add_argument('--output', default='model/model_export.json')
    args = ap.parse_args()

    model = joblib.load(args.model)
    vec = model.named_steps['tfidf']
    clf = model.named_steps['clf']

    n_features = len(vec.vocabulary_)
    ngrams = [None] * n_features
    for term, idx in vec.vocabulary_.items():
        ngrams[idx] = term

    payload = {
        'ngrams': ngrams,
        'idf': [round(x, 5) for x in vec.idf_.tolist()],
        'coef': [round(x, 5) for x in clf.coef_[0].tolist()],
        'intercept': round(float(clf.intercept_[0]), 5),
        'classes': clf.classes_.tolist(),  # classes[1] is the positive class for coef/intercept
        'ngram_range': list(vec.ngram_range),
    }

    with open(args.output, 'w') as f:
        json.dump(payload, f, separators=(',', ':'))

    print(f'Exported {n_features:,} n-gram weights to {args.output}')


if __name__ == '__main__':
    main()
