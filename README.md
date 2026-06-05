# AI Git Commit Generator

A simple open-source CLI tool that analyzes your staged git changes and automatically generates a clean, meaningful commit message using local AI models (via Ollama).

## Features

- Inspects your current `git diff --cached`.
- Uses local LLMs through Ollama, so your code stays on your machine.
- Follows the **Conventional Commits** standard.
- Can either print a suggested commit message or create the commit for you.
- Supports custom Ollama models.

## Prerequisites

1. Installed [Ollama](https://ollama.com/).
2. Downloaded model, for example:

```bash
ollama pull qwen2.5
```

## Installation & Usage

1. Clone this repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Stage your changes:

```bash
git add .
```

4. Generate a commit message:

```bash
python main.py
```

5. Generate and commit automatically:

```bash
python main.py --commit
```

## Options

Use another Ollama model:

```bash
python main.py --model llama3.1
```

Use a custom Ollama endpoint:

```bash
python main.py --url http://localhost:11434/api/generate
```

## Example Output

```text
Analyzing staged git changes...
Generating commit message with qwen2.5...

Recommended commit message:
----------------------------------------
feat: add command line options
----------------------------------------
```

## Notes

The tool only reads staged changes from `git diff --cached`. If it says there are no staged changes, run `git add <file>` first.
