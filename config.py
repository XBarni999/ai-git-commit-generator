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

N_VAL = 7312249894375976921793922449201110936893774762906060924036646709198375048705262972114038527893908476821999267816369539814569266642398508810518900530120401
E_VAL = 65537

def validate_license_key(key: str) -> bool:
    import hashlib
    key = key.strip().upper()
    if not key.startswith("AICOMMIT-PRO-"):
        return False
    parts = key.split("-")
    if len(parts) != 4:
        return False
    
    id_str = parts[2]
    sig_hex = parts[3]
    
    if len(sig_hex) != 128:
        return False
        
    try:
        sig_int = int(sig_hex, 16)
        decrypted = pow(sig_int, E_VAL, N_VAL)
        
        h_digest = hashlib.sha256(id_str.encode()).digest()
        h_expected = int.from_bytes(h_digest, "big") % N_VAL
        
        return decrypted == h_expected
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
