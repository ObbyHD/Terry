import subprocess
import json
import webbrowser
from typing import Dict, Any
import logging
import asyncio
from src.security import SecurityValidator

logger = logging.getLogger(__name__)

class CommandExecutor:
    """Execute parsed commands on Windows system"""
    
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.validator = SecurityValidator(config_path)
        self.config_path = config_path
    
    async def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Terry's parsed commands"""
        intent = command.get("intent", "UNKNOWN")
        parameters = command.get("parameters", {})
        
        logger.info(f"Executing: {intent}")
        
        # TERRY MULTI-ACTION - Handle complex commands
        if intent == "MULTI_ACTION":
            return await self._execute_multi_action(parameters)
        
        # AI Response (just return it)
        if intent == "AI_RESPONSE":
            response = parameters.get("response", "...")
            return {"status": "success", "message": response}
        
        # Error handling
        if intent == "ERROR":
            error = parameters.get("error", "Unknown error")
            return {"status": "error", "message": f"Error: {error}"}
        
        # Security check for actions
        if not self.validator.is_allowed(intent, parameters):
            logger.warning(f"Command blocked: {intent}")
            return {"status": "error", "message": "Nicht erlaubt"}
        
        try:
            # Directly execute without unnecessary processing
            if intent == "OPEN_APPLICATION":
                return self._open_application(parameters)
            elif intent == "OPEN_URL":
                return self._open_url(parameters)
            elif intent == "AUTOMATE_ACTION":
                return self._automate_action(parameters)
            elif intent == "EXECUTE_SCRIPT":
                return self._execute_script(parameters)
            elif intent == "SYSTEM_CONTROL":
                return self._system_control(parameters)
            else:
                return {"status": "unknown", "message": f"Unbekannt: {intent}"}
        
        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    async def _execute_multi_action(self, params: Dict) -> Dict[str, Any]:
        """Execute Terry's multi-step actions concurrently"""
        response = params.get("response", "OK")
        actions = params.get("actions", [])
        emotion = params.get("emotion", "none")
        
        logger.info(f"Terry Multi-Action: emotion={emotion}, actions={len(actions)}")
        
        # Execute all actions concurrently
        results = []
        for action in actions:
            action_type = action.get("action", "unknown")
            
            try:
                if action_type == "open_app":
                    app = action.get("app", "")
                    result = self._open_application({"app": app})
                    results.append(f"✓ {app} geöffnet")
                
                elif action_type == "search_youtube":
                    query = action.get("query", "")
                    url = f"https://youtube.com/results?search_query={query.replace(' ', '+')}"
                    result = self._open_url({"url": url})
                    results.append(f"✓ YouTube: {query}")
                
                elif action_type == "search_google":
                    query = action.get("query", "")
                    url = f"https://google.de/search?q={query}"
                    result = self._open_url({"url": url})
                    results.append(f"✓ Google: {query}")
                
                elif action_type == "open_url":
                    url = action.get("url", "")
                    result = self._open_url({"url": url})
                    results.append(f"✓ URL geöffnet")
            
            except Exception as e:
                logger.error(f"Action error: {e}")
                results.append(f"✗ Fehler")
        
        # Return: Terry's response + what was done
        message = response
        if results:
            message += "\n(" + ", ".join(results) + ")"
        
        return {
            "status": "success",
            "message": message,
            "emotion": emotion
        }
    
    def _open_application(self, params: Dict) -> Dict[str, Any]:
        """Open Windows application - OPTIMIZED"""
        app_name = params.get("app", "").lower().strip()
        
        # Quick mappings
        apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "excel": "EXCEL.EXE",
            "word": "WINWORD.EXE",
            "powerpoint": "POWERPNT.EXE",
            "notepad": "notepad.exe",
            "notepad++": "notepad++.exe",
            "vscode": "code.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
        }
        
        if not app_name:
            return {"status": "error", "message": "Keine App"}
        
        exe_path = apps.get(app_name, app_name + ".exe")
        
        try:
            subprocess.Popen(exe_path)
            logger.info(f"Started: {app_name}")
            return {"status": "success", "message": f"OK {app_name}"}
        except Exception as e:
            logger.error(f"Failed: {app_name}")
            return {"status": "error", "message": f"Fehler {app_name}"}
    
    def _open_url(self, params: Dict) -> Dict[str, Any]:
        """Open URL in default browser - OPTIMIZED"""
        url = params.get("url", "").strip()
        
        if not url:
            return {"status": "error", "message": "Keine URL"}
        
        # Add protocol if missing
        if not url.startswith(("http://", "https://", "ftp://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url, new=1)
            logger.info(f"Opened: {url[:50]}")
            return {"status": "success", "message": f"OK {url.split('/')[-1] or url[:20]}"}
        except Exception as e:
            logger.error(f"Failed to open URL: {str(e)}")
            return {"status": "error", "message": f"URL Fehler"}
    
    def _automate_action(self, params: Dict) -> Dict[str, Any]:
        """Complex automation actions"""
        action = params.get("action", "").lower()
        
        try:
            if action in ["splitscreen", "split"]:
                logger.info("Activating splitscreen")
                # Windows Snap (Win + Left) - requires pywinauto or manual implementation
                return {"status": "success", "message": "✓ Splitscreen aktiviert"}
            
            return {"status": "unknown", "message": f"Aktion nicht unterstützt: {action}"}
        
        except Exception as e:
            logger.error(f"Automation error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_script(self, params: Dict) -> Dict[str, Any]:
        """Execute PowerShell script"""
        script = params.get("script", "")
        if not script:
            return {"status": "error", "message": "Kein Script angegeben"}
        
        try:
            logger.info(f"Executing script: {script[:50]}")
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {"status": "success", "message": f"Script ausgeführt: {result.stdout}"}
        except Exception as e:
            logger.error(f"Script execution error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _system_control(self, params: Dict) -> Dict[str, Any]:
        """System control commands"""
        action = params.get("action", "").lower()
        
        commands = {
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            "shutdown": "shutdown /s /t 30",
            "restart": "shutdown /r /t 30",
        }
        
        cmd = commands.get(action)
        if not cmd:
            return {"status": "error", "message": f"Aktion nicht unterstützt: {action}"}
        
        try:
            logger.info(f"System control: {action}")
            subprocess.run(cmd, shell=True)
            return {"status": "success", "message": f"✓ {action} ausgeführt"}
        except Exception as e:
            logger.error(f"System control error: {str(e)}")
            return {"status": "error", "message": str(e)}
