import subprocess

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
