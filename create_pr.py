import os
import subprocess
import argparse
from google import genai  # type: ignore
from dotenv import load_dotenv
import inquirer  # type: ignore

load_dotenv()

# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    print("Error: LLM_KEY environment variable not set.")
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
        print(f"Error getting git diff: {e}")
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
    response_title = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt_title])
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
        print("PR created successfully!")
        # Extract the PR URL from the output
        pr_url = subprocess.check_output("gh pr view --json url -q .url", shell=True).decode("utf-8").strip()
        print(f"PR URL: {pr_url}")
    else:
        print("Failed to create PR.")
        print(f"Error: {error.decode('utf-8')}")
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
            print("PR creation cancelled.")
            exit(0)
    else:
        # Get the base branch and the current branch from the arguments
        base_branch = args.base_branch
        current_branch = args.current_branch
        title = args.title if args.title else None

    if not base_branch or not current_branch:
        print("Error: Both base_branch and current_branch must be specified.")
        exit(1)

    # Get the git diff
    diff = get_git_diff(base_branch, current_branch)

    # Generate the title and description of the PR
    if title:
        description = generate_title_and_description(diff)[1]
    else:
        title, description = generate_title_and_description(diff)

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
        print(f"Error getting git branches: {e}")
        exit(1)


if __name__ == "__main__":
    main()
