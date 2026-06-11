# AI Git Commit Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Ollama](https://img.shields.io/badge/Ollama-local%20AI-green.svg)](https://ollama.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-cloud%20AI-orange.svg)](https://openrouter.ai/)
[![Groq](https://img.shields.io/badge/Groq-cloud%20AI-red.svg)](https://groq.com/)

AI Git Commit Generator is a small CLI tool that writes clean Git commit messages for you.

It looks at your staged/unstaged changes and handles the heavy lifting using either a **local LLM** (via Ollama) or **cloud APIs** (via OpenRouter or Groq). It automatically formats everything according to the **Conventional Commits** standard:

```text
feat: add command line options
fix: handle empty staged diff
docs: improve installation guide
```

The main idea is simple: instead of writing vague commits like `update`, `changes`, or `fix`, you get a useful message based on what actually changed in your code.

## Features

- Automatically stages all unstaged changes (`git add .`) and inspects them.
- **Hybrid Architecture**: Works locally via Ollama or in the cloud using OpenRouter or Groq.
- **Zero-Config Cloud Mode**: Supports free cloud models (via OpenRouter or Groq) so you don't need a powerful GPU or local installations.
- **Local API Key Storage**: Allows saving API keys locally to avoid setting environment variables on every launch.
- **Interactive Mode**: If run without the `--commit` flag, it provides an interactive menu to commit, edit, regenerate, or cancel.
- **Inline Editing**: Pre-fills the commit message for you to edit inline using `prompt-toolkit`.
- **Fallback Selector**: Interactive selection menu to choose commit type if the AI output is not conventional.
- **50/72 limit checks**: Displays warnings if the message violates conventional commit length restrictions.
- **CLI Aesthetics**: Rich, modern ANSI color terminal outputs (automatically falls back to plain text if not in a TTY).
- Follows the **Conventional Commits** standard (lowercase type, imperative mood).
- Can either print a suggested commit message or create the commit for you.
- Supports custom Ollama/Cloud models.

## When To Use It

Use this tool after you have changed files in any Git project and want to make a commit.

For example, if you edited a Python script, fixed a bug, updated a README, or added a new feature, this tool can read those staged changes and suggest a commit message that describes them.

You do not need to run it from this repository. Run it from the project where you are making a commit.

## Prerequisites

To use the tool, you need one of the following setups:  

### Option A: Cloud Mode via OpenRouter (No AI installation required)
- A free account on [OpenRouter](https://openrouter.ai/).
- A generated API key (`OPENROUTER_API_KEY`).
- Python and Git installed.

### Option B: Cloud Mode via Groq (Fastest cloud mode)
- An account on [Groq](https://groq.com/).
- A generated API key (`GROQ_API_KEY`).
- Python and Git installed.

### Option C: Local Mode
- Installed [Ollama](https://ollama.com/).
- Downloaded local model, for example: `ollama pull qwen2.5`
- Python and Git installed.

## Installation

Install the package directly from PyPI:

```bash
pip install ai-git-commit-generator
```

### Installing from Source (Development)

If you want to run it from source:

1. Clone this repository:
```bash
git clone https://github.com/XBarni999/ai-git-commit-generator.git
```

2. Go into the tool folder:
```bash
cd ai-git-commit-generator
```

3. Install in editable mode:
```bash
python -m pip install -e .
```

After installation, the `ai-commit` command becomes available globally across your system.

## Basic Usage

Go to any Git project where you made changes:

```bash
cd path/to/your/project
```

Stage your changes:

```bash
git add .
```

### Running with Cloud APIs (No Ollama needed)

You can either save your API keys locally (recommended, as they persist across runs), or set them as temporary environment variables.

#### A. Storing API Keys Locally (Recommended)

Save your Groq or OpenRouter API keys to the local config file once:

```bash
# Save Groq API key
ai-commit --setup-groq "gsk_your_key_here"

# Save OpenRouter API key
ai-commit --setup-openrouter "sk-or-v1-your_key_here"
```

Once saved, you can run `ai-commit` anywhere, and the tool will automatically load and use them. To clear a key, simply pass an empty string (e.g. `ai-commit --setup-groq ""`).

#### B. Temporary Environment Variables

If you prefer not to store keys, you can set them as environment variables in your active terminal session:

##### 1. Via Groq Cloud API (Recommended for speed)

**Windows (CMD):**
```cmd
set GROQ_API_KEY=your_groq_key_here
ai-commit
```

**PowerShell:**
```powershell
$env:GROQ_API_KEY="your_groq_key_here"
ai-commit
```

**Bash / Linux / macOS:**
```bash
export GROQ_API_KEY="your_groq_key_here"
ai-commit
```

##### 2. Via OpenRouter Free Cloud API

**Windows (CMD):**
```cmd
set OPENROUTER_API_KEY=your_sk_or_v1_key_here
ai-commit
```

**PowerShell:**
```powershell
$env:OPENROUTER_API_KEY="your_sk_or_v1_key_here"
ai-commit
```

**Bash / Linux / macOS:**
```bash
export OPENROUTER_API_KEY="your_sk_or_v1_key_here"
ai-commit
```

### Running Locally (Via Ollama)

If no API key is found in your environment variables or local config, the tool automatically falls back to your local Ollama instance:

```bash
ai-commit
```

Make sure your Ollama server is running (`ollama serve`).

## Interactive Mode

If you run the tool without the `--commit` flag in an interactive terminal, it will recommend a commit message and present you with options:

```text
Recommended commit message:
----------------------------------------
feat: add user authentication
----------------------------------------
Commit with this message? [y]es / [n]o / [e]dit / [r]egenerate:
```

- **`y` / `yes` / `[Enter]`**: Apply the recommended message and commit.
- **`n` / `no`**: Decline and exit without committing.
- **`e` / `edit`**: Prompt to enter a custom commit message instead.
- **`r` / `regenerate`**: Query the AI again to generate a new suggestion.

## Auto Commit Mode

If you want the tool to generate the message and immediately create the commit (skipping interactive checks), use the `--commit` flag:

```bash
ai-commit --commit
```

## CLI Options

- `help`: Custom command guide (also supports `-h` / `--help`).
- `--model`: Custom Ollama/Cloud model name (Default: `qwen2.5` or `llama-3.3-70b-versatile` on Groq).
- `--url`: Custom Ollama endpoint (Default: `http://localhost:11434/api/generate`).
- `--timeout`: Request timeout in seconds (Default: `90`).
- `--commit`: Automatically create a git commit with the generated message.
- `--status`: Check Pro status and configuration settings.
- `--register <key>`: Register a Pro license key to unlock Pro features.
- `--setup-groq <key>`: Save Groq API key locally (leave empty/use `""` to clear).
- `--setup-openrouter <key>`: Save OpenRouter API key locally (leave empty/use `""` to clear).
- `--review`: [PRO] Run an AI review of changes.
- `--pr`: [PRO] Generate a detailed Pull Request description template.
- `--setup-gitmoji <on/off>`: [PRO] Toggle Gitmoji commit prefix formatting.
- `--setup-jira <on/off>`: [PRO] Toggle automatic Jira ticket matching from branch names.
- `--jira-codes <prefixes>`: [PRO] Configure custom comma-separated Jira issue prefixes.

## Running Tests

To run the automated unit tests, run:

```bash
python -m unittest tests/test_commit.py
```

## ★ Free vs Pro Comparison

| Feature | Free Version | Pro Version |
| :--- | :---: | :---: |
| **Supported Engines** | Local Ollama, Groq Cloud, OpenRouter Cloud | Local Ollama, Groq Cloud, OpenRouter Cloud |
| **Commit Message Body** | Subject line only (Single-line) | Rich explanation body (max 2-3 lines, wrapped at 72 chars) |
| **Diff Character Limit** | Up to 2,000 characters | Up to 16,000 characters |
| **Custom Cloud Models** | Default model only | Any custom model via `--model` flag or config override |
| **AI Code Reviews (`--review`)** | ❌ (Upgrade required) | ✅ Full automated reviews & recommendations |
| **PR Descriptions (`--pr`)** | ❌ (Upgrade required) | ✅ Automated PR markdown descriptions |
| **Smart Integrations** | ❌ (Upgrade required) | ✅ Gitmoji & automatic Jira branch ticket matching |

## ★ Pro Features (Premium Upgrade)

Unlock advanced developer utilities by upgrading to the Pro version. You can purchase the Pro license key on [Itch.io](https://phxntxsm.itch.io/ai-commit-generator).

### 1. AI Code Review
Run code quality audits and security checks directly from your command line:
```bash
ai-commit --review
```

### 2. PR Description Generator
Auto-generate beautifully structured markdown descriptions for your pull requests:
```bash
ai-commit --pr
```

### 3. Smart Integrations (Jira & Gitmoji)
Configure ticket parsing and Gitmoji styles globally:
```bash
ai-commit --setup-gitmoji on
ai-commit --setup-jira on
ai-commit --jira-codes "PROJ,TASK,BUG"
```
Once enabled, commits are automatically structured using conventional formatting, Jira issues extracted from branch names (e.g. `feature/PROJ-123-billing` becomes `[PROJ-123]`), and Gitmojis prepended!

### 🔑 How to Activate Your PRO License

After purchasing your license key on [Itch.io](https://phxntxsm.itch.io/ai-commit-generator) (format: `AICOMMIT-PRO-XXXX-YYYY`), register it globally in your terminal:
```bash
ai-commit --register YOUR_LICENSE_KEY_HERE
```
Check your license and feature status at any time:
```bash
ai-commit --status
```

## Example Output

```text
Analyzing staged git changes...
Using OpenRouter Free Cloud API (openrouter/free)...

Recommended commit message:
----------------------------------------
feat: add command line options
----------------------------------------
```

## Troubleshooting

### It says there are no staged changes
The tool only reads staged changes from `git diff --cached`. Make sure you run `git add .` first.

### It cannot connect to Ollama (Local Mode)
Make sure Ollama is running (`ollama serve`) and you have pulled the default model (`ollama pull qwen2.5`). Alternatively, set the `OPENROUTER_API_KEY` variable to use the cloud mode instead.

### It generated a bad message
Run it again, or try switching your backend or local model using the `--model` option. Or choose `r` (regenerate) in interactive mode.

## Why This Is Useful

Good commit messages make your project history easier to understand. They help you remember what changed, make pull requests clearer, and make open-source repositories look more professional. This tool saves time by turning your actual code changes into a readable commit message automatically.

## Privacy

- **Local Mode**: Your staged diffs stay entirely on your local machine and are processed by Ollama.
- **Cloud Mode**: Diffs are processed securely through OpenRouter's API using open-weights models.

## License

MIT
