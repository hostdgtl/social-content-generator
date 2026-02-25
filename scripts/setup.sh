#!/bin/bash
# Social Content Generator — Dependency Setup
# Run once before first use: bash scripts/setup.sh

set -e

echo "=== Social Content Generator Setup ==="
echo ""

# Python dependencies
echo "[1/3] Installing Python packages..."
pip install google-genai Pillow gspread google-auth google-auth-oauthlib --quiet

# Verify imports
echo "[2/3] Verifying installations..."
python3 -c "
from google import genai
import gspread
from PIL import Image
print('  ✓ google-genai')
print('  ✓ gspread')
print('  ✓ Pillow')
"

# Check for config
echo "[3/3] Checking configuration..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_PATH="$AGENT_DIR/config.json"
EXAMPLE_PATH="$AGENT_DIR/assets/config.example.json"

if [ ! -f "$CONFIG_PATH" ]; then
    echo ""
    echo "  ⚠ No config.json found."
    echo "  Copy the example and fill in your keys:"
    echo ""
    echo "    cp $EXAMPLE_PATH $CONFIG_PATH"
    echo ""
    echo "  You'll need:"
    echo "    1. Google AI API key (for NanoBanana image gen)"
    echo "       → Get one at: https://aistudio.google.com/apikey"
    echo ""
    echo "    2. Google service account JSON (for Sheets API)"
    echo "       → Create at: https://console.cloud.google.com/iam-admin/serviceaccounts"
    echo "       → Enable Google Sheets API & Google Drive API"
    echo "       → Share your target sheet with the service account email"
    echo ""
else
    echo "  ✓ config.json found"
fi

echo ""
echo "=== Setup complete ==="
