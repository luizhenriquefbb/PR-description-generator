import os
import subprocess
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    print("Error: LLM_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=gemini_api_key)

def generate_title_and_description(diff: str, llm: str = "gemini") -> tuple[str, str]:
    """Generates the title and description of the PR using the specified LLM.

    Args:
        diff: The diff between the two branches.
        llm: The LLM to use ("gemini" or "copilot").

    Returns:
        A tuple containing the title and description of the PR.
    """
    if llm == "gemini":
        # Generate the description of the PR
        prompt_description = f"Describe the following code changes:\n{diff}"
        response_description = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt_description])
        description = response_description.text

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

    elif llm == "copilot":
        # Use the Copilot CLI to generate the title and description
        try:
            description = subprocess.check_output(
                ["gh", "copilot", "generate", "--input", f"Describe the following code changes:\n{diff}"],
                text=True,
            ).strip()
            title = subprocess.check_output(
                ["gh", "copilot", "generate", "--input", f"Generate a concise title for the following code changes:\n{diff}"],
                text=True,
            ).strip()
        except subprocess.CalledProcessError as e:
            print(f"Error using Copilot CLI: {e}")
            exit(1)
    else:
        raise ValueError(f"Unsupported LLM: {llm}")

    return title, description
