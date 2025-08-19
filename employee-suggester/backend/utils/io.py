import json
import yaml
import os
from pathlib import Path
from typing import List, Dict, Any

def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML {file_path}: {e}")
        return {}

def save_yaml(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to YAML file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving YAML {file_path}: {e}")
        return False

def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Read JSONL file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception as e:
        print(f"Error reading JSONL {file_path}: {e}")
    return data

def write_jsonl(data: List[Dict[str, Any]], file_path: str) -> bool:
    """Write data to JSONL file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        return True
    except Exception as e:
        print(f"Error writing JSONL {file_path}: {e}")
        return False

def append_jsonl(item: Dict[str, Any], file_path: str) -> bool:
    """Append single item to JSONL file."""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(item) + '\n')
        return True
    except Exception as e:
        print(f"Error appending to JSONL {file_path}: {e}")
        return False

def load_env(file_path: str = None) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if file_path is None:
        file_path = Path(__file__).parent.parent / "config" / ".env"
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error loading .env {file_path}: {e}")
    
    return env_vars

def get_config_path(filename: str) -> Path:
    """Get path to config file."""
    return Path(__file__).parent.parent / "config" / filename
