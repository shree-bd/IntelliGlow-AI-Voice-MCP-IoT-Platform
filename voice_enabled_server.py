#!/usr/bin/env python3
"""
🎤 IntelliGlow - Complete Voice + AI Smart Lighting System

This script runs the complete IntelliGlow experience:
- 🎤 Voice Commands: "Turn on lights", "Set brightness to 75", "Make it blue"
- 🧠 AI Integration: Full MCP server for Claude/GPT integration  
- 📡 UDP Networking: Direct communication with real smart bulbs
- 🔧 Smart Features: Understands context, natural language, and workflows

Usage:
    python voice_enabled_server.py

Example Voice Commands:
    "IntelliGlow, turn on the lights"
    "Set brightness to 50 percent"
    "Make it a warm yellow color"
    "How are the lights doing?"
    "Find smart bulbs on the network"
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceEnabledServer:
    """
    Combines MCP server with voice interface for the ultimate smart bulb control.
    
    Features:
    - Voice commands for convenience (like Alexa)
    - AI reasoning for intelligence (better than Alexa)
    - Direct UDP control for speed (faster than cloud)
    - MCP integration for extensibility (open ecosystem)
    """
    
    def __init__(self):
        self.mcp_server_task: Optional[asyncio.Task] = None
        self.voice_interface_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def start_mcp_server(self):
        """Start the MCP server in the background."""
        try:
            logger.info("🚀 Starting MCP server...")
            from mcp_server_smartbulb.network_server import main as mcp_main
            await mcp_main()
        except Exception as e:
            logger.error(f"❌ MCP server error: {e}")
    
    async def start_voice_interface(self):
        """Start the voice interface."""
        try:
            logger.info("🎤 Starting voice interface...")
            
            # Check if voice dependencies are available
            try:
                import speech_recognition
                import pyttsx3
            except ImportError as e:
                logger.error("❌ Voice dependencies not installed!")
                logger.info("💡 Install with: pip install -e .[voice]")
                return
            
            from mcp_server_smartbulb.voice_interface import VoiceInterface
            voice = VoiceInterface()
            await voice.start_voice_loop()
            
        except Exception as e:
            logger.error(f"❌ Voice interface error: {e}")
    
    async def start_combined_system(self):
        """Start both MCP server and voice interface."""
        self.running = True
        logger.info("🌟 Starting Voice-Enabled Smart Bulb System...")
        
        try:
            # Start both systems concurrently
            self.mcp_server_task = asyncio.create_task(self.start_mcp_server())
            
            # Give MCP server time to initialize
            await asyncio.sleep(2)
            
            self.voice_interface_task = asyncio.create_task(self.start_voice_interface())
            
            # Wait for both to complete
            await asyncio.gather(
                self.mcp_server_task,
                self.voice_interface_task,
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"❌ System error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("🧹 Cleaning up...")
        
        if self.voice_interface_task and not self.voice_interface_task.done():
            self.voice_interface_task.cancel()
        
        if self.mcp_server_task and not self.mcp_server_task.done():
            self.mcp_server_task.cancel()
        
        self.running = False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, shutting down...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point for the voice-enabled server."""
    print("🌟 Voice-Enabled Smart Bulb MCP Server")
    print("=" * 50)
    print("🎤 Voice Commands: 'turn on lights', 'set brightness to 75', 'make it blue'")
    print("🤖 AI Integration: Claude can control via MCP protocol")
    print("📡 UDP Networking: Direct communication with real bulbs")
    print("🏠 Default Bulb: 192.168.1.45:4000")
    print("=" * 50)
    
    server = VoiceEnabledServer()
    server.setup_signal_handlers()
    
    try:
        await server.start_combined_system()
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        await server.cleanup()


if __name__ == "__main__":
    """
    Run the combined voice + MCP system.
    
    Usage:
    1. MCP only: python -m mcp_server_smartbulb.network_server
    2. Voice only: python -m mcp_server_smartbulb.voice_interface  
    3. Combined: python voice_enabled_server.py
    """
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Run the combined system
    asyncio.run(main()) 