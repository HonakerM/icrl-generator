# ICRL Generator

This project generates polished “thought of the day” images for the **International Consciousness Research Laboratories (ICRL)**.  
It uses **LiteLLM** to:

1. Turn a text thought into an *image prompt*
2. Generate an AI image
3. Add fully-wrapped, centered text to the top-right of the final image

The script is exposed as a command-line tool using **Typer**.

---

## Features

- Generate text-to-image prompts using LiteLLM (`completion`)
- Produce images using LiteLLM (`image_generation`)
- Automatically wrap overlay text with pixel-accurate measurement
- Save:
  - the final processed image
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

### CLI

After installation, you can run the following command to generate an image.

Linux:
```bash
export OPENAI_API_KEY = "<openai-api-key>"
icrl-gen \
    --image-prompt-output image-prompt.txt \
    --raw-image-output raw_image.png \
    --log-level DEBUG \
    "Never assume that what you see on a person’s face is what lies in their heart. A frown is not always intended for you, a smile is not always indicative of friendliness or happiness" \
    image.png
```
Windows:
```powershell
$env:OPENAI_API_KEY = "<openai-api-key>"   
icrl-gen `
    --image-prompt-output image-prompt.txt `
    --raw-image-output raw_image.png `
    --log-level DEBUG `
    "Never assume that what you see on a person’s face is what lies in their heart. A frown is not always intended for you, a smile is not always indicative of friendliness or happiness" `
    image.png
```


To view the options and their descriptions you can run:

```bash
icrl-gen --help
```

to see all available commands.


### Code

If you want to call it from Python directly:

```python
from pathlib import Path
from icrl_generator import generate_image

generate_image(
    thought="Reality responds to our expectations.",
    output=Path("out.png"),
    image_prompt_output=Path("prompt.txt"),
    raw_image_output=Path("raw.png")
)
```

### Results

![./image.png](./image.png)

## Requirements

* Python 3.10+
* LiteLLM API keys properly configured (`export OPENAI_API_KEY=...`)
* Pillow
* Typer
