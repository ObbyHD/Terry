"""
TERRY Configuration Management
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

class Config:
    """TERRY Configuration"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.settings = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or use defaults"""
        defaults = {
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434",
                "timeout": 10,
                "auto_detect_model": True,
                "fallback_model": "mistral"
            },
            "terry": {
                "name": "TERRY",
                "startup_message": "Ich bin TERRY, dein persönlicher AI-Assistent!",
                "debug": False
            },
            "ui": {
                "theme": "DarkBlack1",
                "font_size": 11,
                "window_width": 100,
                "window_height": 25
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    logger.info(f"Loaded config from {self.config_file}")
                    # Merge loaded config with defaults
                    return {**defaults, **loaded}
            except Exception as e:
                logger.warning(f"Could not load config: {e}. Using defaults.")
                return defaults
        
        # Save defaults if no config file exists
        self._save_config(defaults)
        return defaults
    
    def _save_config(self, config: dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                logger.info(f"Saved config to {self.config_file}")
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split(".")
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split(".")
        config = self.settings
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.settings)

# Global config instance
config = Config()
