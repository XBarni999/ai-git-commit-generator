# AI Git Commit Generator

A simple open-source CLI tool that analyzes your staged git changes and automatically generates a clean, meaningful commit message using local AI models (via Ollama).

## Features
- Inspects your current `git diff --cached`.
- Uses local LLMs (like Llama 3 or Mistral) so your code stays private.
- Follows the **Conventional Commits** standard.

## Prerequisites
1. Installed [Ollama](https://ollama.com/).
2. Downloaded model (e.g., `ollama run llama3`).

## Installation & Usage
1. Clone this repository.
2. Install dependencies:
```bash
   pip install -r requirements.txt