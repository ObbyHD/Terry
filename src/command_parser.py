import re
import json
from typing import Dict, Any, List
import logging
import time
from src.llm_client import OllamaClient

logger = logging.getLogger(__name__)

class CommandParser:
    """TERRY AGENT - Intelligent multi-step command parser with LLM reasoning"""
    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
        
        # Quick lookup for simple commands
        self.app_map = {
            "chrome": "chrome", "browser": "chrome", "google chrome": "chrome",
            "firefox": "firefox", "mozilla": "firefox",
            "edge": "edge", "msedge": "edge",
            "excel": "excel", "liedekalc": "excel",
            "word": "word", "document": "word", "writer": "word",
            "powerpoint": "powerpoint", "ppt": "powerpoint",
            "notepad": "notepad", "notepad++": "notepad",
            "vscode": "vscode", "code": "vscode", "vs code": "vscode",
            "cmd": "cmd", "command prompt": "cmd", "terminal": "cmd",
            "powershell": "powershell", "ps": "powershell",
            "explorer": "explorer", "file explorer": "explorer",
        }
    
    async def parse(self, user_input: str) -> Dict[str, Any]:
        """TERRY AGENT - Parse natural language into actionable intents"""
        user_input = user_input.strip()
        start_time = time.time()
        
        logger.info(f"Terry parsing: '{user_input}'")
        
        # Quick check for simple commands
        simple = self._try_simple_parse(user_input)
        if simple:
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Simple match in {elapsed:.1f}ms")
            return simple
        
        # Complex command - use LLM to understand intent
        logger.info("Complex command detected - using Terry's intelligence")
        return await self._intelligent_parse(user_input)
    
    def _try_simple_parse(self, text: str) -> Dict[str, Any] | None:
        """Try quick regex patterns first"""
        text_lower = text.lower()
        
        # Simple app open
        if text_lower.startswith("öffne "):
            app_request = text_lower[6:].strip()
            for app_key, app_name in self.app_map.items():
                if app_key in app_request:
                    return {
                        "intent": "OPEN_APPLICATION",
                        "parameters": {"app": app_name},
                        "confidence": 0.95,
                        "method": "regex"
                    }
        
        # YouTube/Search
        if any(x in text_lower for x in ["youtube", "suche ", "google "]):
            return None  # Let LLM handle
        
        return None
    
    async def _intelligent_parse(self, user_input: str) -> Dict[str, Any]:
        """Use Terry's intelligence to parse complex commands"""
        
        # Build TERRY AGENT PROMPT
        system_prompt = """Du bist TERRY, ein intelligenter Desktop-Agent. Deine Aufgabe:
1. Verstehe komplexe Befehle mit mehreren Aktionen
2. Erkenne emotionalen Kontext (z.B. "ich bin müde", "mir ist langweilig")
3. Antworte EMPATHISCH und kurz (1-2 Sätze max)
4. Extrahiere ALLE Aktionen, die du ausführen musst

ANTWORTE IMMER IN DIESEM JSON-FORMAT:
{
  "emotion_detected": "müde/happy/confused/none",
  "sympathetic_response": "Kurze empathische Antwort",
  "actions": [
    {"action": "open_app", "app": "chrome"},
    {"action": "search_youtube", "query": "Entspannungsmusik"}
  ]
}

Erkenne DIESE Aktionsmuster:
- "öffne X" → open_app
- "suche X auf YouTube" → search_youtube
- "google X" / "suche X" → search_google
- "öffne URL" → open_url
- "starte X" → open_app
"""
        
        try:
            response = await self.llm.generate(user_input, system_prompt)
            logger.info(f"Terry Response: {response[:200]}")
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "intent": "MULTI_ACTION",
                    "parameters": {
                        "emotion": parsed.get("emotion_detected", "none"),
                        "response": parsed.get("sympathetic_response", ""),
                        "actions": parsed.get("actions", [])
                    },
                    "confidence": 0.85,
                    "method": "terry_agent"
                }
        except Exception as e:
            logger.error(f"Terry parsing error: {e}")
        
        # Fallback: Just answer the question
        return await self._simple_answer(user_input)
    
    async def _simple_answer(self, user_input: str) -> Dict[str, Any]:
        """Fallback - just answer as Terry"""
        prompt = f"Antworte kurz auf: {user_input}"
        system = "Du bist TERRY, ein hilfreicher Desktop-Assistent. Antworte prägnant (1-2 Sätze)."
        
        try:
            response = await self.llm.generate(prompt, system)
            return {
                "intent": "AI_RESPONSE",
                "parameters": {"response": response},
                "confidence": 0.7,
                "method": "terry_fallback"
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                "intent": "ERROR",
                "parameters": {"error": str(e)},
                "confidence": 0.0
            }
