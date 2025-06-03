#!/usr/bin/env python3
"""
Voice Interface for Smart Bulb MCP Server

This module adds voice command capability to the MCP server,
creating a powerful hybrid system: Voice → AI → MCP → UDP → Bulb
"""

import asyncio
import speech_recognition as sr
import pyttsx3
from typing import Optional, Dict, Any
import logging
from .network_server import app, discovery, get_bulb

logger = logging.getLogger(__name__)


class VoiceInterface:
    """
    Voice interface that bridges speech commands to MCP actions.
    
    Architecture: Voice → STT → AI Processing → MCP Tools → UDP → Bulb
    """
    
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speech rate
        
        # Voice command patterns
        self.running = False
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                logger.info("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("✅ Microphone calibrated")
        except Exception as e:
            logger.error(f"❌ Microphone calibration failed: {e}")
    
    def speak(self, text: str):
        """Convert text to speech."""
        logger.info(f"🗣️ Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_command(self, timeout: float = 5.0) -> Optional[str]:
        """Listen for voice command and convert to text."""
        try:
            with self.microphone as source:
                logger.info("🎤 Listening for command...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
                
            # Convert speech to text
            logger.info("🔄 Processing speech...")
            command = self.recognizer.recognize_google(audio)
            logger.info(f"🎯 Recognized: '{command}'")
            return command.lower()
            
        except sr.WaitTimeoutError:
            logger.info("⏰ Listening timeout")
            return None
        except sr.UnknownValueError:
            logger.info("❓ Could not understand audio")
            self.speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Speech recognition error: {e}")
            self.speak("Speech recognition service error.")
            return None
    
    async def process_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Process voice command using AI reasoning + MCP tools.
        This is where the magic happens - voice gets AI intelligence!
        """
        logger.info(f"🧠 Processing command with AI: '{command}'")
        
        # Simple command mapping (you can enhance this with real AI)
        command = command.lower()
        
        try:
            # Light control commands
            if "turn on" in command or "lights on" in command:
                result = await self._handle_turn_on(command)
            elif "turn off" in command or "lights off" in command:
                result = await self._handle_turn_off(command)
            elif "brightness" in command or "dim" in command or "bright" in command:
                result = await self._handle_brightness(command)
            elif "color" in command or "red" in command or "blue" in command or "green" in command:
                result = await self._handle_color(command)
            elif "status" in command or "how are" in command:
                result = await self._handle_status(command)
            elif "discover" in command or "find" in command:
                result = await self._handle_discovery(command)
            else:
                result = {
                    "success": False,
                    "message": "I didn't understand that command. Try 'turn on lights' or 'set brightness to 50'."
                }
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing command: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_turn_on(self, command: str) -> Dict[str, Any]:
        """Handle turn on commands."""
        try:
            bulb = get_bulb()
            config = bulb.get_config()
            
            success = await bulb.turn_on()
            if success:
                return {
                    "success": True,
                    "message": f"Turned on bulb at {config.ip}:{config.port}",
                    "action": "turn_on"
                }
            else:
                return {"success": False, "message": "Failed to turn on the bulb"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_turn_off(self, command: str) -> Dict[str, Any]:
        """Handle turn off commands."""
        try:
            bulb = get_bulb()
            config = bulb.get_config()
            
            success = await bulb.turn_off()
            if success:
                return {
                    "success": True,
                    "message": f"Turned off bulb at {config.ip}:{config.port}",
                    "action": "turn_off"
                }
            else:
                return {"success": False, "message": "Failed to turn off the bulb"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_brightness(self, command: str) -> Dict[str, Any]:
        """Handle brightness commands with AI parsing."""
        try:
            # Extract brightness value from command
            brightness = self._extract_brightness(command)
            if brightness is None:
                return {"success": False, "message": "Please specify a brightness level, like 'set brightness to 75'"}
            
            bulb = get_bulb()
            config = bulb.get_config()
            
            success = await bulb.set_brightness(brightness)
            if success:
                return {
                    "success": True,
                    "message": f"Set brightness to {brightness}% on bulb at {config.ip}:{config.port}",
                    "action": "set_brightness",
                    "brightness": brightness
                }
            else:
                return {"success": False, "message": f"Failed to set brightness to {brightness}%"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_color(self, command: str) -> Dict[str, Any]:
        """Handle color commands with AI color recognition."""
        try:
            color_hex = self._extract_color(command)
            if not color_hex:
                return {"success": False, "message": "Please specify a color, like 'set color to red' or 'make it blue'"}
            
            bulb = get_bulb()
            config = bulb.get_config()
            
            success = await bulb.set_color_hex(color_hex)
            if success:
                return {
                    "success": True,
                    "message": f"Set color to {color_hex} on bulb at {config.ip}:{config.port}",
                    "action": "set_color",
                    "color": color_hex
                }
            else:
                return {"success": False, "message": f"Failed to set color to {color_hex}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_status(self, command: str) -> Dict[str, Any]:
        """Handle status inquiry commands."""
        try:
            bulb = get_bulb()
            config = bulb.get_config()
            status = await bulb.get_status()
            
            power_status = "on" if status.get("power", False) else "off"
            brightness = status.get("brightness", 0)
            
            return {
                "success": True,
                "message": f"Bulb at {config.ip}:{config.port} is {power_status} with {brightness}% brightness",
                "action": "get_status",
                "status": status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_discovery(self, command: str) -> Dict[str, Any]:
        """Handle bulb discovery commands."""
        try:
            logger.info("🔍 Discovering bulbs via voice command...")
            discovered = await discovery.discover_bulbs(timeout=5.0)
            
            if discovered:
                bulb_list = [f"{bulb.ip}:{bulb.port}" for bulb in discovered]
                return {
                    "success": True,
                    "message": f"Found {len(discovered)} bulbs: {', '.join(bulb_list)}",
                    "action": "discover",
                    "bulbs": bulb_list
                }
            else:
                return {
                    "success": True,
                    "message": "No smart bulbs found on the network",
                    "action": "discover",
                    "bulbs": []
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_brightness(self, command: str) -> Optional[int]:
        """Extract brightness value from voice command using simple parsing."""
        import re
        
        # Look for patterns like "50", "50%", "fifty percent"
        number_match = re.search(r'\b(\d{1,3})\b', command)
        if number_match:
            brightness = int(number_match.group(1))
            return min(100, max(0, brightness))  # Clamp to 0-100
        
        # Handle word numbers and descriptive terms
        word_mappings = {
            "dim": 20, "low": 25, "medium": 50, "high": 75, "bright": 90, "max": 100,
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, 
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
        }
        
        for word, value in word_mappings.items():
            if word in command:
                return value
        
        return None
    
    def _extract_color(self, command: str) -> Optional[str]:
        """Extract color from voice command."""
        color_mappings = {
            "red": "#FF0000", "green": "#00FF00", "blue": "#0000FF",
            "white": "#FFFFFF", "yellow": "#FFFF00", "purple": "#800080",
            "orange": "#FFA500", "pink": "#FFC0CB", "cyan": "#00FFFF",
            "warm": "#FFE4B5", "cool": "#E0FFFF", "warm white": "#FFF2CC"
        }
        
        for color_name, hex_value in color_mappings.items():
            if color_name in command:
                return hex_value
        
        return None
    
    async def start_voice_loop(self):
        """Start the main voice command loop."""
        self.running = True
        logger.info("🎤 Starting voice interface...")
        self.speak("Voice interface ready. Say a command.")
        
        while self.running:
            try:
                # Listen for wake word or direct command
                command = self.listen_for_command(timeout=10.0)
                
                if command:
                    # Process command
                    result = await self.process_voice_command(command)
                    
                    # Speak response
                    if result["success"]:
                        self.speak(result["message"])
                    else:
                        error_msg = result.get("message", result.get("error", "Command failed"))
                        self.speak(f"Error: {error_msg}")
                
                # Short pause between listening cycles
                await asyncio.sleep(0.5)
                
            except KeyboardInterrupt:
                logger.info("🛑 Voice interface stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Voice loop error: {e}")
                await asyncio.sleep(1)
        
        self.speak("Voice interface stopped.")
    
    def stop(self):
        """Stop the voice interface."""
        self.running = False


async def main():
    """Main entry point for voice-enabled smart bulb control."""
    voice_interface = VoiceInterface()
    
    try:
        await voice_interface.start_voice_loop()
    except KeyboardInterrupt:
        logger.info("Shutting down voice interface...")
    finally:
        voice_interface.stop()


if __name__ == "__main__":
    asyncio.run(main()) 