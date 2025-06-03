"""
MCP Smart Bulb Server with UDP Networking

A Model Context Protocol server for controlling real smart bulbs via UDP network communication.
This server allows AI assistants to control actual hardware through standardized MCP tools.

Architecture:
Phone/AI → MCP Server → UDP Network → Smart Bulb (192.168.1.45:4000)
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main UDP networking components
from .network_server import app, main
from .udp_client import UDPBulbClient, BulbConfig, BulbCommand, BulbResponse
from .bulb_discovery import BulbDiscovery, DiscoveredBulb

__all__ = [
    "app",
    "main",
    "UDPBulbClient",
    "BulbConfig", 
    "BulbCommand",
    "BulbResponse",
    "BulbDiscovery",
    "DiscoveredBulb",
] 