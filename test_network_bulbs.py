#!/usr/bin/env python3
"""
Test script for UDP Network Smart Bulb Communication

This script demonstrates real UDP networking with smart bulbs,
matching the architecture shown in the user's diagram.
"""

import asyncio
import logging
from mcp_server_smartbulb.udp_client import UDPBulbClient, BulbConfig
from mcp_server_smartbulb.bulb_discovery import BulbDiscovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_direct_bulb_connection():
    """Test direct connection to the bulb at 192.168.1.45:4000"""
    print("\n" + "="*60)
    print("🔌 TESTING DIRECT BULB CONNECTION")
    print("="*60)
    
    # Create configuration for the specific bulb
    config = BulbConfig(ip="192.168.1.45", port=4000, timeout=5.0)
    client = UDPBulbClient(config)
    
    try:
        print(f"🔗 Connecting to bulb at {config.ip}:{config.port}...")
        await client.connect()
        print("✅ Connection successful!")
        
        # Test ping
        print("\n🏓 Testing ping...")
        ping_result = await client.ping()
        print(f"Ping result: {'✅ SUCCESS' if ping_result else '❌ FAILED'}")
        
        # Get initial status
        print("\n📊 Getting initial status...")
        status = await client.get_status()
        print(f"Current status: {status}")
        
        # Test turn on
        print("\n💡 Testing turn ON...")
        on_result = await client.turn_on()
        if on_result:
            print("✅ Turned ON successfully")
            await asyncio.sleep(1)  # Wait a moment
            status = await client.get_status()
            print(f"New status: {status}")
        else:
            print("❌ Failed to turn on")
        
        # Test brightness
        print("\n🔆 Testing brightness control...")
        brightness_result = await client.set_brightness(75)
        if brightness_result:
            print("✅ Set brightness to 75% successfully")
            await asyncio.sleep(1)
            status = await client.get_status()
            print(f"New status: {status}")
        else:
            print("❌ Failed to set brightness")
        
        # Test color
        print("\n🎨 Testing color control...")
        color_result = await client.set_color_hex("#FF0000")  # Red
        if color_result:
            print("✅ Set color to red successfully")
            await asyncio.sleep(2)
            status = await client.get_status()
            print(f"New status: {status}")
        else:
            print("❌ Failed to set color")
        
        # Test turn off
        print("\n🌑 Testing turn OFF...")
        off_result = await client.turn_off()
        if off_result:
            print("✅ Turned OFF successfully")
            await asyncio.sleep(1)
            status = await client.get_status()
            print(f"Final status: {status}")
        else:
            print("❌ Failed to turn off")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        await client.close()
        print("🔌 Connection closed")


async def test_network_discovery():
    """Test network discovery for smart bulbs"""
    print("\n" + "="*60)
    print("🔍 TESTING NETWORK DISCOVERY")
    print("="*60)
    
    discovery = BulbDiscovery()
    
    try:
        print("🌐 Scanning network for smart bulbs...")
        discovered = await discovery.discover_bulbs(timeout=10.0)
        
        if discovered:
            print(f"✅ Found {len(discovered)} smart bulbs:")
            for bulb in discovered:
                print(f"  • {bulb.ip}:{bulb.port} (response: {bulb.response_time:.2f}s)")
                
                # Try to connect to discovered bulb
                print(f"    🔗 Connecting to {bulb.ip}:{bulb.port}...")
                try:
                    client = await discovery.connect_to_bulb(bulb.ip, bulb.port)
                    status = await client.get_status()
                    print(f"    ✅ Connected! Status: {status}")
                except Exception as e:
                    print(f"    ❌ Connection failed: {e}")
        else:
            print("🔍 No smart bulbs found on the network")
            print("💡 Make sure your bulb is:")
            print("   • Connected to the same network")
            print("   • Powered on and responsive")
            print("   • Listening on the expected port (4000)")
            
    except Exception as e:
        print(f"❌ Discovery error: {e}")
    finally:
        await discovery.close_all_connections()


async def test_mcp_simulation():
    """Simulate MCP commands that an AI would make"""
    print("\n" + "="*60)
    print("🤖 SIMULATING AI/MCP COMMANDS")
    print("="*60)
    
    discovery = BulbDiscovery()
    
    try:
        # Command 1: Discover bulbs (what AI would do first)
        print("🤖 AI Command: 'Find all smart bulbs in my home'")
        discovered = await discovery.discover_bulbs(timeout=5.0)
        print(f"📡 Response: Found {len(discovered)} bulbs")
        
        if not discovered:
            # Try the known bulb directly
            print("🤖 AI Command: 'Connect to bulb at 192.168.1.45:4000'")
            try:
                client = await discovery.connect_to_bulb("192.168.1.45", 4000)
                print("📡 Response: Connected successfully")
                discovered = [type('DiscoveredBulb', (), {'ip': '192.168.1.45', 'port': 4000})()]
            except Exception as e:
                print(f"📡 Response: Connection failed - {e}")
                return
        
        if discovered:
            bulb = discovered[0]
            client = await discovery.connect_to_bulb(bulb.ip, bulb.port)
            
            # Command 2: Turn on the lights
            print("\n🤖 AI Command: 'Turn on the lights'")
            success = await client.turn_on()
            print(f"📡 Response: {'Lights turned on' if success else 'Failed to turn on lights'}")
            
            # Command 3: Make them bright
            print("\n🤖 AI Command: 'Make the lights 90% bright'")
            success = await client.set_brightness(90)
            print(f"📡 Response: {'Brightness set to 90%' if success else 'Failed to set brightness'}")
            
            # Command 4: Change color
            print("\n🤖 AI Command: 'Change the color to blue'")
            success = await client.set_color_hex("#0000FF")
            print(f"📡 Response: {'Color changed to blue' if success else 'Failed to change color'}")
            
            # Command 5: Get status
            print("\n🤖 AI Command: 'What's the current status of the lights?'")
            status = await client.get_status()
            print(f"📡 Response: {status}")
            
            await asyncio.sleep(3)  # Let the bulb stay blue for a moment
            
            # Command 6: Turn off
            print("\n🤖 AI Command: 'Turn off all the lights'")
            success = await client.turn_off()
            print(f"📡 Response: {'Lights turned off' if success else 'Failed to turn off lights'}")
            
    except Exception as e:
        print(f"❌ MCP simulation error: {e}")
    finally:
        await discovery.close_all_connections()


async def main():
    """Main test runner"""
    print("🧪 SMART BULB UDP NETWORK TESTING")
    print("Architecture: AI → MCP → UDP → Smart Bulb (192.168.1.45:4000)")
    print("This matches your TypeScript implementation!")
    
    # Test 1: Direct connection
    await test_direct_bulb_connection()
    
    # Test 2: Network discovery
    await test_network_discovery()
    
    # Test 3: MCP simulation
    await test_mcp_simulation()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
    print("Now you can use the MCP server with real UDP networking!")
    print("Use: python -m mcp_server_smartbulb.network_server")


if __name__ == "__main__":
    asyncio.run(main()) 