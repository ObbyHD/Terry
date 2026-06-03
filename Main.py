#!/usr/bin/env python3
"""
TERRY - Intelligent Desktop AI Assistant
New Clean Version
"""
import sys
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TERRY - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('terry.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("TERRY - Intelligent Desktop AI Assistant")
    logger.info("=" * 70)
    
    try:
        # Import components
        from terry.core.llm import TerryLLM
        from terry.core.agent import TerryAgent  # CHANGED: Agent not Parser
        from terry.core.executor import TerryExecutor
        from terry.ui.gui import TerryGUI
        
        logger.info("[OK] Components loaded")
        
        # Initialize
        llm = TerryLLM()
        agent = TerryAgent(llm)  # NEW: Agent with memory
        executor = TerryExecutor()
        gui = TerryGUI(agent, executor, llm)  # Pass agent not parser
        
        logger.info("[OK] TERRY initialized")
        logger.info(f"[OK] Ollama available: {llm.ollama_available}")
        logger.info("[OK] Agent system ready with chat memory")
        
        # Run GUI
        gui.run()
        
        logger.info("TERRY Shutdown - Goodbye!")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
