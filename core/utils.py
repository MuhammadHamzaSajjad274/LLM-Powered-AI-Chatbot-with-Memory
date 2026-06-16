"""
Utility functions for configuration, logging, and token counting.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file. If None, uses default path.
        
    Returns:
        Dictionary containing configuration settings.
    """
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")

    if config_path is None:
        # Default to configs/model_config.yaml relative to project root
        config_path = project_root / "configs" / "model_config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config


def get_api_key(service: str, config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get API key from environment variable or config.
    
    Args:
        service: Service name (e.g., "openai", "deepseek")
        config: Optional configuration dictionary
        
    Returns:
        API key string or None if not found
    """
    # First try environment variable
    env_key = os.getenv(f"{service.upper()}_API_KEY")
    if env_key:
        return env_key
    
    # Then try config file
    if config and service in config:
        api_key = config[service].get("api_key", "")
        if api_key:
            return api_key
    
    return None


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estimate token count for a given text.
    Simple approximation: ~4 characters per token.
    
    Args:
        text: Input text to count tokens for
        model: Model name (for future use with tiktoken)
        
    Returns:
        Estimated token count
    """
    # Simple approximation: ~4 characters per token
    # For more accurate counting, consider using tiktoken library
    return len(text) // 4


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object pointing to the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


