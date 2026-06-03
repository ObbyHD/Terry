"""
TERRY GUI - PySimpleGUI Interface with Agent
SIMPLE. SYNCHRONOUS. WORKS.
"""
import PySimpleGUI as sg
import threading
import logging
import time

logger = logging.getLogger(__name__)

class TerryGUI:
    """TERRY's GUI - Simple and direct"""
    
    def __init__(self, agent, executor, llm):
        self.agent = agent
        self.executor = executor
        self.llm = llm
        self.window = None
        self.running = True
        
        sg.theme('DarkBlack1')
        sg.set_options(font=('Courier New', 11))
    
    def build(self):
        """Build GUI"""
        layout = [
            [sg.Text('[TERRY] - AI Assistant', font=('Courier New', 16, 'bold'), text_color='#00ff00')],
            [sg.Text('Status: Ready', key='-STATUS-', text_color='#00ff00', size=(80, 1))],
            [sg.Multiline(
                default_text="TERRY: Ready! Give me a command...\n",
                size=(100, 20), 
                key='-OUTPUT-', 
                disabled=True,
                text_color='#00ff00',
                background_color='#0a0a0a',
                font=('Courier New', 10)
            )],
            [sg.InputText(
                key='-INPUT-',
                size=(90, 1),
                focus=True,
                background_color='#1a1a1a',
                text_color='#00ff00'
            )],
            [sg.Button('Send', size=(10, 1), button_color=('#000000', '#00ff00')),
             sg.Button('Clear', size=(10, 1), button_color=('#000000', '#ffaa00')),
             sg.Button('Exit', size=(10, 1), button_color=('#000000', '#ff0000'))]
        ]
        
        self.window = sg.Window('TERRY', layout, finalize=True)
        self.window['-STATUS-'].update(f"[OK] TERRY ready (Ollama: {'YES' if self.llm.ollama_available else 'NO'})")
    
    def append_output(self, message: str):
        """Add to output"""
        current = self.window['-OUTPUT-'].get()
        self.window['-OUTPUT-'].update(current + message)
    
    def update_status(self, status: str):
        """Update status"""
        self.window['-STATUS-'].update(status, text_color='#00ff00')
    
    def process_command(self, user_input: str):
        """Process in background thread"""
        def run():
            try:
                start = time.time()
                self.append_output(f"You: {user_input}\n")
                self.update_status("Processing...")
                
                # Simple & direct - Agent processes
                agent_result = self.agent.process(user_input)
                
                response = agent_result.get("response", "...")
                actions = agent_result.get("actions", [])
                will = agent_result.get("will", "")
                
                # Execute actions
                if actions:
                    results = self.executor.execute_all(actions)
                    exec_msg = " | ".join(results)
                else:
                    exec_msg = "No actions"
                
                elapsed = (time.time() - start) * 1000
                
                # Display
                self.append_output(f"TERRY: {response}\n")
                if will:
                    self.append_output(f"  (will: {will})\n")
                self.append_output(f"  > {exec_msg}\n\n")
                
                self.update_status(f"Ready ({elapsed:.0f}ms)")
            
            except Exception as e:
                logger.error(f"Error: {e}")
                self.append_output(f"TERRY: ERROR - {str(e)[:80]}\n")
                self.update_status("ERROR!")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def run(self):
        """Main GUI loop"""
        self.build()
        
        while self.running:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                self.running = False
                break
            
            if event == 'Send':
                user_input = values['-INPUT-'].strip()
                if user_input:
                    self.process_command(user_input)
                    self.window['-INPUT-'].update('')
            
            if event == 'Clear':
                self.window['-OUTPUT-'].update('')
        
        self.window.close()
