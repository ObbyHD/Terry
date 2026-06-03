# Terry - Desktop AI Assistant

Local desktop assistant with a GUI. Uses Ollama (a locally running LLM) instead of cloud OpenAI, fully offline-capable. Agent system with chat memory, executor for actions, Tkinter GUI.

## Stack
Python 3.x Ollama, Tkinter (see `requirements.txt`)

## Setup
1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3.2`
3. Project:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `Config.example.json` → `Config.json` and adjust values
5. Run:

```bash
python Main.py
# or
start_jarvis.bat
```

## Note
- `Config.json` is gitignored (may contain local paths/settings)
- Log files (`terry.log`, `jarvis.log`, `debug.log`) are kept locally
