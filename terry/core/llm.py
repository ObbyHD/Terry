"""
TERRY LLM Client - Synchronous, Offline-First
"""
import logging
import requests

logger = logging.getLogger(__name__)

class TerryLLM:
    """Simple LLM Client"""
    
    def __init__(self):
        self.cache = {}
        self.ollama_available = False
        self.model = None
        self.ollama_url = "http://localhost:11434"
        self.ollama_timeout = 10
        self._check_ollama()
    
    def _check_ollama(self):
        """Check Ollama - prefer llama2, fallback to any"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    # Prefer llama2 or llama2:latest
                    model_names = [m['name'] for m in models]
                    
                    # Check for llama2
                    for model_name in model_names:
                        if 'llama2' in model_name.lower():
                            self.model = model_name
                            self.ollama_available = True
                            logger.info(f"[OK] Using LLAMA2: {self.model}")
                            return
                    
                    # Fallback to first available
                    self.model = models[0]['name']
                    self.ollama_available = True
                    logger.info(f"[OK] Using Model: {self.model}")
                    return
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        
        self.ollama_available = False
        logger.info("[!] Using Offline Mode")
    
    def generate(self, prompt: str) -> str:
        """Generate response - sync"""
        cache_key = f"{prompt}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try Ollama
        if self.ollama_available:
            try:
                response = self._ollama_generate(prompt)
                if response and not response.startswith("Error"):
                    self.cache[cache_key] = response
                    return response
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")
        
        # Fallback
        response = self._fallback_response(prompt)
        self.cache[cache_key] = response
        return response
    
    def _ollama_generate(self, prompt: str) -> str:
        """Call Ollama (sync)"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": 150
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.ollama_timeout
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            
            logger.error(f"Ollama HTTP {response.status_code}")
            return None
        
        except requests.Timeout:
            logger.warning("Ollama timeout")
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None
    
    def _fallback_response(self, prompt: str) -> str:
        """Offline fallback - intelligente Antworten"""
        text = prompt.lower()
        
        # Greetings
        if any(w in text for w in ["hi", "hey", "hallo", "wassup", "yo", "yoyo", "was geht", "wie geht"]):
            return "Hey, alles klar! Was brauchst du?"
        
        # Tired
        if any(w in text for w in ["muede", "tired", "exhausted", "erschoepft"]):
            return "Entspannungsmusik? Gute Idee!"
        
        # Help questions
        if any(w in text for w in ["was kannst", "help", "hilfe", "kannst du"]):
            return "Ich kann Apps oeffnen, YouTube durchsuchen, Websites aufrufen. Sag mir einfach, was du brauchst!"
        
        # Open/Launch
        if any(w in text for w in ["oeffne", "open", "starte", "start", "launch", "ausf"]):
            return "OK, mache ich!"
        
        # Search/Play
        if any(w in text for w in ["suche", "search", "spiel", "play", "musik", "music", "video"]):
            return "Ich suche das fuer dich!"
        
        # General
        return "OK, verstanden!"

