import argparse

def create_parser():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Create a PR with automatically generated description and title.")
    parser.add_argument("--base_branch", required=False, help="The base branch.")
    parser.add_argument("--current_branch", required=False, help="The current branch.")
    parser.add_argument("--title", required=False, help="Optional title for the PR.")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("--llm", choices=["gemini", "copilot"], default="copilot", help="Choose the LLM to use (gemini or copilot).")
    return parser
