import subprocess

from utils.print_utils import red_print


def get_git_diff(base_branch: str, current_branch: str, repo_path: str = ".") -> str:
    """Gets the diff between two git branches.

    Args:
        base_branch: The base branch.
        current_branch: The current branch.

    Returns:
        The diff between the two branches.
    """
    try:
        diff = subprocess.check_output(["git", "-C", repo_path, "diff", base_branch, current_branch]).decode("utf-8")
        return diff
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        exit(1)


def get_git_branches(repo_path: str = "."):
    """Gets the list of remote git branches.

    Returns:
        A list of remote git branches.
    """
    try:
        branches = subprocess.check_output(["git", "-C", repo_path, "branch", "-r"]).decode("utf-8").splitlines()
        branches = [branch.strip() for branch in branches]
        return branches
    except subprocess.CalledProcessError as e:
        print(f"Error getting git branches: {e}")
        exit(1)


def get_diff_from_pr(pr_id: str, repo_path: str = ".") -> str:
    """Gets the diff from the PR using the gh command.

    Args:
        pr_id: The ID of the PR.
        repo_path: The path to the repository.

    Returns:
        The diff of the PR.
    """
    command = f"gh pr view {pr_id} --json files --jq '.files[].path' | xargs git diff {pr_id} --"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repo_path)
    diff, error = process.communicate()

    # Check if the diff was retrieved successfully
    if process.returncode == 0:
        return diff.decode("utf-8")
    else:
        red_print("Failed to get diff from PR.")
        red_print(f"Error: {error.decode('utf-8')}")
        exit(1)
