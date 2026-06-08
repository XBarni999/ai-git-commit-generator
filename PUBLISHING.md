# Publishing to PyPI (Python Package Index)

This guide documents the steps required to package and publish **AI Git Commit Generator** to PyPI so that users can install it globally via `pip`.

---

## 1. Prerequisites

Before publishing, make sure you have:
1. An account on [PyPI](https://pypi.org/).
2. A PyPI API Token for authentication.
3. Installed packaging tools:
   ```bash
   pip install --upgrade build twine
   ```

---

## 2. Check Package Configuration

Ensure that `pyproject.toml` contains correct metadata:
- **`name`**: `ai-git-commit-generator` (verify if the name is available on PyPI first)
- **`version`**: The current release version (e.g., `0.2.0`)
- **`dependencies`**: Correct list of runtime requirements (e.g. `requests`, `prompt-toolkit`)

---

## 3. Build the Package

From the root directory of the project, run the build command:

```bash
python -m build
```

This will generate a `dist/` directory containing two files:
- A `.tar.gz` source archive (e.g. `ai-git-commit-generator-0.2.0.tar.gz`)
- A `.whl` wheel file (e.g. `ai_git_commit_generator-0.2.0-py3-none-any.whl`)

---

## 4. Validate the Build

Use `twine check` to verify that your package description will render correctly on PyPI:

```bash
python -m twine check dist/*
```

---

## 5. Upload to TestPyPI (Optional but Recommended)

It is highly recommended to upload to TestPyPI first to verify that the release looks good and installs correctly:

```bash
python -m twine upload --repository testpypi dist/*
```

- When prompted for a username, enter `__token__`.
- When prompted for a password, enter your TestPyPI API token (including the `pypi-` prefix).

After uploading, you can try installing from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ai-git-commit-generator
```

---

## 6. Upload to PyPI (Production Release)

Once validated on TestPyPI, publish to the real PyPI:

```bash
python -m twine upload dist/*
```

- Username: `__token__`
- Password: your PyPI API token.

---

## 7. Clean up

After a successful upload, you can clean up the build files:

```bash
rmdir /s /q build dist ai_git_commit_generator.egg-info
```
*(On Linux/macOS: `rm -rf build/ dist/ *.egg-info`)*
