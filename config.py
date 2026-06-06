import json
import os

CONFIG_FILE = os.path.expanduser("~/.ai_commit_config.json")

DEFAULT_CONFIG = {
    "license_key": "",
    "gitmoji": False,
    "jira_integration": False,
    "jira_project_codes": ["PROJ", "TASK", "BUG"],
    "custom_model": ""
}

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all default keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

def validate_license_key(key: str) -> bool:
    key = key.strip().upper()
    if not key.startswith("AICOMMIT-PRO-"):
        return False
    parts = key.split("-")
    if len(parts) != 4:
        return False
    try:
        xxxx = int(parts[2])
        yyyy = int(parts[3])
        if xxxx < 0 or yyyy < 0:
            return False
        return (xxxx * 31) % 10000 == yyyy
    except ValueError:
        return False

def is_pro_active() -> bool:
    config = load_config()
    key = config.get("license_key", "")
    return validate_license_key(key)

def register_license(key: str) -> tuple[bool, str]:
    if validate_license_key(key):
        config = load_config()
        config["license_key"] = key.strip().upper()
        save_config(config)
        return True, "License key registered successfully! Pro features unlocked."
    return False, "Invalid license key format or verification failed."
