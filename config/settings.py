import os
import yaml
from pathlib import Path


def load_config():
    config_path = Path(__file__).parent / "default.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    config["llm"]["groq_api_key"] = os.getenv("GROQ_API_KEY")
    config["llm"]["openrouter_api_key"] = os.getenv("OPENROUTER_API_KEY")

    return config


settings = load_config()
