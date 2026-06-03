import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validate commands against security policies"""
    
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.security = self.config.get("security", {})
        self.whitelist_mode = self.security.get("whitelist_mode", False)
        logger.info(f"Security: Whitelist Mode = {self.whitelist_mode}")
    
    def is_allowed(self, intent: str, parameters: Dict[str, Any]) -> bool:
        """Check if command is allowed"""
        
        # If whitelist disabled, allow all
        if not self.whitelist_mode:
            logger.debug(f"Whitelist disabled - allowing: {intent}")
            return True
        
        # Check specific intents
        if intent == "OPEN_APPLICATION":
            app = parameters.get("app", "").lower()
            allowed = app in self.security.get("allowed_apps", [])
            logger.info(f"App whitelist check '{app}': {allowed}")
            return allowed
        
        elif intent == "OPEN_URL":
            url = parameters.get("url", "")
            allowed_urls = self.security.get("allowed_urls", [])
            allowed = any(domain in url.lower() for domain in allowed_urls)
            logger.info(f"URL whitelist check '{url}': {allowed}")
            return allowed
        
        elif intent in self.security.get("blocked_commands", []):
            logger.warning(f"Command in blocklist: {intent}")
            return False
        
        logger.debug(f"Allowing intent: {intent}")
        return True
