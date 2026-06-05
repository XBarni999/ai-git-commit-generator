# Contributing to AI Git Commit Generator

Thanks for helping improve this project.

## Local Setup

```bash
git clone https://github.com/XBarni999/ai-git-commit-generator.git
cd ai-git-commit-generator
python -m pip install -e .
```

## Development

Run the CLI from any Git repository with staged changes:

```bash
ai-commit
```

Or test the script directly:

```bash
python main.py
```

## Good First Contributions

- Improve prompt quality for generated commit messages.
- Add support for config files.
- Add tests for CLI behavior.
- Improve installation docs for Windows, macOS, and Linux.
- Add support for more local model providers.

## Pull Request Checklist

- The CLI still works with `python main.py`.
- The installed shortcut still works as `ai-commit`.
- User-facing changes are documented in `README.md`.

