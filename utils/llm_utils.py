import os
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from dotenv import load_dotenv

from utils.print_utils import red_print

load_dotenv(dotenv_path=".env")

# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    print("Error: LLM_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=gemini_api_key)

def generate_title_and_description(diff: str) -> tuple[str, str]:
    """Generates the title and description of the PR using the Gemini AI model.

    Args:
        diff: The diff between the two branches.
        gemini_api_key: The Gemini API key.

    Returns:
        A tuple containing the title and description of the PR.
    """
    try:
        # Generate the description of the PR
        prompt_description = f"Describe the following code changes:\n{diff}"
        response_description = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt_description])
        description = response_description.text
    except Exception as e:
        red_print(f"Error generating description: {e}")
        exit(1)

    try:
        # Generate the title of the PR
        prompt_title = f"Generate a concise title for the following code changes:\n{diff}"
        response_title = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt_title],
            config=types.GenerateContentConfig(
                system_instruction="Your only output should be the title of the PR. Do not give any other information nor multiple choices."
            ),
        )
        title = response_title.text
    except Exception as e:
        red_print(f"Error generating title: {e}")
        exit(1)

    return title, description
