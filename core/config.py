from pathlib import Path
import yaml

def load_config(path: str = "config/config.yaml") -> dict:
    """
    Load YAML configuration for the assistant.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Config file {cfg_path} not found."
            f"Create it by copying config/config.example.yaml"
        )
    
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
        
    return cfg