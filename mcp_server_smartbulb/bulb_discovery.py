"""
Bulb Discovery for Smart Bulb Network

This module provides network discovery functionality to find and connect
to smart bulbs on the local network, matching the TypeScript implementation.
"""

import asyncio
import json
import socket
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .udp_client import UDPBulbClient, BulbConfig

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredBulb:
    """Information about a discovered bulb."""
    ip: str
    port: int
    mac_address: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    response_time: Optional[float] = None


class BulbDiscovery:
    """
    Network discovery for smart bulbs.
    
    This matches the TypeScript BulbDiscovery class functionality,
    providing network scanning and bulb management capabilities.
    """
    
    def __init__(self):
        self.connected_bulbs: Dict[str, UDPBulbClient] = {}  # key: "ip:port"
        self.discovery_socket: Optional[socket.socket] = None
        
    def _get_bulb_key(self, ip: str, port: int) -> str:
        """Generate a unique key for a bulb."""
        return f"{ip}:{port}"
    
    async def discover_bulbs(self, timeout: float = 5.0, port_range: Tuple[int, int] = (4000, 4010)) -> List[DiscoveredBulb]:
        """
        Discover smart bulbs on the local network.
        
        This matches the TypeScript discoverBulbs functionality.
        """
        discovered = []
        
        # Get local network range
        local_ip = self._get_local_ip()
        if not local_ip:
            logger.error("Could not determine local IP address")
            return discovered
        
        # Extract network base (e.g., 192.168.1.)
        ip_parts = local_ip.split('.')
        network_base = '.'.join(ip_parts[:3]) + '.'
        
        logger.info(f"Scanning network {network_base}0-255 for smart bulbs...")
        
        # Create discovery tasks
        tasks = []
        for host in range(1, 255):  # Skip .0 and .255
            ip = f"{network_base}{host}"
            for port in range(port_range[0], port_range[1] + 1):
                task = self._check_bulb_at_address(ip, port, timeout)
                tasks.append(task)
        
        # Run all discovery tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful discoveries
        for result in results:
            if isinstance(result, DiscoveredBulb):
                discovered.append(result)
                logger.info(f"Discovered bulb at {result.ip}:{result.port}")
        
        logger.info(f"Discovery completed. Found {len(discovered)} bulbs.")
        return discovered
    
    async def _check_bulb_at_address(self, ip: str, port: int, timeout: float) -> Optional[DiscoveredBulb]:
        """Check if there's a smart bulb at the given address."""
        try:
            # Create a temporary client for testing
            config = BulbConfig(ip=ip, port=port, timeout=timeout / 10)  # Shorter timeout for discovery
            client = UDPBulbClient(config)
            
            await client.connect()
            
            # Try to get device info
            status = await client.get_status()
            
            await client.close()
            
            # If we got a response, it's likely a smart bulb
            if status.get('connected', False):
                return DiscoveredBulb(
                    ip=ip,
                    port=port,
                    response_time=timeout / 10  # Approximate response time
                )
                
        except Exception:
            # Silently ignore failed connections during discovery
            pass
        
        return None
    
    def _get_local_ip(self) -> Optional[str]:
        """Get the local IP address."""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return None
    
    async def connect_to_bulb(self, ip: str, port: int) -> UDPBulbClient:
        """
        Connect to a specific bulb.
        
        This matches the TypeScript connectToBulb functionality.
        """
        bulb_key = self._get_bulb_key(ip, port)
        
        # Check if already connected
        if bulb_key in self.connected_bulbs:
            logger.info(f"Already connected to bulb at {ip}:{port}")
            return self.connected_bulbs[bulb_key]
        
        # Create new connection
        config = BulbConfig(ip=ip, port=port)
        client = UDPBulbClient(config)
        
        try:
            await client.connect()
            self.connected_bulbs[bulb_key] = client
            logger.info(f"Successfully connected to bulb at {ip}:{port}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to connect to bulb at {ip}:{port}: {e}")
            raise
    
    def get_bulb(self, ip: str, port: int) -> Optional[UDPBulbClient]:
        """Get an existing bulb connection."""
        bulb_key = self._get_bulb_key(ip, port)
        return self.connected_bulbs.get(bulb_key)
    
    def get_all_bulbs(self) -> Dict[str, UDPBulbClient]:
        """Get all connected bulbs."""
        return self.connected_bulbs.copy()
    
    async def get_all_bulb_statuses(self) -> List[Dict[str, any]]:
        """
        Get status of all connected bulbs.
        
        This matches the TypeScript getAllBulbStatuses functionality.
        """
        statuses = []
        
        for bulb_key, client in self.connected_bulbs.items():
            try:
                status = await client.get_status()
                config = client.get_config()
                
                statuses.append({
                    "bulb": f"{config.ip}:{config.port}",
                    "status": status
                })
            except Exception as e:
                logger.error(f"Failed to get status for bulb {bulb_key}: {e}")
                statuses.append({
                    "bulb": bulb_key,
                    "status": {"connected": False, "error": str(e)}
                })
        
        return statuses
    
    async def disconnect_bulb(self, ip: str, port: int) -> bool:
        """Disconnect from a specific bulb."""
        bulb_key = self._get_bulb_key(ip, port)
        
        if bulb_key in self.connected_bulbs:
            client = self.connected_bulbs[bulb_key]
            await client.close()
            del self.connected_bulbs[bulb_key]
            logger.info(f"Disconnected from bulb at {ip}:{port}")
            return True
        
        return False
    
    async def close_all_connections(self) -> None:
        """Close all bulb connections."""
        for client in self.connected_bulbs.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing bulb connection: {e}")
        
        self.connected_bulbs.clear()
        logger.info("Closed all bulb connections")
    
    def is_connected(self, ip: str, port: int) -> bool:
        """Check if connected to a specific bulb."""
        bulb_key = self._get_bulb_key(ip, port)
        return bulb_key in self.connected_bulbs 