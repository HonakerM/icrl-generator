# ICRL Image Generator

This project generates polished "thought of the day" images for the **International Consciousness Research Laboratories (ICRL)**.  
It uses **LiteLLM** to:

1. Turn a text thought into an *image prompt*
2. Generate an AI image
3. Blend the generated image with an overlay image

The script is exposed as a command-line tool using **Typer** and can be run locally or via Docker.

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
- Docker support with multi-stage builds for minimal image size

---

## Installation

### Local Installation

```bash
git clone https://github.com/HonakerM/icrl-generator.git
cd icrl-generator
pip install .
```

### Docker

Pull the pre-built image from GitHub Container Registry:

```bash
docker pull ghcr.io/your-username/icrl-generator:latest
```

Or build locally:

```bash
docker build -t icrl-generator .
```

---

## Usage

### Local CLI - Single Image Generation

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

### Local CLI - Batch Generation

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

### Docker - Single Image Generation

Linux/Mac:
```bash
docker run --rm \
  -v $(pwd)/overlay.png:/app/overlays/overlay.png:ro \
  -v $(pwd)/output:/app/output \
  -e OPENAI_API_KEY="sk-your-api-key-here" \
  ghcr.io/your-username/icrl-generator:latest \
  generate-image \
  "Never assume that what you see on a person's face is what lies in their heart." \
  /app/overlays/overlay.png \
  /app/output/result.png \
  --alpha 50 \
  --log-level INFO
```

Windows PowerShell:
```powershell
docker run --rm `
  -v ${PWD}/overlay.png:/app/overlays/overlay.png:ro `
  -v ${PWD}/output:/app/output `
  -e OPENAI_API_KEY="sk-your-api-key-here" `
  ghcr.io/your-username/icrl-generator:latest `
  generate-image `
  "Never assume that what you see on a person's face is what lies in their heart." `
  /app/overlays/overlay.png `
  /app/output/result.png `
  --alpha 50 `
  --log-level INFO
```

### Docker - Batch Generation

Linux/Mac:
```bash
docker run --rm \
  -v $(pwd)/thoughts.csv:/app/input/thoughts.csv:ro \
  -v $(pwd)/overlay.png:/app/overlays/overlay.png:ro \
  -v $(pwd)/output:/app/output \
  -e OPENAI_API_KEY="sk-your-api-key-here" \
  ghcr.io/your-username/icrl-generator:latest \
  generate-batch \
  /app/input/thoughts.csv \
  /app/overlays/overlay.png \
  /app/output \
  --alpha 50 \
  --log-level INFO
```

Windows PowerShell:
```powershell
docker run --rm `
  -v ${PWD}/thoughts.csv:/app/input/thoughts.csv:ro `
  -v ${PWD}/overlay.png:/app/overlays/overlay.png:ro `
  -v ${PWD}/output:/app/output `
  -e OPENAI_API_KEY="sk-your-api-key-here" `
  ghcr.io/your-username/icrl-generator:latest `
  generate-batch `
  /app/input/thoughts.csv `
  /app/overlays/overlay.png `
  /app/output `
  --alpha 50 `
  --log-level INFO
```

### Python Code

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

---

## Docker Volume Mounts

When using Docker, you need to mount directories and files:

| Mount | Purpose | Read/Write |
|-------|---------|-----------|
| `-v $(pwd)/overlay.png:/app/overlays/overlay.png:ro` | Input overlay image | Read-only |
| `-v $(pwd)/thoughts.csv:/app/input/thoughts.csv:ro` | Input CSV file for batch | Read-only |
| `-v $(pwd)/output:/app/output` | Output directory for generated images | Read-write |

**Before running Docker commands:**
1. Create the output directory: `mkdir -p output`
2. Place your `overlay.png` in the current directory
3. For batch processing, place your `thoughts.csv` in the current directory

---

## Requirements

* Python 3.10+
* LiteLLM API keys properly configured (`export OPENAI_API_KEY=...`)
* Pillow
* Typer
* tqdm (for batch processing progress bars)

---

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

---

## Development

### Building the Docker Image

```bash
docker build -t icrl-generator .
```

The Dockerfile uses multi-stage builds to create a minimal runtime image by:
1. Building dependencies in a builder stage with compilation tools
2. Copying only the runtime files to a slim final image
3. Excluding build tools to minimize image size

### CI/CD

This project uses GitHub Actions to automatically build and publish Docker images to GitHub Container Registry (GHCR) on:
- Pushes to `main` or `develop` branches
- Version tags (e.g., `v1.0.0`)
- Pull requests (build only, no push)

Images are published to: `ghcr.io/your-username/icrl-generator`