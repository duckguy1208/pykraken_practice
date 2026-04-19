# Agent Contribution Guide

Welcome to the PyKraken Practice project.

## Critical Technical Findings
- **PyKraken 0.4.0 Quirks:** Window creation with `scaled=True` is recommended for high-DPI displays. Manual physics fallbacks are implemented as core library physics were unstable or missing in this version.
- **Wither's Wake Core Loop:** Essence decay is the primary mechanic. Essence recharges on stable platforms but decays constantly and when creating temporary platforms.
- **Testing:** Integration tests in `tests.py` cover movement, decay, collision, and temporary platform lifecycles. Run with `.\venv\Scripts\python.exe tests.py`.
- **GitHub Project Automation:** Draft issues in GitHub Projects v2 do not support labels or comments. If a task requires labels (like 'planned'), convert the draft to a repository issue first. If `gh project item-convert` is unavailable, manually create a repo issue and add it to the project.
- **CLI Quoting (PowerShell):** When posting multiline comments via `gh issue comment`, use the `-F` flag with a temporary file to avoid complex shell quoting issues in the Windows environment.
- **Project Pivot (Rust Runner -> Wither's Wake):** The project pivoted from a racing game to a platformer. `README.md` and `main.py` should always be checked for consistency with the current jam theme.
- **GitHub Project Automation (V2):** Use `gh project field-list` and `gh project item-list --format json` to find the correct `field-id` and `single-select-option-id` for status updates. `gh project item-edit` does not support `--owner` directly; use `--id` and `--project-id`.

