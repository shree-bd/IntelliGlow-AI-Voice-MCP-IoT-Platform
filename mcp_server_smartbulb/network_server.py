#!/usr/bin/env python3
"""
Network-Enabled Smart Bulb MCP Server

This server implements real UDP networking to communicate with actual smart bulbs,
matching the architecture of the TypeScript implementation.

Architecture:
Phone/AI → MCP Server → UDP Network → Smart Bulb (192.168.1.45:4000)
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from .udp_client import UDPBulbClient, BulbConfig
from .bulb_discovery import BulbDiscovery

# Configuration from environment
DEFAULT_BULB_IP = os.getenv('BULB_IP', '192.168.1.45')
DEFAULT_BULB_PORT = int(os.getenv('BULB_PORT', '4000'))

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
discovery = BulbDiscovery()
default_bulb: Optional[UDPBulbClient] = None

# Create FastMCP app instance
app = FastMCP("Network Smart Bulb Controller")


async def initialize_default_bulb():
    """Initialize connection to the default bulb."""
    global default_bulb
    try:
        default_bulb = await discovery.connect_to_bulb(DEFAULT_BULB_IP, DEFAULT_BULB_PORT)
        logger.info(f"🔌 Connected to default bulb at {DEFAULT_BULB_IP}:{DEFAULT_BULB_PORT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to default bulb: {e}")


def get_bulb(ip: Optional[str] = None, port: Optional[int] = None) -> UDPBulbClient:
    """Get bulb instance (default or specific)."""
    if ip and port:
        bulb = discovery.get_bulb(ip, port)
        if not bulb:
            raise ValueError(f"No connection to bulb at {ip}:{port}")
        return bulb
    
    if not default_bulb:
        raise ValueError("No default bulb connection available")
    
    return default_bulb


@app.tool()
async def discover_bulbs(timeout: Optional[float] = 5.0) -> Dict[str, Any]:
    """
    Discover smart bulbs on the network.
    
    Args:
        timeout: Discovery timeout in seconds (default: 5.0)
        
    Returns:
        List of discovered bulbs with their network information
    """
    try:
        logger.info(f"🔍 Scanning network for smart bulbs (timeout: {timeout}s)...")
        discovered = await discovery.discover_bulbs(timeout)
        
        result = []
        for bulb in discovered:
            result.append({
                "ip": bulb.ip,
                "port": bulb.port,
                "response_time": bulb.response_time
            })
        
        return {
            "success": True,
            "discovered_bulbs": result,
            "count": len(result),
            "message": f"Found {len(result)} smart bulbs on the network"
        }
    except Exception as e:
        logger.error(f"❌ Discovery failed: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def connect_to_bulb(ip: str, port: int) -> Dict[str, Any]:
    """
    Connect to a specific smart bulb.
    
    Args:
        ip: IP address of the bulb
        port: Port number of the bulb
        
    Returns:
        Connection status and bulb information
    """
    try:
        client = await discovery.connect_to_bulb(ip, port)
        status = await client.get_status()
        
        return {
            "success": True,
            "message": f"Successfully connected to bulb at {ip}:{port}",
            "bulb": {
                "address": f"{ip}:{port}",
                "status": status
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to connect to {ip}:{port}: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def turn_on_bulb(ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Turn on a smart bulb via UDP network communication.
    
    Args:
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Success status and updated bulb information
    """
    try:
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"💡 Turning ON bulb at {config.ip}:{config.port}...")
        success = await bulb.turn_on()
        
        if success:
            status = await bulb.get_status()
            return {
                "success": True,
                "message": f"Turned ON bulb at {config.ip}:{config.port}",
                "bulb": {
                    "address": f"{config.ip}:{config.port}",
                    "status": status
                }
            }
        else:
            return {"success": False, "error": "Failed to turn on bulb"}
            
    except Exception as e:
        logger.error(f"❌ Error turning on bulb: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def turn_off_bulb(ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Turn off a smart bulb via UDP network communication.
    
    Args:
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Success status and updated bulb information
    """
    try:
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"🌑 Turning OFF bulb at {config.ip}:{config.port}...")
        success = await bulb.turn_off()
        
        if success:
            status = await bulb.get_status()
            return {
                "success": True,
                "message": f"Turned OFF bulb at {config.ip}:{config.port}",
                "bulb": {
                    "address": f"{config.ip}:{config.port}",
                    "status": status
                }
            }
        else:
            return {"success": False, "error": "Failed to turn off bulb"}
            
    except Exception as e:
        logger.error(f"❌ Error turning off bulb: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def set_bulb_brightness(brightness: int, ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Set the brightness of a smart bulb via UDP network communication.
    
    Args:
        brightness: Brightness level (0-100)
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Success status and updated bulb information
    """
    try:
        if not 0 <= brightness <= 100:
            return {"success": False, "error": "Brightness must be between 0 and 100"}
        
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"🔆 Setting brightness to {brightness}% on bulb at {config.ip}:{config.port}...")
        success = await bulb.set_brightness(brightness)
        
        if success:
            status = await bulb.get_status()
            return {
                "success": True,
                "message": f"Set brightness to {brightness}% on bulb at {config.ip}:{config.port}",
                "bulb": {
                    "address": f"{config.ip}:{config.port}",
                    "status": status
                }
            }
        else:
            return {"success": False, "error": "Failed to set brightness"}
            
    except Exception as e:
        logger.error(f"❌ Error setting brightness: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def set_bulb_color(color: str, ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Set the color of a smart bulb via UDP network communication.
    
    Args:
        color: Hex color code (e.g., '#FF0000' for red)
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Success status and updated bulb information
    """
    try:
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"🎨 Setting color to {color} on bulb at {config.ip}:{config.port}...")
        success = await bulb.set_color_hex(color)
        
        if success:
            status = await bulb.get_status()
            return {
                "success": True,
                "message": f"Set color to {color} on bulb at {config.ip}:{config.port}",
                "bulb": {
                    "address": f"{config.ip}:{config.port}",
                    "status": status
                }
            }
        else:
            return {"success": False, "error": "Failed to set color"}
            
    except Exception as e:
        logger.error(f"❌ Error setting color: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_bulb_status(ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the current status of a smart bulb via UDP network communication.
    
    Args:
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Current bulb status including power, brightness, color, and connectivity
    """
    try:
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"📊 Getting status from bulb at {config.ip}:{config.port}...")
        status = await bulb.get_status()
        
        return {
            "success": True,
            "bulb": {
                "address": f"{config.ip}:{config.port}",
                "status": status
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting bulb status: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def get_all_bulb_statuses() -> Dict[str, Any]:
    """
    Get status of all connected smart bulbs.
    
    Returns:
        Status of all connected bulbs
    """
    try:
        logger.info("📊 Getting status from all connected bulbs...")
        statuses = await discovery.get_all_bulb_statuses()
        
        return {
            "success": True,
            "bulbs": statuses,
            "count": len(statuses),
            "message": f"Retrieved status from {len(statuses)} connected bulbs"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting all bulb statuses: {e}")
        return {"success": False, "error": str(e)}


@app.tool()
async def ping_bulb(ip: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Ping a smart bulb to check network connectivity.
    
    Args:
        ip: IP address of the bulb (optional, uses default if not provided)
        port: Port number of the bulb (optional, uses default if not provided)
        
    Returns:
        Ping result and connectivity status
    """
    try:
        bulb = get_bulb(ip, port)
        config = bulb.get_config()
        
        logger.info(f"🏓 Pinging bulb at {config.ip}:{config.port}...")
        success = await bulb.ping()
        
        return {
            "success": success,
            "bulb": f"{config.ip}:{config.port}",
            "message": f"Ping {'successful' if success else 'failed'} for bulb at {config.ip}:{config.port}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error pinging bulb: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Synchronous entry point for the command line script.
    """
    import sys
    try:
        logger.info("🚀 Starting IntelliGlow MCP Server...")
        
        # Initialize default bulb connection in sync context
        async def init_and_run():
            await initialize_default_bulb()
            logger.info("📡 IntelliGlow ready for UDP network communication with smart bulbs")
            logger.info(f"🏠 Default bulb: {DEFAULT_BULB_IP}:{DEFAULT_BULB_PORT}")
            logger.info("💡 IntelliGlow - Smart lighting, brilliantly simple!")
        
        # Use FastMCP's built-in run method (handles async internally)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("👋 IntelliGlow shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ IntelliGlow error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Entry point when running the server directly.
    """
    main() 