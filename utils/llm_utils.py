import os
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from dotenv import load_dotenv
from typing import List, Optional
from utils.print_utils import blue_print, red_print

load_dotenv(dotenv_path=".env")

# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    print("Error: LLM_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=gemini_api_key)

model_agent = "gemini-2.0-flash"  # The model agent to use for generating the title and description


def generate_title_and_description(diff: str, templates: List[str] = None) -> tuple[str, str]:
    """Generates the title and description of the PR using the Gemini AI model.

    Args:
        diff: The diff between the two branches.
        templates: Optional list of templates to guide the description generation.

    Returns:
        A tuple containing the title and description of the PR.
    """
    title = generate_title(diff)
    description = generate_description(diff, templates)

    return title, description


def generate_description(diff: str, templates: Optional[List[str]] = None) -> str:
    """Generates the description of the PR using the Gemini AI model."""

    prompt_description = f"Generate a detailed description of the following code changes:\n{diff}"
    description_output = (
        "Your only output should be the description of the PR. Do not give any other information nor multiple choices."
    )
    if templates:
        blue_print(f"Using {len(templates)} templates to generate the description of the PR.")
        template_text = [f"{template}" for template in templates if template.strip()]

        try:
            response_description = client.models.generate_content(
                model=model_agent,
                contents=[prompt_description],
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Follow the templates below to generate the description of the PR:\n"
                        + "\n--------\n".join(template_text)
                        + "\n\nMake sure to use the template as a guide and not as a strict rule. "
                        + "You can modify it to fit the context of the PR. "
                        + description_output
                    )
                ),
            )
            return response_description.text
        except Exception as e:
            red_print(f"Error generating description: {e}")
            exit(1)

    else:
        try:
            response_description = client.models.generate_content(
                model=model_agent,
                contents=[prompt_description],
                config=types.GenerateContentConfig(system_instruction=description_output),
            )
            return response_description.text
        except Exception as e:
            red_print(f"Error generating description: {e}")
            exit(1)


def generate_title(diff: str) -> str:
    try:
        # Generate the description of the PR
        prompt_description = f"Describe the following code changes:\n{diff}"
        response_description = client.models.generate_content(
            model=model_agent,
            contents=[prompt_description],
            config=types.GenerateContentConfig(
                system_instruction="Your only output should be the title of the PR. Do not give any other information nor multiple choices."
            ),
        )
        return response_description.text
    except Exception as e:
        red_print(f"Error generating title: {e}")
        exit(1)
