# Data

`sample.csv` in this folder is **synthetic** — a handful of made-up rows, not real people, just here so the expected `SR_NO,NTN,NAME` format is obvious at a glance.

The real training data is **not committed to this repo**, on purpose: it's ~2.5 million real people's names paired with their CNIC/tax number, and a public GitHub repo is not a great place to host that at bulk-download scale, even though the source itself is public.

## Where the real data comes from

Pakistan's Federal Board of Revenue (FBR) publishes the **Active Taxpayer List (ATL)** — a weekly-updated list of registered income tax filers, intended for looking up an individual's filer status. It's downloaded from FBR's ATL portal as an Excel file with several sheets.

## Regenerating it yourself

1. Download the current ATL export from FBR's website.
2. Run the merge/clean step:
   ```bash
   python scripts/merge_sheets.py --input ATL_IT.xlsx --output data/ATL_IT_merged_clean.csv
   ```
   This combines every sheet, dedupes by NTN, and drops rows that are clearly businesses rather than individuals (e.g. "M/S ..." entries) or have corrupted/misaligned fields.
3. Train on it:
   ```bash
   python scripts/train_model.py --input data/ATL_IT_merged_clean.csv
   ```

## A caveat worth knowing

For individuals, FBR uses the CNIC number as the NTN, so this project decodes both **gender** (last digit, odd/even) and **province** (first digit, 1–7 code) straight from that column — see `scripts/train_model.py` and the notebook for the exact rule. The gender rule is NADRA's own convention and holds reliably. The province rule is less reliable in this dataset: Sindh comes out at ~0.03% of rows, which is implausible, most likely because a portion of individual taxpayers — especially older registrations in commercial hubs like Karachi — still carry a legacy NTN issued before FBR's 2011 policy of using the CNIC itself as the NTN. Treat any province-based conclusion from this data as provisional.
