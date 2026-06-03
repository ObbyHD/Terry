# Terry — Desktop AI Assistant

Lokaler Desktop-Assistent mit GUI. Nutzt Ollama (lokales LLM) — voll offline-fähig. Agent-System mit Chat-Memory, Executor für Aktionen, Tkinter-GUI.

## Stack
Python 3.x — Ollama, Tkinter (siehe `requirements.txt`)

## Setup
1. Ollama installieren: https://ollama.com
2. Modell laden: `ollama pull llama3.2`
3. Projekt:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. `Config.example.json` → `Config.json` kopieren, anpassen
5. Start:

```bash
python Main.py
# oder
start_jarvis.bat
```

## Hinweis
- `Config.json` ist gitignored (kann lokale Pfade/Settings enthalten)
- Logs (`terry.log`, `jarvis.log`, `debug.log`) werden lokal gehalten
