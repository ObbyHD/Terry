"""
TERRY Executor - Execute what the agent wants
"""
import subprocess
import webbrowser
import logging
import os
import time

logger = logging.getLogger(__name__)

class TerryExecutor:
    """Execute commands - simple and effective"""
    
    def __init__(self):
        self.results = []
    
    def execute_all(self, actions: list) -> list:
        """Execute all actions from agent"""
        results = []
        
        if not actions:
            return ["[OK] No actions"]
        
        for action in actions:
            try:
                action_type = action.get("type", "").lower()
                
                if action_type == "open_app":
                    result = self._open_app(action.get("app", ""))
                    results.append(result)
                
                elif action_type == "search":
                    result = self._search(action.get("engine", "youtube"), action.get("query", ""))
                    results.append(result)
                
                elif action_type == "navigate":
                    result = self._navigate(action.get("where", ""))
                    results.append(result)
                
                elif action_type == "terminal":
                    result = self._run_command(action.get("command", ""))
                    results.append(result)
                
                time.sleep(0.2)  # Small delay between actions
            
            except Exception as e:
                logger.error(f"Execution error: {e}")
                results.append(f"[ERROR] {str(e)[:50]}")
        
        return results
    
    def _open_app(self, app_name: str) -> str:
        """Open application"""
        if not app_name:
            return "[ERROR] No app specified"
        
        app = app_name.lower().strip()
        
        # Map apps to executables
        app_paths = {
            "chrome": ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                      "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"],
            "firefox": ["C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                       "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"],
            "edge": ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"],
            "explorer": ["explorer.exe"],
            "notepad": ["notepad.exe"],
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe"],
            "vscode": ["code.exe", "C:\\Users\\AlexS\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"],
            "excel": ["C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"],
            "word": ["C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"],
        }
        
        if app not in app_paths:
            return f"[ERROR] Unknown app: {app}"
        
        paths = app_paths[app]
        
        for path in paths:
            try:
                if os.path.exists(path):
                    subprocess.Popen(path, shell=True)
                    logger.info(f"[OK] Opened {app}")
                    return f"[OK] Opened {app}"
            except Exception as e:
                logger.debug(f"Failed path {path}: {e}")
        
        # Fallback - try direct name
        try:
            subprocess.Popen(app, shell=True)
            logger.info(f"[OK] Opened {app} (fallback)")
            return f"[OK] Opened {app}"
        except:
            return f"[ERROR] Could not open {app}"
    
    def _search(self, engine: str, query: str) -> str:
        """Search on engine"""
        engine = engine.lower().strip()
        
        if not query:
            query = "music"
        
        urls = {
            "youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "google": f"https://www.google.de/search?q={query.replace(' ', '+')}",
            "ebay": f"https://www.ebay.de/sch/i.html?_nkw={query.replace(' ', '+')}",
            "amazon": f"https://www.amazon.de/s?k={query.replace(' ', '+')}"
        }
        
        if engine not in urls:
            engine = "youtube"
        
        try:
            webbrowser.open(urls[engine])
            logger.info(f"[OK] Searched {engine} for: {query}")
            return f"[OK] Searching {engine} for: {query}"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"[ERROR] Search failed"
    
    def _navigate(self, where: str) -> str:
        """Navigate to site"""
        where = where.lower().strip()
        
        sites = {
            "ebay": "https://www.ebay.de",
            "amazon": "https://www.amazon.de",
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "twitter": "https://www.twitter.com",
            "reddit": "https://www.reddit.com",
            "twitch": "https://www.twitch.tv"
        }
        
        if where not in sites:
            return f"[ERROR] Site unknown: {where}"
        
        try:
            webbrowser.open(sites[where])
            logger.info(f"[OK] Navigated to {where}")
            return f"[OK] Navigated to {where}"
        except Exception as e:
            logger.error(f"Navigate error: {e}")
            return f"[ERROR] Navigation failed"
    
    def _run_command(self, command: str) -> str:
        """Run terminal command"""
        if not command:
            return "[ERROR] No command"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout[:100] if result.stdout else result.stderr[:100]
            logger.info(f"[OK] Command executed: {command[:30]}")
            return f"[OK] {output}"
        except subprocess.TimeoutExpired:
            return "[ERROR] Command timeout"
        except Exception as e:
            logger.error(f"Command error: {e}")
            return f"[ERROR] {str(e)[:50]}"

