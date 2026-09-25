"""
Train the name -> gender classifier.

Input:  data/ATL_IT_merged_clean.csv  (columns: SR_NO, NTN, NAME — no labels yet)
Output: model/name_gender_classifier.joblib

Labels aren't looked up from anywhere — they're decoded directly from the CNIC:
  - GENDER:   last digit of the 13-digit CNIC. Odd = Male, Even = Female (NADRA's own rule).
  - PROVINCE: first digit of the CNIC, using the commonly documented 1-7 province code.
              See the caveat in the README about this column's reliability.

Usage:
    python scripts/train_model.py --input data/ATL_IT_merged_clean.csv --output model/name_gender_classifier.joblib
"""

import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib

PROVINCE_MAP = {
    '1': 'Khyber Pakhtunkhwa',
    '2': 'FATA',
    '3': 'Punjab',
    '4': 'Sindh',
    '5': 'Balochistan',
    '6': 'Islamabad',
    '7': 'Gilgit-Baltistan',
}


def decode_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows with a real 13-digit CNIC, then decode GENDER and PROVINCE from it."""
    df = df[df['NTN'].astype(str).str.len() == 13].copy()

    last_digit = df['NTN'].str[-1].astype(int)
    df['GENDER'] = last_digit.apply(lambda d: 'Male' if d % 2 == 1 else 'Female')

    first_digit = df['NTN'].str[0]
    df['PROVINCE'] = first_digit.map(PROVINCE_MAP).fillna('Unknown')

    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='data/ATL_IT_merged_clean.csv')
    ap.add_argument('--output', default='model/name_gender_classifier.joblib')
    args = ap.parse_args()

    df = pd.read_csv(args.input, dtype=str)
    print(f'Loaded {len(df):,} rows')

    df = decode_labels(df)
    print(df['GENDER'].value_counts())
    print(df['PROVINCE'].value_counts())

    df['NAME'] = df['NAME'].astype(str).str.upper().str.strip()
    df = df[df['NAME'].str.len() > 0].reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        df['NAME'], df['GENDER'], test_size=0.2, random_state=42, stratify=df['GENDER']
    )

    model = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), min_df=3)),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced')),
    ])
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred, labels=['Male', 'Female']))

    joblib.dump(model, args.output)
    print(f'Saved model to {args.output}')


if __name__ == '__main__':
    main()
