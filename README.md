# ICRL Image Generator

This project generates "thought of the day" images for the **International Consciousness Research Laboratories (ICRL)**.  
It uses **LiteLLM** to:

1. Turn a text thought into an *image prompt*
2. Generate an AI image
3. Blend the generated image with an overlay image

The script is exposed as a command-line tool using **Typer**.

---

## Features

- Generate text-to-image prompts using LiteLLM (`completion`)
- Produce images using LiteLLM (`image_generation`)
- Blend generated images with overlay images using configurable alpha values
- Batch process multiple thoughts from CSV files
- Save:
  - the final blended image
  - the raw generated image (optional)
  - the generated image prompt (optional)
- Easy CLI interface

---

## Installation

```bash
git clone https://github.com/HonakerM/icrl-generator.git
cd icrl-generator
pip install .
```

## Usage

### CLI - Single Image Generation

After installation, you can run the following command to generate an image.

Linux:
```bash
export OPENAI_API_KEY="<openai-api-key>"
python -m icrl_generator generate-image \
    "Never assume that what you see on a person's face is what lies in their heart." \
    overlay.png \
    output.png \
    --image-prompt-output image-prompt.txt \
    --raw-image-output raw_image.png \
    --log-level DEBUG \
    --alpha 50
```

Windows:
```powershell
$env:OPENAI_API_KEY = "<openai-api-key>"   
python -m icrl_generator generate-image `
    "Never assume that what you see on a person's face is what lies in their heart." `
    overlay.png `
    output.png `
    --image-prompt-output image-prompt.txt `
    --raw-image-output raw_image.png `
    --log-level DEBUG `
    --alpha 50
```

To view all options and their descriptions:

```bash
python -m icrl_generator generate-image --help
```

### CLI - Batch Generation

To generate multiple images from a CSV file:

Linux:
```bash
export OPENAI_API_KEY="<openai-api-key>"
python -m icrl_generator generate-batch \
    thoughts.csv \
    overlay.png \
    output_folder \
    --include-image-prompt \
    --include-raw-image \
    --log-level INFO \
    --alpha 50
```

Windows:
```powershell
$env:OPENAI_API_KEY = "<openai-api-key>"
python -m icrl_generator generate-batch `
    thoughts.csv `
    overlay.png `
    output_folder `
    --include-image-prompt `
    --include-raw-image `
    --log-level INFO `
    --alpha 50
```

The CSV file should have thoughts in column 2 (index 1) and publish dates in the second-to-last column in `YYYY-MM-DD` format.

To view all options:

```bash
python -m icrl_generator generate-batch --help
```

### Code

If you want to call it from Python directly:

```python
from pathlib import Path
from icrl_generator import generate_image

generate_image(
    thought="Reality responds to our expectations.",
    overlay=Path("overlay.png"),
    output=Path("out.png"),
    image_prompt_output=Path("prompt.txt"),
    raw_image_output=Path("raw.png"),
    alpha=50
)
```

### Alpha Blending

The `--alpha` parameter controls the blend between the generated image and the overlay:
- `0`: Fully generated image (no overlay)
- `50`: Equal blend (default)
- `100`: Fully overlay image (no generated image visible)

### Results

![./image.png](./image.png)

## Requirements

* Python 3.10+
* LiteLLM API keys properly configured (`export OPENAI_API_KEY=...`)
* Pillow
* Typer
* tqdm (for batch processing progress bars)

## Command Reference

### `generate-image`

Generate a single image with overlay blending.

**Arguments:**
- `THOUGHT`: The thought text to generate an image for
- `OVERLAY`: Path to overlay image to blend with generated image
- `OUTPUT`: Path to save the final blended image

**Options:**
- `--image-prompt-output PATH`: Save the generated image prompt
- `--raw-image-output PATH`: Save the raw image before blending
- `--log-level`: Set logging level (default: INFO)
- `--prompt-gen-model TEXT`: LLM model for prompt generation (default: gpt-4o-mini)
- `--image-gen-model TEXT`: Image generation model (default: gpt-image-1-mini)
- `--alpha INTEGER`: Blend alpha value 0-100 (default: 50)

### `generate-batch`

Generate multiple images from a CSV file.

**Arguments:**
- `INPUT`: Path to CSV file with thoughts and publish dates
- `OVERLAY`: Path to overlay image to blend with all generated images
- `OUTPUT_FOLDER`: Folder to save generated images

**Options:**
- `--include-image-prompt/--no-include-image-prompt`: Save image prompts (default: no)
- `--include-raw-image/--no-include-raw-image`: Save raw images (default: no)
- `--log-level`: Set logging level (default: INFO)
- `--prompt-gen-model TEXT`: LLM model for prompt generation (default: gpt-4o-mini)
- `--image-gen-model TEXT`: Image generation model (default: gpt-image-1-mini)
- `--alpha INTEGER`: Blend alpha value 0-100 (default: 50)