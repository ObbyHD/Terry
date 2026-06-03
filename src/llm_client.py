import requests
import json
import asyncio
from typing import Dict, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for Ollama LLM API - Optimized for speed"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = None):
        """Initialize with available Ollama model"""
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/generate"
        self.response_cache = {}
        
        # Auto-detect model if not specified
        if model:
            self.model = model
        else:
            self.model = self._auto_detect_model()
            logger.info(f"Auto-detected model: {self.model}")
    
    def _auto_detect_model(self) -> str:
        """Try to find an available model, fallback to common ones"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    model_name = models[0]['name']
                    logger.info(f"Found models: {[m['name'] for m in models]}")
                    logger.info(f"Using: {model_name}")
                    return model_name
        except Exception as e:
            logger.warning(f"Could not auto-detect model: {e}")
        
        # Fallback to common Ollama models
        fallback_models = ["mistral", "llama2", "neural-chat", "orca", "zephyr"]
        logger.warning(f"Trying fallback models: {fallback_models}")
        return "mistral"  # Most common default
    
    async def generate(self, prompt: str, system_context: str = "") -> str:
        """Async call to Ollama - optimized for speed"""
        # CACHE CHECK - avoid duplicate LLM calls
        cache_key = f"{prompt}:{system_context}"
        if cache_key in self.response_cache:
            logger.debug(f"Cache hit for: {prompt[:30]}")
            return self.response_cache[cache_key]
        
        full_prompt = f"{system_context}\n\nUser: {prompt}\nAnswer:" if system_context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.3,
            "top_p": 0.5,
            "num_predict": 100
        }
        
        try:
            logger.info(f"LLM Request to {self.model}: {prompt[:50]}")
            
            # Run blocking request in executor with LONGER timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(self.endpoint, json=payload, timeout=10)  # 10s max
                ),
                timeout=11.0  # 11s outer timeout
            )
            
            logger.info(f"LLM Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()['response'].strip()
                    if result:
                        self.response_cache[cache_key] = result
                        logger.info(f"LLM OK: {result[:60]}...")
                        return result
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Invalid response format: {e}")
                    return "Entschuldigung, ich habe ein Problem mit der Antwort."
            elif response.status_code == 404:
                logger.error(f"404: Modell nicht gefunden - {self.model}")
                return f"Das Modell '{self.model}' wurde nicht gefunden. Verfügbare Modelle: {self.get_available_models()}"
            else:
                logger.error(f"HTTP {response.status_code}: {response.text[:100]}")
                return f"Technischer Fehler: HTTP {response.status_code}"
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout nach 10+ Sekunden - Ollama nicht antwortet")
            return self._fallback_response(prompt)
        except requests.Timeout:
            logger.warning(f"Request Timeout")
            return self._fallback_response(prompt)
        except requests.ConnectionError as e:
            logger.error(f"Verbindung zu Ollama fehlgeschlagen: {e}")
            return "Ollama läuft nicht. Starte: ollama serve"
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Simple rule-based fallback when LLM is slow"""
        prompt_lower = prompt.lower()
        
        # Greeting responses
        if any(w in prompt_lower for w in ["hi", "hey", "hallo", "wassup", "yo", "was geht"]):
            responses = ["Heyo! Ich bin TERRY, dein persönlicher AI-Assistent. Wie kann ich dir helfen?",
                        "Hey da! Was brauchst du?"]
            return responses[hash(prompt) % len(responses)]
        
        # Emotion/Feeling responses
        if any(w in prompt_lower for w in ["müde", "tired", "erschöpft"]):
            return "Ich verstehe, dass du müde bist. Möchtest du, dass ich dir etwas Entspannendes öffne?"
        
        if any(w in prompt_lower for w in ["langweilig", "bored", "deprimiert"]):
            return "Mir ist klar, dass dir langweilig ist. Lass mich dir helfen - vielleicht YouTube oder eine Serie?"
        
        # How are you
        if any(w in prompt_lower for w in ["wie geht", "how are you", "alles gut"]):
            return "Mir geht es gut! Ich bin bereit, dir zu helfen. Was möchtest du tun?"
        
        # Help
        if any(w in prompt_lower for w in ["help", "hilfe", "was kannst"]):
            return "Ich kann Apps öffnen, YouTube durchsuchen, Chrome starten - sag einfach, was du brauchst!"
        
        # Default
        return "Interessant! Ich bin noch dabei, dich besser kennenzulernen. Was möchtest du, dass ich für dich tue?"
    
    def health_check(self) -> bool:
        """Check if Ollama is running synchronously"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✓ Ollama OK | Models: {len(models)}")
                if models:
                    logger.info(f"  Available models: {[m.get('name', 'unknown') for m in models[:3]]}")
                return True
            else:
                logger.error(f"Ollama HTTP Error: {response.status_code}")
                return False
        except requests.ConnectionError:
            logger.error("Cannot connect to Ollama - is it running? (ollama serve)")
            return False
        except Exception as e:
            logger.error(f"Ollama Health Check Failed: {str(e)}")
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
            return []
        except:
            return []
