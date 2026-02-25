---
name: social-content-generator
description: Agent that creates publish-ready organic social media content for any brand. Writes copy in the client's brand voice, generates images via NanoBanana (Gemini 2.5 Flash Image API), and pushes both to a Google Sheet for scheduling. Runs in Claude Code with executable scripts. Use this agent whenever the user asks to draft social posts, create a content calendar, generate social graphics, or produce any social media content. Triggers include "draft social", "/draft-social", "social content", "content calendar", "generate a post", or any social media content request. Loads the brand-voice skill first, then executes the pipeline.
---

# Social Content Generator — Agent

Produces publish-ready organic social media content: copy + AI-generated image + Google Sheet output.

## Architecture

```
social-content-generator/
├── SKILL.md                          ← You are here (orchestration)
├── scripts/
│   ├── setup.sh                      ← One-time dependency install
│   ├── generate_image.py             ← NanoBanana (Gemini) image generation
│   └── push_to_sheets.py            ← Google Sheets API push
└── assets/
    └── config.example.json           ← API key + sheet config template
```

## Prerequisites

Before first run, execute `scripts/setup.sh` to install dependencies. The user needs:

1. **Google AI API key** — For NanoBanana (Gemini 2.5 Flash Image). Get one at https://aistudio.google.com/apikey
2. **Google Sheets API credentials** — A service account JSON key with Sheets API enabled. The target sheet must be shared with the service account email.
3. **Config file** — Copy `assets/config.example.json` to `config.json` in the project root and fill in the values.

Run setup:
```bash
bash scripts/setup.sh
```

---

## Workflow

Execute these steps in order. Each step has a clear input and output.

### Step 1 — Load Client Voice

1. Load the brand-voice skill.
2. If no client profile is loaded, ask: *"Which company are we creating content for?"*
3. Load the client's `.md` profile from `brand-voice/references/clients/`.
4. Confirm the loaded voice and ask what we're working on.

**Output:** Client brand voice in context.

### Step 2 — Clarify the Brief

Gather what's needed. Skip anything covered by a loaded creative brief.

| Detail | Default |
|--------|---------|
| Campaign / theme | *(required)* |
| Platforms | Instagram + Facebook |
| Number of posts | *(required)* |
| Products / services to feature | *(ask)* |
| Offers / promotions | None |
| Tone adjustments | Standard brand voice |
| Visual style | Pull from client profile or ask |
| Image format | Lifestyle photography |

**Output:** Confirmed brief.

### Step 3 — Plan Content

Select 4-5 content pillars that fit the client:

| Pillar | Purpose |
|--------|---------|
| **Product / Service Spotlight** | Feature an offering. Benefit-led. |
| **Behind the Scenes** | People, process, place. Humanises. |
| **Education & Expertise** | Knowledge the audience values. |
| **Lifestyle & Values** | Brand-audience identity alignment. |
| **Social Proof & Community** | Customer stories, UGC, milestones. |
| **Seasonal & Cultural** | Timely moments and events. |

Build the calendar overview:

```
| # | Date | Day | Platform | Pillar | Format | Caption Preview | Image Concept |
```

**Balance:** No same pillar 2x in a row. 30-40% sell / 60-70% connect. Strongest content Mon-Wed.

**Campaign arc (if applicable):** Warm-up → Launch → Sustain.

**Output:** Approved content calendar.

### Step 4 — Write Copy

For each post, write the caption following these rules:

- **Hook first.** Opening line stops the scroll.
- **One idea per post.**
- **Short paragraphs.** 1-3 sentences. Phone-formatted.
- **Soft CTAs.** Match client's vocabulary rules.
- **Platform-aware length:** IG 150-300 words, FB longer, LinkedIn 150-300, TikTok 1-2 sentences, X 280 chars.
- **Hashtags (IG):** 5-15, branded + niche + broad, CamelCase.
- **Emojis:** Per client profile policy.

**Output per post:**

```
POST [n]
DATE:
PLATFORM:
PILLAR:
FORMAT:

CAPTION:
[copy]

CTA:
HASHTAGS:
```

Present all copy to the user for approval before generating images.

### Step 5 — Generate Images

Once copy is approved, generate an image for each post using the `generate_image.py` script.

**5a. Build the prompt.**

For each post, construct a NanoBanana prompt with these elements:

| Element | Source |
|---------|--------|
| **Scene** | What is in the image — derived from the caption and product |
| **Style / mood** | Photography style, lighting, colour temperature — from client profile or brief |
| **Brand elements** | Colours, textures, materials that reflect the brand — from client profile |
| **Composition** | Framing, angle, negative space — match the platform format |
| **Technical** | Aspect ratio from platform dimensions table below |

**Platform dimensions:**

| Platform | Format | Aspect Ratio |
|----------|--------|--------------|
| Instagram feed (square) | 1080×1080 | 1:1 |
| Instagram feed (portrait) | 1080×1350 | 4:5 |
| Instagram Story / Reel | 1080×1920 | 9:16 |
| Facebook feed | 1200×630 | 16:9 |
| LinkedIn feed | 1200×627 | 16:9 |
| X post | 1600×900 | 16:9 |

**5b. Run the script.**

```bash
python scripts/generate_image.py \
  --prompt "Your detailed NanoBanana prompt here" \
  --aspect-ratio "1:1" \
  --output "outputs/post-01.png"
```

The script calls the Gemini 2.5 Flash Image API and saves the image locally.

**5c. Review the output.**

Check each image for:
- Brand consistency (matches client visual identity)
- Quality (sharp, professional, no obvious AI artifacts)
- Caption alignment (visual and copy tell the same story)
- Platform fit (correct dimensions)

If it misses, refine the prompt and regenerate. Common fixes:
- Too generic → add specific brand details from client profile
- Wrong mood → adjust lighting/colour descriptors
- Cluttered → add "minimal composition, clean negative space"
- AI artifacts → add "photorealistic, professional product photography"

**5d. Text overlay (if needed).**

NanoBanana supports text rendering. For promo posts needing text on image:
- Keep text minimal (headline + one line max)
- Specify exact text in the prompt
- Include font style guidance
- Ensure contrast

**Output:** Generated `.png` files in `outputs/` directory.

### Step 6 — Push to Google Sheet

Once copy and images are approved, push everything to the scheduling sheet.

```bash
python scripts/push_to_sheets.py \
  --sheet-id "your-google-sheet-id" \
  --data "outputs/content.json"
```

The script reads the structured content JSON and pushes to the sheet with this column structure:

```
| Date | Platform | Pillar | Format | Caption | CTA | Hashtags | Image File | Image Prompt | Status |
```

**Image handling:** The script uploads the generated image to Google Drive and inserts a shareable link in the sheet. If Drive upload isn't configured, it inserts the local file path.

**Output:** Populated Google Sheet ready for scheduling.

---

## Post Output Format

The full output per post (saved to `outputs/content.json`):

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

---

## Refine Mode

When reviewing existing posts:

1. Load client brand voice.
2. Assess caption against voice + quality checklist.
3. Assess image against brand visual identity.
4. Rewrite and/or regenerate with reasoning.

---

## Quality Checklist

Every post must pass before delivery:

1. **Brand voice** — Sounds like the loaded client?
2. **Hook** — Would you stop scrolling?
3. **Single message** — One idea per post?
4. **Calendar balance** — Pillars varied? Sell/connect ratio healthy?
5. **CTA tone** — Invitation, not demand?
6. **Platform fit** — Length, format, tone right for the channel?
7. **Image quality** — Professional and on-brand?
8. **Image-copy alignment** — Visual and caption tell the same story?
9. **Client checklist** — Passes the client's own quality checks?
