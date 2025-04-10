import subprocess

from utils.print_utils import green_print, red_print

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
        green_print(f"PR URL: {pr_url}")
    else:
        red_print("Failed to create PR.")
        red_print(f"Error: {error.decode('utf-8')}")
        exit(1)
