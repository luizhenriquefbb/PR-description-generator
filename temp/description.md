🎫 Jira Ticket
[No specific Jira ticket provided, so leaving as placeholder]

📝 Summary
This PR refactors the project to leverage `fastmcp` for tool creation, streamlining the process of generating PR descriptions. The previous custom scripts and utility functions (`create_pr.py`, `utils/`) have been removed in favor of a `fastmcp`-based tool (`src/tools.py`). This change simplifies the project structure and moves towards a more modular, tool-driven approach.

⚠️ Important Changes
- **Migration to `fastmcp`**: The core logic for generating PR descriptions has been rewritten using the `fastmcp` framework.
- **Removed custom scripts and utilities**: `create_pr.py`, `utils/cli.py`, `utils/git_utils.py`, `utils/llm_utils.py`, and `utils/pr_utils.py`, `utils/print_utils.py` have been deleted.
- **Updated `requirements.txt`**: Dependencies are now minimal, focusing on `fastmcp` and `mypy`.
- **Removed Dockerfile and related files**: The project no longer supports Docker-based execution in this iteration.
- **Renamed `assets/readme-logo.png` to `readme_assets/readme-logo.png`**: Consistent naming for assets.
- **New `.gemini/settings.json`**: Configures `my-git-utils` for `fastmcp`.
- **Updated `README.md`**: Reflects the new setup and usage instructions for the `fastmcp` based tools and Gemini CLI.

🔗 Related PRs (Optional)
[No related PRs mentioned]

🧪 How to Test
1. Ensure `fastmcp` is installed and configured.
2. Run the `generate_description` tool using the new `fastmcp` setup with `origin/main` as `branch_base` and `as-mcp` as `current_branch`.
   Example command: `python src/tools.py generate_description --branch_base origin/main --current_branch as-mcp`
3. Verify that a PR description is generated correctly based on the changes in this branch and saved to `temp/description.md`.

🎨 Figma Designs (If Needed)
[No Figma designs associated with this PR]