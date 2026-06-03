"""
TERRY Agent - Dead Simple. Just works.
"""
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TerryAgent:
    """Dead simple agent - just understand what user wants"""
    
    def __init__(self, llm):
        self.llm = llm
        self.chat_history = []
        self.max_history = 10
        
    def add_to_history(self, role: str, content: str):
        """Add message to chat history"""
        self.chat_history.append({
            "role": role,
            "content": content
        })
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def _build_context(self) -> str:
        """Build chat context"""
        if len(self.chat_history) < 2:
            return ""
        context = "\n=== Previous Chat ===\n"
        for msg in self.chat_history[-6:]:
            context += f"{msg['role']}: {msg['content']}\n"
        return context
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """Process user input - DEAD SIMPLE"""
        self.add_to_history("User", user_input)
        
        # FIRST: Try to parse actions directly from user input
        actions = self._direct_parse_actions(user_input)
        
        # THEN: Get response from LLM
        # Build context if available
        context = self._build_context()
        
        short_prompt = f"""{context}

User: {user_input}

Du bist TERRY, ein intelligenter AI-Assistent. Antworte kurz und nett (1-2 Sätze).
- Wenn User einen Befehl gibt (App/Video/Website), antworte kurz und bestätigend
- Wenn User grüßt, antworte freundlich
- Wenn User dankbar ist, antworte nett
- Wenn User eine Frage stellt, antworte hilfreich

Wichtig: Halte die Antwort KURZ!"""
        
        response = self.llm.generate(short_prompt)
        
        # Clean response
        response = response.strip()[:200]
        if not response or "?" in response and len(response) > 150:
            response = "Alles klar!"
        
        logger.info(f"Response: {response[:80]} | Actions: {len(actions)}")
        
        # Store in history
        self.add_to_history("TERRY", response)
        
        return {
            "response": response if response else "OK",
            "actions": actions,
            "will": ""
        }
    
    def _direct_parse_actions(self, text: str) -> List[Dict[str, Any]]:
        """Parse actions DIRECTLY from user input - no LLM needed"""
        actions = []
        text_lower = text.lower()
        
        # FIREFOX / CHROME / EDGE
        if "firefox" in text_lower or "ff" in text_lower:
            actions.append({"type": "open_app", "app": "firefox"})
        if "chrome" in text_lower:
            actions.append({"type": "open_app", "app": "chrome"})
        if "edge" in text_lower:
            actions.append({"type": "open_app", "app": "edge"})
        
        # YOUTUBE
        if "youtube" in text_lower or "yt" in text_lower or "musik" in text_lower:
            query = "relaxing music"
            if "musik" in text_lower:
                query = "relaxing music"
            if any(word in text_lower for word in ["entspannung", "chill", "lofi", "relax", "gaming"]):
                query = "chill music"
            actions.append({"type": "search", "engine": "youtube", "query": query})
        
        # NAVIGATION
        sites = ["ebay", "amazon", "google", "twitter", "reddit", "github"]
        for site in sites:
            if site in text_lower:
                actions.append({"type": "navigate", "where": site})
        
        # VSCODE / EDITOR
        if "vscode" in text_lower or "code" in text_lower or "editor" in text_lower:
            actions.append({"type": "open_app", "app": "vscode"})
        
        # EXCEL / WORD
        if "excel" in text_lower or "tabelle" in text_lower:
            actions.append({"type": "open_app", "app": "excel"})
        if "word" in text_lower or "dokument" in text_lower:
            actions.append({"type": "open_app", "app": "word"})
        
        # TERMINAL / CMD
        if "cmd" in text_lower or "terminal" in text_lower or "powershell" in text_lower:
            actions.append({"type": "open_app", "app": "cmd"})
        
        logger.info(f"Direct parse: {len(actions)} actions from '{text[:50]}'")
        return actions
    
    def _parse_actions(self, will: str) -> List[Dict[str, Any]]:
        """Parse actions from WILL string (legacy)"""
        actions = []
        will_lower = will.lower()
        
        # Apps
        apps = {
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "edge",
            "excel": "excel",
            "word": "word",
            "vscode": "vscode",
            "cmd": "cmd",
            "explorer": "explorer",
            "spotify": "firefox",
        }
        
        for app_keyword, app_name in apps.items():
            if app_keyword in will_lower and f"open {app_name}" not in [a.get('app', '') for a in actions if a.get('type') == 'open_app']:
                actions.append({"type": "open_app", "app": app_name})
        
        # Search
        if "search" in will_lower or "youtube" in will_lower:
            search_patterns = [
                r"search (.+?)(?:on|$)",
                r"youtube (.+?)(?:$|,)",
                r"(?:suche|search)\s+(.+?)(?:$|,)"
            ]
            for pattern in search_patterns:
                match = re.search(pattern, will_lower)
                if match:
                    query = match.group(1).strip()
                    actions.append({"type": "search", "engine": "youtube", "query": query})
                    break
            
            if not any(a.get('type') == 'search' for a in actions):
                actions.append({"type": "search", "engine": "youtube", "query": "relaxing music"})
        
        # Navigate
        sites = ["ebay", "amazon", "github", "youtube", "google", "twitter", "reddit"]
        for site in sites:
            if f"navigate {site}" in will_lower or f"go {site}" in will_lower or f"geh {site}" in will_lower or f"zu {site}" in will_lower:
                actions.append({"type": "navigate", "where": site})
        
        logger.info(f"Parsed actions: {actions}")
        return actions

