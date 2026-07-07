import json
from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


FINANCIAL_METRICS = {
    "Revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues"
    ],
    "Net Income": [
        "NetIncomeLoss"
    ],
    "Assets": [
        "Assets"
    ],
    "Liabilities": [
        "Liabilities"
    ],
    "Operating Cash Flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ]
}


def load_raw_json(ticker: str) -> dict:
    file_path = RAW_DATA_DIR / f"sec_companyfacts_{ticker}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Raw file not found: {file_path}")

    with open(file_path, "r") as file:
        return json.load(file)


def extract_metric_records(data: dict, ticker: str) -> list[dict]:
    records = []

    company_name = data.get("entityName")
    cik = data.get("cik")
    us_gaap_facts = data.get("facts", {}).get("us-gaap", {})

    for metric_name, possible_tags in FINANCIAL_METRICS.items():
        selected_tag = None

        for tag in possible_tags:
            if tag in us_gaap_facts:
                selected_tag = tag
                break

        if selected_tag is None:
            print(f"Metric not found: {metric_name}")
            continue

        metric_data = us_gaap_facts[selected_tag]
        usd_records = metric_data.get("units", {}).get("USD", [])

        for item in usd_records:
            records.append({
                "ticker": ticker,
                "cik": cik,
                "company_name": company_name,
                "metric_name": metric_name,
                "sec_tag": selected_tag,
                "value": item.get("val"),
                "unit": "USD",
                "fiscal_year": item.get("fy"),
                "fiscal_period": item.get("fp"),
                "form": item.get("form"),
                "filed_date": item.get("filed"),
                "period_end_date": item.get("end"),
                "accession_number": item.get("accn")
            })

    return records


def save_processed_data(records: list[dict], ticker: str) -> Path:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(records)

    output_path = PROCESSED_DATA_DIR / f"sec_financial_metrics_{ticker}.xlsx"
    df.to_excel(output_path, index=False)

    return output_path


def main():
    ticker = "AAPL"

    print(f"Parsing financial metrics for {ticker}...")

    raw_data = load_raw_json(ticker)
    records = extract_metric_records(raw_data, ticker)
    output_path = save_processed_data(records, ticker)

    print(f"Total records extracted: {len(records)}")
    print(f"Saved processed data to: {output_path}")


if __name__ == "__main__":
    main()
