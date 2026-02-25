#!/usr/bin/env python3
"""
Social Content Generator — NanoBanana Image Generation
Uses Google Gemini 2.5 Flash Image API to generate social media images.

Usage:
    python scripts/generate_image.py \
        --prompt "A flat lay of handcrafted soaps on linen, soft morning light, minimal" \
        --aspect-ratio "1:1" \
        --output "outputs/post-01.png"

    # With config file (default: config.json in agent root)
    python scripts/generate_image.py \
        --prompt "..." \
        --config "/path/to/config.json"

    # With inline API key
    python scripts/generate_image.py \
        --prompt "..." \
        --api-key "your-google-api-key"
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_config(config_path=None):
    """Load config from file or environment."""
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)

    # Try default location (agent root / config.json)
    script_dir = Path(__file__).parent
    default_config = script_dir.parent / "config.json"
    if default_config.exists():
        with open(default_config) as f:
            return json.load(f)

    return {}


def generate_image(prompt, aspect_ratio="1:1", output_path="output.png",
                   api_key=None, config_path=None):
    """Generate an image using Gemini 2.5 Flash Image (NanoBanana)."""

    # Resolve API key
    config = load_config(config_path)
    api_key = (
        api_key
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or config.get("google_ai_api_key")
    )

    if not api_key:
        print("ERROR: No API key found.", file=sys.stderr)
        print("Provide via --api-key, GOOGLE_API_KEY env var, or config.json", file=sys.stderr)
        sys.exit(1)

    # Validate aspect ratio
    valid_ratios = [
        "1:1", "3:2", "2:3", "3:4", "4:3",
        "4:5", "5:4", "9:16", "16:9", "21:9"
    ]
    if aspect_ratio not in valid_ratios:
        print(f"WARNING: '{aspect_ratio}' not in supported ratios {valid_ratios}", file=sys.stderr)
        print(f"Defaulting to 1:1", file=sys.stderr)
        aspect_ratio = "1:1"

    # Import and configure
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    print(f"Generating image...")
    print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Output: {output_path}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )

        # Extract and save image
        image_saved = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

                # Save image bytes
                image_data = part.inline_data.data
                with open(output_path, "wb") as f:
                    f.write(image_data)

                image_saved = True
                print(f"  ✓ Image saved to {output_path}")

                # Report file size
                size_kb = os.path.getsize(output_path) / 1024
                print(f"  ✓ Size: {size_kb:.0f} KB")
                break

        if not image_saved:
            # Check for text response (model may have returned text instead)
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"  ⚠ Model returned text instead of image:", file=sys.stderr)
                    print(f"  {part.text}", file=sys.stderr)

            print("ERROR: No image data in response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Image generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate social media images via NanoBanana (Gemini 2.5 Flash Image)"
    )
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--aspect-ratio", default="1:1",
                        help="Aspect ratio (1:1, 4:5, 9:16, 16:9, etc.)")
    parser.add_argument("--output", default="outputs/generated.png",
                        help="Output file path")
    parser.add_argument("--api-key", default=None,
                        help="Google AI API key (or set GOOGLE_API_KEY env var)")
    parser.add_argument("--config", default=None,
                        help="Path to config.json")

    args = parser.parse_args()
    generate_image(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        output_path=args.output,
        api_key=args.api_key,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()
