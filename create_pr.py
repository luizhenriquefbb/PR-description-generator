import os
import subprocess
import argparse
from dotenv import load_dotenv
from google import genai  # type: ignore
import inquirer  # type: ignore
from google.genai import types  # type: ignore

load_dotenv(dotenv_path=".env")

def red_print(text: str) -> None:
    print(f"\033[91m{text}\033[0m")

def green_print(text: str) -> None:
    print(f"\033[92m{text}\033[0m")

def yellow_print(text: str) -> None:
    print(f"\033[93m{text}\033[0m")

def blue_print(text: str) -> None:
    print(f"\033[94m{text}\033[0m")

def magenta_print(text: str) -> None:
    print(f"\033[95m{text}\033[0m")

def cyan_print(text: str) -> None:
    print(f"\033[96m{text}\033[0m")

def white_print(text: str) -> None:
    print(f"\033[97m{text}\033[0m")

# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    red_print("Error: LLM_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=gemini_api_key)


def get_git_diff(base_branch: str, current_branch: str) -> str:
    """Gets the diff between two git branches.

    Args:
        base_branch: The base branch.
        current_branch: The current branch.

    Returns:
        The diff between the two branches.
    """
    try:
        diff = subprocess.check_output(["git", "diff", base_branch, current_branch]).decode("utf-8")
        return diff
    except subprocess.CalledProcessError as e:
        red_print(f"Error getting git diff: {e}")
        exit(1)


def generate_title_and_description(diff: str) -> tuple[str, str]:
    """Generates the title and description of the PR using the Gemini AI model.

    Args:
        diff: The diff between the two branches.
        gemini_api_key: The Gemini API key.

    Returns:
        A tuple containing the title and description of the PR.
    """

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

    return title, description


def create_pr(title: str, description: str, current_branch: str, base_branch: str) -> None:
    """Creates the PR using the gh command.

    Args:
        title: The title of the PR.
        description: The description of the PR.
        current_branch: The current branch.
        base_branch: The base branch.
    """
    # branches names may have "origin/" prefix, we must remove it
    current_branch = current_branch.replace("origin/", "")
    base_branch = base_branch.replace("origin/", "")

    description = description.replace("'", "'\\''")
    command = f"gh pr create --title '{title}' --body '{description}' --head {current_branch} --base {base_branch}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, error = process.communicate()

    # Check if the PR was created successfully
    if process.returncode == 0:
        green_print("PR created successfully!")
        # Extract the PR URL from the output
        pr_url = subprocess.check_output("gh pr view --json url -q .url", shell=True).decode("utf-8").strip()
        blue_print(f"PR URL: {pr_url}")
    else:
        red_print("Failed to create PR.")
        red_print(f"Error: {error.decode('utf-8')}")
        exit(1)


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Create a PR with automatically generated description and title.")
    parser.add_argument("--base_branch", required=False, help="The base branch.")
    parser.add_argument("--current_branch", required=False, help="The current branch.")
    parser.add_argument("--title", required=False, help="Optional title for the PR.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")

    # Parse the arguments
    args = parser.parse_args()

    if args.interactive:
        # Interactive mode
        questions = [
            inquirer.List("base_branch", message="Choose the base branch:", choices=get_git_branches()),
            inquirer.List("current_branch", message="Choose the current branch:", choices=get_git_branches()),
            inquirer.Text("title", message="Enter the title for the PR:"),
        ]
        answers = inquirer.prompt(questions)
        if answers:
            base_branch = answers["base_branch"]
            current_branch = answers["current_branch"]
            title = answers["title"]
        else:
            red_print("PR creation cancelled.")
            exit(0)
    else:
        # Get the base branch and the current branch from the arguments
        base_branch = args.base_branch
        current_branch = args.current_branch
        title = args.title if args.title else None

    if not base_branch or not current_branch:
        red_print("Error: Both base_branch and current_branch must be specified.")
        exit(1)

    # Get the git diff
    diff = get_git_diff(base_branch, current_branch)

    # Generate the title and description of the PR
    if title:
        description = generate_title_and_description(diff)[1]
    else:
        title, description = generate_title_and_description(diff)

    # clear terminal
    os.system("clear")

    # Display the title and description
    blue_print("Generated title:")
    print(title)
    print("\n" + "=" * 50 + "\n")
    blue_print("Generated description:")
    print(description)
    print("\n" + "=" * 50 + "\n")

    while True:
        # Ask the user if they want to edit the title or description
        questions = [
            inquirer.List(
                "action",
                message="What do you want to do?",
                choices=[
                    ("Create PR", "create"),
                    ("Edit title", "edit_title"),
                    ("Edit description", "edit_description"),
                    ("Cancel", "cancel"),
                ],
            )
        ]
        answers = inquirer.prompt(questions)

        if not answers:
            red_print("PR creation cancelled.")
            exit(0)

        action = answers["action"]

        if action == "create":
            break
        elif action == "edit_title":
            questions = [inquirer.Text("title", message="Enter the new title:")]
            answers = inquirer.prompt(questions)
            if answers:
                title = answers["title"]
        elif action == "edit_description":
            questions = [inquirer.Text("description", message="Enter the new description:")]
            answers = inquirer.prompt(questions)
            if answers:
                description = answers["description"]
            else:
                red_print("Description editing cancelled.")
        elif action == "cancel":
            red_print("PR creation cancelled.")
            exit(0)
        else:
            red_print("Title editing cancelled.")

    # Create the PR
    create_pr(title, description, current_branch, base_branch)


def get_git_branches():
    """Gets the list of remote git branches.

    Returns:
        A list of remote git branches.
    """
    try:
        branches = subprocess.check_output(["git", "branch", "-r"]).decode("utf-8").splitlines()
        branches = [branch.strip() for branch in branches]
        return branches
    except subprocess.CalledProcessError as e:
        red_print(f"Error getting git branches: {e}")
        exit(1)


if __name__ == "__main__":
    main()
