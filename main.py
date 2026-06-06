import argparse
import os
import subprocess
import sys
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5"
DEFAULT_TIMEOUT = 90


def setup_console() -> None:
    if sys.platform == "win32":
        try:
            subprocess.run(["chcp", "65001"], capture_output=True, check=True)
        except Exception:
            pass


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


def get_git_diff() -> str:
    try:
        result = run_git(["diff", "--cached"])
        return result.stdout
    except subprocess.CalledProcessError:
        print("Error: run this command inside a git repository.")
        sys.exit(1)


def generate_with_openrouter(diff: str, api_key: str, timeout: int) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/XBarni999/ai-git-commit-generator",
        "X-Title": "AI Git Commit Generator"
    }
    
    prompt = (
        "You are an expert software maintainer. Write exactly one git commit message "
        "for the staged diff below. Use Conventional Commits, lowercase type, and an "
        "imperative English summary. Keep it under 72 characters if possible. "
        "Return only the commit message, without quotes, markdown, explanation, or bullets.\n\n"
        f"Diff:\n{diff}"
    )
    
    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return clean_commit_message(message)
    except requests.exceptions.RequestException as exc:
        return f"Error: OpenRouter cloud request failed: {exc}"


def generate_commit_message(diff: str, model: str, url: str, timeout: int) -> str:
    if not diff.strip():
        return "No staged changes. Add files first with 'git add'."

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        print("Using OpenRouter Free Cloud API (Llama 3)...")
        return generate_with_openrouter(diff, api_key, timeout)

    print(f"No API key found. Using local Ollama with {model}...")
    
    prompt = (
        "You are an expert software maintainer. Write exactly one git commit message "
        "for the staged diff below. Use Conventional Commits, lowercase type, and an "
        "imperative English summary. Keep it under 72 characters if possible. "
        "Return only the commit message, without quotes, markdown, explanation, or bullets.\n\n"
        f"Diff:\n{diff}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        message = response.json().get("response", "").strip()
        return clean_commit_message(message)
    except requests.exceptions.ConnectionError:
        return (
            "Error: could not connect to Ollama. Start it with 'ollama serve' "
            "or set the OPENROUTER_API_KEY environment variable to use free cloud API."
        )
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out."
    except requests.exceptions.RequestException as exc:
        return f"Error: Ollama request failed: {exc}"


def clean_commit_message(message: str) -> str:
    cleaned = message.strip().strip('"').strip("'")
    for prefix in ("Commit message:", "commit message:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned.splitlines()[0].strip() if cleaned else "chore: update project"


def commit(message: str) -> None:
    try:
        run_git(["commit", "-m", message])
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or "Error: git commit failed.")
        sys.exit(exc.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Conventional Commit message from staged git changes using Ollama or OpenRouter."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name. Default: {DEFAULT_MODEL}")
    parser.add_argument("--url", default=OLLAMA_URL, help=f"Ollama generate endpoint. Default: {OLLAMA_URL}")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds.")
    parser.add_argument("--commit", action="store_true", help="Create the git commit after generating the message.")
    return parser


def main(argv: list[str] | None = None) -> int:
    setup_console()
    args = build_parser().parse_args(argv)

    print("Analyzing staged git changes...")
    
    diff = get_git_diff()
    if not diff.strip():
        print("No staged changes. Run 'git add <files>' first.")
        return 1

    commit_message = generate_commit_message(diff, args.model, args.url, args.timeout)

    if commit_message.startswith("Error:"):
        print(commit_message)
        return 1
    
    print("\nRecommended commit message:")
    print("-" * 40)
    print(commit_message)
    print("-" * 40)

    if args.commit:
        commit(commit_message)
        print("Commit created.")

    return 0


if __name__ == "__main__":
    sys.exit(main())