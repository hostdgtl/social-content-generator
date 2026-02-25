# Social Content Generator

A Claude Code skill that creates publish-ready organic social media content for any brand. Writes copy in the client's brand voice, generates images via NanoBanana (Gemini 2.5 Flash Image API), and pushes both to a Google Sheet for scheduling.

## What It Does

1. **Loads a brand voice** — Pulls the client's stored voice profile so every post sounds on-brand
2. **Plans a content calendar** — Selects content pillars, balances sell vs. connect, maps a campaign arc
3. **Writes captions** — Hook-first, phone-formatted, platform-aware copy with CTAs and hashtags
4. **Generates images** — AI-generated social graphics via Gemini 2.5 Flash Image (NanoBanana)
5. **Pushes to Google Sheets** — Populates a scheduling sheet with copy, image links, and metadata

## Requirements

- [Claude Code](https://claude.ai/claude-code) (this is a Claude Code skill)
- Python 3.8+
- Google AI API key (for NanoBanana image generation)
- Google service account JSON (for Sheets API)

## Setup

```bash
bash scripts/setup.sh
```

This installs `google-genai`, `gspread`, `Pillow`, and `google-auth`. Then copy the config:

```bash
cp assets/config.example.json config.json
```

Fill in:
- `google_ai_api_key` — Get one at [Google AI Studio](https://aistudio.google.com/apikey)
- `google_service_account_path` — Path to your service account JSON ([create one here](https://console.cloud.google.com/iam-admin/serviceaccounts))
- `default_sheet_id` — The ID from your Google Sheet URL

Share your target Google Sheet with the service account email address.

## Usage

### Inside Claude Code (recommended)

Trigger with natural language:
- "Draft social content for [client]"
- "Generate a post for Instagram"
- "Create a content calendar for next week"

Or use the slash command: `/social-content`

### Scripts (standalone)

#### Generate an Image

```bash
python scripts/generate_image.py \
  --prompt "Flat lay of handcrafted soaps on linen, soft morning light, minimal" \
  --aspect-ratio "1:1" \
  --output "outputs/post-01.png"
```

#### Push to Google Sheets

```bash
python scripts/push_to_sheets.py \
  --sheet-id "1abc123..." \
  --data "outputs/content.json"
```

### Script Arguments

#### generate_image.py

| Argument | Required | Description |
|----------|----------|-------------|
| `--prompt` | Yes | Image generation prompt |
| `--aspect-ratio` | No | Aspect ratio (1:1, 4:5, 9:16, 16:9, etc. Default: 1:1) |
| `--output` | No | Output file path (default: outputs/generated.png) |
| `--api-key` | No | Google AI API key (or set GOOGLE_API_KEY env var) |
| `--config` | No | Path to config.json |

#### push_to_sheets.py

| Argument | Required | Description |
|----------|----------|-------------|
| `--sheet-id` | Yes | Google Sheet ID (from the URL) |
| `--data` | Yes | Path to content.json file |
| `--worksheet` | No | Worksheet tab name (default: first sheet) |
| `--config` | No | Path to config.json |

## Supported Platforms & Dimensions

| Platform | Format | Aspect Ratio |
|----------|--------|--------------|
| Instagram feed (square) | 1080x1080 | 1:1 |
| Instagram feed (portrait) | 1080x1350 | 4:5 |
| Instagram Story / Reel | 1080x1920 | 9:16 |
| Facebook feed | 1200x630 | 16:9 |
| LinkedIn feed | 1200x627 | 16:9 |
| X post | 1600x900 | 16:9 |

## Content Output Format

Each post is saved to `outputs/content.json`:

```json
{
  "post_number": 1,
  "date": "2026-03-03",
  "platform": "Instagram",
  "pillar": "Product Spotlight",
  "format": "Static",
  "caption": "Full caption text...",
  "cta": "Discover more via the link in bio",
  "hashtags": "#BrandName #Hashtag",
  "image_prompt": "Full NanoBanana prompt...",
  "image_file": "outputs/post-01.png",
  "status": "Ready for Review"
}
```

## How It Works

- Requires the [brand-voice](https://github.com/hostdgtl/brand-voice) skill loaded first for voice consistency
- Content pillars are balanced: no same pillar twice in a row, 30-40% sell / 60-70% connect
- Copy is written hook-first, one idea per post, phone-formatted
- Images are generated with brand-specific prompts (colours, textures, mood from client profile)
- Google Sheet columns: Date, Platform, Pillar, Format, Caption, CTA, Hashtags, Image File, Image Prompt, Status

## License

MIT