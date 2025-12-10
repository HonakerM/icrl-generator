import base64
from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated
from litellm import completion, image_generation
from PIL import Image
from io import BytesIO
from pathlib import Path
from logging import getLogger, _nameToLevel, basicConfig
from tqdm import tqdm
from typer import Typer, Option
import enum
import csv

# Typer App for easy CLI: https://typer.tiangolo.com/
APP = Typer()
# Generic logger for debugging
LOGGER = getLogger(__file__)

# Get raw prompt text. These prompts contain template strings like `{thought}` which
# are replaced during runtime
PROMPT_DIT = Path(__file__).parent / "prompts"
IMAGE_PROMPT_GEN_SYSTEM_PROMPT = (PROMPT_DIT / "image_gen_system.txt").read_text()
IMAGE_PROMPT_GEN_USER_PROMPT = (PROMPT_DIT / "image_gen_user.txt").read_text()


# Get default list of log levels
LogLevelEnum = enum.Enum("LogLevelEnum", {key: key for key in _nameToLevel})


@APP.command()
def generate_image(
    thought: str,
    overlay: Path,
    output: Path,
    image_prompt_output: Path | None = None,
    raw_image_output: Path | None = None,
    log_level: LogLevelEnum | None = LogLevelEnum.INFO,
    prompt_gen_model: str = "gpt-4o-mini",
    image_gen_model: str = "gpt-image-1-mini",
    alpha: Annotated[int, Option(min=0, max=100)] = 50,
):
    """Generate an image for the thought of the day for the International Consciousness Research Laboratories (ICRL) and blend
    it with an overlay image. The output image can be saved in any format supported by PIL: 
    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

    Args:
        thought (str): The thought to use for generation
        overlay (Path): The overlay image path to blend with the generated image
        output (Path): The output image path
        image_prompt_output (Path | None, optional): Optional debug path for storing the generated image prompt. Defaults to None.
        raw_image_output (Path | None, optional): Optional debug path for storing the raw image before blending. Defaults to None.
        log_level (LogLevelEnum, optional): Log level. Defaults to "INFO".
        prompt_gen_model (str, optional): LLM model for prompt generation. Defaults to "gpt-4o-mini".
        image_gen_model (str, optional): Image generation model. Defaults to "gpt-image-1-mini".
        alpha (int, optional): Blend alpha value (0-100), where 0 is transparent and 100 is opaque. Defaults to 50.
    """
    if log_level:
        basicConfig(level=log_level.value)

    # Parse the prompts and apply formatting
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
        model=prompt_gen_model,  # any LLM available through LiteLLM
        messages=prompts,
        temperature=0.9,
    )

    image_prompt = prompt_response.choices[0].message["content"]
    LOGGER.debug("Generated image prompt:\n%s\n", image_prompt)
    if image_prompt_output:
        image_prompt_output.write_text(image_prompt)

    LOGGER.info("Generating Image")
    img_result = image_generation(
        model=image_gen_model,  # Any image model supported by LiteLLM
        prompt=image_prompt,
        quality="low",
        size="1024x1024",
    )
    # Decode the base64-encoded image data
    img_result_bytes = base64.b64decode(img_result.data[0].b64_json.encode("utf-8"))
    img = Image.open(BytesIO(img_result_bytes)).convert("RGB")
    if raw_image_output:
        img.save(raw_image_output)

    # Blend the generated image with the overlay image
    LOGGER.info("Blending Image")
    overlay = Image.open(overlay.open("rb")).convert("RGB")
    overlay = overlay.resize(img.size)
    img = Image.blend(img, overlay, alpha / 100)

    img.save(output)
    LOGGER.info("Saved Output Image to %s", str(output))


@dataclass
class ThoughtData:
    """Data class for storing a thought and its associated publish date
    
    Attributes
        thought (str): The thought
        publish_date (date): The date this will be published"""
    thought: str
    publish_date: date


@APP.command()
def generate_batch(
    input: Path,
    overlay: Path,
    output_folder: Path,
    include_image_prompt: bool = False,
    include_raw_image: bool = False,
    log_level: LogLevelEnum = LogLevelEnum.INFO,
    prompt_gen_model: str = "gpt-4o-mini",
    image_gen_model: str = "gpt-image-1-mini",
    alpha: Annotated[int, Option(min=0, max=100)] = 50,
):
    """Generate a batch of images from a CSV file containing thoughts and publish dates. Each generated image is blended
    with the overlay image and saved to the output folder.

    Args:
        input (Path): Path to input CSV file with thoughts and publish dates
        overlay (Path): The overlay image path to blend with all generated images
        output_folder (Path): Folder to save generated images
        include_image_prompt (bool, optional): Save intermediate image prompts for debugging. Defaults to False.
        include_raw_image (bool, optional): Save raw images before blending for debugging. Defaults to False.
        log_level (LogLevelEnum, optional): Log level. Defaults to "INFO".
        prompt_gen_model (str, optional): LLM model for prompt generation. Defaults to "gpt-4o-mini".
        image_gen_model (str, optional): Image generation model. Defaults to "gpt-image-1-mini".
        alpha (int, optional): Blend alpha value (0-100), where 0 is fully generated image and 100 is fully overlay. Defaults to 50.
    """
    basicConfig(level=log_level.value)

    LOGGER.info("Gathering Thoughts")
    thoughts: list[ThoughtData] = []
    with input.open("r") as input_stream:
        csv_reader = csv.reader(input_stream)

        for idx, row in enumerate(csv_reader):
            # Skip header row
            if idx == 0:
                continue

            thought = ThoughtData(
                thought=row[1], publish_date=datetime.strptime(row[-2], "%Y-%m-%d").date()
            )
            thoughts.append(thought)
    # Sort thoughts chronologically by publish date
    thoughts.sort(key=lambda td: td.publish_date)

    LOGGER.info("Generating Images")
    output_folder.mkdir(parents=True, exist_ok=True)

    for thought in tqdm(thoughts):
        # Format the publish date for use in filenames
        publish_str = thought.publish_date.strftime("%Y_%m_%d")
        image_output = output_folder / f"{publish_str}.png"
        image_prompt_path = output_folder / f"{publish_str}_image_prompt.txt"
        raw_image_output = output_folder / f"{publish_str}_raw.png"

        generate_image(
            thought.thought,
            overlay=overlay,
            output=image_output,
            image_prompt_output=image_prompt_path if include_image_prompt else None,
            raw_image_output=raw_image_output if include_raw_image else None,
            log_level=None,
            prompt_gen_model=prompt_gen_model,
            image_gen_model=image_gen_model,
            alpha=alpha,
        )