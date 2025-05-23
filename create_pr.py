import os
from dotenv import load_dotenv
from google import genai
import inquirer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from utils.llm_utils import generate_title_and_description
from utils.print_utils import (
    red_print,
    blue_print,
)
from utils.cli import create_parser
import glob
from utils.git_utils import get_git_branches, get_git_diff

load_dotenv(dotenv_path=".env")


# Get the Gemini API key from the environment variables
gemini_api_key = os.getenv("LLM_KEY")
if not gemini_api_key:
    red_print("Error: LLM_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=gemini_api_key)


def main():
    args = create_parser()

    repo_path = args.git_repo or "/git_repo"

    # make sure the repo path is valid
    if not os.path.exists(repo_path):
        red_print(f"Error: The specified path '{repo_path}' does not exist.")
        exit(1)
    if not os.path.isdir(repo_path):
        red_print(f"Error: The specified path '{repo_path}' is not a directory.")
        exit(1)
    if not os.path.exists(os.path.join(repo_path, ".git")):
        red_print(f"Error: The specified path '{repo_path}' is not a git repository.")
        exit(1)

    # os.chdir(repo_path)

    if args.interactive:
        # Get the list of branches
        branches = get_git_branches(repo_path)

        # Create a fuzzy completer for branch names
        branch_completer = WordCompleter(
            branches,
            ignore_case=True,
            match_middle=True,
        )

        # Prompt for base branch
        base_branch = prompt("Choose the base branch: ", completer=branch_completer)

        # Prompt for current branch
        current_branch = prompt("Choose the current branch: ", completer=branch_completer)

        # Prompt for PR title
        title = prompt("Enter the title for the PR: ")

    else:
        # Get the base branch and the current branch from the arguments
        base_branch = args.base_branch
        current_branch = args.current_branch
        title = args.title if args.title else None

    if not base_branch or not current_branch:
        red_print("Error: Both base_branch and current_branch must be specified.")
        exit(1)

    # Get the git diff
    diff = get_git_diff(base_branch, current_branch, repo_path)

    # Load PR description templates from the templates folder
    template_dir = "templates"
    templates = []
    for template_file in glob.glob(os.path.join(template_dir, "*.md")):
        with open(template_file, "r") as f:
            templates.append(f.read())

    # Generate the title and description of the PR
    if title:
        description = generate_title_and_description(diff, templates=templates)[1]
    else:
        try:
            title, description = generate_title_and_description(diff, templates=templates)
        except Exception as e:
            red_print(f"Error generating title and description: {e}")
            exit(1)

    # clear terminal
    # os.system("cls" if os.name == "nt" else "clear")

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
            questions = [inquirer.Editor("description", message="Edit the description:", default=description)]
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
    # create_pr(title, description, current_branch, base_branch)
    blue_print("Creating PR...")


if __name__ == "__main__":
    main()
