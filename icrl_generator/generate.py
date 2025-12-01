import base64
from litellm import completion, image_generation
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path
from logging import getLogger, INFO, _nameToLevel, basicConfig
from typer import Typer, Option
import enum

APP = Typer()
LOGGER = getLogger("LOG")

PROMPT_DIT = Path(__file__).parent / "prompts"
IMAGE_PROMPT_GEN_SYSTEM_PROMPT = (PROMPT_DIT / "image_gen_system.txt").read_text()
IMAGE_PROMPT_GEN_USER_PROMPT = (PROMPT_DIT / "image_gen_user.txt").read_text()

LogLevelEnum = enum.Enum('LogLevelEnum', {key:key for key in _nameToLevel})

def add_text_to_image(img: Image, text: str):
    draw = ImageDraw.Draw(img)

    relative_font_scale = 0.05
    padding_ratio = 0.02
    max_width_ratio = 0.45

    # Compute font size based on image height
    img_w, img_h = img.size
    font_size = int(img_h * relative_font_scale)
    font = ImageFont.load_default(font_size)

    # Max wrap width in pixels
    max_width_px = int(img_w * max_width_ratio)

    # ---- TEXT WRAPPING ----
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test_line = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width_px:
            current = test_line
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    # Measure total wrapped text block
    line_sizes = []  # store (w, h)
    max_line_width = 0
    total_height = 0

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_sizes.append((w, h))
        total_height += h
        if w > max_line_width:
            max_line_width = w

    # Padding
    pad = int(img_w * padding_ratio)

    # Top-right block origin (block width = max_line_width)
    x_block = img_w - max_line_width - pad
    y_block = pad

    # Draw each centered line
    offset_y = y_block
    for i, line in enumerate(lines):
        line_w, line_h = line_sizes[i]

        # center this line within the block
        x_line = x_block + (max_line_width - line_w) // 2

        draw.text((x_line, offset_y), line, font=font, fill="white")
        offset_y += line_h

@APP.command()
def generate_image(
    thought: str,
    output: Path,
    image_prompt_output: Path | None = None,
    raw_image_output: Path | None = None,
    log_level: LogLevelEnum = LogLevelEnum.INFO,
):
    """Generate a image for the thought of the day for the International Consciousness Research Laboratories (ICRL)."""
    basicConfig(level=log_level.value)

    system_prompt = IMAGE_PROMPT_GEN_SYSTEM_PROMPT
    LOGGER.debug("System Prompt:\n%s\n", system_prompt)
    user_prompt = IMAGE_PROMPT_GEN_USER_PROMPT.format(thought=thought)
    LOGGER.debug("User Prompt:\n%s\n", user_prompt)
    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    LOGGER.info("Generating Image Prompt")
    prompt_response = completion(
        model="gpt-4o-mini",  # any LLM available through LiteLLM
        messages=prompts,
        temperature=0.9,
    )

    image_prompt = prompt_response.choices[0].message["content"]
    LOGGER.debug("Generated Image Prompt")
    print("\nGenerated image prompt:\n%s\n", image_prompt)
    if image_prompt_output:
        image_prompt_output.write_text(image_prompt)

    LOGGER.info("Generating Image")
    img_result = image_generation(
        model="gpt-image-1-mini",  # Any image model supported by LiteLLM
        prompt=image_prompt,
        quality="low",
        size="1024x1024",
    )
    img_result_bytes = base64.b64decode(img_result.data[0].b64_json.encode("utf-8"))
    img = Image.open(BytesIO(img_result_bytes)).convert("RGB")
    if raw_image_output:
        img.save(raw_image_output)

    LOGGER.info("Updating Image with Text")
    add_text_to_image(img, thought)

    img.save(output)
    LOGGER.info("Saved Output Image to %s", str(output))
