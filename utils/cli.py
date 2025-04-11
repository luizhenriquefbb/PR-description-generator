import argparse
from typing import Optional, TypedDict, cast


class Args(TypedDict):
    base_branch: Optional[str]
    current_branch: Optional[str]
    title: Optional[str]
    interactive: bool
    repo_path: str


def create_parser() -> Args:
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Create a PR with automatically generated description and title.")
    parser.add_argument("--base_branch", required=False, help="The base branch.")
    parser.add_argument("--current_branch", required=False, help="The current branch.")
    parser.add_argument("--title", required=False, help="Optional title for the PR.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("--repo-path", help="Path to the target Git repository", required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Convert Namespace to a dictionary for type safety
    return cast(Args, args)
