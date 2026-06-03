import sys
import asyncio
import threading
import time
import PySimpleGUI as sg
from src.llm_client import OllamaClient
from src.command_parser import CommandParser
from src.executor import CommandExecutor
import logging

logger = logging.getLogger(__name__)

# Initialize PySimpleGUI theme
sg.theme('DarkBlack1')
sg.set_options(font=('Courier New', 11), element_padding=(10, 10))

class JarvisGUI:
    """TERRY AI Assistant GUI using PySimpleGUI - OPTIMIZED"""
    
    def __init__(self):
        # LAZY LOAD: Don't initialize everything at once
        self.llm_client = None
        self.parser = None
        self.executor = None
        self.window = None
        self.is_processing = False
        self.ollama_ready = False
        
        logger.info("GUI initialized (lazy loading)")
    
    def _lazy_init(self):
        """Initialize components on first use (not on startup)"""
        if self.llm_client is None:
            logger.info("Lazy loading components...")
            self.llm_client = OllamaClient()
            self.parser = CommandParser(self.llm_client)
            self.executor = CommandExecutor()
            logger.info("Components loaded")
    
    def build_window(self):
        """Build UI layout"""
        layout = [
            [sg.Text('TERRY - AI Assistant', font=('Courier New', 16, 'bold'), text_color='#00ff00')],
            [sg.Text('Status: Initialisieren...', key='-STATUS-', text_color='#ffaa00', size=(60, 1))],
            [sg.Multiline(size=(80, 20), key='-OUTPUT-', disabled=True, 
                         text_color='#00ff00', background_color='#0a0a0a')],
            [sg.InputText(key='-INPUT-', size=(70, 1), focus=True, 
                         background_color='#1a1a1a', text_color='#00ff00')],
            [sg.Button('Senden', size=(10, 1), button_color=('#000000', '#00ff00')),
             sg.Button('Clear', size=(10, 1), button_color=('#000000', '#ffaa00')),
             sg.Button('Quit', size=(10, 1), button_color=('#000000', '#ff0000'))]
        ]
        
        self.window = sg.Window('Jarvis - Local AI Assistant', layout, 
                               finalize=True, icon=None)
        
        # Bind Enter key
        self.window['-INPUT-'].bind('<Return>', '_Return')
        
        return self.window
    
    def check_ollama_status(self):
        """Check Ollama and update status - ASYNC"""
        def check_async():
            try:
                self._lazy_init()
                if self.llm_client.health_check():
                    models = self.llm_client.get_available_models()
                    status = f"✓ TERRY aktiv | Model: {self.llm_client.model} | Models: {len(models)}"
                    self.append_output("TERRY: Bereit! Befehl eingeben...", color='green')
                    self.window['-STATUS-'].update(status, text_color='#00ff00')
                    self.ollama_ready = True
                else:
                    status = "✗ Ollama nicht erreichbar"
                    self.append_output("TERRY: Ollama nicht gefunden. Starte: ollama serve", color='red')
                    self.window['-STATUS-'].update(status, text_color='#ff0000')
                    self.ollama_ready = False
            except Exception as e:
                logger.error(f"Ollama check failed: {e}")
                self.ollama_ready = False
        
        # Check in background thread (non-blocking)
        thread = threading.Thread(target=check_async, daemon=True)
        thread.start()
    
    def append_output(self, message: str, color='green'):
        """Append message to output display"""
        current = self.window['-OUTPUT-'].get()
        
        # Simple text append
        new_text = current + message + '\n' if current else message + '\n'
        self.window['-OUTPUT-'].update(new_text)
        self.window.refresh()
    
    def process_command_async(self, user_input: str):
        """Process command in async thread - INSTANT!"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                start_time = time.time()
                
                # Parse (INSTANT - < 5ms for standard commands)
                command = loop.run_until_complete(self.parser.parse(user_input))
                parse_time = (time.time() - start_time) * 1000
                
                # Show result
                intent = command.get('intent', 'UNKNOWN')
                method = command.get('method', 'unknown')
                
                if intent == "UNKNOWN":
                    self.append_output(f"  [NO MATCH] - unbekannter Befehl", color='orange')
                    self.window['-STATUS-'].update("Ready", text_color='#00ff00')
                else:
                    self.append_output(f"  [{method.upper()}] {parse_time:.0f}ms", color='orange')
                    
                    # Execute immediatly (also very fast)
                    exec_start = time.time()
                    result = loop.run_until_complete(self.executor.execute(command))
                    exec_time = (time.time() - exec_start) * 1000
                    
                    message = result.get("message", "OK")
                    total_time = (time.time() - start_time) * 1000
                    
                    self.append_output(f"TERRY: {message} ({total_time:.0f}ms total)", color='green')
                    self.window['-STATUS-'].update(f"Ready ({total_time:.0f}ms)", text_color='#00ff00')
            
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                self.append_output(f"TERRY: ERROR - {str(e)}", color='red')
                self.window['-STATUS-'].update("ERROR", text_color='#ff0000')
            finally:
                self.is_processing = False
                loop.close()
        
        # Run in background thread
        self.is_processing = True
        self.window['-STATUS-'].update("Processing...", text_color='#ffaa00')
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def run(self):
        """Run GUI event loop - OPTIMIZED startup"""
        self.build_window()
        self.check_ollama_status()  # Non-blocking now
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                break
            
            if (event == 'Senden' or event == '-INPUT-_Return') and not self.is_processing:
                user_input = values['-INPUT-'].strip()
                if user_input:
                    self.append_output(f"User: {user_input}", color='green')
                    self.window['-INPUT-'].update('')
                    # Try lazy init if not done
                    if self.llm_client is None:
                        self._lazy_init()
                    self.process_command_async(user_input)
            
            if event == 'Clear':
                self.window['-OUTPUT-'].update('')
        
        self.window.close()

def main():
    """Launch Jarvis GUI"""
    gui = JarvisGUI()
    gui.run()

if __name__ == "__main__":
    main()

