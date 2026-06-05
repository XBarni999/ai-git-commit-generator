# AI Git Commit Generator

AI Git Commit Generator is a small CLI tool that writes clean Git commit messages for you.

It looks at your staged changes, sends the diff to a local AI model through Ollama, and suggests a short Conventional Commit message like:

```text
feat: add command line options
fix: handle empty staged diff
docs: improve installation guide
```

The main idea is simple: instead of writing vague commits like `update`, `changes`, or `fix`, you get a useful message based on what actually changed in your code.

## Features

- Inspects your current `git diff --cached`.
- Uses local LLMs through Ollama, so your code stays on your machine.
- Follows the **Conventional Commits** standard.
- Can either print a suggested commit message or create the commit for you.
- Supports custom Ollama models.

## When To Use It

Use this tool after you have changed files in any Git project and want to make a commit.

For example, if you edited a Python script, fixed a bug, updated a README, or added a new feature, this tool can read those staged changes and suggest a commit message that describes them.

You do not need to run it from this repository. Run it from the project where you are making a commit.

## Prerequisites

1. Installed [Ollama](https://ollama.com/).
2. Downloaded model, for example:

```bash
ollama pull qwen2.5
```

3. Python installed.

4. Git installed.

## Installation

Clone this repository:

```bash
git clone https://github.com/XBarni999/ai-git-commit-generator.git
```

Go into the tool folder:

```bash
cd ai-git-commit-generator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

Go to any Git project where you made changes:

```bash
cd path/to/your/project
```

Stage your changes:

```bash
git add .
```

Run the generator:

```bash
python path/to/ai-git-commit-generator/main.py
```

It will print a recommended commit message:

```text
Recommended commit message:
----------------------------------------
feat: add user settings page
----------------------------------------
```

Then you can copy it and commit manually:

```bash
git commit -m "feat: add user settings page"
```

## Auto Commit Mode

If you want the tool to generate the message and immediately create the commit, use:

```bash
python path/to/ai-git-commit-generator/main.py --commit
```

This is the fastest workflow:

```bash
git add .
python path/to/ai-git-commit-generator/main.py --commit
```

## Windows Example

If this repository is stored here:

```text
C:\Users\123\Desktop\work\Git\Ai Git
```

And you are working in another project, run:

```powershell
cd "C:\Users\123\Desktop\work\Git\my-project"
git add .
python "C:\Users\123\Desktop\work\Git\Ai Git\main.py"
```

To create the commit automatically:

```powershell
python "C:\Users\123\Desktop\work\Git\Ai Git\main.py" --commit
```

## Full Practical Workflow

1. Make changes in your project.

2. Check what changed:

```bash
git status
```

3. Stage the files you want to commit:

```bash
git add .
```

4. Generate a commit message:

```bash
python path/to/ai-git-commit-generator/main.py
```

5. If the message looks good, commit:

```bash
git commit -m "generated message here"
```

Or do steps 4 and 5 together:

```bash
python path/to/ai-git-commit-generator/main.py --commit
```

## CLI Options

Use another Ollama model:

```bash
python path/to/ai-git-commit-generator/main.py --model llama3.1
```

Use a custom Ollama endpoint:

```bash
python path/to/ai-git-commit-generator/main.py --url http://localhost:11434/api/generate
```

Set a longer timeout for big diffs:

```bash
python path/to/ai-git-commit-generator/main.py --timeout 180
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

## Troubleshooting

### It says there are no staged changes

The tool only reads staged changes from:

```bash
git diff --cached
```

So you need to stage files first:

```bash
git add .
```

### It cannot connect to Ollama

Make sure Ollama is installed and running:

```bash
ollama serve
```

Then make sure the model exists:

```bash
ollama pull qwen2.5
```

### It generated a bad message

Run it again, or use another model:

```bash
python path/to/ai-git-commit-generator/main.py --model llama3.1
```

You can always copy the suggested message, edit it, and commit manually.

## Why This Is Useful

Good commit messages make your project history easier to understand. They help you remember what changed, make pull requests clearer, and make open-source repositories look more professional.

This tool saves time by turning your actual code changes into a readable commit message automatically.

## Privacy

By default, the tool uses Ollama locally. Your staged diff is sent to your local Ollama server, not to a cloud API.

## License

MIT
