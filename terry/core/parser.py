"""
TERRY Intelligent Command Parser - Multi-Action Support
"""
import asyncio
import logging
import json
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TerryParser:
    """Intelligent command parser with multi-action support"""
    
    def __init__(self, llm):
        self.llm = llm
        self.app_keywords = {
            "chrome": ["chrome", "browser", "google", "chromen"],
            "firefox": ["firefox", "mozilla"],
            "edge": ["edge", "msedge"],
            "excel": ["excel", "calc"],
            "word": ["word", "document", "writer"],
            "powerpoint": ["powerpoint", "ppt"],
            "notepad": ["notepad", "text editor"],
            "vscode": ["vscode", "code", "vs code"],
            "cmd": ["cmd", "command prompt", "terminal", "powershell"],
            "powershell": ["powershell", "ps"],
            "explorer": ["explorer", "file manager"],
        }
        
        # Action patterns - stricter matching
        self.action_patterns = {
            "open_app": r"(?:öffne|starte|open|launch|start)\s+(\w+)",
            "search_youtube": r"(?:youtube|suche auf youtube|yt|tube)\s+(?:nach\s+)?([^.!?]+?)(?:\.|$|!|$)",
            "search_google": r"(?:google|suche|search)\s+([^.!?]+?)(?:\.|$|!|$)",
        }
    
    async def parse(self, user_input: str) -> Dict[str, Any]:
        """Parse user input into actionable commands"""
        user_input = user_input.strip()
        logger.info(f"Parsing: {user_input[:80]}")
        
        # WICHTIG: Nutze IMMER LLM für echte Verstehung, nicht nur Fallback!
        # Der LLM ist viel intelligenter als einfaches Regex-Matching
        return await self._intelligent_parse(user_input)
    
    async def _intelligent_parse(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to understand ALL commands intelligently"""
        
        # Prompt für LLM - EXTREM detailliert!
        prompt = f"""Analysiere diesen Benutzer-Input und extrahiere ALLE relevanten Informationen:
Input: "{user_input}"

Antworte im JSON Format, auch wenn es nur eine Frage/Gruß ist:
{{
  "has_greeting": true/false,
  "greeting_response": "optional empathische kurze Antwort auf den Gruß",
  "actions": [
    {{"action": "open_app", "app": "chrome"}},
    {{"action": "search_youtube", "query": "Entspannungsmusik"}}
  ],
  "confidence": 0.0-1.0
}}

WICHTIG - Diese Variationen alle erkennen und konvertieren:
- "öffne chrome" → open_app: chrome
- "chrome öffnen" → open_app: chrome
- "starte firefox" → open_app: firefox
- "ich will youtube" → search_youtube oder open_app
- "suche musik" → search_youtube
- "google das" → search_google
- "ebay aufrufen" → kombiniert: open_app: firefox / chrome, DANN navigate ebay

Apps erkennen: chrome, firefox, edge, excel, word, powerpoint, notepad, vscode, cmd, powershell, explorer

WICHTIG: Wenn jemand sagt "öffne firefox und ebay", dann:
- action 1: open_app firefox
- action 2: open_url ebay.de

Erkenne diese Kombinationen:
- "öffne X und suche Y" → open_app + search
- "öffne X auf Y" → open_app X, dann navigate zu Y
- "du vollidiot sollst X" → Erkenne trotzdem den Befehl X!

Antworte IMMER gültiges JSON!"""
        
        try:
            response = await self.llm.generate(prompt)
            logger.info(f"LLM Response: {response[:150]}")
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                
                # Build result
                result = {
                    "intent": "MULTI_ACTION",
                    "actions": parsed.get("actions", []),
                    "response": parsed.get("greeting_response", "OK"),
                    "confidence": parsed.get("confidence", 0.8),
                    "has_greeting": parsed.get("has_greeting", False)
                }
                
                logger.info(f"Parsed: actions={len(result['actions'])}, greeting={result['has_greeting']}")
                return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
        except Exception as e:
            logger.error(f"LLM error: {e}")
        
        # Fallback: einfach antworten
        return {
            "intent": "RESPONSE_ONLY",
            "response": await self.llm.generate(f"Antworte kurz auf: {user_input}"),
            "confidence": 0.5
        }
