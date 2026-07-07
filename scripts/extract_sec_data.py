import json
import time
from pathlib import Path

import requests


# Apple CIK from SEC. SEC CIK values need to be 10 digits for the companyfacts API.
COMPANIES = {
    "AAPL": "0000320193"
}

RAW_DATA_DIR = Path("data/raw")


def fetch_company_facts(ticker: str, cik: str) -> dict:
    """
    Extract company financial facts from the SEC companyfacts API.
    """

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    headers = {
        "User-Agent": "SEC Financial Data Pipeline contact@example.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()


def save_raw_json(data: dict, ticker: str) -> Path:
    """
    Save raw SEC API response as JSON.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / f"sec_companyfacts_{ticker}.json"

    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)

    return output_path


def main():
    for ticker, cik in COMPANIES.items():
        print(f"Extracting SEC company facts for {ticker}...")

        company_data = fetch_company_facts(ticker, cik)
        output_path = save_raw_json(company_data, ticker)

        print(f"Saved raw data to: {output_path}")

        # SEC fair access: keep requests controlled.
        time.sleep(1)


if __name__ == "__main__":
    main()
