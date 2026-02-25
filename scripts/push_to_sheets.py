#!/usr/bin/env python3
"""
Social Content Generator — Push to Google Sheets
Reads content.json and pushes rows to a Google Sheet for scheduling.

Usage:
    python scripts/push_to_sheets.py \
        --sheet-id "1abc123..." \
        --data "outputs/content.json"

    # Specify worksheet tab name
    python scripts/push_to_sheets.py \
        --sheet-id "1abc123..." \
        --data "outputs/content.json" \
        --worksheet "March Campaign"

    # With explicit config path
    python scripts/push_to_sheets.py \
        --sheet-id "1abc123..." \
        --data "outputs/content.json" \
        --config "/path/to/config.json"

Expected content.json structure:
[
    {
        "post_number": 1,
        "date": "2026-03-03",
        "platform": "Instagram",
        "pillar": "Product Spotlight",
        "format": "Static",
        "caption": "Full caption...",
        "cta": "Link in bio",
        "hashtags": "#Brand #Tag",
        "image_prompt": "NanoBanana prompt...",
        "image_file": "outputs/post-01.png",
        "status": "Ready for Review"
    }
]
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_config(config_path=None):
    """Load config from file."""
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)

    script_dir = Path(__file__).parent
    default_config = script_dir.parent / "config.json"
    if default_config.exists():
        with open(default_config) as f:
            return json.load(f)

    return {}


def push_to_sheets(sheet_id, data_path, worksheet_name=None, config_path=None):
    """Push content data to Google Sheets."""

    import gspread
    from google.oauth2.service_account import Credentials

    # Load config
    config = load_config(config_path)
    service_account_path = (
        os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        or config.get("google_service_account_path")
    )

    if not service_account_path or not os.path.exists(service_account_path):
        print("ERROR: Google service account JSON not found.", file=sys.stderr)
        print("Set in config.json or GOOGLE_SERVICE_ACCOUNT_JSON env var.", file=sys.stderr)
        sys.exit(1)

    # Load content data
    if not os.path.exists(data_path):
        print(f"ERROR: Content file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    with open(data_path) as f:
        posts = json.load(f)

    if not isinstance(posts, list):
        posts = [posts]

    print(f"Pushing {len(posts)} posts to Google Sheet...")
    print(f"  Sheet ID: {sheet_id}")
    print(f"  Data file: {data_path}")

    # Authenticate
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file(
        service_account_path, scopes=scopes
    )
    gc = gspread.authorize(credentials)

    # Open sheet
    try:
        spreadsheet = gc.open_by_key(sheet_id)
    except Exception as e:
        print(f"ERROR: Could not open sheet: {e}", file=sys.stderr)
        print("Make sure the sheet is shared with the service account email.", file=sys.stderr)
        sys.exit(1)

    # Get or create worksheet
    if worksheet_name:
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"  [OK] Using existing worksheet: {worksheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name, rows=100, cols=12
            )
            print(f"  [OK] Created new worksheet: {worksheet_name}")
    else:
        worksheet = spreadsheet.sheet1
        print(f"  [OK] Using first worksheet")

    # Define headers
    headers = [
        "Date", "Platform", "Pillar", "Format", "Caption",
        "CTA", "Hashtags", "Image File", "Image Prompt", "Status"
    ]

    # Check if headers exist, add if not
    existing = worksheet.row_values(1)
    if not existing or existing != headers:
        worksheet.update("A1", [headers])
        print(f"  [OK] Headers written")
        start_row = 2
    else:
        # Find next empty row
        all_values = worksheet.get_all_values()
        start_row = len(all_values) + 1
        print(f"  [OK] Appending from row {start_row}")

    # Build rows
    rows = []
    for post in posts:
        rows.append([
            post.get("date", ""),
            post.get("platform", ""),
            post.get("pillar", ""),
            post.get("format", ""),
            post.get("caption", ""),
            post.get("cta", ""),
            post.get("hashtags", ""),
            post.get("image_file", ""),
            post.get("image_prompt", ""),
            post.get("status", "Draft"),
        ])

    # Push rows
    if rows:
        cell_range = f"A{start_row}"
        worksheet.update(cell_range, rows)
        print(f"  [OK] {len(rows)} rows written")

    print(f"  [OK] Done! Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Push social content to Google Sheets"
    )
    parser.add_argument("--sheet-id", required=True,
                        help="Google Sheet ID (from the URL)")
    parser.add_argument("--data", required=True,
                        help="Path to content.json file")
    parser.add_argument("--worksheet", default=None,
                        help="Worksheet tab name (default: first sheet)")
    parser.add_argument("--config", default=None,
                        help="Path to config.json")

    args = parser.parse_args()
    push_to_sheets(
        sheet_id=args.sheet_id,
        data_path=args.data,
        worksheet_name=args.worksheet,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()
