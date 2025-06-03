"""
UDP Client for Smart Bulb Communication

This module provides UDP-based communication with real smart bulbs,
matching the functionality of the TypeScript implementation.
"""

import asyncio
import json
import socket
import uuid
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BulbConfig:
    """Configuration for a smart bulb connection."""
    ip: str
    port: int
    timeout: float = 5.0


@dataclass 
class BulbCommand:
    """Command to send to a smart bulb."""
    command: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


@dataclass
class BulbResponse:
    """Response from a smart bulb."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    id: Optional[str] = None


class UDPBulbClient:
    """
    UDP client for communicating with real smart bulbs.
    
    This mirrors the TypeScript SmartBulb class functionality but in Python,
    providing real network communication with physical bulbs.
    """
    
    def __init__(self, config: BulbConfig):
        self.config = config
        self.pending_commands: Dict[str, asyncio.Future] = {}
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.last_status: Dict[str, Any] = {
            "power": False,
            "brightness": 0,
            "color": {"r": 255, "g": 255, "b": 255},
            "connected": False
        }
        
    async def connect(self) -> None:
        """Establish UDP connection to the bulb."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.config.timeout)
            self.running = True
            
            # Test connection with ping
            await self.ping()
            self.last_status["connected"] = True
            logger.info(f"Connected to bulb at {self.config.ip}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to bulb: {e}")
            self.last_status["connected"] = False
            raise
    
    def generate_command_id(self) -> str:
        """Generate unique command ID."""
        return str(uuid.uuid4())[:8]
    
    async def send_command(self, command: BulbCommand) -> BulbResponse:
        """
        Send a command to the bulb and wait for response.
        
        This matches the TypeScript sendCommand functionality.
        """
        if not self.socket or not self.running:
            raise ConnectionError("Not connected to bulb")
        
        # Generate command ID if not provided
        if not command.id:
            command.id = self.generate_command_id()
        
        # Prepare command
        command_data = {
            "command": command.command,
            "id": command.id
        }
        if command.params:
            command_data["params"] = command.params
        
        # Create future for response
        response_future = asyncio.get_event_loop().create_future()
        self.pending_commands[command.id] = response_future
        
        try:
            # Send UDP packet
            message = json.dumps(command_data).encode('utf-8')
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.socket.sendto, 
                message, 
                (self.config.ip, self.config.port)
            )
            
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=self.config.timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Command {command.command} timed out")
            return BulbResponse(success=False, error="Command timeout", id=command.id)
        except Exception as e:
            logger.error(f"Failed to send command {command.command}: {e}")
            return BulbResponse(success=False, error=str(e), id=command.id)
        finally:
            # Clean up pending command
            self.pending_commands.pop(command.id, None)
    
    async def turn_on(self) -> bool:
        """Turn on the bulb."""
        command = BulbCommand(command="set_power", params={"power": True})
        response = await self.send_command(command)
        
        if response.success:
            self.last_status["power"] = True
            logger.info(f"Turned on bulb at {self.config.ip}:{self.config.port}")
        
        return response.success
    
    async def turn_off(self) -> bool:
        """Turn off the bulb."""
        command = BulbCommand(command="set_power", params={"power": False})
        response = await self.send_command(command)
        
        if response.success:
            self.last_status["power"] = False
            logger.info(f"Turned off bulb at {self.config.ip}:{self.config.port}")
        
        return response.success
    
    async def set_brightness(self, brightness: int) -> bool:
        """Set bulb brightness (0-100)."""
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be between 0 and 100")
        
        command = BulbCommand(command="set_brightness", params={"brightness": brightness})
        response = await self.send_command(command)
        
        if response.success:
            self.last_status["brightness"] = brightness
            logger.info(f"Set brightness to {brightness}% on bulb at {self.config.ip}:{self.config.port}")
        
        return response.success
    
    async def set_color_rgb(self, r: int, g: int, b: int) -> bool:
        """Set bulb color using RGB values (0-255)."""
        if not all(0 <= val <= 255 for val in [r, g, b]):
            raise ValueError("RGB values must be between 0 and 255")
        
        command = BulbCommand(
            command="set_color", 
            params={"color": {"r": r, "g": g, "b": b}}
        )
        response = await self.send_command(command)
        
        if response.success:
            self.last_status["color"] = {"r": r, "g": g, "b": b}
            logger.info(f"Set color to RGB({r}, {g}, {b}) on bulb at {self.config.ip}:{self.config.port}")
        
        return response.success
    
    async def set_color_hex(self, hex_color: str) -> bool:
        """Set bulb color using hex string (e.g., '#FF0000')."""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters")
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return await self.set_color_rgb(r, g, b)
        except ValueError:
            raise ValueError("Invalid hex color format")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current bulb status."""
        command = BulbCommand(command="get_status")
        response = await self.send_command(command)
        
        if response.success and response.data:
            # Update local status with fresh data
            self.last_status.update(response.data)
            self.last_status["connected"] = True
        else:
            # Mark as disconnected if we can't get status
            self.last_status["connected"] = False
        
        return self.last_status.copy()
    
    async def ping(self) -> bool:
        """Ping the bulb to check connectivity."""
        command = BulbCommand(command="ping")
        response = await self.send_command(command)
        return response.success
    
    def get_last_status(self) -> Dict[str, Any]:
        """Get the last known status without network call."""
        return self.last_status.copy()
    
    def get_config(self) -> BulbConfig:
        """Get bulb configuration."""
        return self.config
    
    async def close(self) -> None:
        """Close the UDP connection."""
        self.running = False
        
        # Cancel all pending commands
        for future in self.pending_commands.values():
            if not future.done():
                future.cancel()
        self.pending_commands.clear()
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        logger.info(f"Closed connection to bulb at {self.config.ip}:{self.config.port}") 