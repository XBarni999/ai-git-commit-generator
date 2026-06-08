import argparse
import os
import subprocess
import sys
import requests
import config

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5"
DEFAULT_TIMEOUT = 90

COLOR_GREEN = "32"
COLOR_RED = "31"
COLOR_YELLOW = "33"
COLOR_CYAN = "36"
COLOR_BOLD_GREEN = "1;32"
COLOR_BOLD = "1"
COLOR_MAGENTA = "35"
COLOR_BOLD_YELLOW = "1;33"
COLOR_BOLD_CYAN = "1;36"


def color_text(text: str, color_code: str) -> str:
    """Wrap text with ANSI escape codes for terminal coloring if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"\033[{color_code}m{text}\033[0m"
    return text


def setup_console() -> None:
    if sys.platform == "win32":
        try:
            os.system("")
        except Exception:
            pass
        try:
            subprocess.run(["chcp", "65001"], capture_output=True, check=True)
        except Exception:
            pass
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
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


def generate_ai_response(diff: str, prompt: str, system_prompt: str, model: str, url: str, timeout: int) -> str:
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        selected_model = "llama-3.3-70b-versatile"
        if model != DEFAULT_MODEL:
            selected_model = model
            
        print(color_text(f"Using Groq API ({selected_model})...", COLOR_CYAN))
        
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        try:
            response = requests.post(groq_url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as exc:
            return f"Error: Groq request failed: {exc}"
            
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        import config
        is_pro = config.is_pro_active()
        cfg = config.load_config()
        
        selected_model = "nvidia/nemotron-3.5-content-safety:free"
        if is_pro:
            if cfg.get("custom_model"):
                selected_model = cfg.get("custom_model")
            else:
                selected_model = "meta-llama/llama-3.1-8b-instruct"
        
        if model != DEFAULT_MODEL:
            selected_model = model
            
        print(color_text(f"Using OpenRouter Cloud API ({selected_model})...", COLOR_CYAN))
        
        router_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/XBarni999/ai-git-commit-generator",
            "X-Title": "AI Git Commit Generator"
        }
        
        payload = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        try:
            response = requests.post(router_url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as exc:
            return f"Error: OpenRouter request failed: {exc}"
            
    else:
        print(color_text(f"No API key found. Using local Ollama with model '{model}'...", COLOR_CYAN))
        
        chat_url = url
        if url.endswith("/api/generate"):
            chat_url = url.replace("/api/generate", "/api/chat")
            
        combined_prompt = f"{system_prompt}\n\n{prompt}"
        chat_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": combined_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }
        
        try:
            response = requests.post(chat_url, json=chat_payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "").strip()
        except Exception:
            payload = {
                "model": model,
                "prompt": combined_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            }
            try:
                response = requests.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except requests.exceptions.ConnectionError:
                return (
                    "Error: could not connect to Ollama. Start it with 'ollama serve' "
                    "or set the OPENROUTER_API_KEY environment variable to use cloud API."
                )
            except requests.exceptions.Timeout:
                return "Error: Ollama request timed out."
            except requests.exceptions.RequestException as exc:
                return f"Error: Ollama request failed: {exc}"


def generate_commit_message(diff: str, model: str, url: str, timeout: int) -> str:
    if not diff.strip():
        return "No staged changes. Add files first with 'git add'."
    
    max_diff_len = 10000
    if len(diff) > max_diff_len:
        diff = diff[:max_diff_len] + "\n\n[Diff truncated for length...]"
        
    prompt = (
        f"Diff:\n{diff}\n\n"
        "Instructions:\n"
        "You are an expert software maintainer. Write exactly one git commit message for the diff above. "
        "Use Conventional Commits standard (lowercase type, imperative summary).\n"
        "Ensure the first line (subject) does not exceed 50 characters.\n"
        "If a body is necessary, separate it from the subject with a blank line, and wrap each line of the body at 72 characters.\n"
        "Do NOT write any introduction, explanation, quotes, or markdown. "
        "Do NOT write 'Here is the commit message:' or 'Your updated script...'. "
        "Start directly with the conventional commit prefix (e.g., feat:, fix:, chore:, docs:).\n\n"
        "Examples of desired output format:\n"
        "- feat: add user authentication option\n"
        "- fix: resolve crash in console output\n"
        "- docs: improve installation guide in readme"
    )
    
    system_prompt = "You are an expert software maintainer."
    
    message = generate_ai_response(diff, prompt, system_prompt, model, url, timeout)
    if message.startswith("Error:"):
        return message
    return clean_commit_message(message)


def clean_commit_message(message: str) -> str:
    cleaned = message.strip().strip('"').strip("'").strip()
    for prefix in ("Commit message:", "commit message:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            
    cleaned = cleaned.strip('"').strip("'").strip()
    lines = cleaned.splitlines()
    if not lines:
        return "chore: update project"
        
    import re
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\([^)]+\))?:\s+.+"
    
    start_idx = -1
    for idx, line in enumerate(lines):
        line_stripped = line.strip().strip('"').strip("'")
        if re.match(pattern, line_stripped, re.IGNORECASE):
            start_idx = idx
            break
            
    if start_idx != -1:
        reconstructed = "\n".join(lines[start_idx:]).strip()
        reconstructed = reconstructed.strip('"').strip("'").strip()
        return reconstructed
        
    return cleaned


def is_conventional_commit(message: str) -> bool:
    lines = message.splitlines()
    if not lines:
        return False
    import re
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\([^)]+\))?:\s+.+"
    return bool(re.match(pattern, lines[0].strip(), re.IGNORECASE))


def check_50_72_compliance(message: str) -> list[str]:
    warnings = []
    lines = message.splitlines()
    if not lines:
        return warnings
    
    subject = lines[0]
    if len(subject) > 50:
        warnings.append(f"Subject line exceeds 50 characters (currently {len(subject)} chars).")
        
    if len(lines) > 1:
        if lines[1].strip() != "":
            warnings.append("Subject and body should be separated by a blank line.")
            
        for i, line in enumerate(lines[2:], start=3):
            if len(line) > 72:
                warnings.append(f"Line {i} in the body exceeds 72 characters (currently {len(line)} chars).")
    return warnings


def prompt_commit_type(message: str) -> str:
    print(color_text("\nAI returned a message that doesn't follow the Conventional Commits standard:", COLOR_YELLOW))
    print(color_text(f"  {message.splitlines()[0] if message.splitlines() else message}", COLOR_BOLD))
    print()
    print("Please select a conventional commit type:")
    types = [
        ("feat", "new feature"),
        ("fix", "bug fix"),
        ("docs", "documentation changes"),
        ("style", "formatting, missing semi-colons, etc."),
        ("refactor", "refactoring production code"),
        ("perf", "performance improvements"),
        ("test", "adding/refactoring tests"),
        ("chore", "updating build tasks, configs, etc."),
        ("ci", "CI configuration files/scripts"),
        ("build", "build system or external dependencies"),
        ("revert", "reverting a previous commit")
    ]
    for idx, (t, desc) in enumerate(types, 1):
        print(f"  {idx:2d}) {t:<10} - {desc}")
    print()
    
    while True:
        try:
            choice = input(color_text("Select type (1-11) or press Enter to skip: ", COLOR_YELLOW)).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSelection skipped.")
            return message
            
        if not choice:
            return message
            
        if choice.isdigit() and 1 <= int(choice) <= len(types):
            selected_type = types[int(choice) - 1][0]
            break
        print(color_text("Invalid selection. Please enter a number between 1 and 11.", COLOR_RED))
        
    try:
        scope = input(color_text("Enter optional scope (e.g. parser, auth) or press Enter to skip: ", COLOR_YELLOW)).strip()
    except (KeyboardInterrupt, EOFError):
        scope = ""
        
    first_line = message.splitlines()[0] if message.splitlines() else ""
    subject_content = first_line.strip()
    
    scope_str = f"({scope})" if scope else ""
    new_subject = f"{selected_type}{scope_str}: {subject_content}"
    
    lines = message.splitlines()
    if len(lines) > 1:
        return new_subject + "\n" + "\n".join(lines[1:])
    return new_subject


def commit(message: str) -> None:
    try:
        run_git(["commit", "-m", message])
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or "Error: git commit failed.")
        sys.exit(exc.returncode)


def show_pro_required_message(feature_name: str) -> None:
    print(color_text("=" * 60, COLOR_RED))
    print(color_text(f"★ {feature_name.upper()} - PRO FEATURE ★", COLOR_BOLD_YELLOW))
    print(color_text("=" * 60, COLOR_RED))
    print("This feature is only available in the Pro version of AI Git Commit Generator.")
    print("Upgrade to Pro to unlock:")
    print("  - AI Code Reviews (--review)")
    print("  - PR Description Generator (--pr)")
    print("  - Auto-Jira/Linear ticket prepending")
    print("  - Gitmoji support & custom formatting templates")
    print("  - Premium Cloud AI models (Claude 3.5, GPT-4o)")
    print()
    print("To purchase/register a license key:")
    print(color_text("  1. Visit: https://ai-commit.com/upgrade", COLOR_CYAN))
    print(color_text("  2. Activate key: ai-commit --register AICOMMIT-PRO-XXXX-YYYY", COLOR_CYAN))
    print(color_text("=" * 60, COLOR_RED))


def register_key(key: str) -> int:
    import config
    success, msg = config.register_license(key)
    if success:
        print(color_text("=" * 60, COLOR_GREEN))
        print(color_text("★ PRO VERSION ACTIVATED ★", COLOR_BOLD_GREEN))
        print(color_text("=" * 60, COLOR_GREEN))
        print(color_text(msg, COLOR_GREEN))
        print("You have successfully unlocked all Pro features.")
        print("Try running:")
        print(color_text("  ai-commit --status", COLOR_CYAN))
        print(color_text("  ai-commit --review", COLOR_CYAN))
        print(color_text("=" * 60, COLOR_GREEN))
        return 0
    else:
        print(color_text("=" * 60, COLOR_RED))
        print(color_text("❌ REGISTRATION FAILED", COLOR_RED))
        print(color_text("=" * 60, COLOR_RED))
        print(color_text(msg, COLOR_RED))
        print("Please check your license key and try again.")
        print("Valid keys format: AICOMMIT-PRO-XXXX-YYYY")
        print(color_text("=" * 60, COLOR_RED))
        return 1


def show_status() -> int:
    import config
    cfg = config.load_config()
    is_pro = config.is_pro_active()
    
    if is_pro:
        print(color_text("=" * 60, COLOR_GREEN))
        print(color_text("★ AI GIT COMMIT GENERATOR - PRO ACTIVE ★", COLOR_BOLD_GREEN))
        print(color_text("=" * 60, COLOR_GREEN))
        print(f"License Key: {cfg.get('license_key')}")
        print()
        print("Pro Features Status:")
        print(f"  - AI Code Review (--review):       " + color_text("[ENABLED]", COLOR_GREEN))
        print(f"  - PR Description (--pr):            " + color_text("[ENABLED]", COLOR_GREEN))
        print(f"  - Premium Cloud Models:            " + color_text("[ENABLED]", COLOR_GREEN))
        
        status_gitmoji = "[ENABLED]" if cfg.get("gitmoji") else "[DISABLED]"
        color_gitmoji = COLOR_GREEN if cfg.get("gitmoji") else COLOR_YELLOW
        print(f"  - Gitmoji commit style:            " + color_text(status_gitmoji, color_gitmoji))
        
        status_jira = "[ENABLED]" if cfg.get("jira_integration") else "[DISABLED]"
        color_jira = COLOR_GREEN if cfg.get("jira_integration") else COLOR_YELLOW
        print(f"  - Jira branch ticket matching:     " + color_text(status_jira, color_jira))
        print(f"    Jira codes to look for:          {', '.join(cfg.get('jira_project_codes', []))}")
        
        custom_model = cfg.get("custom_model")
        model_display = custom_model if custom_model else "Default Premium Model"
        print(f"  - Custom premium model override:   {model_display}")
        print(color_text("=" * 60, COLOR_GREEN))
    else:
        print(color_text("=" * 60, COLOR_YELLOW))
        print(color_text("☆ AI GIT COMMIT GENERATOR - FREE ☆", COLOR_BOLD_YELLOW))
        print(color_text("=" * 60, COLOR_YELLOW))
        print("License Status: " + color_text("FREE VERSION", COLOR_RED))
        print()
        print("Unlock PRO features to supercharge your developer workflow:")
        print("  1. AI Code Review (--review): Get bug & style suggestions.")
        print("  2. PR Description Generator (--pr): Automatic detailed PRs.")
        print("  3. Jira & Gitmoji: Auto-match ticket numbers & gitmojis.")
        print("  4. Premium AI Models: Claude 3.5 Sonnet, GPT-4o quality.")
        print()
        print("To activate Pro, run:")
        print(color_text("  ai-commit --register AICOMMIT-PRO-XXXX-YYYY", COLOR_CYAN))
        print(color_text("=" * 60, COLOR_YELLOW))
    return 0


def setup_gitmoji(value: str) -> int:
    import config
    if not config.is_pro_active():
        show_pro_required_message("Gitmoji Commit Style")
        return 1
    cfg = config.load_config()
    cfg["gitmoji"] = (value == "on")
    config.save_config(cfg)
    status = "enabled" if cfg["gitmoji"] else "disabled"
    print(color_text(f"Gitmoji commit style has been {status}.", COLOR_GREEN))
    return 0


def setup_jira(value: str) -> int:
    import config
    if not config.is_pro_active():
        show_pro_required_message("Jira Integration")
        return 1
    cfg = config.load_config()
    cfg["jira_integration"] = (value == "on")
    config.save_config(cfg)
    status = "enabled" if cfg["jira_integration"] else "disabled"
    print(color_text(f"Jira branch ticket integration has been {status}.", COLOR_GREEN))
    return 0


def setup_jira_codes(value: str) -> int:
    import config
    if not config.is_pro_active():
        show_pro_required_message("Jira Project Prefixes")
        return 1
    cfg = config.load_config()
    codes = [code.strip().upper() for code in value.split(",") if code.strip()]
    if not codes:
        print(color_text("Error: Jira codes cannot be empty.", COLOR_RED))
        return 1
    cfg["jira_project_codes"] = codes
    config.save_config(cfg)
    print(color_text(f"Jira project prefixes updated to: {', '.join(codes)}", COLOR_GREEN))
    return 0


def run_code_review(diff: str, model: str, url: str, timeout: int) -> int:
    import config
    if not config.is_pro_active():
        show_pro_required_message("AI Code Review")
        return 1
        
    print(color_text("Running AI Code Review on staged changes...", COLOR_CYAN))
    
    system_prompt = (
        "You are an expert principal software engineer and security auditor. "
        "Analyze the following git diff and perform a comprehensive code review. "
        "Provide constructive, clear, and actionable feedback. "
        "Use markdown formatting with emojis for sections: "
        "1. 💡 Summary of changes "
        "2. ⚠️ Potential Bugs & Logic Errors "
        "3. 🔒 Security & Performance Bottlenecks "
        "4. 🎨 Style & Refactoring Suggestions. "
        "Keep your response concise but highly detailed."
    )
    prompt = f"Diff:\n{diff}"
    
    review_output = generate_ai_response(diff, prompt, system_prompt, model, url, timeout)
    
    if review_output.startswith("Error:"):
        print(color_text(review_output, COLOR_RED))
        return 1
        
    print(color_text("\n" + "=" * 60, COLOR_GREEN))
    print(color_text("★ PRO: AI CODE REVIEW ★", COLOR_BOLD_GREEN))
    print(color_text("=" * 60, COLOR_GREEN))
    print(review_output)
    print(color_text("=" * 60, COLOR_GREEN))
    return 0


def generate_pr_description(diff: str, model: str, url: str, timeout: int) -> int:
    import config
    if not config.is_pro_active():
        show_pro_required_message("PR Description Generator")
        return 1
        
    print(color_text("Generating Pull Request description...", COLOR_CYAN))
    
    system_prompt = (
        "You are an expert software developer. Generate a detailed, professional Pull Request "
        "description in Markdown format based on the following diff. "
        "Include these sections:\n"
        "## 📝 Description\n"
        "## 🛠 Key Changes\n"
        "## 🧪 How Has This Been Tested?\n"
        "Use bullet points for lists and keep the tone professional. "
        "Do not include any greeting or explanation outside the Markdown content."
    )
    prompt = f"Diff:\n{diff}"
    
    pr_output = generate_ai_response(diff, prompt, system_prompt, model, url, timeout)
    
    if pr_output.startswith("Error:"):
        print(color_text(pr_output, COLOR_RED))
        return 1
        
    print(color_text("\n" + "=" * 60, COLOR_GREEN))
    print(color_text("★ PRO: PULL REQUEST DESCRIPTION ★", COLOR_BOLD_GREEN))
    print(color_text("=" * 60, COLOR_GREEN))
    print(pr_output)
    print(color_text("=" * 60, COLOR_GREEN))
    return 0


def get_jira_ticket(prefixes: list[str]) -> str | None:
    try:
        res = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = res.stdout.strip()
        import re
        prefix_pattern = "|".join(re.escape(p) for p in prefixes)
        if not prefix_pattern:
            prefix_pattern = "[A-Z]+"
        pattern = rf"\b({prefix_pattern})-\d+"
        match = re.search(pattern, branch, re.IGNORECASE)
        if match:
            return match.group(0).upper()
    except Exception:
        pass
    return None


def apply_pro_formatting(commit_message: str) -> str:
    import config
    if not config.is_pro_active():
        return commit_message
        
    cfg = config.load_config()
    
    if cfg.get("jira_integration"):
        ticket = get_jira_ticket(cfg.get("jira_project_codes", []))
        if ticket:
            if ticket not in commit_message:
                commit_message = f"[{ticket}] {commit_message}"
                
    if cfg.get("gitmoji"):
        import re
        GITMOJIS = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📝",
            "style": "💄",
            "refactor": "♻️",
            "perf": "⚡",
            "test": "✅",
            "chore": "🔧",
            "ci": "👷",
            "build": "📦",
            "revert": "⏪"
        }
        
        match = re.search(r"(\b[a-z]+)(\([^)]+\))?:", commit_message)
        if match:
            c_type = match.group(1)
            emoji = GITMOJIS.get(c_type)
            if emoji:
                pos = match.end()
                commit_message = f"{commit_message[:pos]} {emoji} {commit_message[pos:].strip()}"
                
    return commit_message


def show_custom_help() -> int:
    print(color_text("=" * 60, COLOR_BOLD_CYAN))
    print(color_text("★ AI GIT COMMIT GENERATOR - COMMAND GUIDE ★", COLOR_BOLD_GREEN))
    print(color_text("=" * 60, COLOR_BOLD_CYAN))
    print("Usage: " + color_text("ai-commit [options]", COLOR_BOLD_YELLOW))
    print()
    print(color_text("Core Commands:", COLOR_BOLD))
    print("  (default)            Generate commit message from changes (stages via git add .)")
    print("  --commit             Generate and automatically commit changes")
    print("  --timeout <sec>      Set request timeout (default: 90)")
    print("  --model <model>      Set custom Ollama model name (default: qwen2.5)")
    print("  --url <url>          Set custom Ollama endpoint")
    print()
    print(color_text("Licensing & Status:", COLOR_BOLD))
    print("  --status             Check license and Pro configurations")
    print("  --register <key>     Register a Pro license key")
    print()
    print(color_text("Pro Features:", COLOR_BOLD_GREEN))
    print("  --review             Run an AI code review of staged changes")
    print("  --pr                 Generate a detailed Pull Request description")
    print("  --setup-gitmoji <on/off>   Turn Gitmoji prefixing on or off")
    print("  --setup-jira <on/off>      Turn Jira branch matching on or off")
    print("  --jira-codes <codes>       Set comma-separated Jira project codes")
    print()
    print("Run with " + color_text("help", COLOR_BOLD_YELLOW) + " or " + color_text("-h / --help", COLOR_BOLD_YELLOW) + " to see this guide.")
    print(color_text("=" * 60, COLOR_BOLD_CYAN))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Conventional Commit message from staged git changes using Ollama or OpenRouter.",
        add_help=False  
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name. Default: {DEFAULT_MODEL}")
    parser.add_argument("--url", default=OLLAMA_URL, help=f"Ollama generate endpoint. Default: {OLLAMA_URL}")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds.")
    parser.add_argument("--commit", action="store_true", help="Create the git commit after generating the message.")
    
    parser.add_argument("--register", help="Register a Pro license key.")
    parser.add_argument("--status", action="store_true", help="Check license and feature configuration status.")
    parser.add_argument("--review", action="store_true", help="[PRO] Run an AI review of your staged changes.")
    parser.add_argument("--pr", action="store_true", help="[PRO] Generate a Pull Request description.")
    parser.add_argument("--setup-gitmoji", choices=["on", "off"], help="[PRO] Turn Gitmoji commit style on/off.")
    parser.add_argument("--setup-jira", choices=["on", "off"], help="[PRO] Turn Jira integration on/off.")
    parser.add_argument("--jira-codes", help="[PRO] Comma-separated Jira project prefixes (e.g., PROJ,TASK).")
    return parser


def main(argv: list[str] | None = None) -> int:
    setup_console()
    
    args_list = argv if argv is not None else sys.argv[1:]
    if args_list and args_list[0] in ("help", "h", "-h", "--help"):
        return show_custom_help()
        
    args = build_parser().parse_args(argv)

    if args.register is not None:
        return register_key(args.register)

    if args.status:
        return show_status()

    if args.setup_gitmoji is not None:
        return setup_gitmoji(args.setup_gitmoji)

    if args.setup_jira is not None:
        return setup_jira(args.setup_jira)

    if args.jira_codes is not None:
        return setup_jira_codes(args.jira_codes)

    try:
        run_git(["add", "."])
    except Exception as exc:
        print(color_text(f"Error: failed to stage changes with git add .: {exc}", COLOR_RED))
        return 1

    diff = get_git_diff()
    if not diff.strip():
        print(color_text("No changes found to commit.", COLOR_RED))
        return 1

    if args.review:
        return run_code_review(diff, args.model, args.url, args.timeout)

    if args.pr:
        return generate_pr_description(diff, args.model, args.url, args.timeout)

    print(color_text("Analyzing staged git changes...", COLOR_CYAN))
    
    commit_message = generate_commit_message(diff, args.model, args.url, args.timeout)

    if commit_message.startswith("Error:"):
        print(color_text(commit_message, COLOR_RED))
        return 1
    
    if not is_conventional_commit(commit_message):
        commit_message = prompt_commit_type(commit_message)

    commit_message = apply_pro_formatting(commit_message)
    
    import config
    is_pro = config.is_pro_active()
    badge = color_text(" [PRO ACTIVE]", COLOR_GREEN) if is_pro else ""
    
    print(color_text(f"\nRecommended commit message{badge}:", COLOR_BOLD_GREEN))
    print(color_text("-" * 40, COLOR_GREEN))
    print(color_text(commit_message, COLOR_BOLD))
    print(color_text("-" * 40, COLOR_GREEN))

    warnings = check_50_72_compliance(commit_message)
    if warnings:
        print(color_text("Warning: Commit message style warnings:", COLOR_BOLD_YELLOW))
        for warn in warnings:
            print(color_text(f"  ⚠️  {warn}", COLOR_YELLOW))
        print()

    if args.commit:
        commit(commit_message)
        print(color_text("Commit created successfully.", COLOR_GREEN))
    elif sys.stdin.isatty():
        while True:
            prompt_str = color_text("Commit with this message? [y]es / [n]o / [e]dit / [r]egenerate: ", COLOR_YELLOW)
            try:
                choice = input(prompt_str).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print(color_text("\nCommit aborted.", COLOR_RED))
                return 1
            
            if choice in ("y", "yes", ""):
                commit(commit_message)
                print(color_text("Commit created successfully.", COLOR_GREEN))
                break
            elif choice in ("n", "no"):
                print(color_text("Commit aborted.", COLOR_YELLOW))
                break
            elif choice in ("e", "edit"):
                try:
                    try:
                        # pyrefly: ignore [missing-import]
                        from prompt_toolkit import prompt as pt_prompt
                        print(color_text("Editing commit message inline. Press Enter when done.", COLOR_CYAN))
                        custom_message = pt_prompt("> ", default=commit_message).strip()
                    except ImportError:
                        prompt_edit = color_text("Enter custom commit message: ", COLOR_YELLOW)
                        custom_message = input(prompt_edit).strip()
                except (KeyboardInterrupt, EOFError):
                    print(color_text("\nCommit aborted.", COLOR_RED))
                    return 1
                if custom_message:
                    commit(custom_message)
                    print(color_text("Commit created successfully.", COLOR_GREEN))
                    break
                else:
                    print(color_text("Empty message. Action cancelled.", COLOR_RED))
            elif choice in ("r", "regenerate"):
                print(color_text("\nRegenerating commit message...", COLOR_CYAN))
                commit_message = generate_commit_message(diff, args.model, args.url, args.timeout)
                if commit_message.startswith("Error:"):
                    print(color_text(commit_message, COLOR_RED))
                    return 1
                if not is_conventional_commit(commit_message):
                    commit_message = prompt_commit_type(commit_message)
                commit_message = apply_pro_formatting(commit_message)
                print(color_text(f"\nRecommended commit message{badge}:", COLOR_BOLD_GREEN))
                print(color_text("-" * 40, COLOR_GREEN))
                print(color_text(commit_message, COLOR_BOLD))
                print(color_text("-" * 40, COLOR_GREEN))
                warnings = check_50_72_compliance(commit_message)
                if warnings:
                    print(color_text("Warning: Commit message style warnings:", COLOR_BOLD_YELLOW))
                    for warn in warnings:
                        print(color_text(f"  ⚠️  {warn}", COLOR_YELLOW))
                    print()
            else:
                print(color_text("Invalid option. Please choose y, n, e, or r.", COLOR_RED))

    return 0


if __name__ == "__main__":
    sys.exit(main())
